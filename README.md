# 🛰️ GPS-RT Protocol v1.0
## Protocolo de Mensajería para Dispositivos GPS en Tiempo Real

**Práctica 3 - Redes de Computadoras**  
**Grupo 46**  
**Universidad Mayor de San Simón - UMSS**  
**Cochabamba, Bolivia**  
**Enero 2026**

---

## 📋 Descripción del Proyecto

Sistema de comunicación en tiempo real para dispositivos GPS que envían su posición a un servidor central. Diseñado para operar en condiciones de **batería limitada** y **ancho de banda restringido** sobre redes celulares 2G/3G/4G.

---

## 🎯 Características del Protocolo

### ✅ Ventajas Principales

- **Eficiencia**: Mensajes de solo 44 bytes
- **Confiabilidad**: TCP con CRC32 para integridad
- **Escalabilidad**: Soporta múltiples dispositivos simultáneos
- **Seguridad**: Autenticación por Device ID único
- **Recuperación**: Sistema automático de reintentos

### 📦 Componentes del Sistema

1. **protocolo.py** - Librería del protocolo (empaquetado/desempaquetado)
2. **servidor.py** - Servidor central receptor
3. **cliente_gps.py** - Simulador de dispositivo GPS

---

## 🔧 Requisitos del Sistema

### Software Necesario

- **Python 3.7 o superior**
- Módulos estándar de Python (incluidos):
  - `socket`
  - `struct`
  - `zlib`
  - `hashlib`
  - `threading`
  - `time`
  - `datetime`

### Sistema Operativo

- ✅ Windows 10/11
- ✅ Linux (Ubuntu, Debian, etc.)
- ✅ macOS

---

## 📥 Instalación

### 1. Verificar Python

```bash
python --version
# o
python3 --version
```

Debe mostrar Python 3.7 o superior.

### 2. Descargar los Archivos

Coloca los siguientes archivos en una carpeta:
- `protocolo.py`
- `servidor.py`
- `cliente_gps.py`
- `README.md`

---

## 🚀 Instrucciones de Uso

### Paso 1: Probar el Módulo del Protocolo

```bash
python protocolo.py
```

Esto ejecutará pruebas automáticas del protocolo y mostrará:
- ✓ Creación y empaquetado de mensajes
- ✓ Desempaquetado de mensajes
- ✓ Validación de datos
- ✓ Creación de mensajes ACK
- ✓ Verificación de integridad (CRC32)

**Resultado esperado:** Todas las pruebas deben pasar exitosamente.

---

### Paso 2: Iniciar el Servidor

Abre una terminal/consola y ejecuta:

```bash
python servidor.py
```

**Salida esperada:**
```
======================================================================
🛰️  SERVIDOR GPS-RT v1.0 INICIADO
======================================================================
📡 Escuchando en 0.0.0.0:9999
⏰ Timeout: 10 segundos
👥 Máximo de clientes: 10
======================================================================
```

**⚠️ IMPORTANTE:** Deja esta terminal abierta. El servidor debe estar ejecutándose.

---

### Paso 3: Iniciar el Cliente GPS

Abre **OTRA** terminal/consola (deja el servidor corriendo) y ejecuta:

```bash
python cliente_gps.py
```

**Menú interactivo:**
```
Seleccione un dispositivo GPS para simular:
1. GPS-001 (Taxi)
2. GPS-002 (Camión de reparto)
3. GPS-003 (Ambulancia)
4. Personalizado

Opción [1-4]:
```

Selecciona una opción (por ejemplo, `1`) y presiona Enter.

---

### Paso 4: Observar la Comunicación

#### En la Terminal del SERVIDOR verás:

```
✓ Nueva conexión desde 127.0.0.1:xxxxx

──────────────────────────────────────────────────────────────────────
📍 MENSAJE GPS RECIBIDO #1
🆔 Device ID: 12345678901234567
📊 Secuencia: 1
⏰ Timestamp: 14:30:45
🌍 Coordenadas:
   • Latitud:  -17.389400°
   • Longitud: -66.058800°
   • Altitud:  2558 metros
📡 Estado del Dispositivo:
   • 🔋 Batería: 100%
   • 📶 Señal:   85%
🔗 Origen: 127.0.0.1:xxxxx
──────────────────────────────────────────────────────────────────────
```

#### En la Terminal del CLIENTE verás:

```
──────────────────────────────────────────────────────────────────────
📡 ENVIANDO MENSAJE GPS #1
🆔 Dispositivo: GPS-001-TAXI (ID: 12345678901234567)
⏰ Hora: 14:30:45
🌍 Posición:
   • Latitud:  -17.389400°
   • Longitud: -66.058800°
   • Altitud:  2558 m
📊 Estado:
   • Batería: 100%
   • Señal:   85%
📦 Tamaño: 44 bytes
✓ Mensaje enviado
✓ ACK recibido (secuencia: 1)
──────────────────────────────────────────────────────────────────────
```

El cliente enviará un nuevo mensaje cada **5 segundos**.

---

### Paso 5: Detener el Sistema

#### Para detener el CLIENTE:
Presiona `Ctrl + C` en la terminal del cliente.

Verás un resumen final:
```
======================================================================
📊 RESUMEN FINAL
======================================================================
✓ Mensajes enviados exitosamente: 15
✗ Mensajes fallidos: 0
📈 Tasa de éxito: 100.0%
🔋 Batería final: 97%
======================================================================
```

#### Para detener el SERVIDOR:
Presiona `Ctrl + C` en la terminal del servidor.

---

## 🧪 Escenarios de Prueba

### Prueba 1: Cliente Único
1. Inicia el servidor
2. Inicia un cliente
3. Observa el intercambio de mensajes por 1 minuto
4. Detén el cliente
5. Verifica las estadísticas

**Resultado esperado:** 100% de mensajes exitosos

---

### Prueba 2: Múltiples Clientes
1. Inicia el servidor
2. Abre 3 terminales adicionales
3. En cada una, inicia un cliente diferente:
   - Terminal 1: `python cliente_gps.py` → Opción 1 (Taxi)
   - Terminal 2: `python cliente_gps.py` → Opción 2 (Camión)
   - Terminal 3: `python cliente_gps.py` → Opción 3 (Ambulancia)
4. Observa cómo el servidor maneja múltiples conexiones

**Resultado esperado:** El servidor recibe y procesa mensajes de los 3 clientes simultáneamente

---

### Prueba 3: Desconexión y Reconexión
1. Inicia servidor y cliente
2. Espera 30 segundos
3. Detén el servidor (Ctrl + C)
4. El cliente intentará reconectar automáticamente
5. Reinicia el servidor
6. Observa la reconexión del cliente

**Resultado esperado:** El cliente se reconecta automáticamente

---

### Prueba 4: Simulación de Batería Baja
1. Modifica `cliente_gps.py` línea 120:
   ```python
   self.battery = 15  # Cambiar de 100 a 15
   ```
2. Ejecuta el cliente
3. Observa las advertencias de batería baja

**Resultado esperado:** Advertencias cuando batería < 10%

---

## 📊 Configuración Avanzada

### Cambiar el Intervalo de Envío

En `cliente_gps.py`, línea 26:
```python
SEND_INTERVAL = 5  # Cambiar a 2, 10, etc.
```

### Cambiar el Puerto del Servidor

En `servidor.py` línea 24:
```python
SERVER_PORT = 9999  # Cambiar a otro puerto
```

**IMPORTANTE:** También cambia en `cliente_gps.py` línea 25:
```python
SERVER_PORT = 9999  # Debe coincidir con el servidor
```

### Conectar a Servidor Remoto

Si el servidor está en otra computadora:

1. En la máquina del servidor, encuentra su IP:
   ```bash
   # Windows
   ipconfig
   
   # Linux/Mac
   ifconfig
   # o
   ip addr show
   ```

2. En `cliente_gps.py` línea 24, cambia:
   ```python
   SERVER_HOST = '192.168.1.100'  # IP del servidor
   ```

3. Asegúrate de que el firewall permita conexiones en el puerto 9999

---

## 🐛 Solución de Problemas

### Error: "Address already in use"

**Causa:** El puerto 9999 ya está en uso.

**Solución:**
1. Espera 30 segundos y reintenta
2. O cambia el puerto en la configuración

---

### Error: "Connection refused"

**Causa:** El servidor no está ejecutándose.

**Solución:**
1. Verifica que el servidor esté corriendo
2. Verifica que el puerto sea el correcto
3. Verifica la dirección IP si es remoto

---

### Error: "Module not found"

**Causa:** Python no encuentra `protocolo.py`

**Solución:**
1. Asegúrate de que todos los archivos estén en la misma carpeta
2. Ejecuta los scripts desde esa carpeta

---

### El cliente no se conecta

**Soluciones:**
1. Verifica que el servidor esté ejecutándose
2. Verifica firewall (Windows Defender, iptables, etc.)
3. Si es remoto, verifica conectividad de red:
   ```bash
   ping IP_DEL_SERVIDOR
   ```

---

## 📈 Interpretación de Resultados

### Indicadores de Batería
- 🔋 Verde (>80%): Batería alta
- 🔋 Amarillo (50-80%): Batería media
- 🪫 Naranja (20-50%): Batería baja
- 🪫 Rojo (<20%): Batería crítica

### Indicadores de Señal
- 📶 (>70%): Señal excelente
- 📶 (40-70%): Señal buena
- 📵 (<40%): Señal débil

### Mensajes del Sistema
- ✓ Verde: Operación exitosa
- ⚠️ Amarillo: Advertencia
- ❌ Rojo: Error

---

## 📚 Estructura del Protocolo

### Formato del Mensaje (44 bytes)

```
HEADER (16 bytes):
  - Version (1 byte): Versión del protocolo
  - Tipo (1 byte): GPS_DATA=0x01, ACK=0x02, NACK=0x03
  - Device ID (8 bytes): Identificador único
  - Sequence (2 bytes): Número de secuencia
  - Reserved (4 bytes): Para expansión futura

PAYLOAD (24 bytes):
  - Timestamp (8 bytes): Unix epoch en milisegundos
  - Latitud (4 bytes): Coordenada GPS
  - Longitud (4 bytes): Coordenada GPS
  - Altitud (2 bytes): Metros sobre nivel del mar
  - Batería (1 byte): Porcentaje 0-100
  - Señal (1 byte): Nivel 0-100
  - Estado (1 byte): Flags de estado
  - Reserved (3 bytes): Para expansión futura

FOOTER (4 bytes):
  - CRC32 (4 bytes): Checksum de integridad
```

---

## 🔒 Seguridad

### Autenticación
- Cada dispositivo tiene un Device ID único generado por SHA-256
- El servidor puede validar dispositivos autorizados

### Integridad
- CRC32 detecta errores de transmisión con 99.9999% efectividad
- Mensajes corruptos son rechazados automáticamente

### Extensibilidad
- Preparado para agregar TLS/SSL
- Campos reservados para cifrado futuro

---

## 📞 Soporte

**Grupo 46 - Redes de Computadoras**  
Universidad Mayor de San Simón  
Cochabamba, Bolivia

---

## 📄 Licencia

Proyecto académico - Práctica 3  
Uso educativo exclusivamente

---

## ✅ Checklist de Entrega

- [x] Diseño del protocolo documentado
- [x] Formato de mensaje definido (44 bytes)
- [x] Método de transmisión: TCP
- [x] Manejo de errores: CRC32 + reintentos
- [x] Seguridad: Device ID único
- [x] Servidor funcional (multi-cliente)
- [x] Cliente simulador funcional
- [x] Documentación completa
- [x] Pruebas realizadas exitosamente

---

**¡Protocolo GPS-RT v1.0 listo para producción! 🚀**
