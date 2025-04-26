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
    cpu_used = memory_used = cpu_hard = memory_hard = None

    for line in output.splitlines():
        # Captura o nome da quota
        if "Name:" in line:
            quota_name = line.split(":")[1].strip()
        
        # Captura o uso e limites de CPU e memória
        if "requests.cpu" in line:
            parts = re.split(r'\s{2,}', line.strip())
            cpu_used = parts[1]
            cpu_hard = parts[2]
        elif "requests.memory" in line:
            parts = re.split(r'\s{2,}', line.strip())
            memory_used = parts[1]
            memory_hard = parts[2]

    return quota_name, cpu_used, cpu_hard, memory_used, memory_hard

def convert_cpu(cpu_str):
    return float(cpu_str.replace("m", "")) / 1000 if "m" in cpu_str else float(cpu_str)

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
    args = parser.parse_args()

    try:
        output = run_kubectl_describe(args.namespace)
        quota_name, cpu_used, cpu_hard, mem_used, mem_hard = parse_quota_output(output)

        cpu_used_f = convert_cpu(cpu_used)
        cpu_hard_f = convert_cpu(cpu_hard)
        mem_used_f = convert_memory(mem_used)
        mem_hard_f = convert_memory(mem_hard)

        print(f"\n📦 Namespace: {args.namespace}")
        print(f"Quota: {quota_name}")
        print(f"⚙️  CPU Usada: {cpu_used_f:.2f} cores")
        print(f"⚙️  CPU Total: {cpu_hard_f:.2f} cores")
        print(f"⚙️  CPU Livre: {cpu_hard_f - cpu_used_f:.2f} cores")

        print(f"🧠 Memória Usada: {mem_used_f:.2f} Gi")
        print(f"🧠 Memória Total: {mem_hard_f:.2f} Gi")
        print(f"🧠 Memória Livre: {mem_hard_f - mem_used_f:.2f} Gi\n")

    except subprocess.CalledProcessError as e:
        print("Erro ao executar o kubectl. Verifique se você está conectado ao cluster.")
        print(e)

if __name__ == "__main__":
    main()

