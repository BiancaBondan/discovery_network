import ipaddress
import socket
import os
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

def identificar_vendor(banner):
    if not banner:
        return "Desconhecido"
    banner = banner.lower()
    if "cisco" in banner:
        return "Cisco"
    elif "mikrotik" in banner:
        return "MikroTik"
    elif "fortios" in banner or "fortigate" in banner:
        return "Fortinet"
    elif "junos" in banner:
        return "Juniper"
    elif "huawei" in banner:
        return "Huawei"
    elif "openssh" in banner:
        return "Linux/BSD"
    elif "microsoft_win32" in banner or "cygwin" in banner:
        return "Windows"
    elif "dropbear" in banner:
        return "Dispositivo Embarcado"
    elif "synology" in banner:
        return "Synology"
    elif "qnap" in banner:
        return "QNAP"
    else:
        return "Desconhecido"

def gerar_ips():
    subredes = ["10.0.0.0/12"]
    for rede in subredes:
        try:
            rede_obj = ipaddress.ip_network(rede)
            for ip in rede_obj.hosts():
                yield str(ip)
        except Exception as e:
            print(f"Erro ao processar {rede}: {e}")

def testar_ssh(ip, porta):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(8)
            s.connect((ip, porta))
            s.sendall(b"SSH-2.0-Test")
            banner = s.recv(1024).decode(errors="ignore")
            if "SSH-" in banner:
                vendor = identificar_vendor(banner)
                return ip, "SSH", porta, vendor
    except Exception:
        return None
    return None

def testar_telnet(ip):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(8)
            s.connect((ip, 23))
            banner = s.recv(1024).decode(errors="ignore")
            vendor = identificar_vendor(banner)
            return ip, "Telnet", 23, vendor
    except Exception:
        return None

def testar_ip(ip, barra_ativos, ativos, inativos):
    for porta in [22, 2269]:
        resultado = testar_ssh(ip, porta)
        if resultado:
            ip_respondido, metodo, porta, vendor = resultado
            ativos.append((ip_respondido, metodo, porta, vendor))
            barra_ativos.update(1)
            return

    resultado = testar_telnet(ip)
    if resultado:
        ip_respondido, metodo, porta, vendor = resultado
        ativos.append((ip_respondido, metodo, porta, vendor))
        barra_ativos.update(1)
        return

    inativos.append(ip)

def scan_dispositivos():
    ativos = []
    inativos = []
    print("\nEscaneando ...\n")

    with tqdm(desc="Testando IPs", unit="IP", dynamic_ncols=True) as barra_ips:
        with tqdm(desc="Dispositivos Ativos", unit="ativo", dynamic_ncols=True) as barra_ativos:
            with ThreadPoolExecutor(max_workers=50) as executor:
                futures = []
                for ip in gerar_ips():
                    barra_ips.update(1)
                    future = executor.submit(testar_ip, ip, barra_ativos, ativos, inativos)
                    futures.append(future)
                for future in futures:
                    future.result()

    return ativos

def salvar_ips_ativos(ativos):
    caminho = "/root/scripts/"
    os.makedirs(caminho, exist_ok=True)
    with open(caminho + "MA_ips_ativos_teste.txt", "w") as f:
        for ip, metodo, porta, vendor in ativos:
            f.write(f"{ip} - {metodo} - Porta: {porta} - Vendor: {vendor}\n")
    print(f"{len(ativos)} IPs ativos salvos em 'MA_ips_ativos_teste.txt'.")

if __name__ == "__main__":
    ativos = scan_dispositivos()
    salvar_ips_ativos(ativos)


