# Version decisions and official sources

Reviewed 2026-10-14. Use committed locks for exact dependencies; do not replace them with unbounded installs in CI.

| Component | Selected | Basis |
|---|---|---|
| Python | 3.12.14 | Bundled local interpreter; Python 3.12 container and CI |
| FastAPI | 0.143.0 | https://fastapi.tiangolo.com/release-notes/ |
| SQLAlchemy / Alembic | 2.1.4 / 1.20.0 | Current PyPI metadata, successfully installed/tested together |
| Psycopg | 3.3.6 | Binary PostgreSQL driver; exact lock |
| React / Vite / TypeScript | 19.3.0 / 8.3.4 / 7.0.2 | npm registry; https://vite.dev/guide/; production build passes |
| Node | 24.15.0 | Installed version; satisfies Vite Node requirements |
| PostgreSQL | 17.11-alpine3.24 | Official Docker Hub tag listing; current 17 patch |
| Nginx unprivileged | 1.30.5-alpine3.24 | Official nginxinc Docker Hub tags |
| Terraform / AWS provider | 1.13.3 / exact lockfile | Official HashiCorp release; init and validate passed |
| EKS | 1.35 | https://docs.aws.amazon.com/eks/latest/userguide/kubernetes-versions.html |
| Helm | 3.19.0 | Official release checksum verified locally |
| Traefik chart | 41.7.1 | Official https://traefik.github.io/charts/index.yaml |
| Metrics Server chart | 3.14.0 | Official https://kubernetes-sigs.github.io/metrics-server/index.yaml |
| kube-prometheus-stack | 92.3.1 | Official https://prometheus-community.github.io/helm-charts/index.yaml |
| Trivy | 0.75.0 | Official GitHub release metadata |

Image tags are version-pinned, not digest-pinned. Trivy gates both built images on every release; both application image scans passed in CI run 38586804223. EKS addon versions are discovered for compatibility during planning and should be copied into addon_versions after review. Chart version availability and rendered validity do not prove EKS runtime compatibility; actual installation remains pending.

Official assessment sources: https://github.com/Nency-Ravaliya/devops-heros/blob/main/session21-python/README.md and GRADING.md. No student-guide.md or equivalent session-21 guide was found in the repository tree.

Backend runtime remediation: Python 3.12.14 Alpine 3.24 replaced Debian Bookworm following actual Trivy findings; both scans and Compose passed in run 38586804223. See security-results.md.
