---
name: aws-cost-guard
description: "Use when investigating AWS spending, unused cloud resources, or Kubernetes pod status and logs."
---

# AWS Cost Guard

Investigate AWS costs and Kubernetes problems with the `aws` and `kubectl` command line tools the user already has configured.

## Before you start

1. Check the tools exist: `aws --version`, `kubectl version --client`. If one is missing, tell the user and continue with the other.
2. Show which account and cluster you will query: `aws sts get-caller-identity` and `kubectl config current-context`. Ask the user to confirm before running more commands.
3. Use only read-only commands. Never create, modify or delete resources. If a fix needs a change, write the exact command and let the user run it.

## Costs by service

Cost Explorer charges a small fee per request, so mention it once before the first call.

```bash
aws ce get-cost-and-usage \
  --time-period Start=YYYY-MM-01,End=YYYY-MM-DD \
  --granularity MONTHLY --metrics UnblendedCost \
  --group-by Type=DIMENSION,Key=SERVICE
```

Sort services by cost, show the top ones and compare with the previous period when the user asks about a change.

## Idle resources

Check each region the user cares about (`--region`):

- Unattached EBS volumes: `aws ec2 describe-volumes --filters Name=status,Values=available`
- Unassociated Elastic IPs: `aws ec2 describe-addresses` (entries without `AssociationId`)
- Stopped instances: `aws ec2 describe-instances --filters Name=instance-state-name,Values=stopped`
- Old snapshots: `aws ec2 describe-snapshots --owner-ids self`
- Load balancers without targets: `aws elbv2 describe-load-balancers` then `describe-target-health`

List each resource with its ID, size or type, age, and an estimate of its monthly cost when you can state one.

## Kubernetes

- Cluster status: `kubectl get nodes`, `kubectl get pods -A | grep -v Running`
- A failing pod: `kubectl describe pod <pod> -n <ns>` then `kubectl logs <pod> -n <ns> --tail=200` and `--previous` for crash loops
- Resource use: `kubectl top pods -n <ns>` when metrics-server is installed

Explain the likely cause (OOMKilled, image pull errors, failing probes, pending scheduling) and the fix.
