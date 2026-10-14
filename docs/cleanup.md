# Cleanup plan — prepared before provisioning

Do not execute until evaluation is finished and the owner explicitly confirms destruction and data retention policy. Proposed policy: discard synthetic database contents after evaluation; preserve sanitized evidence. Confirm before executing.

1. Save screenshots, workflow links, current release SHA, sanitized Terraform outputs and any agreed database export. Never commit credentials, kubeconfig, raw state or binary plans.
2. Stop load generation (Ctrl+C; all scripts are bounded). Disable scheduled/manual deployment triggers or avoid pushes during cleanup.
3. While the controllers/nodes still work: `helm uninstall applytrail -n applytrail`; `helm uninstall traefik -n ingress-system`; `helm uninstall monitoring -n monitoring`; `helm uninstall metrics-server -n kube-system`.
4. Wait for Service finalizers and AWS load balancers to disappear. Check `kubectl get svc -A` and `aws elbv2 describe-load-balancers --region ap-south-1`; also check classic load balancers with `aws elb describe-load-balancers`. Identify only resources belonging to this project. Do not destroy controllers while external cleanup is pending.
5. PostgreSQL StatefulSet PVC is retained by Kubernetes. With confirmed discard policy, delete `data-postgres-0` in applytrail. The StorageClass also uses Retain: identify its exact EBS volume ID from the PV, confirm ownership, then delete the retained PV and EBS volume explicitly. Do not blanket-delete volumes.
6. `terraform -chdir=terraform plan -destroy -out=destroy.tfplan`; review; `terraform -chdir=terraform apply destroy.tfplan`. Record sanitized successful output only after it occurs.
7. Check for leftover EBS volumes/snapshots, load balancers, network interfaces, public IPs, CloudWatch log groups and NAT gateways. The design has no NAT, but verify the account inventory anyway. Recheck the billing console after charges settle; it is delayed.
8. The state bucket is deliberately outside the application state. Retain encrypted state until teardown is confirmed. Delete object versions/lock files and the bucket only with separate approval and only if dedicated to this project. Do not delete an existing shared GitHub OIDC provider.

Local: `docker compose down` preserves data. **Destructive local reset:** `docker compose down -v` deletes the local PostgreSQL volume permanently. Never use that command merely to restart the app.

Status: no AWS resources created; destroy evidence pending, not simulated.
