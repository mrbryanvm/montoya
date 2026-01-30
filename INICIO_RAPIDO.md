# 🚀 INICIO RÁPIDO - GPS-RT Protocol v1.0

## ⚡ En 3 Pasos

### Paso 1: Probar el Protocolo
```bash
python protocolo.py
```
**Resultado esperado:** Todas las pruebas pasan ✓

---

### Paso 2: Iniciar el Servidor
**Abrir una terminal/consola:**
```bash
python servidor.py
```
**Resultado esperado:**
```
======================================================================
🛰️  SERVIDOR GPS-RT v1.0 INICIADO
======================================================================
📡 Escuchando en 0.0.0.0:9999
```
**⚠️ DEJAR ESTA TERMINAL ABIERTA**

---

### Paso 3: Iniciar el Cliente
**Abrir OTRA terminal/consola:**
```bash
python cliente_gps.py
```
**Opciones:**
1. GPS-001 (Taxi)
2. GPS-002 (Camión)
3. GPS-003 (Ambulancia)
4. Personalizado

**Selecciona una opción (1-4) y presiona Enter**

---

## 📊 Qué Verás

### En el SERVIDOR:
```
──────────────────────────────────────────────────────────────────────
📍 MENSAJE GPS RECIBIDO #1
🆔 Device ID: 15664371594725980587
📊 Secuencia: 1
⏰ Timestamp: 14:30:45
🌍 Coordenadas:
   • Latitud:  -17.389400°
   • Longitud: -66.058800°
   • Altitud:  2558 metros
📡 Estado del Dispositivo:
   • 🔋 Batería: 100%
   • 📶 Señal:   85%
──────────────────────────────────────────────────────────────────────
```

### En el CLIENTE:
```
──────────────────────────────────────────────────────────────────────
📡 ENVIANDO MENSAJE GPS #1
✓ Mensaje enviado
✓ ACK recibido
──────────────────────────────────────────────────────────────────────
```

---

## 🛑 Para Detener

**Cliente:** `Ctrl + C`
**Servidor:** `Ctrl + C`

---

## 🧪 Prueba Rápida de Múltiples Clientes

1. Inicia el servidor (1 terminal)
2. Abre 3 terminales más
3. En cada una ejecuta: `python cliente_gps.py` con opciones 1, 2 y 3
4. Observa cómo el servidor maneja las 3 conexiones simultáneas

---

## 📝 Archivos del Proyecto

- **protocolo.py** - Librería del protocolo
- **servidor.py** - Servidor central
- **cliente_gps.py** - Simulador GPS
- **README.md** - Manual completo
- **Especificacion_Protocolo_GPS-RT.docx** - Documento formal

---

## ⚠️ Solución Rápida de Problemas

### "Connection refused"
→ El servidor no está corriendo. Inicia el servidor primero.

### "Address already in use"
→ Espera 30 segundos o reinicia la computadora.

### "Module not found"
→ Asegúrate de ejecutar desde la misma carpeta donde están los archivos.

---

## 📈 Interpretación de Resultados

### Símbolos:
- ✓ Verde = Exitoso
- ⚠️ Amarillo = Advertencia
- ❌ Rojo = Error

### Batería:
- 🔋 >80% = Buena
- 🪫 <20% = Baja

### Señal:
- 📶 >70% = Excelente
- 📵 <40% = Débil

---

## ✅ Checklist de Entrega

- [x] Documento de especificación (DOCX)
- [x] Código fuente (3 archivos Python)
- [x] Manual de usuario (README.md)
- [x] Pruebas exitosas
- [x] Sistema funcional

---

**¡Sistema listo para demostración! 🎉**

**Grupo 46 - UMSS - Enero 2026**
