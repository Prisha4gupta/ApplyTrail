# AWS approval and bootstrap

Status: **Blocked** pending secure AWS authentication, explicit cost approval and account-specific configuration. No apply or state-bucket creation has been run.

## Proposed resources and provisional budget

Region ap-south-1 (Mumbai), EKS 1.35 standard support, two t3.medium nodes (2 vCPU/4 GiB each), 40 GiB combined node root disks, 10 GiB gp3 database, one internet-facing NLB in two AZs, four estimated public IPv4 addresses (two nodes/two LB addresses), encrypted versioned S3 state and seven-day control-plane logs. No NAT gateway. Worker max=3 allows manual growth; HPA scales pods, not nodes.

Pricing pages checked 2026-10-14: [EKS](https://aws.amazon.com/eks/pricing/), [EC2](https://aws.amazon.com/ec2/pricing/on-demand/), [load balancing](https://aws.amazon.com/elasticloadbalancing/pricing/), [IPv4](https://aws.amazon.com/vpc/pricing/), [EBS](https://aws.amazon.com/ebs/pricing/).

Working estimate (USD, no credits assumed): EKS $0.10/hour; two nodes approximately $0.0896/hour combined; NLB budget approximately $0.025/hour plus usage; four IPv4 addresses approximately $0.020/hour; storage approximately $5/month. This gives roughly **$0.24–$0.30/hour, $6–$8/day, or $175–$220 for 730 hours**, before tax, outbound transfer, logs, state requests, CPU-credit surcharges and unusually high LB traffic. This is a planning range, **not a confirmed regional quote**: regenerate an AWS Pricing Calculator estimate for Mumbai before requesting apply approval. A third node adds compute, root disk and IPv4 cost. Extended-support Kubernetes versions increase the EKS control-plane price substantially.

Two medium workers are a demo starting point, not a capacity guarantee. Monitor allocatable memory/CPU with the monitoring stack installed and during load; do not silently increase worker count or size beyond the approved budget. User approval must name region, resources, intended run duration, estimate and cleanup policy. Cleanup instructions are prepared in cleanup.md. Do not destroy before evaluation.

## Secure prerequisites

Install AWS CLI v2, Docker Desktop/Engine, Helm and kubectl from official sources. Authenticate locally with `aws configure sso` and `aws sso login --profile PROFILE`; export AWS_PROFILE for the session. Verify `aws sts get-caller-identity` locally, never paste credentials into chat. Use the IAM role ARN underlying the SSO/assumed role as admin_principal_arn.

State bootstrap uses a dedicated bucket, not one shared with unrelated projects. After approval, use AWS CLI or a separate small bootstrap stack to create it in Mumbai; enable bucket versioning, AES256/KMS encryption and all public-access blocks. Grant the operator least-privilege Get/Put/List on the state prefix and Get/Put/Delete on its `.tflock` object. CI deployment does not need Terraform state permissions. Fill backend.hcl and use S3 native `use_lockfile=true`. Keep bootstrap state separate. Never store state in Git.

Review existing GitHub OIDC providers before apply. If the account already has token.actions.githubusercontent.com, supply its ARN to avoid duplicate creation and ownership. Terraform creates a deployment role trusted only for `repo:Prisha4gupta/ApplyTrail:environment:demo`. Configure the GitHub demo environment to allow main only.

## Runtime Secrets

Create namespace first. Generate a random URL-safe password using a secure local password manager. Prepare a temporary file outside the repository with mode 0600 containing keys POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB and DATABASE_URL. The URL must point to `postgres:5432/applytrail` and contain the matching encoded password. Do not include quotes as part of values. Then:

```bash
kubectl create secret generic applytrail-db -n applytrail --from-env-file=/PRIVATE/TEMP/DB_ENV
kubectl create namespace monitoring
kubectl create secret generic grafana-admin -n monitoring --from-env-file=/PRIVATE/TEMP/GRAFANA_ENV
```

Grafana file keys: admin-user and admin-password. Remove temporary secret files safely after applying and verifying; never capture their contents or run commands with plaintext passwords in history. Environment variables can be observed by local privileged processes; use a trusted computer. There are no committed real credentials.

Run scripts/bootstrap-cluster.sh as the human cluster administrator after EBS CSI and worker nodes are Ready. It installs Traefik (supported Ingress controller), Metrics Server and the pinned monitoring stack. Verify storage class, CSI pods and `kubectl get apiservice v1beta1.metrics.k8s.io`. Then deploy the app. Set the GitHub environment's role/region/cluster variables. If images are private, provision a pull secret and wire it through a non-secret Helm values override in deploy.sh. Prefer public synthetic-demo images to avoid persistent registry credentials.

## Evidence gates

Capture a real plan only after backend/auth configuration. Review resolved EKS addon versions and pin them before subsequent changes. Apply needs explicit approval. After apply, verify subnets, nodes, access, CSI, controllers, PVC Bound, pods Ready, Service endpoints, Ingress CRUD, image SHAs, target UP, Grafana and HPA. No generated file substitutes for these checks.
