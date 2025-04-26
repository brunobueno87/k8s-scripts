#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<EOF
Uso: $0 <replica-set> [namespace]

Parâmetros:
  replica-set   Nome ou hash do ReplicaSet (ex: repicaset-name-5d8479d499)
  namespace     Namespace Kubernetes (padrão: seu-name-space)

Exemplo:
  $0 replicaset-name-5d8479d499 seu-name-space
EOF
  exit 1
}

trap 'echo "\nErro durante a execução do script."; usage' ERR

if [[ $# -lt 1 ]]; then
  echo "Erro: ReplicaSet não informado."
  usage
fi

RS=$1
NS=${2:-seu-name-space}

if ! kubectl get namespace "$NS" &>/dev/null; then
  echo "Erro: namespace '$NS' não encontrado."
  usage
fi

mapfile -t pods < <(
  kubectl get pods -n "$NS" --no-headers -o custom-columns=NAME:.metadata.name \
    | grep -E "^${RS}-" || true
)

if [[ ${#pods[@]} -eq 0 ]]; then
  echo "Erro: nenhum pod encontrado para ReplicaSet '$RS' no namespace '$NS'."
  usage
fi

toMi() {
  local val="$1" unit num
  unit="${val: -2}"
  num="${val:0:${#val}-2}"
  case "$unit" in
    Ki) awk "BEGIN{printf \"%.2f\", $num/1024}";;
    Mi) printf "%s" "$num";;
    Gi) awk "BEGIN{printf \"%.2f\", $num*1024}";;
    *)  printf "%s" "$num";;
  esac
}

printf "%-40s %8s %8s %8s %8s\n" "POD" "CPU(m)" "CPU%" "MEM(Mi)" "MEM%"

for pod in "${pods[@]}"; do
  read cpuUsedRaw memUsedRaw < <(kubectl top pod "$pod" -n "$NS" --no-headers | awk '{print $2, $3}')
  cpuUsed=${cpuUsedRaw%m}
  memUsed=${memUsedRaw%Mi}

  cpuLimRaw=$(kubectl get pod "$pod" -n "$NS" -o jsonpath='{.spec.containers[0].resources.limits.cpu}')
  cpuLim=${cpuLimRaw%m}

  memLimRaw=$(kubectl get pod "$pod" -n "$NS" -o jsonpath='{.spec.containers[0].resources.limits.memory}')
  memLim=$(toMi "$memLimRaw")

  cpuPct=$(awk "BEGIN{printf \"%.1f\", ($cpuUsed/$cpuLim)*100}")
  memPct=$(awk "BEGIN{printf \"%.1f\", ($memUsed/$memLim)*100}")

  printf "%-40s %8s %7s%% %8s %7s%%\n" \
    "$pod" "$cpuUsed" "$cpuPct" "$memUsed" "$memPct"
done
