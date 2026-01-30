"""
Servidor Central GPS-RT
Recibe y procesa mensajes GPS de dispositivos en tiempo real
"""

import socket
import threading
import time
from datetime import datetime
from protocolo import (
    GPSMessage, 
    create_ack_message, 
    create_nack_message,
    MSG_TYPE_GPS_DATA,
    TOTAL_MESSAGE_SIZE
)

# ==================== CONFIGURACIÓN DEL SERVIDOR ====================

SERVER_HOST = '0.0.0.0'  # Escuchar en todas las interfaces
SERVER_PORT = 9999
MAX_CLIENTS = 10
TIMEOUT = 10  # segundos

# Colores para la consola (ANSI escape codes)
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# ==================== CLASE SERVIDOR GPS ====================

class GPSServer:
    """
    Servidor que maneja múltiples conexiones de dispositivos GPS
    """
    
    def __init__(self, host=SERVER_HOST, port=SERVER_PORT):
        """
        Inicializa el servidor
        
        Args:
            host (str): IP del servidor
            port (int): Puerto de escucha
        """
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.clients = {}  # {device_id: {socket, address, last_sequence, last_seen}}
        self.message_count = 0
        self.lock = threading.Lock()
    
    def start(self):
        """
        Inicia el servidor
        """
        try:
            # Crear socket TCP
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(MAX_CLIENTS)
            self.server_socket.settimeout(1.0)  # Timeout para revisar Ctrl+C cada segundo
            
            self.running = True
            
            print(f"{Colors.HEADER}{'=' * 70}{Colors.ENDC}")
            print(f"{Colors.BOLD}{Colors.OKGREEN}🛰️  SERVIDOR GPS-RT v1.0 INICIADO{Colors.ENDC}")
            print(f"{Colors.HEADER}{'=' * 70}{Colors.ENDC}")
            print(f"{Colors.OKCYAN}📡 Escuchando en {self.host}:{self.port}{Colors.ENDC}")
            print(f"{Colors.OKCYAN}⏰ Timeout: {TIMEOUT} segundos{Colors.ENDC}")
            print(f"{Colors.OKCYAN}👥 Máximo de clientes: {MAX_CLIENTS}{Colors.ENDC}")
            print(f"{Colors.HEADER}{'=' * 70}{Colors.ENDC}\n")
            
            # Hilo para monitorear clientes inactivos
            monitor_thread = threading.Thread(target=self.monitor_clients, daemon=True)
            monitor_thread.start()
            
            # Aceptar conexiones
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    
                    # Crear hilo para manejar el cliente
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    client_thread.start()
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"{Colors.FAIL}❌ Error aceptando conexión: {e}{Colors.ENDC}")
        
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error iniciando servidor: {e}{Colors.ENDC}")
        finally:
            self.stop()
    
    def handle_client(self, client_socket, client_address):
        """
        Maneja la comunicación con un cliente específico
        
        Args:
            client_socket: Socket del cliente
            client_address: Dirección del cliente
        """
        client_socket.settimeout(TIMEOUT)
        device_id = None
        
        try:
            print(f"{Colors.OKGREEN}✓ Nueva conexión desde {client_address[0]}:{client_address[1]}{Colors.ENDC}")
            
            while self.running:
                # Recibir mensaje completo (44 bytes)
                data = b''
                while len(data) < TOTAL_MESSAGE_SIZE:
                    try:
                        chunk = client_socket.recv(TOTAL_MESSAGE_SIZE - len(data))
                        if not chunk:
                            raise ConnectionError("Conexión cerrada por el cliente")
                        data += chunk
                    except socket.timeout:
                        print(f"{Colors.WARNING}⚠️  Timeout esperando datos de {client_address}{Colors.ENDC}")
                        return
                
                # Desempaquetar mensaje
                msg = GPSMessage.unpack(data)
                
                if msg is None:
                    # Enviar NACK
                    if device_id:
                        nack = create_nack_message(device_id, 0)
                        client_socket.sendall(nack)
                    print(f"{Colors.FAIL}❌ Mensaje inválido recibido de {client_address}{Colors.ENDC}")
                    continue
                
                # Validar mensaje
                is_valid, error_msg = msg.validate()
                if not is_valid:
                    print(f"{Colors.FAIL}❌ Validación fallida: {error_msg}{Colors.ENDC}")
                    nack = create_nack_message(msg.device_id, msg.sequence)
                    client_socket.sendall(nack)
                    continue
                
                # Actualizar información del cliente
                device_id = msg.device_id
                with self.lock:
                    if device_id not in self.clients:
                        self.clients[device_id] = {
                            'socket': client_socket,
                            'address': client_address,
                            'last_sequence': 0,
                            'last_seen': time.time(),
                            'message_count': 0
                        }
                    
                    self.clients[device_id]['last_sequence'] = msg.sequence
                    self.clients[device_id]['last_seen'] = time.time()
                    self.clients[device_id]['message_count'] += 1
                    self.message_count += 1
                
                # Procesar mensaje según tipo
                if msg.msg_type == MSG_TYPE_GPS_DATA:
                    self.process_gps_data(msg, client_address)
                    
                    # Enviar ACK
                    ack = create_ack_message(msg.device_id, msg.sequence)
                    client_socket.sendall(ack)
                else:
                    print(f"{Colors.OKCYAN}📨 Mensaje tipo {msg.msg_type} recibido{Colors.ENDC}")
        
        except ConnectionError as e:
            print(f"{Colors.WARNING}⚠️  Conexión cerrada: {client_address} - {e}{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error manejando cliente {client_address}: {e}{Colors.ENDC}")
        finally:
            # Limpiar cliente
            if device_id:
                with self.lock:
                    if device_id in self.clients:
                        del self.clients[device_id]
            
            try:
                client_socket.close()
            except:
                pass
            
            print(f"{Colors.WARNING}🔌 Desconectado: {client_address}{Colors.ENDC}")
    
    def process_gps_data(self, msg, address):
        """
        Procesa y muestra los datos GPS recibidos
        
        Args:
            msg (GPSMessage): Mensaje GPS
            address: Dirección del cliente
        """
        timestamp_str = datetime.fromtimestamp(msg.timestamp / 1000).strftime('%H:%M:%S')
        
        # Determinar símbolo de batería
        if msg.battery > 80:
            battery_symbol = "🔋"
        elif msg.battery > 50:
            battery_symbol = "🔋"
        elif msg.battery > 20:
            battery_symbol = "🪫"
        else:
            battery_symbol = "🪫"
        
        # Determinar símbolo de señal
        if msg.signal > 70:
            signal_symbol = "📶"
        elif msg.signal > 40:
            signal_symbol = "📶"
        else:
            signal_symbol = "📵"
        
        print(f"\n{Colors.BOLD}{Colors.OKGREEN}{'─' * 70}{Colors.ENDC}")
        print(f"{Colors.BOLD}📍 MENSAJE GPS RECIBIDO #{self.message_count}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}🆔 Device ID:{Colors.ENDC} {msg.device_id}")
        print(f"{Colors.OKBLUE}📊 Secuencia:{Colors.ENDC} {msg.sequence}")
        print(f"{Colors.OKBLUE}⏰ Timestamp:{Colors.ENDC} {timestamp_str}")
        print(f"{Colors.OKBLUE}🌍 Coordenadas:{Colors.ENDC}")
        print(f"   • Latitud:  {msg.latitude:+.6f}°")
        print(f"   • Longitud: {msg.longitude:+.6f}°")
        print(f"   • Altitud:  {msg.altitude} metros")
        print(f"{Colors.OKBLUE}📡 Estado del Dispositivo:{Colors.ENDC}")
        print(f"   • {battery_symbol} Batería: {msg.battery}%")
        print(f"   • {signal_symbol} Señal:   {msg.signal}%")
        print(f"{Colors.OKBLUE}🔗 Origen:{Colors.ENDC} {address[0]}:{address[1]}")
        print(f"{Colors.BOLD}{Colors.OKGREEN}{'─' * 70}{Colors.ENDC}\n")
    
    def monitor_clients(self):
        """
        Monitorea clientes inactivos y muestra estadísticas
        """
        while self.running:
            time.sleep(30)  # Revisar cada 30 segundos
            
            current_time = time.time()
            disconnected = []
            
            with self.lock:
                for device_id, info in self.clients.items():
                    if current_time - info['last_seen'] > TIMEOUT * 2:
                        disconnected.append(device_id)
                
                for device_id in disconnected:
                    print(f"{Colors.WARNING}⏱️  Cliente {device_id} inactivo por mucho tiempo{Colors.ENDC}")
                    del self.clients[device_id]
            
            # Mostrar estadísticas
            if self.clients:
                print(f"\n{Colors.OKCYAN}📊 ESTADÍSTICAS:{Colors.ENDC}")
                print(f"   Clientes activos: {len(self.clients)}")
                print(f"   Total mensajes: {self.message_count}\n")
    
    def stop(self):
        """
        Detiene el servidor
        """
        print(f"\n{Colors.WARNING}🛑 Deteniendo servidor...{Colors.ENDC}")
        self.running = False
        
        # Cerrar todas las conexiones
        with self.lock:
            for device_id, info in self.clients.items():
                try:
                    info['socket'].close()
                except:
                    pass
        
        # Cerrar socket del servidor
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        print(f"{Colors.OKGREEN}✓ Servidor detenido{Colors.ENDC}")


# ==================== MAIN ====================

if __name__ == "__main__":
    server = GPSServer()
    
    try:
        server.start()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}⚠️  Interrupción por teclado (Ctrl+C){Colors.ENDC}")
        server.stop()
    except Exception as e:
        print(f"{Colors.FAIL}❌ Error crítico: {e}{Colors.ENDC}")
        server.stop()
