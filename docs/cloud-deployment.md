# Optional EKS deployment

The `terraform/` configuration defines a VPC, two public subnets, an EKS cluster, a managed node group, IAM access, EBS CSI integration and GitHub OIDC deployment permissions. The default region is `ap-south-1`; select the region deliberately in both Terraform and its state backend.

## Prerequisites

- AWS CLI authentication with permissions to manage the required network, IAM, EKS and storage resources. Organization policies can restrict these operations even for administrator roles.
- Terraform 1.13.3, Helm 3.19.0 and a compatible kubectl.
- A dedicated encrypted, versioned S3 state bucket with public access blocked and native state locking enabled.
- Reachability from your operator machine and deployment runner to the EKS API. Standard GitHub-hosted runners do not have a fixed outgoing IP; use a suitable runner/network design rather than assuming your home IP allowlist is sufficient.
- A current regional estimate and a resource cleanup plan. EKS, worker instances, storage, public IP addresses, load balancing and logs can incur charges.

The default worker group uses two `t3.medium` instances. Public worker subnets avoid NAT gateway costs for short-lived environments; longer-lived installations should consider private workers and suitable egress. No SSH access is configured.

## Configure and review

Copy `terraform/terraform.tfvars.example` and `terraform/backend.hcl.example` to their corresponding names without `.example`, only if those files do not already exist. Both private files are ignored by Git.

Set the region, state bucket, repository name, approved API CIDRs and permanent operator IAM role ARN. Use the IAM role ARN, including its path, rather than the temporary STS session ARN. Supply `github_oidc_provider_arn` if the account already has the GitHub provider.

```bash
terraform -chdir=terraform init -reconfigure -backend-config=backend.hcl
terraform -chdir=terraform fmt -check
terraform -chdir=terraform validate
terraform -chdir=terraform plan -out=applytrail.tfplan
```

Review the plan, pricing and compatible addon versions before applying. Never commit state, binary plans or credentials.

```bash
terraform -chdir=terraform apply applytrail.tfplan
aws eks update-kubeconfig --region YOUR_REGION --name applytrail
kubectl get nodes
```

## Install supporting services

Create namespaces `applytrail` and `monitoring`. Provision these Secrets from private temporary files using `kubectl create secret generic --from-env-file=...`:

- `applytrail-db` in `applytrail`: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `DATABASE_URL`.
- `grafana-admin` in `monitoring`: `admin-user`, `admin-password`.

The database URL must use the same URL-safe password and point to `postgres:5432/applytrail`. Keep temporary files private and remove them after use. Then run `bash scripts/bootstrap-cluster.sh` and verify storage, controllers and monitoring readiness.

## Enable delivery

Create the GitHub environment `demo`, restrict its deployment branch to `main`, and add environment variables:

| Variable | Value |
|---|---|
| `AWS_REGION` | Configured region |
| `EKS_CLUSTER` | Cluster name |
| `AWS_DEPLOY_ROLE_ARN` | Terraform `deployment_role_arn` output |

Set repository variable `ENABLE_EKS_DEPLOY=true` to enable the EKS job. The workflow uses OIDC; do not add long-lived AWS keys. Container packages must be publicly pullable or use a scoped registry pull Secret referenced by `imagePullSecrets` in the chart values.

The deployment script installs the verified commit-SHA images, waits for rollout and runs HTTP smoke checks. Check Pods, Ingress, PVC binding, HPA metrics and Prometheus targets after deployment. Follow [cleanup](cleanup.md) when the environment is no longer needed.
