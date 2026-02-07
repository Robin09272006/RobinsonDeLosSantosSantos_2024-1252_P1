# RobinsonDeLosSantosSantos_2024-1252_P1
# Como atacar y mitigar los ARP Spoofing y los CDP Flooding


**Matrícula:** 2024-1252
**Asignatura:** Seguridad de Sistemas Operativos / Redes
**Entorno:** Laboratorio Virtual (GNS3/EVE-ng con Kali Linux y Cisco IOSv)

---

## 1. Objetivo de los Scripts

El propósito de este conjunto de herramientas es demostrar las vulnerabilidades inherentes en protocolos de red que carecen de autenticación predeterminada.

1.  **`mitm_arp.py` (ARP Spoofing):**
    * Intercepta el tráfico entre una víctima y la puerta de enlace (Gateway).
    * Envenena la tabla ARP de la víctima haciéndole creer que la máquina atacante es el Router.
    * Envenena la tabla ARP del Router haciéndole creer que la máquina atacante es la víctima.

2.  **`cdp_dos.py` (CDP Flooding):**
    * Genera una inundación de paquetes *Cisco Discovery Protocol* (CDP) con identificadores aleatorios.
    * Satura la tabla de vecinos del switch y consume recursos de CPU/Memoria del dispositivo de red.

---

## 2. Topología de Red

El laboratorio se ha configurado utilizando el esquema de direccionamiento basado en la matrícula: `24.12.52.0/24`.

### Diagrama Lógico
> **Nota:** La topología consta de un Router (Gateway), un Switch L2, una máquina atacante (Kali Linux) y una víctima (PC/Windows).

<img width="498" height="542" alt="Captura de pantalla 2026-02-06 222701" src="https://github.com/user-attachments/assets/61f72364-0cf8-45bc-b48c-258a53963584" />


### Tabla de Direccionamiento e Interfaces

| Dispositivo | Interfaz | Dirección IP | Dirección MAC (Ejemplo) | Rol |
| :--- | :--- | :--- | :--- | :--- |
| **R1 (Gateway)** | Gi0/0 | `24.12.52.1/24` | `00:0c:29:30:5f:25` | Puerta de Enlace |
| **Switch L2** | VLAN 1 | N/A | N/A | Distribución |
| **Kali Linux** | Eth0 | `24.12.52.2` | `aa:bb:cc:dd:ee:ff` | Atacante |
| **PC1 / Victima** | Eth0 | `24.12.52.3` | `ca:01:1a:40:00:00` | Víctima |

---

## 3. 🛠️ Requisitos del Sistema

Para ejecutar estas herramientas se requiere el siguiente entorno:

* **Sistema Operativo:** Kali Linux (o cualquier distribución Linux basada en Debian).
* **Lenguaje:** Python 3.x.
* **Privilegios:** Root / Sudo (necesario para la manipulación de sockets de red).
* **Librerías Python:**
    ```bash
    pip3 install scapy
    ```

---

## 4. Ejecución y Parámetros

### A. Ataque ARP Spoofing (`mitm_arp.py`)

Este script utiliza la librería Scapy para enviar paquetes ARP "is-at" falsificados.

**Parámetros configurables en el script:**
* `VICTIM_IP`: Dirección IP del objetivo (Ej: `24.12.52.3`).
* `GATEWAY_IP`: Dirección IP del router (Ej: `24.12.52.1`).
* `time.sleep(2)`: Intervalo de envío para mantener el envenenamiento sin saturar la red.

**Evidencia de Ejecución:**

1.  *Estado inicial (Ping correcto antes del ataque):*
    Ping y prueba con arp
<img width="534" height="215" alt="Captura de pantalla 2026-02-06 222834" src="https://github.com/user-attachments/assets/c830de2a-e735-48e5-8c26-3cae1662ff94" />

2.  *Ejecución del Script en Kali Linux:*
Primero realizar un ping a la ip del router para luego ejecutar el script
<img width="594" height="458" alt="Captura de pantalla 2026-02-06 222917" src="https://github.com/user-attachments/assets/8b3d4055-c89b-4b26-881e-f992a4a0dafc" />


3.  *Resultado en la Víctima (Tabla ARP Envenenada):*
    Se observa que tanto la IP del Gateway (`.1`) como la del atacante tienen la **misma dirección MAC**.
<img width="473" height="90" alt="Captura de pantalla 2026-02-06 222939" src="https://github.com/user-attachments/assets/8b217d0c-05fc-4532-806b-dcd022f087a9" />


---

### B. Ataque CDP Flooding (`cdp_dos.py`)

Este script inyecta tramas Ethernet con cabeceras CDP, aleatorizando el `Device ID` para llenar la memoria del switch.

**Parámetros configurables en el script:**
* `interface`: Interfaz de red de salida (Ej: `"eth0"`).
* `load_contrib("cdp")`: Carga los módulos específicos de Cisco en Scapy.
* `CDPMsgDeviceID`: Se genera un string aleatorio (`random_string(10)`) para simular múltiples dispositivos distintos.

**Evidencia de Ejecución:**

1.  *Ejecución del Script:*
<img width="437" height="191" alt="Captura de pantalla 2026-02-06 223128" src="https://github.com/user-attachments/assets/1653af28-d41f-4929-ac76-c307f7de8d8e" />


2.  *Impacto en el Switch (Saturación de vecinos):*
    El comando `show cdp neighbors` muestra muchos dispositivos falsos conectados a la misma interfaz.
 <img width="626" height="475" alt="Captura de pantalla 2026-02-06 223146" src="https://github.com/user-attachments/assets/150b4e4b-79dd-4073-b05d-1eabc254a512" />


---

## 5.Medidas de Mitigación

Para proteger la infraestructura contra estos ataques, se deben implementar las siguientes configuraciones de "Hardening" en los dispositivos Cisco:

### Contra ARP Spoofing
La solución principal es **Dynamic ARP Inspection (DAI)** junto con **DHCP Snooping**.

```cisco
! 1. Habilitar DHCP Snooping globalmente
ip dhcp snooping
ip dhcp snooping vlan 1

! 2. Configurar puertos de confianza (
interface GigabitEthernet0/0
 ip dhcp snooping trust

! 3. Habilitar Dynamic ARP Inspection
ip arp inspection vlan 1
! Esto valida los paquetes ARP contra la base de datos del DHCP Snooping
