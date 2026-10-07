# IaC Reviewer: Terraform Security and Cost Check

Review Terraform and OpenTofu code for open ports, public buckets, hardcoded secrets, missing encryption, unpinned modules and cost traps, then run validate and plan safely.

## What it does

- A bundled Python script reads every `.tf` file and flags credentials written in code, security groups open to `0.0.0.0/0` (SSH, RDP and database ports first), public S3 ACLs, public databases, IAM policies with `Action: *`, disabled or missing encryption, missing IMDSv2, no final snapshot, log groups kept forever, untagged resources, unpinned modules and providers, and a missing remote backend.
- If `terraform` or `tofu` is installed, Claude runs `fmt -check`, `validate` and `plan` and groups the plan by what is created, changed and destroyed, with every destroy and replace called out first.
- Claude proposes the smallest fix for each finding and never runs `apply` or `destroy`.

## Use it

- `/iac-reviewer:iac-check`
- `/iac-reviewer:iac-plan infra/prod`
- Or ask: "Is this Terraform safe to merge?"

## Requirements

Python 3. Optional: `terraform` or `tofu` for validate and plan.

## Data

The check runs locally. `terraform plan` talks to your cloud provider with the credentials already configured on your machine, exactly as it does when you run it yourself. The plugin sends nothing anywhere else.

## About the author

<a href="https://petrovicistefan.ro"><img src="https://raw.githubusercontent.com/petrovicistefan/claude-code-plugins/main/assets/ps-logo.png" alt="Stefan Petrovici logo" width="120"></a>

Built by [Stefan Petrovici](https://petrovicistefan.ro), a software engineer open to freelance projects and full-time roles. I build websites, web and mobile apps, Meta (Facebook and Instagram) integrations, and business automations, including AI-powered ones.

Need something like this for your team? Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro), or see my work at [petrovicistefan.ro](https://petrovicistefan.ro) and [iasi.dev](https://iasi.dev).

## License

MIT. Made by [Stefan Petrovici](https://petrovicistefan.ro).
