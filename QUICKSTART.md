# Guía de Inicio Rápido - AutoDocVision

## 🚀 Inicio Rápido en 5 Minutos

### Paso 1: Clonar y Preparar

```bash
# Clonar repositorio
git clone https://github.com/RicardoGarfias/AutoDocVision-Detector-de-Documentos-Vehiculares-con-IA.git
cd AutoDocVision-Detector-de-Documentos-Vehiculares-con-IA

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### Paso 2: Iniciar la Aplicación

```bash
# Opción A: Interfaz Web (Recomendado)
python app.py
# Luego abre: http://localhost:5000

# Opción B: Detección desde Cámara
python camera_detection.py

# Opción C: Procesar una imagen
python detect_image.py --image ruta/imagen.jpg
```

---

## 📋 Ejemplos de Uso

### Ejemplo 1: Usar la Interfaz Web

1. Ejecuta `python app.py`
2. Abre navegador en `http://localhost:5000`
3. Carga una imagen o activa la cámara
4. Ver resultado en tiempo real

### Ejemplo 2: Detectar desde Línea de Comandos

```bash
# Simple
python detect_image.py --image documento.jpg

# Con confianza personalizada
python detect_image.py --image documento.jpg --confidence 0.8

# Guardar resultado
python detect_image.py --image documento.jpg --output resultado.jpg

# Formato JSON
python detect_image.py --image documento.jpg --json
```

### Ejemplo 3: Detección en Tiempo Real

```bash
python camera_detection.py

# Controles mientras se ejecuta:
# q = salir
# s = guardar captura
# c = limpiar pantalla
# t = mostrar estadísticas
```

---

## 🔧 Troubleshooting

### Error: "Modelo no encontrado"
```bash
# Verifica que exista la carpeta RECONOCIMIENTO DE DOCUMENTOS
ls -la "RECONOCIMIENTO DE DOCUMENTOS/"
```

### Error: "No se puede acceder a la cámara"
```bash
# Linux: Agrega permisos
sudo usermod -a -G video $USER

# Windows/Mac: Verifica permisos de cámara en configuración
```

### Error: "Puerto 5000 en uso"
```python
# Edita app.py, última línea:
app.run(port=5001)  # Usa otro puerto
```

---

## 📚 Documentación Completa

Ver archivos:
- **README.md** - Documentación general
- **REPORTE.md** - Análisis técnico detallado
- **docs/DOCUMENTACION_CODIGO.md** - Referencia de módulos

---

## 🎬 Características Principales

✅ **Detección en Tiempo Real** - Cámara web en vivo
✅ **Interfaz Web** - Acceso desde navegador
✅ **CLI** - Línea de comandos
✅ **Múltiples Formatos** - JPG, PNG, BMP, GIF
✅ **Historial** - Registro de detecciones
✅ **API REST** - Para integración

---

## 📞 Soporte

¿Problemas? Abre un issue en GitHub:
https://github.com/RicardoGarfias/AutoDocVision-Detector-de-Documentos-Vehiculares-con-IA/issues
