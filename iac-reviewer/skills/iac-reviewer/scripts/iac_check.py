#!/usr/bin/env python3
"""Check Terraform / OpenTofu files for common security, cost and hygiene problems.

  iac_check.py                 scan every .tf file under the current folder
  iac_check.py <file-or-dir>   scan specific files or folders

The checks are text based, so no Terraform install is needed. Each finding has a
file, a line, a severity and a fix. Confirm each one in context before changing it.
"""
import os
import re
import sys

SKIP_DIRS = {".terraform", ".git", "node_modules", ".terragrunt-cache"}


def tf_files(args):
    for a in args or ["."]:
        if os.path.isfile(a):
            yield a
        for root, dirs, files in os.walk(a):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for f in sorted(files):
                if f.endswith(".tf"):
                    yield os.path.join(root, f)


def blocks(lines):
    """Yield (kind, type, name, start, end) for top-level resource/module/provider blocks."""
    i = 0
    while i < len(lines):
        m = re.match(r'^(resource|module|provider|data|terraform)\s*(?:"([^"]+)")?\s*(?:"([^"]+)")?\s*\{', lines[i])
        if m:
            depth, j = 0, i
            while j < len(lines):
                depth += lines[j].count("{") - lines[j].count("}")
                if depth <= 0:
                    break
                j += 1
            yield m.group(1), m.group(2) or "", m.group(3) or "", i, j
            i = j
        i += 1


def check_file(path):
    out = []
    with open(path, encoding="utf-8", errors="replace") as fh:
        lines = fh.read().splitlines()

    def add(i, sev, msg):
        out.append((path, i + 1, sev, msg))

    for kind, rtype, rname, s, e in blocks(lines):
        body = "\n".join(lines[s:e + 1])
        label = f"{rtype}.{rname}" if rname else rtype

        for k in range(s, e + 1):
            line = lines[k]
            if re.search(r"^\s*(password|secret|secret_key|access_key|token|master_password)\s*=\s*\"[^\"$][^\"]*\"", line, re.I):
                add(k, "high", f"{label}: credential written in the file. Use a variable marked `sensitive = true`, a secrets manager or `manage_master_user_password`.")
            if re.search(r"cidr_blocks\s*=\s*\[\s*\"0\.0\.0\.0/0\"", line) or re.search(r"ipv6_cidr_blocks\s*=\s*\[\s*\"::/0\"", line):
                port = re.search(r"(from_port|to_port)\s*=\s*(22|3389|3306|5432|6379|27017)\b", body)
                if port or "ingress" in body:
                    add(k, "high" if port else "medium", f"{label}: open to the whole internet. Restrict the CIDR, especially for SSH, RDP and database ports.")
            if re.search(r"publicly_accessible\s*=\s*true", line):
                add(k, "high", f"{label}: database is publicly accessible. Put it in a private subnet.")
            if re.search(r"\bacl\s*=\s*\"(public-read|public-read-write)\"", line):
                add(k, "high", f"{label}: public S3 ACL. Use a private bucket with a CloudFront or presigned-URL access path.")
            if re.search(r"\"(Action|actions)\"?\s*[:=]\s*\[?\s*\"\*\"", line) or re.search(r"Action\s*=\s*\"\*\"", line):
                add(k, "high", f"{label}: IAM policy allows every action (`*`). List the actions that are needed.")
            if re.search(r"skip_final_snapshot\s*=\s*true", line):
                add(k, "medium", f"{label}: no final snapshot on destroy. Data is lost if the resource is removed.")
            if re.search(r"deletion_protection\s*=\s*false", line):
                add(k, "low", f"{label}: deletion protection off. Turn it on for production databases.")
            if re.search(r"storage_encrypted\s*=\s*false|encrypted\s*=\s*false", line):
                add(k, "high", f"{label}: encryption disabled.")

        if kind == "resource":
            if rtype in ("aws_db_instance", "aws_rds_cluster") and "storage_encrypted" not in body:
                add(s, "medium", f"{label}: `storage_encrypted` not set (default is unencrypted for aws_db_instance).")
            if rtype == "aws_ebs_volume" and "encrypted" not in body:
                add(s, "medium", f"{label}: `encrypted` not set.")
            if rtype == "aws_instance" and "http_tokens" not in body:
                add(s, "low", label + ": no `metadata_options` block with `http_tokens = \"required\"` (IMDSv2).")
            if rtype == "aws_cloudwatch_log_group" and "retention_in_days" not in body:
                add(s, "low", f"{label}: logs are kept forever. Set `retention_in_days` to control cost.")
            if rtype in ("aws_instance", "aws_db_instance", "aws_s3_bucket", "aws_lb") and "tags" not in body:
                add(s, "low", f"{label}: no tags. Tags are needed for cost reports and ownership.")
            if rtype == "aws_nat_gateway":
                add(s, "info", f"{label}: NAT gateways cost per hour plus per GB. Check you need one per AZ.")
        if kind == "module" and "source" in body and "version" not in body:
            src = re.search(r'source\s*=\s*"([^"]+)"', body)
            if src and not src.group(1).startswith((".", "/")) and "?ref=" not in src.group(1):
                add(s, "medium", f"module {rtype}: remote module without `version` or `?ref=`. Pin it.")
        if kind == "terraform" and "required_version" not in body:
            add(s, "low", "terraform block without `required_version`.")
        if kind == "terraform":
            for k in range(s, e + 1):
                if re.search(r"version\s*=\s*\">=", lines[k]) and "required_providers" in body and "required_version" not in lines[k]:
                    add(k, "low", "provider constraint is open-ended (`>=`). Use `~>` to avoid surprise major upgrades.")
    return out, lines


def main():
    findings, files = [], list(tf_files(sys.argv[1:]))
    if not files:
        print("No .tf files found.")
        return 0
    has_backend = False
    for f in files:
        out, lines = check_file(f)
        findings += out
        if any(re.match(r'\s*backend\s+"', l) for l in lines):
            has_backend = True
    if not has_backend:
        findings.append((files[0], 1, "medium", "no remote `backend` block found: state is local, so it cannot be shared or locked."))
    order = {"high": 0, "medium": 1, "low": 2, "info": 3}
    findings.sort(key=lambda x: (order[x[2]], x[0], x[1]))
    for path, line, sev, msg in findings:
        print(f"[{sev.upper():6}] {path}:{line}  {msg}")
    counts = {s: sum(1 for f in findings if f[2] == s) for s in order}
    print(f"\n{len(files)} files, {len(findings)} findings: " + ", ".join(f"{v} {k}" for k, v in counts.items()))
    return 1 if counts["high"] else 0


if __name__ == "__main__":
    sys.exit(main())
