#!/usr/bin/env bash
# Confere o vehicle-sales publicado no cluster atual do kubectl: API no ar e
# conectada ao próprio banco. O fluxo de compra com o vehicle-core é testado
# à parte, com "make e2e-test" no repositório vehicle-core.
# Uso: scripts/smoke-test.sh
set -euo pipefail

NAMESPACE="vehicle-sales"
LOCAL_PORT="${LOCAL_PORT:-18000}"

kubectl -n "${NAMESPACE}" port-forward svc/vehicle-sales-api "${LOCAL_PORT}:8000" >/dev/null &
PF_PID=$!
trap 'kill "${PF_PID}" 2>/dev/null || true' EXIT
for _ in $(seq 1 30); do
  nc -z localhost "${LOCAL_PORT}" 2>/dev/null && break
  sleep 1
done

request() {
  curl -sS --fail-with-body --retry 10 --retry-delay 2 --retry-connrefused "http://localhost:${LOCAL_PORT}$1"
}

echo "1. Conferindo se a API responde"
request /health | jq -e '.status == "ok"' >/dev/null

echo "2. Conferindo a conexão com o banco vehicle_sales"
request /health/ready | jq -e '.database == "ok"' >/dev/null

echo "3. Conferindo as réplicas do HPA"
kubectl -n "${NAMESPACE}" get hpa vehicle-sales-api

echo "Smoke test concluído com sucesso."
