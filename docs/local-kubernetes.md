# Local Kubernetes

This setup runs a real Kubernetes cluster inside Docker Desktop using kind. The application is deployed through Helm with PostgreSQL persistent storage, two frontend replicas, backend autoscaling (minimum two), Traefik Ingress, Metrics Server, Prometheus and Grafana.

## Start

Keep Docker Desktop running with approximately 8 GB memory available. Install kubectl, kind 0.33.0 and Helm 3.19.0. This checkout also supports the verified binaries under `.tools/` (ignored by Git).

```bash
cd /path/to/ApplyTrail
bash scripts/local-cluster.sh
export KUBECONFIG="$PWD/.tools/kubeconfig"
export PATH="$PWD/.tools:$PWD/.tools/darwin-arm64:$PATH"
kubectl exec -n applytrail deployment/backend -- python -m app.seed
```

Open http://localhost:8080. Port 3000 is the separate Docker Compose application. This cluster's API and Ingress bind to localhost. Do not share the kubeconfig or Secret contents.

The script creates fresh random credentials only when their Secrets do not exist. Data survives pod recreation but deleting the kind cluster deletes its local database storage. Local replicas share one Docker node; this is a demonstration of Kubernetes scheduling, not multi-machine availability.

## Inspect the deployment

```bash
helm list -A
kubectl get pods,svc,ingress,pvc,hpa -n applytrail
kubectl top pods -n applytrail
python3 scripts/smoke.py http://localhost:8080
```

Confirm Running/Ready pods, Bound storage and successful smoke checks. An HPA may need a minute to collect CPU metrics after startup.

## Open monitoring

In two separate terminals, from the repository root:

```bash
kubectl --kubeconfig .tools/kubeconfig -n monitoring port-forward svc/monitoring-grafana 3001:80
```

```bash
kubectl --kubeconfig .tools/kubeconfig -n monitoring port-forward svc/monitoring-kube-prometheus-prometheus 9090:9090
```

Open http://localhost:3001 (Grafana) and http://localhost:9090 (Prometheus). Grafana's username is `admin`. To copy its generated password directly to your Mac clipboard without printing it:

```bash
kubectl --kubeconfig .tools/kubeconfig -n monitoring get secret grafana-admin -o jsonpath='{.data.admin-password}' | base64 --decode | pbcopy
```

Paste into Grafana, then replace the clipboard contents. Open the **ApplyTrail · Application health** dashboard. In Prometheus, inspect Targets and find the ApplyTrail backend targets.

Generate traffic in a third terminal:

```bash
python3 scripts/load.py http://localhost:8080 120 16
```

Wait for scrapes; request-rate and latency panels should populate. Watch `kubectl get hpa backend -n applytrail -w` during load. The HPA scales only when measured CPU utilization exceeds its target.

## Update a release

Use a unique image tag for each local release, so Kubernetes observes the image change:

```bash
IMAGE_TAG="demo-$(date +%Y%m%d%H%M%S)" bash scripts/local-cluster.sh
```

The backend's `/api/version` reports this tag. GitHub Actions also deploys the scanned, published commit-SHA images to a disposable kind cluster and runs the smoke checks. This automated deployment runs on the GitHub runner; it does not update your laptop. The separate EKS deployment job is opt-in through repository variable `ENABLE_EKS_DEPLOY=true` and requires its documented environment configuration.

## Runtime checks

Check the application CRUD flow, Helm releases, Ready replicas, Services, Ingress, Bound PVC, live Prometheus targets and populated Grafana panels. Compare release versions with the GitHub run and image tags. Use the controlled Service-selector failure and recovery procedure in `docs/troubleshooting.md`, confined to this demonstration cluster.

The setup runs entirely in Docker Desktop. The optional Terraform configuration is independent of this local cluster.

## Stop and remove the cluster

Ctrl+C stops port forwarding. Quitting Docker Desktop makes the local demonstration unavailable. To permanently delete this demo and its database, explicitly run:

```bash
.tools/kind delete cluster --name applytrail
```

There is no scheduled automatic deletion. Export any data you need before deleting the cluster.
