# AWS Cost Guard: Cloud Cost and Kubernetes Debugging

Find out why your AWS bill grew and why Kubernetes pods fail, using your own read-only `aws` and `kubectl` tools.

## What it does

Claude uses your existing `aws` and `kubectl` command line tools to break down costs by service, find idle resources such as unattached volumes, unused Elastic IPs and stopped instances, and diagnose failing pods from their events and logs. It shows which account and cluster it will query and asks before running commands. It only runs read-only commands and never changes your infrastructure.

## Use it

- `/aws-cost-guard:costs`, `/aws-cost-guard:unused`, `/aws-cost-guard:k8s-status`
- Or ask: "Why did our AWS bill go up this month?"

## Requirements

AWS CLI v2 with credentials configured, and `kubectl` with a context for Kubernetes checks. Cost Explorer API calls are billed by AWS per request.

## Data

Commands run on your machine with your own credentials and talk only to AWS and your cluster. The plugin stores nothing.

## About the author

<a href="https://petrovicistefan.ro"><img src="https://raw.githubusercontent.com/petrovicistefan/claude-code-plugins/main/assets/ps-logo.png" alt="Stefan Petrovici logo" width="120"></a>

Built by [Stefan Petrovici](https://petrovicistefan.ro), a software engineer open to freelance projects and full-time roles. I build websites, web and mobile apps, Meta (Facebook and Instagram) integrations, and business automations, including AI-powered ones.

Need something like this for your team? Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro), or see my work at [petrovicistefan.ro](https://petrovicistefan.ro) and [iasi.dev](https://iasi.dev).

## License

MIT. Made by [Stefan Petrovici](https://petrovicistefan.ro).
