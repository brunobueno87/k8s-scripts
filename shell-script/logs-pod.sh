#!/bin/bash
# --------------------------------------------------------------------
# Script para coletar logs de múltiplos pods em um namespace no K8s.
# Uso:
#   ./logs-pod.sh <namespace> <filtro-nome-do-pod>
#
# Parâmetros:
#   $1 - Nome do namespace (ex: psp-receivable-assignment)
#   $2 - Parte do nome do pod para filtrar (ex: receivable-assignment-acquirer)
# --------------------------------------------------------------------

if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Uso: $0 <namespace> <filtro-nome-do-pod>"
  exit 1
fi

for pod in $(kubectl get pods -n $1 -o name | grep $2); do
  echo ">>> Logs do pod: $pod"
  kubectl logs $pod -n $1 | egrep -i 'decode|retryable|error|exception|warn'
done
