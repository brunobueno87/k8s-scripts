import subprocess
import argparse
import re

def run_kubectl_describe(namespace: str) -> str:
    result = subprocess.run(
        ["kubectl", "describe", "quota", "-n", namespace],
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout

def parse_quota_output(output: str):
    quota_name = None
    cpu_used = cpu_hard = None

    for line in output.splitlines():
        # Captura o nome da quota
        if "Name:" in line:
            quota_name = line.split(":")[1].strip()
        
        # Captura o uso e limites de CPU
        if "requests.cpu" in line:
            parts = re.split(r'\s{2,}', line.strip())
            cpu_used = parts[1]
            cpu_hard = parts[2]

    return quota_name, cpu_used, cpu_hard

def convert_cpu(cpu_str):
    return float(cpu_str.replace("m", "")) / 1000 if "m" in cpu_str else float(cpu_str)

def main():
    parser = argparse.ArgumentParser(
        description="Calcula o uso de CPU e recursos de um namespace Kubernetes com base no deployment."
    )
    parser.add_argument(
        "-n", "--namespace", required=True, help="Nome do namespace no Kubernetes"
    )
    parser.add_argument(
        "-c", "--cpu", required=True, help="Quantidade de CPU por pod (ex: 1900m)"
    )
    parser.add_argument(
        "-r", "--replicas", type=int, required=True, help="Número de réplicas"
    )

    # Adicionando um exemplo na ajuda
    parser.epilog = (
        "Exemplo de execução:\n"
        "$ python3 k8s_calculator_cpu_and_namespace.py -n psp-receivable-assignment -c '1900m' -r 4"
    )

    args = parser.parse_args()

    try:
        output = run_kubectl_describe(args.namespace)
        quota_name, cpu_used, cpu_hard = parse_quota_output(output)

        cpu_used_f = convert_cpu(cpu_used)
        cpu_hard_f = convert_cpu(cpu_hard)
        cpu_per_pod_f = convert_cpu(args.cpu)

        print(f"\n📦 Namespace: {args.namespace}")
        print(f"Quota: {quota_name}")
        print(f"⚙️  CPU Usada: {cpu_used_f:.2f} cores")
        print(f"⚙️  CPU Total: {cpu_hard_f:.2f} cores")
        print(f"⚙️  CPU Livre: {cpu_hard_f - cpu_used_f:.2f} cores")

        print(f"\n⚙️  CPU por pod: {args.cpu}")
        print(f"🔢 Número de réplicas: {args.replicas}")
        print(f"⚙️  CPU Total do deployment: {cpu_per_pod_f * args.replicas:.2f} cores\n")

    except subprocess.CalledProcessError as e:
        print("Erro ao executar o kubectl. Verifique se você está conectado ao cluster.")
        print(e)

if __name__ == "__main__":
    main()

