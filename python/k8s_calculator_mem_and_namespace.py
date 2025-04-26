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
    memory_used = memory_hard = None

    for line in output.splitlines():
        # Captura o nome da quota
        if "Name:" in line:
            quota_name = line.split(":")[1].strip()
        
        # Captura o uso e limites de memória
        if "requests.memory" in line:
            parts = re.split(r'\s{2,}', line.strip())
            memory_used = parts[1]
            memory_hard = parts[2]

    return quota_name, memory_used, memory_hard

def convert_memory(mem_str):
    mem_str = mem_str.lower()
    if "mi" in mem_str:
        return float(mem_str.replace("mi", "")) / 1024
    elif "gi" in mem_str:
        return float(mem_str.replace("gi", ""))
    return float(mem_str)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--namespace", required=True, help="Nome do namespace")
    parser.add_argument("-m", "--memory", required=True, help="Memória por pod (ex: 1.6Gi)")
    parser.add_argument("-r", "--replicas", type=int, required=True, help="Número de réplicas")
    args = parser.parse_args()

    try:
        output = run_kubectl_describe(args.namespace)
        quota_name, mem_used, mem_hard = parse_quota_output(output)

        mem_used_f = convert_memory(mem_used)
        mem_hard_f = convert_memory(mem_hard)
        memory_per_pod_f = convert_memory(args.memory)

        print(f"\n📦 Namespace: {args.namespace}")
        print(f"Quota: {quota_name}")
        print(f"🧠 Memória Usada: {mem_used_f:.2f} Gi")
        print(f"🧠 Memória Total: {mem_hard_f:.2f} Gi")
        print(f"🧠 Memória Livre: {mem_hard_f - mem_used_f:.2f} Gi")

        print(f"\n🧠  Memória por pod: {args.memory}")
        print(f"🔢 Número de réplicas: {args.replicas}")
        print(f"🧠  Memória Total do deployment: {memory_per_pod_f * args.replicas:.2f} Gi\n")

    except subprocess.CalledProcessError as e:
        print("Erro ao executar o kubectl. Verifique se você está conectado ao cluster.")
        print(e)

if __name__ == "__main__":
    main()

