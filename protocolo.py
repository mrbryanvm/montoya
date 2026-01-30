"""
GPS-RT Protocol v1.0
Protocolo de mensajería para dispositivos GPS en tiempo real

Autor: Grupo 46
Materia: Redes de Computadoras - UMSS
Fecha: Enero 2026
"""

import struct
import time
import zlib
import hashlib

# ==================== CONSTANTES DEL PROTOCOLO ====================

PROTOCOL_VERSION = 0x01

# Tipos de mensaje
MSG_TYPE_GPS_DATA = 0x01
MSG_TYPE_ACK = 0x02
MSG_TYPE_NACK = 0x03

# Tamaños
HEADER_SIZE = 16
PAYLOAD_SIZE = 24
FOOTER_SIZE = 4
TOTAL_MESSAGE_SIZE = HEADER_SIZE + PAYLOAD_SIZE + FOOTER_SIZE  # 44 bytes

# Estados del dispositivo (flags)
STATE_MOVING = 0x01      # bit 0: En movimiento
STATE_GPS_FIX = 0x02     # bit 1: GPS tiene fix
STATE_ALERT = 0x04       # bit 2: Alerta activa

# ==================== CLASE MENSAJE GPS ====================

class GPSMessage:
    """
    Representa un mensaje del protocolo GPS-RT
    """
    
    def __init__(self, device_id, latitude, longitude, altitude=0, 
                 battery=100, signal=100, state=STATE_GPS_FIX, 
                 sequence=0, msg_type=MSG_TYPE_GPS_DATA):
        """
        Inicializa un mensaje GPS
        
        Args:
            device_id (int): ID único del dispositivo (0-2^64)
            latitude (float): Latitud (-90 a 90)
            longitude (float): Longitud (-180 a 180)
            altitude (int): Altitud en metros (-500 a 9000)
            battery (int): Porcentaje de batería (0-100)
            signal (int): Nivel de señal (0-100)
            state (int): Flags de estado
            sequence (int): Número de secuencia (0-65535)
            msg_type (int): Tipo de mensaje
        """
        self.version = PROTOCOL_VERSION
        self.msg_type = msg_type
        self.device_id = device_id
        self.sequence = sequence
        self.timestamp = int(time.time() * 1000)  # Unix timestamp en milisegundos
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.battery = battery
        self.signal = signal
        self.state = state
        self.crc32 = 0
    
    def pack(self):
        """
        Empaqueta el mensaje en formato binario
        
        Returns:
            bytes: Mensaje empaquetado (44 bytes)
        """
        # HEADER (16 bytes)
        # B = unsigned char (1 byte)
        # B = unsigned char (1 byte)
        # Q = unsigned long long (8 bytes)
        # H = unsigned short (2 bytes)
        # I = unsigned int (4 bytes) - reserved
        header = struct.pack('!BBQHI',
            self.version,      # 1 byte
            self.msg_type,     # 1 byte
            self.device_id,    # 8 bytes
            self.sequence,     # 2 bytes
            0                  # 4 bytes reserved
        )
        
        # PAYLOAD (24 bytes)
        # Q = unsigned long long (8 bytes) - timestamp
        # f = float (4 bytes) - latitude
        # f = float (4 bytes) - longitude
        # h = short (2 bytes) - altitude
        # B = unsigned char (1 byte) - battery
        # B = unsigned char (1 byte) - signal
        # B = unsigned char (1 byte) - state
        # 3s = 3 bytes string - reserved
        payload = struct.pack('!Qffh BBB3s',
            self.timestamp,    # 8 bytes
            self.latitude,     # 4 bytes
            self.longitude,    # 4 bytes
            self.altitude,     # 2 bytes
            self.battery,      # 1 byte
            self.signal,       # 1 byte
            self.state,        # 1 byte
            b'\x00\x00\x00'    # 3 bytes reserved
        )
        
        # Calcular CRC32 sobre header + payload
        data_for_crc = header + payload
        crc32 = zlib.crc32(data_for_crc) & 0xffffffff
        
        # FOOTER (4 bytes)
        footer = struct.pack('!I', crc32)
        
        # Mensaje completo
        message = header + payload + footer
        
        return message
    
    @staticmethod
    def unpack(data):
        """
        Desempaqueta un mensaje binario
        
        Args:
            data (bytes): Datos binarios (44 bytes)
            
        Returns:
            GPSMessage: Objeto mensaje o None si es inválido
        """
        if len(data) != TOTAL_MESSAGE_SIZE:
            print(f"❌ Error: Tamaño de mensaje inválido ({len(data)} bytes, esperado {TOTAL_MESSAGE_SIZE})")
            return None
        
        try:
            # Extraer header
            header_data = data[:HEADER_SIZE]
            version, msg_type, device_id, sequence, reserved = struct.unpack('!BBQHI', header_data)
            
            # Extraer payload
            payload_data = data[HEADER_SIZE:HEADER_SIZE + PAYLOAD_SIZE]
            timestamp, latitude, longitude, altitude, battery, signal, state, reserved_payload = \
                struct.unpack('!Qffh BBB3s', payload_data)
            
            # Extraer footer
            footer_data = data[HEADER_SIZE + PAYLOAD_SIZE:]
            received_crc32 = struct.unpack('!I', footer_data)[0]
            
            # Validar CRC32
            data_for_crc = header_data + payload_data
            calculated_crc32 = zlib.crc32(data_for_crc) & 0xffffffff
            
            if received_crc32 != calculated_crc32:
                print(f"❌ Error: CRC32 inválido (recibido: {received_crc32:08x}, calculado: {calculated_crc32:08x})")
                return None
            
            # Validar versión
            if version != PROTOCOL_VERSION:
                print(f"❌ Error: Versión de protocolo inválida ({version}, esperado {PROTOCOL_VERSION})")
                return None
            
            # Crear objeto mensaje
            msg = GPSMessage(
                device_id=device_id,
                latitude=latitude,
                longitude=longitude,
                altitude=altitude,
                battery=battery,
                signal=signal,
                state=state,
                sequence=sequence,
                msg_type=msg_type
            )
            msg.timestamp = timestamp
            msg.crc32 = received_crc32
            
            return msg
            
        except struct.error as e:
            print(f"❌ Error al desempaquetar mensaje: {e}")
            return None
    
    def validate(self):
        """
        Valida que los valores del mensaje estén en rangos correctos
        
        Returns:
            tuple: (bool, str) - (es_válido, mensaje_error)
        """
        if not (-90 <= self.latitude <= 90):
            return False, f"Latitud fuera de rango: {self.latitude}"
        
        if not (-180 <= self.longitude <= 180):
            return False, f"Longitud fuera de rango: {self.longitude}"
        
        if not (-500 <= self.altitude <= 9000):
            return False, f"Altitud fuera de rango: {self.altitude}"
        
        if not (0 <= self.battery <= 100):
            return False, f"Batería fuera de rango: {self.battery}"
        
        if not (0 <= self.signal <= 100):
            return False, f"Señal fuera de rango: {self.signal}"
        
        return True, "OK"
    
    def __str__(self):
        """
        Representación en string del mensaje
        """
        state_flags = []
        if self.state & STATE_MOVING:
            state_flags.append("MOVIMIENTO")
        if self.state & STATE_GPS_FIX:
            state_flags.append("GPS_FIX")
        if self.state & STATE_ALERT:
            state_flags.append("ALERTA")
        
        state_str = "|".join(state_flags) if state_flags else "NORMAL"
        
        msg_type_str = {
            MSG_TYPE_GPS_DATA: "GPS_DATA",
            MSG_TYPE_ACK: "ACK",
            MSG_TYPE_NACK: "NACK"
        }.get(self.msg_type, "UNKNOWN")
        
        timestamp_readable = time.strftime('%Y-%m-%d %H:%M:%S', 
                                          time.localtime(self.timestamp / 1000))
        
        return (f"[{msg_type_str}] Device:{self.device_id} Seq:{self.sequence} "
                f"Time:{timestamp_readable} | "
                f"Pos:({self.latitude:.6f}, {self.longitude:.6f}, {self.altitude}m) | "
                f"Bat:{self.battery}% Señal:{self.signal}% Estado:{state_str}")


# ==================== FUNCIONES AUXILIARES ====================

def create_ack_message(device_id, sequence):
    """
    Crea un mensaje ACK
    
    Args:
        device_id (int): ID del dispositivo
        sequence (int): Número de secuencia a confirmar
        
    Returns:
        bytes: Mensaje ACK empaquetado
    """
    msg = GPSMessage(
        device_id=device_id,
        latitude=0.0,
        longitude=0.0,
        sequence=sequence,
        msg_type=MSG_TYPE_ACK
    )
    return msg.pack()


def create_nack_message(device_id, sequence):
    """
    Crea un mensaje NACK
    
    Args:
        device_id (int): ID del dispositivo
        sequence (int): Número de secuencia rechazado
        
    Returns:
        bytes: Mensaje NACK empaquetado
    """
    msg = GPSMessage(
        device_id=device_id,
        latitude=0.0,
        longitude=0.0,
        sequence=sequence,
        msg_type=MSG_TYPE_NACK
    )
    return msg.pack()


def generate_device_id(identifier):
    """
    Genera un Device ID único basado en un identificador
    
    Args:
        identifier (str): Identificador (ej: "GPS-001")
        
    Returns:
        int: Device ID (8 bytes)
    """
    # Usar hash SHA-256 y tomar los primeros 8 bytes
    hash_obj = hashlib.sha256(identifier.encode())
    hash_bytes = hash_obj.digest()[:8]
    device_id = struct.unpack('!Q', hash_bytes)[0]
    return device_id


# ==================== PRUEBAS DEL MÓDULO ====================

if __name__ == "__main__":
    print("=" * 70)
    print("PRUEBA DEL PROTOCOLO GPS-RT v1.0")
    print("=" * 70)
    print()
    
    # Test 1: Crear y empaquetar mensaje
    print("📝 Test 1: Crear y empaquetar mensaje")
    device_id = generate_device_id("GPS-001")
    msg = GPSMessage(
        device_id=device_id,
        latitude=-17.3894,
        longitude=-66.0588,
        altitude=2558,
        battery=85,
        signal=75,
        state=STATE_GPS_FIX | STATE_MOVING,
        sequence=1
    )
    
    print(f"   Device ID: {device_id}")
    print(f"   Mensaje: {msg}")
    
    packed = msg.pack()
    print(f"   ✓ Tamaño empaquetado: {len(packed)} bytes")
    print(f"   ✓ Datos (hex): {packed[:20].hex()}...")
    print()
    
    # Test 2: Desempaquetar mensaje
    print("📦 Test 2: Desempaquetar mensaje")
    unpacked = GPSMessage.unpack(packed)
    if unpacked:
        print(f"   ✓ Mensaje desempaquetado exitosamente")
        print(f"   ✓ {unpacked}")
    else:
        print(f"   ❌ Error al desempaquetar")
    print()
    
    # Test 3: Validación
    print("✅ Test 3: Validación de mensaje")
    is_valid, error = unpacked.validate()
    if is_valid:
        print(f"   ✓ Mensaje válido")
    else:
        print(f"   ❌ Mensaje inválido: {error}")
    print()
    
    # Test 4: Mensaje ACK
    print("🔄 Test 4: Crear mensaje ACK")
    ack = create_ack_message(device_id, 1)
    ack_msg = GPSMessage.unpack(ack)
    print(f"   ✓ {ack_msg}")
    print()
    
    # Test 5: Integridad (CRC)
    print("🔒 Test 5: Verificación de integridad (CRC)")
    corrupted = bytearray(packed)
    corrupted[20] = corrupted[20] ^ 0xFF  # Corromper un byte
    corrupted_msg = GPSMessage.unpack(bytes(corrupted))
    if corrupted_msg is None:
        print(f"   ✓ CRC detectó correctamente mensaje corrupto")
    else:
        print(f"   ❌ CRC no detectó corrupción")
    print()
    
    print("=" * 70)
    print("✓ TODAS LAS PRUEBAS COMPLETADAS")
    print("=" * 70)
