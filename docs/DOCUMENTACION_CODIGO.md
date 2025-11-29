# Documentación del Código - AutoDocVision

## 📑 Índice

1. [Estructura de Módulos](#estructura-de-módulos)
2. [Módulo: app.py](#módulo-apppy)
3. [Módulo: camera_detection.py](#módulo-camera_detectionpy)
4. [Módulo: detect_image.py](#módulo-detect_imagepy)
5. [Módulo: model_loader.py](#módulo-model_loaderpy)
6. [Módulo: image_processor.py](#módulo-image_processorpy)
7. [Módulo: predictor.py](#módulo-predictorpy)
8. [Arquitectura Detallada](#arquitectura-detallada)
9. [Ejemplos de Uso](#ejemplos-de-uso)

---

## Estructura de Módulos

```
AutoDocVision/
├── app.py                    # Aplicación principal Flask
├── camera_detection.py       # Detección en tiempo real desde cámara
├── detect_image.py          # Detección de imágenes estáticas
│
├── utils/
│   ├── __init__.py
│   ├── model_loader.py      # Carga y gestión del modelo
│   ├── image_processor.py   # Procesamiento de imágenes
│   └── predictor.py         # Motor de predicción
│
├── templates/
│   ├── base.html            # Plantilla base
│   ├── index.html           # Página principal
│   └── results.html         # Resultados
│
└── static/
    ├── css/
    │   └── style.css        # Estilos
    └── js/
        └── app.js           # JavaScript del cliente
```

---

## Módulo: app.py

**Propósito:** Servidor Flask que proporciona la interfaz web principal

### Importaciones

```python
from flask import Flask, render_template, request, jsonify, send_from_directory
import json
import os
from datetime import datetime
from utils.model_loader import ModelLoader
from utils.image_processor import ImageProcessor
from utils.predictor import Predictor
```

### Estructura Principal

```python
app = Flask(__name__)
model_loader = ModelLoader()
image_processor = ImageProcessor()
predictor = Predictor(model_loader)
```

### Endpoints Principales

#### 1. GET `/`
**Descripción:** Sirve la página principal

```python
@app.route('/')
def index():
    return render_template('index.html')
```

**Respuesta:** Página HTML con interfaz web

---

#### 2. POST `/detect`
**Descripción:** Detecta documentos desde imagen subida

**Parámetros:**
```json
{
    "image": "archivo multipart/form-data",
    "confidence_threshold": 0.7  // opcional
}
```

**Respuesta Exitosa (200):**
```json
{
    "success": true,
    "class": "Título Americano",
    "confidence": 0.985,
    "class_index": 0,
    "processing_time": 0.38,
    "timestamp": "2025-11-29T10:30:45.123Z"
}
```

**Respuesta Error (400):**
```json
{
    "success": false,
    "error": "Formato de imagen no soportado"
}
```

---

#### 3. POST `/detect_camera`
**Descripción:** Detecta desde frame de cámara web

**Parámetros:**
```json
{
    "frame_data": "base64 encoded image"
}
```

**Respuesta:**
```json
{
    "success": true,
    "class": "Tarjeta de Circulación México",
    "confidence": 0.951,
    "processing_time": 0.35
}
```

---

#### 4. GET `/history`
**Descripción:** Obtiene historial de detecciones

**Parámetros Query:**
- `limit` (int, default=10): Número máximo de registros
- `class_filter` (string, optional): Filtrar por clase

**Respuesta:**
```json
{
    "history": [
        {
            "id": 1,
            "class": "Título Americano",
            "confidence": 0.985,
            "timestamp": "2025-11-29T10:30:45Z"
        }
    ],
    "total": 1
}
```

---

### Funciones Auxiliares

```python
def allowed_file(filename):
    """Valida extensión de archivo"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_confidence_color(confidence):
    """Retorna color basado en nivel de confianza"""
    if confidence >= 0.9:
        return 'green'
    elif confidence >= 0.75:
        return 'yellow'
    else:
        return 'red'
```

---

## Módulo: camera_detection.py

**Propósito:** Detectar documentos en tiempo real desde cámara web

### Función Principal

```python
def camera_detection(camera_id=0, confidence_threshold=0.7):
    """
    Inicia detección en tiempo real desde cámara
    
    Args:
        camera_id (int): ID de cámara (0 = predeterminada)
        confidence_threshold (float): Umbral mínimo de confianza (0-1)
    
    Yields:
        dict: Predicción y frame actual
    
    Raises:
        RuntimeError: Si no hay cámara disponible
    """
```

### Inicialización

```python
import cv2
import numpy as np
from utils.model_loader import ModelLoader
from utils.image_processor import ImageProcessor
from utils.predictor import Predictor

cap = cv2.VideoCapture(camera_id)
if not cap.isOpened():
    raise RuntimeError("No se pudo acceder a la cámara")

model_loader = ModelLoader()
image_processor = ImageProcessor()
predictor = Predictor(model_loader)
```

### Loop Principal

```python
while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Redimensionar para procesamiento rápido
    display_frame = cv2.resize(frame, (800, 600))
    
    # Procesar imagen
    processed = image_processor.process(display_frame)
    
    # Predicción
    prediction = predictor.predict(processed)
    
    # Dibujar resultados
    if prediction['confidence'] >= confidence_threshold:
        label = f"{prediction['class']} ({prediction['confidence']:.1%})"
        cv2.putText(display_frame, label, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # Mostrar frame
    cv2.imshow('AutoDocVision - Detección en Tiempo Real', display_frame)
    
    # Controles
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('s'):
        save_frame(display_frame, prediction)

cap.release()
cv2.destroyAllWindows()
```

### Controles

| Tecla | Acción |
|-------|--------|
| `q` | Salir |
| `s` | Guardar captura con resultado |
| `c` | Limpiar pantalla |

---

## Módulo: detect_image.py

**Propósito:** Detectar documentos en imágenes estáticas desde línea de comandos

### Interfaz de Línea de Comandos

```bash
python detect_image.py --image ruta/imagen.jpg [opciones]
```

### Argumentos

```python
parser = argparse.ArgumentParser(description='Detector de Documentos Vehiculares')
parser.add_argument('--image', type=str, required=True,
                   help='Ruta a la imagen a procesar')
parser.add_argument('--confidence', type=float, default=0.5,
                   help='Umbral de confianza (0-1)')
parser.add_argument('--output', type=str, default=None,
                   help='Ruta para guardar resultado')
parser.add_argument('--json', action='store_true',
                   help='Salida en formato JSON')
```

### Ejemplo de Uso

```bash
# Básico
python detect_image.py --image documento.jpg

# Con umbral de confianza
python detect_image.py --image documento.jpg --confidence 0.8

# Guardar resultado
python detect_image.py --image documento.jpg --output resultado.jpg

# Salida JSON
python detect_image.py --image documento.jpg --json
```

### Salida

**Texto:**
```
=== AutoDocVision - Resultado de Detección ===
Archivo: documento.jpg
Clase: Título Americano
Confianza: 98.5%
Tiempo de procesamiento: 0.38s
```

**JSON:**
```json
{
    "file": "documento.jpg",
    "class": "Título Americano",
    "confidence": 0.985,
    "processing_time": 0.38,
    "success": true
}
```

---

## Módulo: model_loader.py

**Propósito:** Gestionar la carga y caché del modelo de IA

### Clase: ModelLoader

```python
class ModelLoader:
    def __init__(self, model_path='RECONOCIMIENTO DE DOCUMENTOS/'):
        """
        Inicializa el cargador de modelo
        
        Args:
            model_path (str): Ruta a la carpeta del modelo
        """
        self.model_path = model_path
        self.model = None
        self.metadata = None
        self.load()
    
    def load(self):
        """Carga el modelo y metadatos"""
        # Cargar metadata
        with open(f'{self.model_path}metadata.json', 'r') as f:
            self.metadata = json.load(f)
        
        # Cargar modelo
        # Implementación depende del formato (TFLite, ONNX, etc)
        self.model = self._load_tensorflow_model()
    
    def get_model(self):
        """Retorna el modelo cargado"""
        if self.model is None:
            self.load()
        return self.model
    
    def get_metadata(self):
        """Retorna metadatos del modelo"""
        return self.metadata
    
    def get_class_names(self):
        """Retorna lista de clases"""
        return self.metadata.get('labels', [])
    
    def _load_tensorflow_model(self):
        """Carga modelo TensorFlow"""
        import tensorflow as tf
        return tf.saved_model.load(self.model_path)
```

### Propiedades

| Propiedad | Tipo | Descripción |
|-----------|------|------------|
| `model_path` | str | Ruta del modelo |
| `model` | object | Modelo cargado |
| `metadata` | dict | Metadatos del modelo |

---

## Módulo: image_processor.py

**Propósito:** Procesar imágenes para predicción

### Clase: ImageProcessor

```python
class ImageProcessor:
    def __init__(self, target_size=(224, 224)):
        """
        Inicializa el procesador
        
        Args:
            target_size (tuple): Tamaño de salida (ancho, alto)
        """
        self.target_size = target_size
    
    def process(self, image_input):
        """
        Procesa una imagen para predicción
        
        Args:
            image_input (np.array o str): Array de imagen o ruta
        
        Returns:
            np.array: Imagen procesada y normalizada
        """
        # Cargar imagen si es ruta
        if isinstance(image_input, str):
            image = cv2.imread(image_input)
        else:
            image = image_input
        
        # Redimensionar
        image = cv2.resize(image, self.target_size)
        
        # Convertir BGR a RGB (OpenCV usa BGR)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Normalizar [0, 1]
        image = image.astype(np.float32) / 255.0
        
        return image
    
    def augment(self, image, num_augmentations=5):
        """
        Aumenta datos de imagen con transformaciones
        
        Args:
            image (np.array): Imagen a aumentar
            num_augmentations (int): Número de versiones
        
        Yields:
            np.array: Imágenes aumentadas
        """
        from albumentations import Compose, Rotate, ShiftScaleRotate
        
        transform = Compose([
            Rotate(limit=15, p=0.7),
            ShiftScaleRotate(shift_limit=0.1, scale_limit=0.2, p=0.7)
        ])
        
        for _ in range(num_augmentations):
            yield transform(image=image)['image']
    
    def preprocess_batch(self, images):
        """Procesa lote de imágenes"""
        return np.array([self.process(img) for img in images])
```

### Métodos Principales

| Método | Entrada | Salida | Descripción |
|--------|---------|--------|------------|
| `process()` | Imagen | Array normalizado | Preprocesa imagen |
| `augment()` | Imagen | Generador | Aumenta datos |
| `preprocess_batch()` | Lista imágenes | Array 4D | Procesa lote |

---

## Módulo: predictor.py

**Propósito:** Motor de predicción usando modelo cargado

### Clase: Predictor

```python
class Predictor:
    def __init__(self, model_loader, confidence_threshold=0.7):
        """
        Inicializa predictor
        
        Args:
            model_loader (ModelLoader): Cargador del modelo
            confidence_threshold (float): Umbral mínimo
        """
        self.model = model_loader.get_model()
        self.metadata = model_loader.get_metadata()
        self.class_names = model_loader.get_class_names()
        self.confidence_threshold = confidence_threshold
    
    def predict(self, image, return_all_probabilities=False):
        """
        Realiza predicción sobre imagen
        
        Args:
            image (np.array): Imagen procesada
            return_all_probabilities (bool): Retorna todas las clases
        
        Returns:
            dict: Resultado con clase y confianza
            
            Ejemplo:
            {
                'class': 'Título Americano',
                'class_index': 0,
                'confidence': 0.985,
                'all_probabilities': [0.985, 0.01, 0.004, 0.001]
            }
        """
        # Añadir dimensión batch
        if image.ndim == 3:
            image = np.expand_dims(image, axis=0)
        
        # Predicción
        predictions = self.model(image)
        probabilities = predictions[0].numpy()
        
        # Clase con máxima probabilidad
        max_index = np.argmax(probabilities)
        max_confidence = probabilities[max_index]
        class_name = self.class_names[max_index]
        
        result = {
            'class': class_name,
            'class_index': int(max_index),
            'confidence': float(max_confidence),
            'above_threshold': max_confidence >= self.confidence_threshold
        }
        
        if return_all_probabilities:
            result['all_probabilities'] = probabilities.tolist()
        
        return result
    
    def predict_batch(self, images):
        """Predicción en lote"""
        results = []
        for image in images:
            results.append(self.predict(image))
        return results
    
    def set_threshold(self, threshold):
        """Establece nuevo umbral de confianza"""
        if 0 <= threshold <= 1:
            self.confidence_threshold = threshold
        else:
            raise ValueError("Threshold debe estar entre 0 y 1")
```

---

## Arquitectura Detallada

### Flujo de Predicción

```
Entrada (Imagen)
       ↓
[ImageProcessor.process]
  • Cargar imagen
  • Redimensionar 224×224
  • BGR → RGB
  • Normalizar [0, 1]
       ↓
   Array Normalizado
       ↓
[Model.predict]
  • Forward pass
  • Obtener logits
  • Softmax
       ↓
   Vector de Probabilidades
       ↓
[Predictor.post_process]
  • Argmax → clase
  • Aplicar threshold
  • Formatear resultado
       ↓
Predicción Final (Clase + Confianza)
```

### Gestión de Memoria

```python
# Caché del modelo para evitar recarga
_model_cache = {}

def get_cached_model(path):
    if path not in _model_cache:
        _model_cache[path] = load_model(path)
    return _model_cache[path]
```

---

## Ejemplos de Uso

### Ejemplo 1: Uso en Script Python

```python
from utils.model_loader import ModelLoader
from utils.image_processor import ImageProcessor
from utils.predictor import Predictor

# Inicializar componentes
model_loader = ModelLoader()
image_processor = ImageProcessor()
predictor = Predictor(model_loader)

# Procesar imagen
image = image_processor.process('documento.jpg')

# Hacer predicción
result = predictor.predict(image)

print(f"Clase: {result['class']}")
print(f"Confianza: {result['confidence']:.1%}")
```

### Ejemplo 2: Uso en Aplicación Web

```python
from flask import Flask, request, jsonify

@app.route('/detect', methods=['POST'])
def detect():
    # Obtener imagen
    file = request.files['image']
    
    # Procesamiento
    image = image_processor.process(file.stream)
    
    # Predicción
    result = predictor.predict(image)
    
    # Respuesta
    return jsonify({
        'class': result['class'],
        'confidence': result['confidence']
    })
```

### Ejemplo 3: Detección en Lote

```python
import os

images_dir = 'documentos/'
results = []

for filename in os.listdir(images_dir):
    image_path = os.path.join(images_dir, filename)
    image = image_processor.process(image_path)
    result = predictor.predict(image)
    results.append({
        'file': filename,
        **result
    })

# Guardar resultados
import json
with open('resultados.json', 'w') as f:
    json.dump(results, f, indent=2)
```

---

## Mejores Prácticas

### 1. Manejo de Errores

```python
try:
    image = image_processor.process(image_path)
    result = predictor.predict(image)
except FileNotFoundError:
    print("Archivo no encontrado")
except ValueError as e:
    print(f"Error de validación: {e}")
except Exception as e:
    print(f"Error inesperado: {e}")
```

### 2. Logging

```python
import logging

logger = logging.getLogger(__name__)

logger.info(f"Procesando imagen: {image_path}")
logger.debug(f"Predicción: {result}")
logger.warning(f"Confianza baja: {result['confidence']}")
```

### 3. Performance

```python
import time

start_time = time.time()
result = predictor.predict(image)
processing_time = time.time() - start_time

print(f"Tiempo de procesamiento: {processing_time:.3f}s")
```

---

**Documento Versión:** 1.0.0  
**Fecha:** Noviembre 2025

