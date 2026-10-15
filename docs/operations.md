# Operations reference

**Your next opportunity, organised.** A student-focused application tracker with a React/TypeScript frontend, FastAPI API, PostgreSQL, Alembic, Docker, GitHub Actions, Terraform/EKS, Helm and Prometheus/Grafana.

This is a **single-user, unauthenticated demonstration for synthetic data only**. A public demo can be read and changed by anyone. Do not enter real personal information. It is not a private multi-user service.

Current audit: PostgreSQL tests, both image builds/security scans/GHCR pushes, and Compose CRUD/restart persistence passed in CI. AWS deployment/evidence remains blocked by account bootstrap. See [progress](progress.md), [rubric matrix](rubric-matrix.md) and [evidence](evidence-checklist.md). A configuration file is not proof of a running system; no grade is guaranteed.

## Features

Dashboard with precisely defined counts, upcoming interviews and Saved-stage deadlines; application CRUD, search/filter/sort/pagination; stage board with keyboard-accessible dropdowns; interview CRUD with local-time display; visible release identifier. Deleting an application cascades to its interviews. Historical application dates are supported. Details in [architecture](architecture.md).

## Prerequisites and versions

Python 3.12, Node 24.15.0, PostgreSQL 17, Git, Docker Engine/Desktop with Compose. For cloud work: Terraform 1.13.x, Helm 3.19.0, kubectl compatible with EKS 1.35, AWS CLI v2 and secure local AWS SSO authentication. Dependencies and chart versions are pinned; Python transitives are frozen in `backend/requirements.txt`, npm uses `package-lock.json`, Terraform uses `.terraform.lock.hcl`. See [version sources](versions.md).

## Docker Compose

```bash
cp .env.example .env
# Edit .env: choose a random URL-safe local DB password and matching DATABASE_URL.
docker compose up --build -d
# Migration service must finish successfully before backend starts.
docker compose ps -a
docker compose run --rm backend python -m app.seed  # optional, explicit and idempotent
```

Open http://localhost:3000. Backend docs: http://localhost:8000/docs. PostgreSQL is not exposed to the host. No seed occurs automatically. `docker compose logs -f backend frontend postgres migrate` shows logs. `docker compose restart backend frontend` must preserve an existing application; verify it in the browser to capture persistence evidence. `docker compose down` preserves data. **Destructive reset:** `docker compose down -v` permanently removes the local DB volume.

Migrations: `docker compose run --rm migrate`. With running replicas, use compatible additive migrations. The migration is controlled independently from normal application startup.

## Direct development

```bash
python3.12 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
# Export DATABASE_URL securely to a local PostgreSQL instance.
cd backend
../.venv/bin/alembic upgrade head
../.venv/bin/python -m app.seed
../.venv/bin/uvicorn app.main:app --reload --port 8000
# Second terminal, repository root:
cd frontend
npm ci
npm run dev
```

For a lightweight preview when PostgreSQL is unavailable, explicitly set `DATABASE_URL=sqlite:////tmp/applytrail-preview.db` before migrations, seeding and the API. This is a development fallback only, not PostgreSQL or deployment evidence. Use Python 3.12+, not macOS's legacy system Python.

## Verification

```bash
(cd backend && ../.venv/bin/pytest -v)
(cd frontend && npm ci && npm run build)
python3 scripts/smoke.py http://localhost:3000
helm lint helm/applytrail
helm template applytrail helm/applytrail -n applytrail --set monitoring.enabled=true > /tmp/applytrail.yaml
.venv/bin/python scripts/verify-manifests.py /tmp/applytrail.yaml
terraform -chdir=terraform fmt -check
terraform -chdir=terraform init -backend=false
terraform -chdir=terraform validate
```

Tests default to fresh isolated SQLite with foreign keys enabled. For PostgreSQL, create a dedicated database **named `applytrail_test`**, set TEST_DATABASE_URL to it, run its Alembic migrations with DATABASE_URL set to that same test DB, then pytest. The fixture refuses other database names and cleans test rows; never use a deployed database. CI does this with an ephemeral PostgreSQL service. `/health` is lightweight; `/ready` checks database connectivity; `/metrics` exposes counters/histograms. Validation errors use FastAPI's standard detail schema; missing records return 404; unavailable DB returns 503. The smoke test writes uniquely identified synthetic records and removes them in a finally block.

## GitHub delivery and GHCR

Repository: https://github.com/Prisha4gupta/ApplyTrail. See `.github/workflows/delivery.yml`: PR/main tests → both image builds → mandatory Trivy HIGH/CRITICAL gate → same local images pushed with full SHA → EKS deployment via Helm → rollout and smoke. Failed scans retain JSON reports. No ignore-unfixed switch or broad suppression. Read each report's package, installed/fixed versions, CVE and severity; patch dependencies/base images, rebuild, and rerun. Until reports exist, no clean-scan claim is valid.

Bootstrap before first deployment:

1. Provision approved AWS infrastructure using the next section. Set repository environment **demo**, restricted to main; add environment variables AWS_DEPLOY_ROLE_ARN (Terraform output), AWS_REGION, EKS_CLUSTER. Configure optional human approvals as appropriate.
2. Grant Actions package write access. For this public synthetic capstone, make both GHCR packages public after their first push so nodes can pull them without registry credentials. If private, create a namespace registry pull secret securely (read:packages only), then set `imagePullSecrets: [{name: ghcr-pull}]` in a committed non-secret values override used by deploy.sh. Do not put tokens in values files or shell history.
3. Configure EKS API connectivity: operator and CI fixed-egress CIDRs, or consciously review a wider allowlist for GitHub-hosted runners. OIDC does not solve networking.
4. Operator bootstraps namespaces, database/Grafana Secrets, storage and controllers. The deploy role has namespace access, not cluster bootstrap privileges.
5. Push main only after bootstrap for a fully green delivery run. Before bootstrap, tests/scans may run, but deployment will fail honestly for missing configuration. Record that failure as a blocker, not a successful delivery.

Full SHA tags are traceable but tags can technically be overwritten; do not overwrite them. Retain registry digests alongside the run evidence. GitHub concurrency prevents overlapping releases. CI does not provision infrastructure or run Terraform apply.

## AWS infrastructure and cost approval

**Do not apply until the owner explicitly approves a current regional estimate and cleanup plan.** See [costs/bootstrap](aws-bootstrap.md) and [cleanup](cleanup.md). Proposed: ap-south-1, EKS 1.35, two t3.medium workers, 20 GiB root disk each, 10 GiB gp3 database, one Ingress load balancer, no NAT. Use only secure local SSO/profile authentication; never paste credentials into chat.

```bash
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
cp terraform/backend.hcl.example terraform/backend.hcl
# Configure operator role, CIDRs, unique encrypted state bucket; no credential values.
terraform -chdir=terraform init -reconfigure -backend-config=backend.hcl
terraform -chdir=terraform plan -out=applytrail.tfplan
# Review real plan and cost estimate; obtain explicit approval before next command.
terraform -chdir=terraform apply applytrail.tfplan
```

State must be in a dedicated encrypted, versioned S3 bucket with public access blocked and `use_lockfile=true`. Bucket bootstrap is separate and also requires approval. See docs for IAM/state access. Do not commit state or plan binaries. EKS resolves compatible addon builds during plan; record them and pin `addon_versions` before later updates. Terraform's provider lock does not pin managed addon versions.

## Cluster bootstrap and release

```bash
aws eks update-kubeconfig --region ap-south-1 --name applytrail
kubectl apply -f k8s/namespace.yaml
# Create applytrail-db and grafana-admin securely as described in docs/aws-bootstrap.md.
bash scripts/bootstrap-cluster.sh
IMAGE_REPOSITORY=ghcr.io/prisha4gupta/applytrail IMAGE_TAG=FULL_COMMIT_SHA bash scripts/deploy.sh
```

The app chart uses ClusterIP services; Traefik routes `/` and `/api` without rewrites. PostgreSQL uses retained gp3 storage and EBS CSI Pod Identity. Migrations run as post-install/pre-upgrade hook Jobs with bounded retries; readiness checks connectivity so first-install waiting does not depend on tables existing yet. Bootstrap checks DB readiness before release. Two frontend replicas; backend HPA min=2/max=5, CPU request=100m, target=65%. Helm omits backend replica count under HPA. Monitor rollout; allow Metrics Server time to populate. Namespace is one ApplyTrail release only (stable service names are intentional).

Initial HTTP Ingress is for synthetic demonstration; use a domain/TLS certificate and ingress TLS configuration before any real service. Grafana is never public.

## Monitoring, load and recovery

```bash
kubectl -n monitoring port-forward svc/monitoring-grafana 3001:80
kubectl -n monitoring port-forward svc/monitoring-kube-prometheus-prometheus 9090:9090
python3 scripts/load.py http://INGRESS_ADDRESS 120 16
kubectl top pods -n applytrail
kubectl get hpa backend -n applytrail -w
```

Use the secret-supplied Grafana login locally, open the provisioned ApplyTrail dashboard. Check Prometheus Targets for UP first. Allow at least several scrapes for rate panels. Metrics use bounded route templates/method/status, not company names or raw IDs. Load is limited to 300 seconds and 32 workers; Ctrl+C stops it. A light API may not trigger scaling: capture actual results, then tune controlled load without falsely claiming scale-up.

See [troubleshooting](troubleshooting.md) for six failure modes, a reversible selector exercise and rollback caveats. See [demo script](demo-script.md), [viva preparation](viva-preparation.md), [evidence checklist](evidence-checklist.md), and [cleanup](cleanup.md).
