# Rubric coverage — honest audit

[Official rubric](https://github.com/Nency-Ravaliya/devops-heros/blob/main/session21-python/GRADING.md) and [brief](https://github.com/Nency-Ravaliya/devops-heros/blob/main/session21-python/README.md), reviewed 2026-10-14. Marks are available weights, not predicted grades. No equivalent session-21 student guide found. Official requirements match the requested allocation, additionally specifying k8s/namespace.yaml and instructor repository access.

| Criterion | Marks | Implementation | Verification command / action | Genuine evidence | Status / blocker |
|---|---:|---|---|---|---|
| M1: health, CRUD, PostgreSQL migration, React and responsive UI | 10 | backend/app; backend/alembic/versions/0001_initial.py; frontend/src | pytest; alembic upgrade/check; browser CRUD | pytest.txt, local-smoke.txt, dashboard screenshot | Verified in CI for PostgreSQL + Compose; browser Verified locally |
| M2: >=5 tests, >=3 endpoints, isolation/config | 10 | backend/tests; pytest.ini | pytest -v | evidence/pytest.txt: 16 passed | Verified in CI: 16 PostgreSQL tests passed |
| M3: repository access, meaningful history, ignores | 5 | .gitignore; Git history; public GitHub repo | git log; git ls-remote | evidence/git-history.txt; https://github.com/Prisha4gupta/ApplyTrail | Verified locally: ten genuine commits pushed |
| M4: Dockerfiles, multistage Nginx, non-root, Compose | 10 | backend/Dockerfile; frontend/Dockerfile; docker-compose.yml | docker compose up --build; ps; browser; restart | evidence/compose-persistence-38586804223.txt | Verified in CI: builds, Compose startup, CRUD and restart persistence passed; user verified local Docker Compose |
| M5: push-main tests, frontend build, both images, GHCR SHA | 15 | .github/workflows/delivery.yml; scripts/deploy.sh | actual workflow + rollout + smoke | https://github.com/Prisha4gupta/ApplyTrail/actions/runs/38586804223 | Verified in CI through both GHCR pushes; CI kind deployment and monitoring passed: https://github.com/Prisha4gupta/ApplyTrail/actions/runs/38849684438 |
| M6: both scans, HIGH/CRITICAL gate, explanation | 5 | delivery.yml scan step; README security guidance | inspect both Trivy JSON artifacts | evidence/trivy-*-38586804223.json; docs/security-results.md | Verified in CI: both scans passed after documented remediation |
| M7: valid HCL/init/plan, VPC/two public subnets/EKS/nodes/destroy/example | 15 | terraform/ | fmt; init -backend=false; validate; approved plan/apply/destroy | terraform-init.txt; terraform-validate.txt | Verified locally for init/validate; cloud execution not part of selected local demonstration |
| M8: namespace/chart/release/two replicas/ClusterIP/Ingress/running pods | 15 | k8s/; helm/applytrail/ | helm lint/template; invariant script; actual rollout | helm-lint.txt; helm-invariants.txt | Verified locally for rendering; local kind deployment verified October 16 |
| M9: metrics endpoint/scrape/Grafana/live panels | 10 | main.py; ServiceMonitor; monitoring/ | parser test; target UP; populated panels | metrics test passes; evidence/2026-10-16-kind-monitoring.json | Implemented; endpoint Verified locally; live monitoring verified on kind October 16 |
| M10: README and full change-to-deployment demo | 5 | README; docs/demo-script.md | execute 13-step sequence | Documentation and local screenshot only | Implemented; CI kind Helm deployment verified at 9b400e2; student presentation still required |

## Additional requirements and acceptance gates

| Requirement | Files | Check/evidence | Status / blocker |
|---|---|---|---|
| Exact dashboard counts and Saved-only deadlines | main.py, test_api.py | dashboard tests | Verified locally |
| Interview CRUD, aware times, parent cascade | models.py, schemas.py, tests | interview/cascade tests | Verified locally |
| Search/filter/sort/pagination, accessible board changes | main.py, main.tsx | filter tests; browser create/stage move | Verified locally; 390px layout verified; browser interview scheduling limitation documented |
| Historical dates and HTTP URL validation | schemas.py, tests | historical/invalid cases | Verified locally |
| Explicit idempotent fictional seed | app/seed.py | invoked twice, remained eight seed rows | Verified locally |
| No automatic production table creation | Alembic migration; Docker/Helm Jobs | source inspection; alembic check | Verified locally; PostgreSQL migration Verified in CI |
| Health/readiness error behavior | main.py, tests | DB failure returns 503, health stays 200 | Verified locally |
| Bounded metric labels | main.py, tests | dynamic IDs/unmatched paths absent | Verified locally |
| Frontend /api routing and version | Vite/Nginx/Ingress; /api/version | local proxy smoke; deployed SHA smoke | Verified locally; container/cloud routing pending |
| Persistent PostgreSQL and restart proof | Compose volume; StatefulSet/PVC | restart and read same record | Verified in CI for Compose; AWS pending |
| One migration per release, initial readiness | migration.yaml; Compose migrate | controlled Job and initial install | Implemented; real rollout pending |
| Image scan/push identity and retained failures | delivery.yml | build once; same IMAGE used in scan/push | Implemented; both scans/pushes Verified in CI |
| OIDC trust and namespace permissions | Terraform IAM/access; deploy-rbac.yaml | assume role; Helm incl. ServiceMonitor | Implemented; cloud configuration only; local kind deployment verified |
| GHCR private/public pulls | README | public packages or scoped imagePullSecret | Published in CI; EKS pull/visibility configuration still pending |
| EKS API connectivity and access | api_allowed_cidrs; access entries | operator + CI API request | Blocked pending account/runner configuration |
| EBS CSI and secure state locking | Terraform addons; storage.yaml; backend example | PVC Bound; encrypted/locked S3 state | Implemented; AWS pending |
| Supported Ingress controller | bootstrap-cluster.sh; Traefik values | install; external routes | Implemented; cluster pending |
| CPU HPA 2–5, requests, Metrics Server | network/workloads templates; bootstrap | kubectl top/hpa during bounded load | Implemented; verified locally: 2→4→5 under load |
| Resource/probe/security contexts | Helm templates | rendered invariant checks | Verified locally; pod readiness pending |
| Matching ServiceMonitor selectors | network.yaml; monitoring values | target UP in real Prometheus | Rendered locally; live scrape pending |
| Grafana provisioned panels and secure access | dashboard.json; monitoring values | port-forward; actual samples | Implemented; cluster pending |
| Bounded traffic and stop instructions | scripts/load.py; README | max 300s/32 workers; Ctrl+C | Implemented; cluster execution pending |
| Reversible failure, diagnosis and recovery | troubleshooting.md | before/broken/fixed captures | Implemented runbook; verified locally: evidence/2026-10-16-kind-recovery.txt |
| Rollback caveat and cleanup before provisioning | troubleshooting.md; cleanup.md | approved teardown + remaining-billables inventory | Implemented; no destruction before evaluation |
| Cost estimate and explicit consent | aws-bootstrap.md | refresh regional quote and approve before apply | Blocked; no provisioning attempted |
| Genuine screenshots, CI links, cloud evidence | evidence/; checklist | observe/capture each result | Partial local evidence only |

Status vocabulary: Not started, Implemented, Verified locally, Verified in CI, Verified on AWS, Blocked. The project is **not complete** while required deployment/evidence remains unverified.
