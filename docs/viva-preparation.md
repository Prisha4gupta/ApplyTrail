# Viva preparation

- **Why FastAPI?** Typed validation, OpenAPI and a small ASGI service make the API easy to test and operate.
- **Why PostgreSQL?** Durable relational data, constraints and transactions; interviews have a foreign key to applications.
- **What does Alembic do?** Versions schema changes separately from runtime startup. One controlled release Job migrates, not every replica.
- **Readiness versus liveness?** Liveness checks the process cheaply. Readiness checks DB connectivity; an unready pod leaves Service endpoints without unnecessary process restarts.
- **Why a multi-stage image?** Build tooling stays out of the Nginx runtime. Runtime containers use non-root identities and drop capabilities.
- **Why full SHA tags?** A release maps to source. CI builds once, scans that local image and pushes it without rebuilding. Registry digests provide stronger content identity.
- **What does Trivy prove?** It matches image packages to known vulnerabilities at scan time. A clean report is not a guarantee; HIGH/CRITICAL findings stop delivery, including unfixed ones.
- **What is OIDC?** GitHub exchanges a short-lived identity token for an AWS role. Trust requires this repository and demo environment; role permission only describes this cluster, and EKS access is namespace-scoped.
- **Terraform versus Helm?** Terraform creates network/cluster/IAM; Helm packages resources inside Kubernetes. State needs encrypted storage and locking.
- **Why two subnets?** EKS spans availability zones. Public nodes avoid demo NAT cost but have weaker network isolation than private nodes.
- **Why CPU requests for HPA?** Utilization is CPU usage divided by requested CPU. Without requests or Metrics Server, the HPA cannot compute its target.
- **What survives a restart?** PostgreSQL data on the PVC/Compose volume. Container-local files do not. A PVC alone is not a backup or HA.
- **Why route templates in metrics?** One label per route prevents unbounded time-series growth and avoids leaking IDs/notes into monitoring.
- **Why no success rate?** Current offer count divided by all saved applications is misleading. The dashboard shows clearly defined counts.
- **What can fail after rollback?** Schema changes may be incompatible with the old app; rolling back the image does not undo the database safely.
- **What does this project still need for production?** Authentication, authorization, TLS, tested backups, HA database, abuse controls and a formal threat/cost review.
- **How do you prove delivery?** Match Git commit, Actions run, GHCR SHA/digest, running pod images and visible release identifier. Configuration alone proves none of these.
