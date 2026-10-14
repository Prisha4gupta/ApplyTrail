# Capstone demonstration

Before recording: confirm synthetic data only, successful bootstrap, current release SHA, GitHub package visibility, evidence directory and cleanup approval procedure. Do not expose secrets on-screen.

1. Open Ingress; create “Demo Aurora / Platform Intern”, Applied. Show it survives page reload.
2. Board: move to Interview. Open application; add a future Video interview in your local timezone. Show dashboard active/interview counts and upcoming event.
3. Explain PostgreSQL, foreign key cascade and Alembic. Show `alembic current` via a temporary backend execution without printing connection strings.
4. Change a visible line (e.g. dashboard subtitle) in frontend/src/main.tsx. Run build and tests, commit a meaningful message, push main.
5. Open actual Actions run: isolated PostgreSQL migration/tests, frontend build, both image builds, both Trivy JSON artifacts. Explain findings honestly; a failing gate correctly prevents deployment.
6. Show GHCR full SHA tags and image digests. Show the Helm deployment job using the same SHA, rollout completion and self-cleaning smoke check.
7. Reload Ingress; verify the visible change and Release label match the commit. Confirm Kubernetes images with `kubectl get deployments -n applytrail -o wide`.
8. Generate traffic: `python3 scripts/load.py http://INGRESS_ADDRESS 120 16`. Open Prometheus through port-forward; show target UP. Show Grafana request rate, errors, latency and replica panels with real samples (allow several scrapes).
9. In another terminal, `kubectl get hpa backend -n applytrail -w` and `kubectl top pods -n applytrail`. Record numeric utilization and any scale-up/down. A lightweight request may not cross the threshold. If it does not scale, report that and adjust bounded concurrency within capacity; never invent scaling evidence or add an unsafe unbounded CPU endpoint.
10. Execute the reversible selector exercise in troubleshooting.md; show baseline, diagnosis, fix and passing smoke.
11. Explain state locking, OIDC trust, no committed credentials, single-user limitations and persistence tradeoffs.
12. After assessment and explicit confirmation, follow cleanup.md and capture actual destroy/remaining-resource evidence.

Current status: live GitHub/AWS demonstration pending. This script describes required actions, not completed evidence.
