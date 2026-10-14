#!/usr/bin/env bash
set -euo pipefail
# Run only after approved Terraform apply, authenticated kubeconfig, and DB/Grafana secrets.
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/deploy-rbac.yaml
kubectl apply -f k8s/storage.yaml
helm repo add traefik https://traefik.github.io/charts
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm upgrade --install traefik traefik/traefik --version 41.7.1 -n ingress-system --create-namespace -f k8s/traefik-values.yaml --wait --timeout 10m
helm upgrade --install metrics-server metrics-server/metrics-server --version 3.14.0 -n kube-system --wait --timeout 5m
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack --version 92.3.1 -n monitoring --create-namespace -f monitoring/values.yaml --wait --timeout 15m
kubectl create configmap applytrail-dashboard -n monitoring --from-file=applytrail.json=monitoring/dashboard.json --dry-run=client -o yaml | kubectl apply -f -
kubectl label configmap applytrail-dashboard -n monitoring grafana_dashboard=1 --overwrite
kubectl get --raw /apis/metrics.k8s.io/v1beta1/nodes
