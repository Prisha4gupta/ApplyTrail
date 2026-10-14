# Troubleshooting and reversible recovery

Always capture `kubectl get pods,svc,ingress,pvc,hpa -n applytrail`, current images and `helm history applytrail -n applytrail` before changing anything. Redact secret-bearing output. Never paste Secret contents into evidence.

| Failure / symptom | Diagnose | Likely cause | Fix | Recovery proof |
|---|---|---|---|---|
| ImagePullBackOff, Pending pod | `kubectl describe pod POD -n applytrail`; `kubectl get events -n applytrail --sort-by=.lastTimestamp` | Wrong SHA, unavailable GHCR package, private image missing credentials | Verify package/tag; set exact image; configure imagePullSecrets or public packages | rollout succeeds; actual imageID matches registry digest |
| Ingress 503 / no service endpoints | `kubectl get endpointslices -n applytrail`; `kubectl get pods --show-labels -n applytrail`; `kubectl describe svc backend -n applytrail` | Selector mismatch | Restore app=applytrail, component=backend | endpoints populated; smoke passes |
| Database connection 503 | `kubectl logs deploy/backend -n applytrail`; `kubectl logs postgres-0 -n applytrail`; `kubectl get pvc -n applytrail` | Bad secret, DNS, unavailable volume or postgres | Correct runtime Secret and restart backend; resolve PVC/CSI events; preserve data | /ready 200 and persisted CRUD succeeds |
| Readiness failed | `kubectl describe pod POD -n applytrail`; `kubectl logs POD -n applytrail` | Wrong port/path or DB unreachable | Restore /ready:8000 and DB connection; liveness stays lightweight | ready endpoints return; rollout completes |
| Prometheus target missing/down | `kubectl get servicemonitor -n applytrail -o yaml`; `kubectl get svc backend -n applytrail -o yaml` | Namespace/release label/port mismatch | release=monitoring; component=backend; named port http; /metrics | target UP and rate query populated |
| HPA unknown CPU | `kubectl describe hpa backend -n applytrail`; `kubectl top pods -n applytrail`; `kubectl get apiservice v1beta1.metrics.k8s.io` | Metrics Server unavailable or missing CPU request | Fix Metrics Server connectivity/TLS and CPU requests; do not blindly disable TLS verification | numeric utilization and desired replicas; bounded-load observation |

## Controlled selector failure (demo environment only)

Use an interactive terminal with a second terminal ready for immediate recovery. Do not run during CI deployment.

```bash
kubectl get svc backend -n applytrail -o yaml > /tmp/applytrail-known-good-service.yaml
kubectl get endpointslices -n applytrail
kubectl patch svc backend -n applytrail --type merge -p '{"spec":{"selector":{"component":"deliberate-demo-failure"}}}'
kubectl describe svc backend -n applytrail
kubectl get endpointslices -n applytrail
kubectl get events -n applytrail --sort-by=.lastTimestamp
# Recover immediately, including if diagnosis is interrupted:
kubectl patch svc backend -n applytrail --type merge -p '{"spec":{"selector":{"component":"backend"}}}'
kubectl get endpointslices -n applytrail
python3 scripts/smoke.py http://INGRESS_ADDRESS
```

Capture before/broken/diagnosis/fixed screenshots and the exact time. Expected behavior is a temporary API failure with frontend error feedback. The exercise is **pending** until performed on the real demo cluster. A written runbook is not recovery evidence.

## Rollback

`helm history applytrail -n applytrail`, then `helm rollback applytrail PREVIOUS_REVISION -n applytrail --wait --timeout 10m`, inspect image SHAs and smoke-test. Application rollback does not safely reverse a database migration. Use additive, backward-compatible schema changes and a tested backup/restore plan before destructive schema changes. Do not blindly run Alembic downgrade against deployed data.
