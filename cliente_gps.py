"""
Cliente GPS Simulador
Simula un dispositivo GPS que envía su posición en tiempo real
"""

import socket
import time
import random
import math
from datetime import datetime
from protocolo import (
    GPSMessage, 
    generate_device_id,
    MSG_TYPE_ACK,
    MSG_TYPE_NACK,
    STATE_GPS_FIX,
    STATE_MOVING,
    TOTAL_MESSAGE_SIZE
)

# ==================== CONFIGURACIÓN ====================

SERVER_HOST = 'localhost'  # Cambiar a IP del servidor si está en otra máquina
SERVER_PORT = 9999
SEND_INTERVAL = 5  # segundos entre envíos
MAX_RETRIES = 3
RETRY_DELAY = 2  # segundos entre reintentos

# Colores para la consola
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# ==================== CLASE CLIENTE GPS ====================

class GPSClient:
    """
    Simula un dispositivo GPS móvil
    """
    
    def __init__(self, device_name, start_lat, start_lon, altitude=2558):
        """
        Inicializa el cliente GPS
        
        Args:
            device_name (str): Nombre del dispositivo (ej: "GPS-001")
            start_lat (float): Latitud inicial
            start_lon (float): Longitud inicial
            altitude (int): Altitud en metros
        """
        self.device_name = device_name
        self.device_id = generate_device_id(device_name)
        self.latitude = start_lat
        self.longitude = start_lon
        self.altitude = altitude
        self.sequence = 0
        self.battery = 100
        self.signal = random.randint(70, 100)
        self.socket = None
        self.connected = False
        
        # Simulación de movimiento
        self.speed = 0.001  # Grados por actualización (aprox 110metros)
        self.direction = random.uniform(0, 2 * math.pi)  # Dirección en radianes
    
    def connect(self):
        """
        Conecta al servidor
        
        Returns:
            bool: True si conectó exitosamente
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((SERVER_HOST, SERVER_PORT))
            self.connected = True
            
            print(f"{Colors.OKGREEN}✓ Conectado al servidor {SERVER_HOST}:{SERVER_PORT}{Colors.ENDC}")
            return True
        
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error conectando: {e}{Colors.ENDC}")
            self.connected = False
            return False
    
    def disconnect(self):
        """
        Desconecta del servidor
        """
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.connected = False
        print(f"{Colors.WARNING}🔌 Desconectado del servidor{Colors.ENDC}")
    
    def update_position(self):
        """
        Actualiza la posición simulando movimiento
        """
        # Movimiento aleatorio con tendencia
        self.direction += random.uniform(-0.3, 0.3)  # Cambio gradual de dirección
        
        # Calcular nuevo desplazamiento
        dx = self.speed * math.cos(self.direction)
        dy = self.speed * math.sin(self.direction)
        
        self.latitude += dy
        self.longitude += dx
        
        # Mantener coordenadas en rango válido
        self.latitude = max(-90, min(90, self.latitude))
        self.longitude = max(-180, min(180, self.longitude))
        
        # Simular variación de altitud
        self.altitude += random.randint(-5, 5)
        self.altitude = max(2500, min(2600, self.altitude))
        
        # Simular descarga de batería
        self.battery = max(0, self.battery - random.uniform(0.5, 1.5))
        
        # Simular variación de señal
        self.signal = max(0, min(100, self.signal + random.randint(-15, 15)))
    
    def send_gps_data(self):
        """
        Envía datos GPS al servidor
        
        Returns:
            bool: True si envió y recibió ACK exitosamente
        """
        if not self.connected:
            print(f"{Colors.FAIL}❌ No conectado al servidor{Colors.ENDC}")
            return False
        
        try:
            # Incrementar secuencia
            self.sequence = (self.sequence + 1) % 65536
            
            # Crear mensaje
            msg = GPSMessage(
                device_id=self.device_id,
                latitude=self.latitude,
                longitude=self.longitude,
                altitude=self.altitude,
                battery=int(self.battery),
                signal=self.signal,
                state=STATE_GPS_FIX | STATE_MOVING,
                sequence=self.sequence
            )
            
            # Empaquetar y enviar
            packed = msg.pack()
            
            timestamp_str = datetime.now().strftime('%H:%M:%S')
            print(f"\n{Colors.BOLD}{Colors.OKBLUE}{'─' * 70}{Colors.ENDC}")
            print(f"{Colors.BOLD}📡 ENVIANDO MENSAJE GPS #{self.sequence}{Colors.ENDC}")
            print(f"{Colors.OKCYAN}🆔 Dispositivo:{Colors.ENDC} {self.device_name} (ID: {self.device_id})")
            print(f"{Colors.OKCYAN}⏰ Hora:{Colors.ENDC} {timestamp_str}")
            print(f"{Colors.OKCYAN}🌍 Posición:{Colors.ENDC}")
            print(f"   • Latitud:  {self.latitude:+.6f}°")
            print(f"   • Longitud: {self.longitude:+.6f}°")
            print(f"   • Altitud:  {self.altitude} m")
            print(f"{Colors.OKCYAN}📊 Estado:{Colors.ENDC}")
            print(f"   • Batería: {int(self.battery)}%")
            print(f"   • Señal:   {self.signal}%")
            print(f"{Colors.OKCYAN}📦 Tamaño:{Colors.ENDC} {len(packed)} bytes")
            
            self.socket.sendall(packed)
            print(f"{Colors.OKGREEN}✓ Mensaje enviado{Colors.ENDC}")
            
            # Esperar respuesta (ACK o NACK)
            response = self.socket.recv(TOTAL_MESSAGE_SIZE)
            response_msg = GPSMessage.unpack(response)
            
            if response_msg:
                if response_msg.msg_type == MSG_TYPE_ACK:
                    print(f"{Colors.OKGREEN}✓ ACK recibido (secuencia: {response_msg.sequence}){Colors.ENDC}")
                    print(f"{Colors.BOLD}{Colors.OKBLUE}{'─' * 70}{Colors.ENDC}\n")
                    return True
                elif response_msg.msg_type == MSG_TYPE_NACK:
                    print(f"{Colors.WARNING}⚠️  NACK recibido (secuencia: {response_msg.sequence}){Colors.ENDC}")
                    print(f"{Colors.BOLD}{Colors.OKBLUE}{'─' * 70}{Colors.ENDC}\n")
                    return False
            
            print(f"{Colors.WARNING}⚠️  Respuesta desconocida{Colors.ENDC}")
            print(f"{Colors.BOLD}{Colors.OKBLUE}{'─' * 70}{Colors.ENDC}\n")
            return False
        
        except socket.timeout:
            print(f"{Colors.FAIL}❌ Timeout esperando respuesta del servidor{Colors.ENDC}")
            print(f"{Colors.BOLD}{Colors.OKBLUE}{'─' * 70}{Colors.ENDC}\n")
            return False
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error enviando datos: {e}{Colors.ENDC}")
            print(f"{Colors.BOLD}{Colors.OKBLUE}{'─' * 70}{Colors.ENDC}\n")
            self.connected = False
            return False
    
    def run(self):
        """
        Ejecuta el ciclo principal del cliente
        """
        print(f"{Colors.HEADER}{'=' * 70}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.OKGREEN}📱 CLIENTE GPS SIMULADOR{Colors.ENDC}")
        print(f"{Colors.HEADER}{'=' * 70}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}🆔 Dispositivo:{Colors.ENDC} {self.device_name}")
        print(f"{Colors.OKCYAN}🔢 Device ID:{Colors.ENDC} {self.device_id}")
        print(f"{Colors.OKCYAN}📍 Posición inicial:{Colors.ENDC} ({self.latitude:.6f}, {self.longitude:.6f})")
        print(f"{Colors.OKCYAN}⏱️  Intervalo:{Colors.ENDC} {SEND_INTERVAL} segundos")
        print(f"{Colors.HEADER}{'=' * 70}{Colors.ENDC}\n")
        
        # Conectar al servidor
        if not self.connect():
            print(f"{Colors.FAIL}❌ No se pudo conectar al servidor. Abortando.{Colors.ENDC}")
            return
        
        try:
            message_count = 0
            failed_count = 0
            
            while True:
                # Actualizar posición (simular movimiento)
                self.update_position()
                
                # Intentar enviar con reintentos
                success = False
                for attempt in range(MAX_RETRIES):
                    if self.send_gps_data():
                        success = True
                        message_count += 1
                        break
                    else:
                        failed_count += 1
                        if attempt < MAX_RETRIES - 1:
                            print(f"{Colors.WARNING}⚠️  Reintento {attempt + 1}/{MAX_RETRIES} en {RETRY_DELAY} segundos...{Colors.ENDC}")
                            time.sleep(RETRY_DELAY)
                        else:
                            print(f"{Colors.FAIL}❌ Fallo después de {MAX_RETRIES} intentos{Colors.ENDC}")
                
                # Si no está conectado, intentar reconectar
                if not self.connected:
                    print(f"{Colors.WARNING}⚠️  Intentando reconectar...{Colors.ENDC}")
                    time.sleep(5)
                    if not self.connect():
                        print(f"{Colors.FAIL}❌ Reconexión fallida. Esperando 10 segundos...{Colors.ENDC}")
                        time.sleep(10)
                        continue
                
                # Mostrar estadísticas periódicamente
                if message_count > 0 and message_count % 5 == 0:
                    success_rate = (message_count / (message_count + failed_count)) * 100
                    print(f"\n{Colors.OKCYAN}📊 ESTADÍSTICAS:{Colors.ENDC}")
                    print(f"   Mensajes enviados: {message_count}")
                    print(f"   Fallos: {failed_count}")
                    print(f"   Tasa de éxito: {success_rate:.1f}%")
                    print(f"   Batería restante: {int(self.battery)}%\n")
                
                # Verificar batería
                if self.battery < 10:
                    print(f"{Colors.WARNING}⚠️  ¡BATERÍA BAJA! ({int(self.battery)}%){Colors.ENDC}")
                
                if self.battery <= 0:
                    print(f"{Colors.FAIL}🔋 BATERÍA AGOTADA. Simulación terminada.{Colors.ENDC}")
                    break
                
                # Esperar antes del siguiente envío
                time.sleep(SEND_INTERVAL)
        
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}⚠️  Interrupción por teclado (Ctrl+C){Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error en el cliente: {e}{Colors.ENDC}")
        finally:
            self.disconnect()
            
            # Resumen final
            print(f"\n{Colors.HEADER}{'=' * 70}{Colors.ENDC}")
            print(f"{Colors.BOLD}📊 RESUMEN FINAL{Colors.ENDC}")
            print(f"{Colors.HEADER}{'=' * 70}{Colors.ENDC}")
            print(f"{Colors.OKCYAN}✓ Mensajes enviados exitosamente:{Colors.ENDC} {message_count}")
            print(f"{Colors.OKCYAN}✗ Mensajes fallidos:{Colors.ENDC} {failed_count}")
            if message_count + failed_count > 0:
                success_rate = (message_count / (message_count + failed_count)) * 100
                print(f"{Colors.OKCYAN}📈 Tasa de éxito:{Colors.ENDC} {success_rate:.1f}%")
            print(f"{Colors.OKCYAN}🔋 Batería final:{Colors.ENDC} {int(self.battery)}%")
            print(f"{Colors.HEADER}{'=' * 70}{Colors.ENDC}\n")


# ==================== MAIN ====================

if __name__ == "__main__":
    # Coordenadas iniciales: Centro de Cochabamba, Bolivia
    COCHABAMBA_LAT = -17.3894
    COCHABAMBA_LON = -66.0588
    COCHABAMBA_ALT = 2558
    
    print(f"{Colors.BOLD}Seleccione un dispositivo GPS para simular:{Colors.ENDC}")
    print(f"1. GPS-001 (Taxi)")
    print(f"2. GPS-002 (Camión de reparto)")
    print(f"3. GPS-003 (Ambulancia)")
    print(f"4. Personalizado")
    
    try:
        choice = input(f"\n{Colors.OKCYAN}Opción [1-4]:{Colors.ENDC} ").strip()
        
        if choice == "1":
            device_name = "GPS-001-TAXI"
        elif choice == "2":
            device_name = "GPS-002-CAMION"
        elif choice == "3":
            device_name = "GPS-003-AMBULANCIA"
        elif choice == "4":
            device_name = input(f"{Colors.OKCYAN}Nombre del dispositivo:{Colors.ENDC} ").strip()
            if not device_name:
                device_name = "GPS-CUSTOM"
        else:
            device_name = "GPS-001-TAXI"
        
        # Crear y ejecutar cliente
        client = GPSClient(
            device_name=device_name,
            start_lat=COCHABAMBA_LAT,
            start_lon=COCHABAMBA_LON,
            altitude=COCHABAMBA_ALT
        )
        
        client.run()
    
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}⚠️  Programa interrumpido{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}❌ Error: {e}{Colors.ENDC}")
