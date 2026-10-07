---
name: iac-reviewer
description: "Use when reviewing, writing or planning Terraform or OpenTofu code, to find security, cost and hygiene problems and summarize a plan by risk."
---

# IaC Reviewer

Scripts: `${CLAUDE_SKILL_DIR}` is the folder that contains this file. If your agent does not define it, use the folder where this `SKILL.md` is located.

Review infrastructure-as-code (Terraform and OpenTofu) the way a careful teammate would before merge.

## 1. Run the static check

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/iac_check.py            # every .tf file under the current folder
python3 ${CLAUDE_SKILL_DIR}/scripts/iac_check.py infra/prod
```

Each finding has a severity, file, line and fix. The checks read text, so confirm each in context: a public bucket for a static site or a `0.0.0.0/0` rule on port 443 of a public load balancer is intended. Do not "fix" those; say why they are fine.

Report **high** findings first (credentials in code, SSH/RDP/database ports open to the internet, public databases, `Action: *`, encryption off), then medium and low.

## 2. Validate and plan (read-only)

Only if `terraform` or `tofu` is installed:

```bash
terraform fmt -check -recursive
terraform init -backend=false      # skip the backend so no state is touched
terraform validate
terraform plan -input=false -lock=false -out=/tmp/plan.bin   # needs credentials; ask first if the folder uses a real backend
terraform show -no-color /tmp/plan.bin
```

Ask before running `plan` against a folder with a remote backend or production credentials, since it reads real infrastructure and state. Summarize the plan as: resources to **destroy or replace** (first, with the reason a replace is forced), then changes in place, then creates. Flag changes to databases, IAM, networking and anything marked `prevent_destroy`.

**Never run `terraform apply`, `destroy`, `state rm`, `import` or `taint`.** Tell the user the command and let them run it.

## 3. Fix

Make the smallest change that removes the finding:

- Secrets: replace the literal with `variable "x" { sensitive = true }` supplied from the environment or a secrets manager, or let the service manage the password (`manage_master_user_password = true` on RDS).
- Open ports: replace `0.0.0.0/0` with a variable holding the real CIDR, a security-group reference or a VPN/bastion range.
- Encryption: add `storage_encrypted = true` / `encrypted = true` and a `kms_key_id` if the team uses a managed key. Note that enabling encryption on an existing database forces a replace; say so before changing it.
- Pin modules and providers: `version = "~> 5.0"` for registry modules, `?ref=v1.2.3` for git modules, `required_version` and `required_providers` with `~>`.
- Cost: set `retention_in_days` on log groups, review NAT gateways per AZ, add tags (`owner`, `env`, `cost-center`).

Show the diff for each file and re-run the script to confirm the finding is gone. Do not claim a monthly saving without a price from the user's own plan or pricing page.
