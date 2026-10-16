# Local Kubernetes verification — October 16, 2026

Environment: Docker Desktop on Apple silicon, kind 0.33.0, Kubernetes 1.37.0, one local node. App URL: http://localhost:8080 through Traefik Ingress. This report records observed results rather than inferred configuration behavior.

| Check | Observed result |
|---|---|
| Helm release and Ingress | Application deployed; frontend HTML and API CRUD smoke passed |
| Replicas | Two frontend and initially two backend pods Ready |
| Database storage | PostgreSQL PVC Bound using local standard storage |
| Persistence | A disposable application remained after deleting/recreating the PostgreSQL pod |
| Monitoring | Backend scrape targets UP; all four panel queries returned finite values |
| Grafana | Authenticated dashboard API returned the provisioned ApplyTrail dashboard |
| Load | 46,894 successful requests, zero failed, 90 seconds, 16 workers |
| Autoscaling | HPA events recorded growth from two to four to five backend replicas |
| Failure/recovery | Deliberate backend Service selector mismatch produced HTTP 503; restoring the selector recovered the API and stored data |

Runtime fixes: Traefik 41.7.1 requires `service.spec.type`; Grafana 13 required more than the original 256 MiB memory cap, so the cap was raised to 768 MiB. The error-rate query now returns zero when there are no recorded 5xx responses.

Sanitized captures live in `evidence/2026-10-16-kind-*`. The application screenshot is a real browser capture. Prometheus values are measured at capture time and will change with traffic; replicas fall back toward two after load subsides.

The new GitHub Actions Kubernetes job uses a disposable runner cluster and pulls the exact scanned SHA images. The [GitHub run](https://github.com/Prisha4gupta/ApplyTrail/actions/runs/38849684438) at commit `9b400e2` completed successfully, including deployment and live monitoring checks. The optional EKS job was skipped. Local verification does not claim Terraform plan/apply/destroy execution or cloud infrastructure.

For the presentation, follow [Local Kubernetes](local-kubernetes.md). Keep Docker Desktop running. Your professor cannot reach your laptop through a localhost URL from another computer; provide the repository and a recording or demonstrate on this Mac.

Browser verification also confirmed four populated Grafana graphs, including the load spike and replicas increasing to five then returning to two. The percentage axis is explicitly bounded from zero to one (0–100%), and legends use readable panel names.
