# Stopping and removing environments

## Docker Compose

Stop the stack while preserving its data:

```bash
docker compose down
```

For a deliberate fresh start, `docker compose down -v` permanently deletes the database volume. Export any records you need first.

## Local Kubernetes

Stop port forwarding with Ctrl+C. Quitting Docker Desktop makes the cluster temporarily unavailable. To permanently delete the ApplyTrail cluster and its database:

```bash
.tools/kind delete cluster --name applytrail
```

There is no automatic deletion schedule. GitHub Actions deletes its own disposable kind cluster at the end of each deployment job.

## Optional cloud infrastructure

Before removal, export needed database data and identify the exact resources owned by this installation. Avoid deploying while teardown is running.

1. Uninstall the application and Ingress release while controllers and worker nodes are still available. Remove monitoring and Metrics Server when no longer needed.
2. Wait for the Ingress load balancer and its Service finalizers to disappear. Verify through the AWS load-balancer inventory in the configured region before removing the cluster.
3. Decide whether to retain the PostgreSQL PVC. The gp3 StorageClass uses `Retain`; deleting a claim does not automatically remove its EBS volume. Identify and explicitly handle that specific volume.
4. Review a Terraform destroy plan, then apply only after confirming its contents:

   ```bash
   terraform -chdir=terraform plan -destroy -out=destroy.tfplan
   terraform -chdir=terraform apply destroy.tfplan
   ```

5. Check for leftover load balancers, EBS volumes/snapshots, network interfaces, public IP addresses and log groups. Billing updates can be delayed.
6. Keep encrypted Terraform state until teardown is confirmed. The dedicated state bucket is managed separately; remove its versions and lock objects only when no longer needed. Never delete shared infrastructure or a shared GitHub OIDC provider.
