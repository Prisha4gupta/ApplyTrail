# Your next steps: from the current project to the capstone demo

**Current route (October 16):** use [Local Kubernetes](local-kubernetes.md) for your submission demo. The local cluster, monitoring, autoscaling and recovery are verified, and the [Kubernetes CI run](https://github.com/Prisha4gupta/ApplyTrail/actions/runs/38849684438) passed. The cloud setup sections below are optional reference material, not your next action.

This guide is written for Prisha's existing checkout at `/Users/prisha/Desktop/ApplyTrail`. You do **not** need to build the application again or clone a second copy. Read one numbered step, complete it, check its expected result, then continue. Stop at a failed check instead of running later commands against a broken setup.

**What is already done:** application code, tests, containers, CI/security pipeline, Terraform, Helm, monitoring configuration and documentation. A recorded CI run passed PostgreSQL tests, both image builds/scans/pushes and Compose restart persistence. **What remains:** your local Docker demonstration, account-specific AWS setup, actual cloud deployment, live evidence, presentation and eventual cleanup.

The cloud steps below are instructions, not actions already performed. No AWS infrastructure has been provisioned by this project so far.

## 1. Open the existing project

Open Terminal on your Mac and run:

```bash
cd /Users/prisha/Desktop/ApplyTrail
git status
git remote -v
```

Expected: the repository is ApplyTrail and the remote points to `Prisha4gupta/ApplyTrail`. If there are changes you made, keep them; do not reset the repository. All following commands run from this directory unless a step says otherwise.

## 2. Install and start Docker Desktop

1. Open [Docker's official Mac installation page](https://docs.docker.com/desktop/setup/install/mac-install/).
2. Download the Apple silicon version for this Mac.
3. Open the downloaded installer and move Docker to Applications.
4. Open Docker from Applications. Review and accept its terms yourself if you agree.
5. Wait for Docker Engine to finish starting.
6. Open a new Terminal window and check:

```bash
docker --version
docker compose version
docker info
```

Expected: version output and a working Docker server. “Cannot connect to the Docker daemon” usually means Docker Desktop is not running yet. Do not continue until `docker info` works. PostgreSQL will run in Docker; do not install a separate database for this route.

## 3. Create the local configuration once

Check whether `.env` already exists:

```bash
ls -l .env
```

If it exists, keep it. If it does not, run this block from the repository root. It creates a random password, puts matching values in the two required settings and avoids printing the password. It refuses to overwrite an existing file.

```bash
python3 - <<'PY'
import os, secrets
password = secrets.token_hex(24)
fd = os.open('.env', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
with os.fdopen(fd, 'w') as f:
    f.write('POSTGRES_USER=applytrail\nPOSTGRES_DB=applytrail\n')
    f.write(f'POSTGRES_PASSWORD={password}\n')
    f.write(f'DATABASE_URL=postgresql+psycopg://applytrail:{password}@postgres:5432/applytrail\n')
    f.write('APP_VERSION=local\n')
print('Created private .env configuration.')
PY
```

Verify Git ignores it:

```bash
git check-ignore .env
```

Expected: `.env`. Do not upload this file or include its contents in screenshots. If a database volume already exists, changing the password in `.env` does not change the database's existing password—keep the original matching configuration.

## 4. Start the complete local application

```bash
docker compose up --build -d
docker compose ps -a
```

The first build needs network access and may take several minutes. Expected: PostgreSQL, backend and frontend running; `migrate` exited with code **0**. A successful migration container is meant to stop.

If something fails:

```bash
docker compose logs --tail=100 postgres migrate backend frontend
```

Read the error before continuing. You can share a redacted error message for help, but not `.env` or passwords.

## 5. Load fictional data and open the app

```bash
docker compose run --rm backend python -m app.seed
```

Open [http://localhost:3000](http://localhost:3000). Use port **3000** for Docker Compose; the old port 5173 was the temporary development preview and is not currently running.

Expected: dashboard, Applications, Board and Interviews pages with fictional opportunities. Running the seed command twice should not duplicate its records.

## 6. Practise the user flow and capture local evidence

1. Add a fictional application, such as “Demo Aurora / Platform Intern”, stage Applied.
2. Open its details and edit a field.
3. Search for it by company name and try stage/employment filters.
4. Open Board and change its stage to Interview.
5. Open its details, add a future interview, and check the local date/time carefully.
6. Confirm the interview appears in Interviews and the dashboard.
7. Edit the interview. Delete a disposable interview and confirm it disappears.
8. Test application deletion only on a disposable fictional application; its linked interviews should disappear too.
9. Reload the page to confirm changes persist.
10. Capture desktop and narrow/mobile layout screenshots. For manual mobile testing, use your browser's responsive-device tools or narrow its window.

This also completes the outstanding manual browser interview-form check; the API behavior is already tested, but the prior automated browser date-input interaction was not completed.

Save screenshots under `evidence/` using names such as `2026-10-15-compose-dashboard.png`. Capture real results only.

## 7. Run the local smoke and persistence checks

```bash
python3 scripts/smoke.py http://localhost:3000
python3 scripts/compose-check.py
```

Expected: PASS messages for CRUD, interview/dashboard behavior, cleanup and persistence after frontend/backend restart. The scripts create identifiable synthetic records and clean them up.

For a repeat of the API suite using the backend image:

```bash
docker compose run --rm -v "$PWD/backend/tests:/app/tests:ro" -v "$PWD/backend/pytest.ini:/app/pytest.ini:ro" backend pytest -v
```

This command uses the suite's isolated SQLite fallback, not the running demo database. PostgreSQL integration evidence is in CI. Do not set TEST_DATABASE_URL to your demonstration database.

When finished locally:

```bash
docker compose down
```

This preserves your data. Do not add `-v` unless you explicitly want to erase the local database.

## 8. Review your GitHub results

1. Open [the repository](https://github.com/Prisha4gupta/ApplyTrail).
2. Select **Actions**, then **Verify and deliver ApplyTrail**.
3. Inspect a run's jobs separately. A red overall run does not mean every job failed.
4. The recorded [run 38586804223](https://github.com/Prisha4gupta/ApplyTrail/actions/runs/38586804223) passed `verify`, both `images` jobs and `compose`. Its `deploy` job failed because AWS access was not configured.
5. Open the job logs and download the Trivy, test and Compose artifacts. Existing downloaded evidence is already in `evidence/`.
6. Understand the explanation in [security-results.md](security-results.md): the first backend image failed; the revised base passed the same strict gate.

Keep the successful job links. A completely green delivery run is still required after AWS setup; do not present the current partial run as end-to-end success.

## 9. Check the two GHCR packages

On your GitHub profile, open **Packages** and locate `applytrail-frontend` and `applytrail-backend`. Verify each has a full commit-SHA tag from a successful image job.

The easiest pull configuration for this public, synthetic-data capstone is public container packages. Review the contents and make each package public through its package settings if you choose this route. Public repository visibility does not automatically guarantee public package visibility. Follow [GitHub's package-visibility guide](https://docs.github.com/en/packages/learn-github-packages/configuring-a-packages-access-control-and-visibility).

If you need private images, stop here for configuration help: the EKS namespace needs a read-only GHCR pull secret, and deploy.sh needs a Helm values override referring to it. Do not publish a token in Git or paste it into chat.

## 10. Establish which AWS account you can use — checkpoint

Before any paid provisioning, determine:

- Is this your personal AWS account, an institution account or an AWS Academy/Learner Lab?
- Are EKS, IAM roles, OIDC providers, Pod Identity, EC2, VPC and S3 permitted?
- Do you have an assigned operator role with sufficient infrastructure permissions?
- Who pays, what is the spending limit, and when is your demonstration?

A student account may restrict IAM or EKS. Do not assume a lab will support this Terraform project. If the account is restricted, ask the instructor which permitted account/role to use before changing the infrastructure design.

**Stop and tell your project mentor the account type and available login method. Do not send access keys, secret keys, session tokens or passwords.** Account type and a profile name are enough to choose the correct next instructions. SSO steps below apply only if IAM Identity Center has been configured for you.

## 11. Prepare the cloud tools and authenticate

Install AWS CLI v2 from [AWS's official instructions](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html), and kubectl using [the EKS installation guidance](https://docs.aws.amazon.com/eks/latest/userguide/install-kubectl.html). Use a kubectl version compatible with Kubernetes 1.35 rather than blindly selecting the newest major/minor.

This existing workspace already has validation copies of Terraform and Helm. Add them to the current Terminal session:

```bash
export PATH="$PWD/.tools:$PWD/.tools/darwin-arm64:$PATH"
terraform version
helm version
aws --version
kubectl version --client
```

`.tools` is intentionally not tracked in Git. On another computer, install Terraform 1.13.x and Helm 3.19.0 from official releases; do not assume those local files exist.

For an account with IAM Identity Center access:

```bash
aws configure sso --profile applytrail
aws sso login --profile applytrail
export AWS_PROFILE=applytrail
export AWS_REGION=ap-south-1
aws sts get-caller-identity
```

The SSO wizard needs your assigned start/issuer URL and SSO region, then an account and permission set. **The SSO region can differ from the workload region Mumbai.** Use information supplied by your account administrator. Choose `applytrail` as the profile name. Follow [AWS's SSO guide](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html).

Expected: the identity command shows the intended account and role. If you do not have SSO, do not invent a start URL or create root access keys; arrange the appropriate temporary-credential login with your account administrator first.

## 12. Agree the cost and cleanup plan — stop before spending

Review [aws-bootstrap.md](aws-bootstrap.md) and [cleanup.md](cleanup.md). Proposed resources: Mumbai, EKS 1.35, two t3.medium workers, two public subnets, node disks, a 10 GiB database volume, one public load balancer and encrypted Terraform state.

Prepare a fresh regional estimate in the [AWS Pricing Calculator](https://calculator.aws/), including EKS, EC2, EBS, public IPv4, load balancing, logs and data transfer. Specify the expected number of hours/days. The previous planning range in the bootstrap document is not a confirmed quote or a spending cap. AWS budget alerts warn; they do not automatically stop all spending.

**Approve the region, sizes, expected runtime, estimate and cleanup policy before creating even the state bucket.** No Terraform apply or cluster bootstrap command should be executed before this checkpoint.

## 13. Create secure Terraform state storage — after approval

Use a dedicated S3 bucket, not an unrelated/shared bucket. Choose a globally unique lowercase name; replace the sample below before running it:

```bash
export APPLYTRAIL_STATE_BUCKET='replace-with-your-unique-applytrail-state-bucket'
aws s3api create-bucket --bucket "$APPLYTRAIL_STATE_BUCKET" --region ap-south-1 --create-bucket-configuration LocationConstraint=ap-south-1
aws s3api put-public-access-block --bucket "$APPLYTRAIL_STATE_BUCKET" --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
aws s3api put-bucket-versioning --bucket "$APPLYTRAIL_STATE_BUCKET" --versioning-configuration Status=Enabled
aws s3api put-bucket-encryption --bucket "$APPLYTRAIL_STATE_BUCKET" --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'
```

Verify using `get-public-access-block`, `get-bucket-versioning` and `get-bucket-encryption` with the same `--bucket`. Your operator role needs state-prefix access and locking-object permissions described in the bootstrap guide. This bucket is outside the application Terraform state and must be handled separately during cleanup.

## 14. Fill in Terraform's account-specific values

Create these files only if they do not already exist:

```bash
cp -n terraform/terraform.tfvars.example terraform/terraform.tfvars
cp -n terraform/backend.hcl.example terraform/backend.hcl
```

Edit `backend.hcl`: put your bucket name in `bucket`, keep the region matching the bucket, and keep encryption and `use_lockfile=true`.

Edit `terraform.tfvars`:

| Setting | What to enter |
|---|---|
| region | `ap-south-1`, if that is the approved region |
| name | `applytrail` |
| kubernetes_version | `1.35` |
| admin_principal_arn | The underlying IAM **role ARN**, including its path, supplied by your administrator—not the temporary STS assumed-role ARN from the identity command |
| github_repository | `Prisha4gupta/ApplyTrail` |
| api_allowed_cidrs | Your operator and CI runner's approved public egress CIDRs |
| github_oidc_provider_arn | Existing GitHub OIDC provider ARN if the account already has one; otherwise omit |

**Network checkpoint:** the workflow currently uses standard GitHub-hosted runners. Your home IP `/32` alone will not let those runners reach EKS. Decide between a runner with fixed egress and an explicitly reviewed broader API allowlist. Do not guess a permanent GitHub runner IP or automatically insert `0.0.0.0/0`. Fixed-egress/self-hosted runners may also require changing the workflow's `runs-on` configuration.

Verify neither private configuration file is tracked:

```bash
git check-ignore terraform/terraform.tfvars terraform/backend.hcl
```

## 15. Initialise and review the real infrastructure plan

```bash
terraform -chdir=terraform init -reconfigure -backend-config=backend.hcl
terraform -chdir=terraform fmt -check
terraform -chdir=terraform validate
terraform -chdir=terraform plan -out=applytrail.tfplan
```

Expected: valid configuration and a real plan for the approved VPC/subnets/EKS/workers/IAM/addons. Fix permission, quota or existing-provider errors before proceeding. Review the exact plan and resolved addon versions with your mentor. Record compatible addon builds in `addon_versions` before later changes; re-plan if you change configuration. Do not commit the binary plan or state.

**Stop again if the plan differs from the approved resource sizes, region or costs.** Only after the real plan is reviewed and explicit provisioning approval is in place:

```bash
terraform -chdir=terraform apply applytrail.tfplan
```

Allow it to finish. If it fails partway, inspect the Terraform state and actual resources; some billable resources may already exist. Do not run destroy reflexively or repeatedly apply without diagnosing the error.

## 16. Connect to the actual EKS cluster

```bash
aws eks update-kubeconfig --region ap-south-1 --name applytrail
kubectl get nodes
kubectl get pods -n kube-system
terraform -chdir=terraform output
```

Expected: worker nodes Ready and core networking/storage components healthy. If access is denied, check the operator IAM role and EKS access entry. If the command times out, check the API CIDRs/network path. Capture real VPC/subnet/EKS/node evidence, avoiding credentials and kubeconfig contents.

## 17. Create the application and monitoring secrets

```bash
kubectl apply -f k8s/namespace.yaml
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -
```

Create Kubernetes Secret `applytrail-db` in namespace `applytrail` with keys:

```text
POSTGRES_USER=applytrail
POSTGRES_DB=applytrail
POSTGRES_PASSWORD=your-new-random-cloud-password
DATABASE_URL=postgresql+psycopg://applytrail:your-new-random-cloud-password@postgres:5432/applytrail
```

Create Secret `grafana-admin` in namespace `monitoring` with keys `admin-user` and `admin-password`. Pick and save the Grafana login in your password manager. Use fresh cloud values, not placeholders.

The [runtime secret instructions](aws-bootstrap.md#runtime-secrets) show the `--from-env-file` method: use private temporary files outside the repository with mode 0600, apply the Secrets, then remove those temporary files. Do not put secret values in command arguments, GitHub variables, screenshots or chat. Verify only metadata:

```bash
kubectl get secret applytrail-db -n applytrail
kubectl get secret grafana-admin -n monitoring
```

## 18. Install the cluster's supporting services

```bash
bash scripts/bootstrap-cluster.sh
```

This creates storage/RBAC configuration and installs the pinned Traefik Ingress controller, Metrics Server, Prometheus and Grafana. The Ingress load balancer is chargeable and is part of the approved cost plan.

Check:

```bash
helm list -A
kubectl get pods -n ingress-system
kubectl get pods -n monitoring
kubectl get svc -n ingress-system
kubectl get storageclass gp3
kubectl get apiservice v1beta1.metrics.k8s.io
```

Expected: releases deployed, supporting pods Ready, gp3 present and Metrics Server API available. Do not deploy the app until these prerequisites and the Secrets are ready. Allow time for load-balancer provisioning and metrics collection.

## 19. Configure the GitHub deployment environment

Open the repository → **Settings → Environments**. Create or open **demo**, and restrict deployment branches to `main`. See [GitHub's environment guide](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments).

Under **environment variables**, add:

| Name | Value |
|---|---|
| `AWS_REGION` | `ap-south-1` |
| `EKS_CLUSTER` | `applytrail` |
| `AWS_DEPLOY_ROLE_ARN` | Exact output of the command below |

```bash
terraform -chdir=terraform output -raw deployment_role_arn
```

These are identifiers, not AWS secret keys. Do **not** add long-lived AWS access keys: the workflow uses OIDC. The environment name must be exactly `demo` because the IAM trust rule expects that name. Verify package pull visibility from step 9 and API connectivity from step 14.

## 20. Trigger delivery and verify the first cloud release

Open GitHub **Actions → Verify and deliver ApplyTrail → Run workflow**, choose `main` and start it. This runs the committed workflow at main, including rebuilding/scanning images, before deploying the matching SHA. Wait for every job to finish.

Expected: verify, image jobs, compose and deploy all pass. If deployment fails, inspect the failed step. Typical first-run blockers are OIDC trust, EKS API connectivity, namespace RBAC, GHCR pull access or a PVC that has not bound. Use [troubleshooting.md](troubleshooting.md); do not disable checks to obtain a green run.

After a successful run:

```bash
kubectl get pods,svc,ingress,pvc,hpa -n applytrail
helm list -n applytrail
kubectl get deployments -n applytrail -o wide
```

Find the Ingress address:

```bash
kubectl get ingress applytrail -n applytrail
```

Open `http://` followed by its actual ADDRESS value. Do not type the literal word `INGRESS_ADDRESS`. Verify the release identifier and compare it to the workflow's full commit SHA. The chart uses HTTP for this fictional demo; do not enter personal data.

## 21. Seed the cloud demo explicitly and check CRUD

```bash
kubectl exec -n applytrail deployment/backend -- python -m app.seed
```

This is an explicit demonstration-data command, not a startup behavior. Open the Ingress URL, create a fictional application, move its stage and add an interview. Repeat the smoke check with the real URL:

```bash
python3 scripts/smoke.py http://YOUR_ACTUAL_INGRESS_ADDRESS
```

Capture screenshots of the app through Ingress, the Helm release, Ready pods, ClusterIP Services and Bound database PVC. Check at least two frontend and two backend replicas. The database is intentionally a single StatefulSet replica.

## 22. Show real monitoring data

Use two separate Terminal windows:

```bash
kubectl -n monitoring port-forward svc/monitoring-grafana 3001:80
```

```bash
kubectl -n monitoring port-forward svc/monitoring-kube-prometheus-prometheus 9090:9090
```

Keep those commands running. Open [Grafana](http://localhost:3001) and sign in using the login you saved in step 17. Open [Prometheus](http://localhost:9090) and its Targets page; confirm ApplyTrail is **UP**.

In a third terminal:

```bash
python3 scripts/load.py http://YOUR_ACTUAL_INGRESS_ADDRESS 120 16
```

Wait for several scrape intervals. Open the **ApplyTrail · Application health** Grafana dashboard and capture populated panels. A blank panel is not proof of working monitoring. Keep Grafana private; port forwarding is sufficient. Ctrl+C stops each port forward or the load generator.

## 23. Observe HPA and practise recovery

While bounded load runs:

```bash
kubectl top pods -n applytrail
kubectl get hpa backend -n applytrail -w
```

Capture utilization and actual replica changes if they occur. Lightweight requests may not cross the threshold; report the real observation and review load/capacity rather than inventing scale-up evidence. Stop the watch with Ctrl+C. The load script limits itself to 300 seconds and 32 workers.

Then follow the **Controlled selector failure** section of [troubleshooting.md](troubleshooting.md). It includes a known-good capture, the deliberate failure, diagnosis commands, the exact recovery command and a smoke test. Keep recovery instructions open in a second terminal. Do this only in the synthetic demo environment and never during a deployment.

## 24. Demonstrate a visible code change through the pipeline

1. Change a small visible sentence in `frontend/src/main.tsx`.
2. Build the frontend locally and inspect the diff.
3. Commit that real change with a descriptive message, then push main.
4. Show the actual Actions run, tests, image builds, Trivy reports and full SHA tags.
5. Show the automatic Helm deployment and smoke check.
6. Reload the Ingress page; show the new sentence and matching release identifier.
7. Save the run link and recording/screenshots.

Use [demo-script.md](demo-script.md) to rehearse the full presentation and [viva-preparation.md](viva-preparation.md) to explain the decisions. Do not memorise outputs; understand why each check exists.

## 25. Assemble the submission, then clean up after evaluation

Work through [evidence-checklist.md](evidence-checklist.md) and [rubric-matrix.md](rubric-matrix.md). Add only real captures, review them for secrets, and keep instructor access to the repository. A screenshot of configuration is not a substitute for actual deployment or monitoring evidence.

**Do not destroy before the demonstration.** After evaluation, explicitly confirm the data-retention policy and follow [cleanup.md](cleanup.md) in order: remove Kubernetes-managed external resources while controllers still work; verify load balancers disappear; handle retained PVC/EBS data; review and run Terraform destroy; inspect remaining billable resources; handle the separate state bucket. Capture genuine cleanup evidence.

## What to do first today

Complete **steps 1–7** to run the app on your Mac and practise the feature flow. Then report your **AWS account type/login method from step 10**, your demonstration date and whether you have a spending limit. Those details determine the next account-specific actions. Keep all credentials private.
