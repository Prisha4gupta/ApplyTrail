# Rubric coverage

Source: [official rubric](https://github.com/Nency-Ravaliya/devops-heros/blob/main/session21-python/GRADING.md), reviewed 2026-10-14. Status describes observed verification, never inferred deployment success.

| Area | Marks | Implementation | Verification | Evidence | Status / blocker |
|---|---:|---|---|---|---|
| Application | 10 | backend/, frontend/ | pytest; npm run build; browser CRUD | evidence/ | Not started |
| Testing | 10 | backend/tests/ | pytest -v | evidence/pytest.txt | Not started |
| Git/GitHub | 5 | .gitignore, history | git log; remote URL | evidence/git-history.txt | Implemented; remote pending |
| Docker | 10 | Dockerfiles, docker-compose.yml | compose up; restart/persistence | evidence/compose.txt | Not started; Docker absent |
| CI/CD | 15 | .github/workflows/ | actual Actions run and rollout | workflow URL | Not started; repository/AWS pending |
| Security | 5 | Trivy workflow | both image reports | scan artifacts | Not started |
| Terraform | 15 | terraform/ | fmt, init, validate, plan/apply/destroy | redacted logs | Not started; AWS approval pending |
| Kubernetes/Helm | 15 | helm/, k8s/ | lint/render; rollout/CRUD/HPA | cluster outputs | Not started; cluster pending |
| Monitoring | 10 | monitoring/, ServiceMonitor | metrics parser; target UP; live panels | metrics and screenshots | Not started |
| Documentation/demo | 5 | README.md, docs/ | walkthrough and actual release | recording URL | Implemented in progress; demo pending |

Additional requirements are tracked in the evidence checklist and subsequent phase notes: migrations, seed idempotency, interview cascade, bounded metrics, two replicas, readiness, HPA, persistence, Ingress controller, OIDC, cost approval and confirmed cleanup.
