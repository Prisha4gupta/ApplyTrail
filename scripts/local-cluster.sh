#!/usr/bin/env bash
# Reproducible local demonstration; never selects a cloud context.
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="$PWD/.tools:$PWD/.tools/darwin-arm64:$PATH"
export KUBECONFIG="$PWD/.tools/kubeconfig"
mkdir -p .tools
IMAGE_REPOSITORY="${IMAGE_REPOSITORY:-applytrail}"
IMAGE_TAG="${IMAGE_TAG:-local}"
if ! kind get clusters | grep -qx applytrail; then
  kind create cluster --name applytrail --config k8s/kind.yaml --kubeconfig "$KUBECONFIG" --wait 180s
fi
test "$(kubectl config current-context)" = kind-applytrail
for component in backend frontend; do
  image="$IMAGE_REPOSITORY-$component:$IMAGE_TAG"
  if [[ "${PULL_IMAGES:-false}" == true ]]; then
    docker pull "$image"
  else
    docker build --build-arg "APP_VERSION=$IMAGE_TAG" -t "$image" "$component"
  fi
  kind load docker-image --name applytrail "$image"
done
kubectl apply -f k8s/namespace.yaml
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -
python3 - <<'PY'
import json, secrets, subprocess
def secret(namespace, name, values):
    if subprocess.run(['kubectl','get','secret',name,'-n',namespace],capture_output=True).returncode == 0:
        return
    manifest={'apiVersion':'v1','kind':'Secret','metadata':{'name':name,'namespace':namespace},'type':'Opaque','stringData':values}
    subprocess.run(['kubectl','create','-f','-'],input=json.dumps(manifest),text=True,check=True)
p=secrets.token_hex(24)
secret('applytrail','applytrail-db',dict(POSTGRES_USER='applytrail',POSTGRES_DB='applytrail',POSTGRES_PASSWORD=p,DATABASE_URL=f'postgresql+psycopg://applytrail:{p}@postgres:5432/applytrail'))
secret('monitoring','grafana-admin',{'admin-user':'admin','admin-password':secrets.token_hex(24)})
PY
helm repo add traefik https://traefik.github.io/charts
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm upgrade --install traefik traefik/traefik --version 41.7.1 -n ingress-system --create-namespace -f k8s/traefik-local-values.yaml --wait --timeout 10m
# kind kubelets use locally generated certificates, only in this isolated cluster.
helm upgrade --install metrics-server metrics-server/metrics-server --version 3.14.0 -n kube-system --set 'args[0]=--kubelet-insecure-tls' --wait --timeout 5m
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack --version 92.3.1 -n monitoring -f monitoring/values.yaml --wait --timeout 15m
kubectl create configmap applytrail-dashboard -n monitoring --from-file=applytrail.json=monitoring/dashboard.json --dry-run=client -o yaml | kubectl apply -f -
kubectl label configmap applytrail-dashboard -n monitoring grafana_dashboard=1 --overwrite
helm upgrade --install applytrail helm/applytrail -n applytrail -f helm/applytrail/values-local.yaml --set-string "image.repository=$IMAGE_REPOSITORY" --set-string "image.tag=$IMAGE_TAG" --wait --timeout 10m
kubectl rollout status deployment/backend -n applytrail --timeout=180s
kubectl rollout status deployment/frontend -n applytrail --timeout=180s
python3 scripts/smoke.py http://127.0.0.1:8080
kubectl get pods,svc,ingress,pvc,hpa -n applytrail
