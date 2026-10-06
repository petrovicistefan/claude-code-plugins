#!/usr/bin/env python3
"""Check Dockerfiles for image size, build cache and security problems.

  dockerfile_check.py                  check ./Dockerfile and its .dockerignore
  dockerfile_check.py path/Dockerfile  check a specific file (Containerfile and *.Dockerfile work too)
  dockerfile_check.py <dir>            check every Dockerfile under a folder
"""
import os
import re
import sys

SKIP_DIRS = {"node_modules", ".git", "vendor", "dist", "build"}
FAT_BASES = re.compile(r"^(node|python|ruby|golang|openjdk|maven|gradle|php|rust|ubuntu|debian|centos|fedora)(:[\w.\-]*)?$", re.I)
SECRET_NAME = re.compile(r"(PASSWORD|PASSWD|SECRET|TOKEN|API_?KEY|PRIVATE_?KEY|ACCESS_?KEY|CREDENTIALS)", re.I)
IGNORE_WANTED = {
    ".git": "the git history",
    "node_modules": "local node_modules (also breaks native modules built for another OS)",
    ".env": "local secrets",
}


def logical_lines(text):
    """Join continuation lines; return [(line_no, instruction, args)]."""
    out, buf, start = [], "", None
    escape = "\\"
    m = re.search(r"^#\s*escape\s*=\s*(\S)", text, re.M | re.I)
    if m:
        escape = m.group(1)
    for i, raw in enumerate(text.splitlines(), 1):
        line = raw.rstrip()
        if not buf and (not line.strip() or line.lstrip().startswith("#")):
            continue
        if buf and line.lstrip().startswith("#"):
            continue
        if start is None:
            start = i
        if line.endswith(escape):
            buf += line[:-1] + " "
            continue
        buf += line
        parts = buf.strip().split(None, 1)
        out.append((start, parts[0].upper(), parts[1] if len(parts) > 1 else ""))
        buf, start = "", None
    if buf:
        parts = buf.strip().split(None, 1)
        out.append((start, parts[0].upper(), parts[1] if len(parts) > 1 else ""))
    return out


def check(path):
    text = open(path, encoding="utf-8", errors="replace").read()
    lines = logical_lines(text)
    findings = []

    def add(line, kind, msg):
        findings.append((path, line, kind, msg))

    froms = [(ln, args) for ln, ins, args in lines if ins == "FROM"]
    stages = len(froms)
    last_from = froms[-1] if froms else (1, "")
    stage_names = {m.group(1).lower() for _, a in froms for m in [re.search(r"\bAS\s+(\S+)", a, re.I)] if m}

    for ln, args in froms:
        image = re.sub(r"--platform=\S+\s*", "", args).split()[0] if args.strip() else ""
        if image.lower() in stage_names or image.lower() == "scratch" or image.startswith("$"):
            continue
        name, _, tag = image.partition("@")[0].partition(":")
        if "@sha256:" in image:
            pass
        elif not tag or tag == "latest":
            add(ln, "reproducibility", f"`{image}` is not pinned; use a version tag (and ideally a digest) so rebuilds are repeatable")
    if froms:
        final = re.sub(r"--platform=\S+\s*", "", last_from[1]).split()[0]
        if FAT_BASES.match(final) and not re.search(r"(slim|alpine|distroless|minimal|chiseled|ubi-micro)", final, re.I):
            add(last_from[0], "size", f"final image is based on full `{final}`; a `-slim`, `-alpine` or distroless variant is usually several hundred MB smaller")
    build_tools = re.search(r"\b(npm (ci|install)|yarn( install)?|pnpm install|pip install|go build|mvn |gradle |cargo build|composer install|bundle install|tsc\b|npm run build|vite build|next build)", text)
    if stages == 1 and build_tools:
        add(froms[0][0] if froms else 1, "size", "single-stage build: compilers, dev dependencies and caches end up in the final image. Build in one stage and `COPY --from=` only the output into a small runtime stage")

    # cache order: COPY . . before dependency install
    copied_all_at = None
    final_stage_start = froms[-1][0] if froms else 0
    stage_start = 0
    for ln, ins, args in lines:
        if ins == "FROM":
            stage_start = ln
            copied_all_at = None
        if ins in ("COPY", "ADD") and re.search(r"(^|\s)\.\s+\S+\s*$", args) and "--from" not in args:
            copied_all_at = copied_all_at or ln
        if ins == "RUN" and copied_all_at and re.search(r"\b(npm (ci|install)|yarn install|yarn\s*$|pnpm install|pip install -r|poetry install|bundle install|composer install|go mod download|mvn dependency)", args):
            add(copied_all_at, "cache", f"the whole source is copied before dependencies are installed (line {ln}); any code change re-installs everything. Copy the manifest and lockfile first, install, then copy the rest")
            copied_all_at = None

    run_count = 0
    for ln, ins, args in lines:
        a = args
        if ins == "ADD" and not re.search(r"https?://|\.tar(\.\w+)?(\s|$)|\.tgz", a) and "--checksum" not in a:
            add(ln, "clarity", "use COPY instead of ADD for local files; ADD also extracts archives and fetches URLs")
        if ins == "ADD" and re.search(r"https?://", a) and "--checksum" not in a:
            add(ln, "security", "ADD from a URL without `--checksum`; the download is not verified")
        if ins == "RUN":
            run_count += 1
            if re.search(r"apt-get install", a):
                if "--no-install-recommends" not in a:
                    add(ln, "size", "apt-get install without `--no-install-recommends`")
                if not re.search(r"rm -rf /var/lib/apt/lists", a) and "--mount=type=cache" not in a:
                    add(ln, "size", "apt lists are not removed in the same RUN (`&& rm -rf /var/lib/apt/lists/*`)")
                if not re.search(r"apt-get update", a):
                    add(ln, "reliability", "apt-get install without `apt-get update` in the same RUN uses a stale cached index")
                if re.search(r"apt-get\s+install(?![^&;]*-y)", a):
                    add(ln, "reliability", "apt-get install without `-y` waits for input and fails the build")
            if re.search(r"apt-get (upgrade|dist-upgrade)", a):
                add(ln, "reproducibility", "apt-get upgrade inside the image; prefer a newer base image tag")
            if re.search(r"\bapk add\b", a) and "--no-cache" not in a:
                add(ln, "size", "apk add without `--no-cache`")
            if re.search(r"\b(yum|dnf) install\b", a) and not re.search(r"(yum|dnf) clean all", a):
                add(ln, "size", "yum/dnf install without `clean all` in the same RUN")
            if re.search(r"\bpip3? install\b", a) and "--no-cache-dir" not in a and "--mount=type=cache" not in a and "PIP_NO_CACHE_DIR" not in text:
                add(ln, "size", "pip install without `--no-cache-dir` keeps the wheel cache in the layer")
            if re.search(r"\bnpm install\b", a) and not re.search(r"npm install\s+(-g|--global)", a):
                add(ln, "reproducibility", "`npm install` in an image; `npm ci` installs exactly the lockfile")
            if re.search(r"\bnpm (ci|install)\b", a) and stages == 1 and not re.search(r"--(omit=dev|only=prod|production)", a) and "NODE_ENV=production" not in text:
                add(ln, "size", "dev dependencies are installed into the final image; use `npm ci --omit=dev` or a multi-stage build")
            if re.search(r"curl[^|]*\|\s*(ba|z)?sh", a) or re.search(r"wget[^|]*\|\s*(ba|z)?sh", a):
                add(ln, "security", "piping a downloaded script into a shell; download, verify the checksum, then run")
            if re.search(r"chmod\s+(-R\s+)?777", a):
                add(ln, "security", "chmod 777 makes files writable by every user in the container")
            if re.search(r"\bsudo\b", a):
                add(ln, "clarity", "sudo is not needed in RUN (it already runs as the current USER) and adds a package")
            if re.search(r"^\s*cd\s", a):
                add(ln, "clarity", "use WORKDIR instead of `cd` in RUN")
        if ins in ("ENV", "ARG"):
            for name in re.findall(r"([A-Za-z_][\w]*)\s*=", a) or [a.split()[0] if a.split() else ""]:
                if SECRET_NAME.search(name) and not re.search(r"(_FILE|_PATH|_URL|_ID)$", name, re.I):
                    add(ln, "security", f"{ins} {name}: values of ENV and ARG are stored in the image history. Use `RUN --mount=type=secret` instead")
        if ins == "COPY" and re.search(r"(^|\s)(\.env|id_rsa|\.npmrc|\.pypirc|credentials)\b", a):
            add(ln, "security", f"COPY of a credentials file ({a.split()[0]}) bakes it into a layer")
        if ins == "EXPOSE" and re.search(r"\b22\b", a):
            add(ln, "security", "port 22 exposed; containers should not run an SSH server")
        if ins == "CMD" or ins == "ENTRYPOINT":
            if not a.strip().startswith("["):
                add(ln, "reliability", f"{ins} in shell form runs under /bin/sh, so the app does not receive SIGTERM and stops only after the 10 s timeout. Use the JSON form: {ins} [\"node\", \"server.js\"]")

    users = [(ln, args) for ln, ins, args in lines if ins == "USER" and ln >= final_stage_start]
    final_base = re.sub(r"--platform=\S+\s*", "", last_from[1]).split()[0] if froms else ""
    if not users and "distroless" not in final_base and ":nonroot" not in final_base and final_base.lower() != "scratch":
        add(final_stage_start or 1, "security", "the final stage has no USER, so the app runs as root. Add a non-root user (official node images ship `USER node`)")
    elif users and users[-1][1].strip() in ("root", "0", "0:0"):
        add(users[-1][0], "security", "the final USER is root")
    if not any(ins == "HEALTHCHECK" for _, ins, _ in lines):
        add(len(text.splitlines()), "reliability", "no HEALTHCHECK (fine on Kubernetes, which uses its own probes; useful for docker compose and swarm)")
    if run_count > 8:
        add(1, "size", f"{run_count} RUN instructions; consecutive package installs can be merged to cut layers")

    ctx = os.path.dirname(os.path.abspath(path))
    ign = os.path.join(ctx, ".dockerignore")
    copies_context = re.search(r"^\s*(COPY|ADD)\s+(--\S+\s+)*\.\s", text, re.M | re.I)
    if not os.path.exists(ign) and not os.path.exists(path + ".dockerignore"):
        if copies_context:
            add(1, "size", "no .dockerignore next to the Dockerfile and the whole folder is copied; .git, node_modules and .env end up in the build context")
    else:
        content = open(ign if os.path.exists(ign) else path + ".dockerignore", encoding="utf-8", errors="replace").read()
        entries = {l.strip().strip("/").lstrip("*/") for l in content.splitlines() if l.strip() and not l.startswith("#")}
        for want, why in IGNORE_WANTED.items():
            if want == "node_modules" and not os.path.exists(os.path.join(ctx, "package.json")):
                continue
            if want not in entries and not any(e.startswith(want) for e in entries) and "*" not in entries:
                add(1, "size", f".dockerignore does not exclude `{want}` ({why})")
    return findings


def find(args):
    if not args:
        args = ["Dockerfile"] if os.path.exists("Dockerfile") else ["."]
    for a in args:
        if os.path.isfile(a):
            yield a
        elif os.path.isdir(a):
            for dirpath, dirs, names in os.walk(a):
                dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
                for n in sorted(names):
                    if n in ("Dockerfile", "Containerfile") or n.endswith(".Dockerfile") or n.startswith("Dockerfile."):
                        yield os.path.join(dirpath, n)


def main():
    if any(a in ("-h", "--help") for a in sys.argv[1:]):
        print(__doc__)
        return
    files = list(find(sys.argv[1:]))
    if not files:
        sys.exit("No Dockerfile found.")
    order = {"security": 0, "size": 1, "cache": 2, "reliability": 3, "reproducibility": 4, "clarity": 5}
    total = 0
    for f in files:
        fs = sorted(set(check(f)), key=lambda x: (x[1], order[x[2]]))
        total += len(fs)
        for path, ln, kind, msg in fs:
            print(f"{path}:{ln}: [{kind}] {msg}")
    print(f"\n{len(files)} Dockerfile(s), {total} findings")


if __name__ == "__main__":
    main()
