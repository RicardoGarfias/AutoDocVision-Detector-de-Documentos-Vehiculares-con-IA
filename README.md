# 🚗 AutoDocVision - Detector de Documentos Vehiculares con IA

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![TensorFlow](https://img.shields.io/badge/TensorFlow.js-Latest-orange)
![License](https://img.shields.io/badge/License-MIT-green)

## 📌 Descripción General

**AutoDocVision** es una aplicación inteligente de visión artificial que detecta y clasifica automáticamente documentos vehiculares en tiempo real. Utiliza un modelo entrenado con **Google Teachable Machine** para identificar diferentes tipos de documentos con alta precisión.

**Documentos detectados:**
- 📄 Títulos americanos (Vehicle Title)
- 🇲🇽 Tarjetas de circulación de México
- 🆔 Licencias DMV (Driver's License)
- 📋 Otros documentos vehiculares

---

## ⚙️ Requisitos Previos

```
✓ Python 3.8 o superior
✓ pip (gestor de paquetes)
✓ Cámara web (para detección en tiempo real)
✓ Navegador web moderno (Chrome, Firefox, Edge)
✓ 100 MB de espacio libre (modelo incluido)
```

---

## 🚀 Instalación Paso a Paso

### **PASO 1: Clonar el repositorio**

```bash
git clone https://github.com/RicardoGarfias/AutoDocVision-Detector-de-Documentos-Vehiculares-con-IA.git
cd AutoDocVision-Detector-de-Documentos-Vehiculares-con-IA
```

### **PASO 2: Crear entorno virtual (Recomendado)**

**En Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**En Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### **PASO 3: Instalar dependencias**

```bash
pip install -r requirements.txt
```

**Esto instalará:**
- Flask (servidor web)
- TensorFlow.js (modelo)
- OpenCV (procesamiento de imágenes)
- NumPy (cálculos numéricos)

### **PASO 4: Verificar instalación**

```bash
python --version
pip list | grep -E "flask|opencv|tensorflow"
```

---

## 💻 Cómo Usar la Aplicación

### **OPCIÓN 1: Interfaz Web (Recomendado para principiantes)**

**1. Iniciar la aplicación:**
```bash
python app.py
```

**2. Abre en tu navegador:**
```
http://localhost:5000
```

**3. Usa la interfaz para:**
- Cargar imágenes
- Capturar con cámara web
- Ver resultados en tiempo real
- Ver confianza de predicción

---

### **OPCIÓN 2: Detección en Tiempo Real desde Cámara**

**1. Ejecutar:**
```bash
python camera_detection.py
```

**2. La ventana mostrará:**
- Video en vivo de tu cámara
- Clasificación en tiempo real
- Porcentaje de confianza
- Cuadros delimitadores

**3. Presiona `q` para salir**

---

### **OPCIÓN 3: Procesar una Imagen Individual**

**1. Ejecutar con ruta a imagen:**
```bash
python detect_image.py --image ruta/a/imagen.jpg
```

**Ejemplo:**
```bash
python detect_image.py --image documento.jpg
```

**2. Salida:**
- Clase detectada
- Porcentaje de confianza
- Imagen procesada guardada

---

## 📁 Estructura del Proyecto

```
📦 AutoDocVision/
│
├── 📄 README.md                          ← Este archivo
├── 📄 REPORTE.md                         ← Análisis técnico completo
├── 📄 requirements.txt                   ← Dependencias
├── 📄 QUICKSTART.md                      ← Inicio rápido
│
├── 🐍 Archivos Python Principales:
│   ├── app.py                            ← Servidor web (USAR ESTO)
│   ├── camera_detection.py               ← Cámara en tiempo real
│   ├── detect_image.py                   ← Procesar imágenes
│
├── 📂 utils/                             ← Módulos auxiliares
│   ├── model_loader.py                   ← Carga el modelo
│   ├── image_processor.py                ← Procesa imágenes
│   └── predictor.py                      ← Realiza predicciones
│
├── 📂 RECONOCIMIENTO DE DOCUMENTOS/      ← Modelo IA (NO EDITAR)
│   ├── model.json                        ← Arquitectura del modelo
│   ├── weights.bin                       ← Pesos entrenados
│   └── metadata.json                     ← Información del modelo
│
├── 📂 static/                            ← Archivos del navegador
│   └── css/style.css                     ← Estilos
│   └── js/app.js                         ← JavaScript
│
├── 📂 templates/                         ← Páginas HTML
│   ├── index.html                        ← Página principal
│   └── about.html                        ← Información
│
└── 📂 docs/                              ← Documentación
    └── DOCUMENTACION_CODIGO.md           ← Detalles técnicos
```

---

## 🎯 Ejemplos de Uso

### **Ejemplo 1: Usar la interfaz web**
```bash
python app.py
# Luego abre http://localhost:5000 en tu navegador
```

### **Ejemplo 2: Detectar desde cámara**
```bash
python camera_detection.py
# Presiona Q para salir
```

### **Ejemplo 3: Procesar archivo**
```bash
python detect_image.py --image documento_vehicular.jpg
```

---

## 🤖 Entendiendo el Modelo IA

### **¿Cómo funciona?**

```
Imagen → Redimensionada → Procesada → Modelo IA → Clasificación + Confianza
         (640x480)         (128x128)   (TensorFlow)    (%)
```

### **Clases del modelo:**
| Clase | Confianza Esperada |
|-------|-------------------|
| Título Americano | >95% |
| Tarjeta Circulación MX | >95% |
| Licencia DMV | >90% |
| Otros/Fondo | >85% |

### **Transferencia de Aprendizaje:**
- Base: MobileNet (pre-entrenada en ImageNet)
- Capas personalizadas: Documento vehicular
- Entrenamiento: Google Teachable Machine

---

## 🔧 Solución de Problemas

### **Problema: "ModuleNotFoundError: No module named 'flask'"**
```bash
# Solución: Reinstalar dependencias
pip install --upgrade -r requirements.txt
```

### **Problema: Cámara no funciona**
```bash
# Verificar permisos
# En Linux: sudo usermod -a -G video $USER
# En Windows: Reiniciar aplicación con admin
```

### **Problema: Modelo no se carga**
```bash
# Verificar carpeta del modelo
ls "RECONOCIMIENTO DE DOCUMENTOS/"
# Debe contener: model.json, weights.bin, metadata.json
```

### **Problema: Puerto 5000 ocupado**
```bash
# Usar otro puerto:
python app.py --port 8080
# Abre: http://localhost:8080
```

---

## 📊 Rendimiento

| Métrica | Valor |
|---------|-------|
| Precisión (Validación) | >95% |
| Tiempo por predicción | <500ms |
| Tamaño del modelo | ~45MB |
| Clases soportadas | 4+ |
| Requisitos RAM | 512MB mínimo |

---

## 🎥 Video Explicativo

Mira cómo funciona AutoDocVision:

📺 **[Ver en YouTube]([[https://www.youtube.com/watch?v=TU_URL_AQUI](https://youtu.be/lDsw31TqXrA)](https://youtu.be/lDsw31TqXrA))**

*Duración: 2-3 minutos*
*Incluye: Captura de pantalla real, voz y demostración completa*

---

## 📚 Documentación Adicional

- **`REPORTE.md`** - Análisis técnico, decisiones y resultados
- **`QUICKSTART.md`** - Guía de inicio rápido
- **`docs/DOCUMENTACION_CODIGO.md`** - Detalles de funciones
- **`VIDEO_INSTRUCTIONS.md`** - Cómo grabar el video

---

## 🛠️ Tecnologías Utilizadas

| Tecnología | Propósito |
|-----------|----------|
| **Python 3.8+** | Lenguaje principal |
| **Flask** | Servidor web |
| **TensorFlow.js** | Motor de IA |
| **OpenCV** | Visión por computadora |
| **NumPy** | Cálculos numéricos |
| **Google Teachable Machine** | Entrenamiento del modelo |

---

## 📝 Licencia

Este proyecto está bajo licencia **MIT**. Eres libre de usar, modificar y distribuir.
Ver `LICENSE` para detalles completos.

---

## 👤 Autor

**Ricardo Garfias**
- GitHub: [@RicardoGarfias](https://github.com/RicardoGarfias)
- Proyecto: AutoDocVision

---

## ❓ ¿Necesitas Ayuda?

1. **Revisa `QUICKSTART.md`** para inicio rápido
2. **Consulta `REPORTE.md`** para detalles técnicos
3. **Abre un Issue** en GitHub
4. **Mira el video** explicativo en YouTube

---

## ✅ Checklist de Verificación

- [ ] Python 3.8+ instalado
- [ ] Dependencias instaladas: `pip install -r requirements.txt`
- [ ] Modelo en carpeta: `RECONOCIMIENTO DE DOCUMENTOS/`
- [ ] Aplicación inicia: `python app.py`
- [ ] Interfaz accesible: `http://localhost:5000`
- [ ] Cámara funciona (si usas `camera_detection.py`)

---

**Última actualización:** Noviembre 2025
**Versión:** 1.0.0
