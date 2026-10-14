# Implementation progress

2026-10-14: Empty workspace inspected; no existing work to preserve. Official README and GRADING reviewed. Node 24.15.0 and bundled Python 3.12.14 available. Docker, Terraform, Helm, kubectl and AWS CLI absent from PATH. No GitHub remote or cloud resources exist for this project yet.

Phase 1 — requirements: Verified locally. Official marks match the requested matrix. The official rubric additionally names `k8s/namespace.yaml` and repository access for the instructor. ApplyTrail is an original domain rather than a copy of TaskBoard. No grade is guaranteed.

Cloud provisioning requires a current regional cost estimate and explicit approval. No chargeable resources have been requested.

Phase 2 — backend implemented: full application/interview CRUD, validated HTTP URLs and aware timestamps, dashboard calculations, explicit Alembic migration and database constraints. Related interviews cascade on application deletion. Liveness, readiness and bounded route-template metrics added. Python syntax compilation passed; runtime tests pending dependency installation.

Phase 3 — testing: Verified locally, 16 Pytest cases pass using isolated SQLite with foreign keys enabled. CI PostgreSQL integration remains pending. Dependency versions (including transitives) frozen in requirements.txt. A Starlette warning notes its future test-client transition; no failures. No equivalent student guide found in the official repository tree. Initial system-Python compile attempt hit a cache sandbox restriction; rerun with bundled Python 3.12 passed.

Phase 4 — frontend implemented: responsive Dashboard, Applications, Board and Interviews; search/filter/sort/pagination, accessible native dialogs, forms, stage updates, confirmation and local-time interview display. Production TypeScript/Vite build verified locally after adding Vite CSS module declarations. Browser interaction verification pending.

Phase 5 — runtime packaging implemented: explicit idempotent fictional seed, self-cleaning HTTP smoke test, non-root Dockerfiles and readiness-ordered Compose with persistent PostgreSQL and one controlled migration service. Container execution remains Blocked: Docker is not installed. No image-build or persistence-restart claim is made.

Phase 6 — Helm implemented: two frontend replicas, backend HPA min=2 with no replicas field to override scaling, resource requests, probes, ClusterIP Services, prefix-preserving Ingress, PostgreSQL StatefulSet/PVC, ConfigMap/Secret references, migration hook and optional ServiceMonitor. Database is installed before the initial post-install migration; upgrades run migration before changing pods. Readiness is intentionally connectivity-only so initial migration cannot deadlock Helm waiting. AWS execution remains pending.
