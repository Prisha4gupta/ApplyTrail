# Evidence checklist

Store captures as `evidence/YYYY-MM-DD-area-description.ext`. Review for secrets before adding. The text files already present are genuine local command output; screenshot entries remain pending unless a file is linked below.

| Item | Capture method | What it proves | Current status |
|---|---|---|---|
| App desktop/mobile | Browser screenshot after CRUD, different viewport | Rendered UI and visible data | evidence/2026-10-14-dashboard.png and 2026-10-14-mobile.png; browser-checks.txt records scope |
| Pytest | `cd backend; pytest -v` | Actual isolated test outcomes | evidence/pytest.txt; Verified locally (SQLite) |
| PostgreSQL tests | Actions verify log | Actual PostgreSQL migration/CRUD | Verified in CI: run 38502731767 verify job passed |
| Frontend build | `npm ci; npm run build` | TypeScript and bundle build | evidence/frontend-build.txt; Verified locally |
| Git history | `git log --oneline` and screenshot | At least ten real commits | evidence/git-history.txt; ten commits pushed |
| Compose | `docker compose ps`; logs; browser | Containers healthy | Verified in CI run 38586804223; local Docker absent |
| Restart persistence | Create record; restart backend/frontend; GET again | DB data survives app restart | Verified in CI: compose-persistence-38586804223.txt |
| Actions | Actual run permalink | Individual pipeline gates | Run 38586804223: all predeployment jobs passed; deployment failed on missing AWS setup |
| GHCR | Both package pages with full SHA/digest | Published release identity | Both push jobs passed in CI; package screenshot/pull from EKS pending |
| Trivy | Both retained JSON artifacts and 2–3 sentence finding explanation | What was scanned; CVE severity/gate | Both scans passed in run 38586804223; original failed report and explanation retained |
| Terraform init/validate | Local command logs | Provider init and syntax/schema validity | evidence/terraform-init.txt, terraform-validate.txt |
| Terraform plan/apply | Sanitized CLI output and Console | Actual resources, not templates | Blocked: AWS credentials/cost approval |
| VPC/subnets/EKS/nodes | Console screenshots and describe commands | Two public AZ subnets and workers | Pending |
| Helm local | lint and rendered invariant checks | Coherent rendered configuration | evidence/helm-lint.txt, helm-invariants.txt |
| Kubernetes release | `helm list`; pods, svc, ingress, pvc, hpa | Actual running deployment | Pending |
| Ingress CRUD | Browser + smoke log + running image versions | Working routes and release | Pending AWS; evidence/local-smoke.txt is local only |
| Metrics endpoint | curl then Prometheus parser | Valid metrics exposition | Pytest verified; live capture pending |
| Prometheus UP | Targets page with app endpoint | Actual scraping | Pending |
| Grafana data | Dashboard screenshot during traffic | Real measurements | Pending |
| HPA | Timestamped watch/top output during bounded load | Actual scaling | Pending |
| Recovery | Baseline, failure, diagnosis, fix and smoke | Controlled incident recovery | Pending |
| Demo recording | Link with commit-to-release sequence | End-to-end delivery understanding | Pending |
| Destroy | Sanitized destroy output + leftover inventory | Cleanup actually occurred | Pending evaluation/approval |

No CI/AWS row should be promoted to Verified in CI / Verified on AWS until the corresponding actual observation exists.
