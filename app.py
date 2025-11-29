"""
AutoDocVision - Aplicación Principal Flask
Servidor web para detección de documentos vehiculares
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import json
import os
from datetime import datetime
import logging
from functools import wraps
import time

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear aplicación Flask
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB máximo
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

# Crear carpeta de uploads si no existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Importar módulos de utilidad
from utils.model_loader import ModelLoader
from utils.image_processor import ImageProcessor
from utils.predictor import Predictor

# Inicializar componentes
try:
    model_loader = ModelLoader()
    image_processor = ImageProcessor()
    predictor = Predictor(model_loader)
    logger.info("Modelo cargado correctamente")
except Exception as e:
    logger.error(f"Error al cargar modelo: {e}")
    model_loader = None


# ============================================================================
# UTILIDADES
# ============================================================================

def allowed_file(filename):
    """Valida si el archivo tiene extensión permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def timer_decorator(func):
    """Decorador para medir tiempo de ejecución"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        logger.info(f"{func.__name__} ejecutado en {elapsed_time:.3f}s")
        return result
    return wrapper


def get_confidence_color(confidence):
    """Retorna color HTML basado en nivel de confianza"""
    if confidence >= 0.9:
        return 'success'  # Verde
    elif confidence >= 0.75:
        return 'warning'  # Amarillo
    else:
        return 'danger'   # Rojo


# ============================================================================
# RUTAS - PÁGINAS
# ============================================================================

@app.route('/')
def index():
    """Página principal con interfaz web"""
    return render_template('index.html')


@app.route('/about')
def about():
    """Página de información del proyecto"""
    return render_template('about.html')


# ============================================================================
# RUTAS - API DE DETECCIÓN
# ============================================================================

@app.route('/api/detect', methods=['POST'])
@timer_decorator
def detect_image():
    """
    Endpoint para detectar documento desde imagen subida
    
    Parámetros:
        - image: archivo de imagen (multipart/form-data)
        - confidence: umbral de confianza (opcional, default=0.7)
    
    Retorna:
        JSON con resultado de detección
    """
    
    # Validar que modelo está cargado
    if model_loader is None:
        return jsonify({
            'success': False,
            'error': 'Modelo no disponible'
        }), 503
    
    # Validar que hay archivo
    if 'image' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No se encontró archivo de imagen'
        }), 400
    
    file = request.files['image']
    
    # Validar nombre de archivo
    if file.filename == '':
        return jsonify({
            'success': False,
            'error': 'Nombre de archivo vacío'
        }), 400
    
    # Validar extensión
    if not allowed_file(file.filename):
        return jsonify({
            'success': False,
            'error': 'Formato de archivo no permitido. Use: PNG, JPG, JPEG, GIF, BMP'
        }), 400
    
    # Obtener umbral de confianza
    confidence_threshold = request.form.get('confidence', 0.7, type=float)
    if not 0 <= confidence_threshold <= 1:
        confidence_threshold = 0.7
    
    try:
        # Procesar imagen
        import cv2
        import numpy as np
        
        # Leer imagen
        file_data = file.read()
        nparr = np.frombuffer(file_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({
                'success': False,
                'error': 'No se pudo leer la imagen'
            }), 400
        
        # Procesar y predecir
        processed_image = image_processor.process(img)
        prediction = predictor.predict(processed_image)
        
        # Preparar respuesta
        response = {
            'success': True,
            'class': prediction['class'],
            'confidence': round(prediction['confidence'], 4),
            'class_index': prediction['class_index'],
            'above_threshold': prediction['confidence'] >= confidence_threshold,
            'timestamp': datetime.now().isoformat(),
            'confidence_color': get_confidence_color(prediction['confidence'])
        }
        
        logger.info(f"Detección exitosa: {response['class']} ({response['confidence']})")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error en detección: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al procesar imagen: {str(e)}'
        }), 500


@app.route('/api/detect-camera', methods=['POST'])
@timer_decorator
def detect_camera():
    """
    Endpoint para detectar desde frame de cámara (base64)
    
    Parámetros JSON:
        - frame_data: imagen en base64
        - confidence: umbral (opcional)
    
    Retorna:
        JSON con resultado de detección
    """
    
    if model_loader is None:
        return jsonify({
            'success': False,
            'error': 'Modelo no disponible'
        }), 503
    
    try:
        import base64
        import cv2
        import numpy as np
        
        data = request.get_json()
        
        if 'frame_data' not in data:
            return jsonify({
                'success': False,
                'error': 'No se proporcionó frame_data'
            }), 400
        
        # Decodificar base64
        frame_data = data['frame_data']
        if ',' in frame_data:
            frame_data = frame_data.split(',')[1]
        
        frame_bytes = base64.b64decode(frame_data)
        nparr = np.frombuffer(frame_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({
                'success': False,
                'error': 'No se pudo decodificar frame'
            }), 400
        
        # Procesar y predecir
        processed_image = image_processor.process(frame)
        prediction = predictor.predict(processed_image)
        
        response = {
            'success': True,
            'class': prediction['class'],
            'confidence': round(prediction['confidence'], 4),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error en detección de cámara: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/classes', methods=['GET'])
def get_classes():
    """
    Obtiene lista de clases que el modelo puede detectar
    
    Retorna:
        JSON con lista de clases
    """
    
    if model_loader is None:
        return jsonify({
            'success': False,
            'error': 'Modelo no disponible'
        }), 503
    
    try:
        classes = model_loader.get_class_names()
        return jsonify({
            'success': True,
            'classes': classes,
            'count': len(classes)
        }), 200
    except Exception as e:
        logger.error(f"Error al obtener clases: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/model-info', methods=['GET'])
def get_model_info():
    """
    Obtiene información del modelo cargado
    
    Retorna:
        JSON con detalles del modelo
    """
    
    if model_loader is None:
        return jsonify({
            'success': False,
            'error': 'Modelo no disponible'
        }), 503
    
    try:
        metadata = model_loader.get_metadata()
        return jsonify({
            'success': True,
            'model_info': metadata
        }), 200
    except Exception as e:
        logger.error(f"Error al obtener info del modelo: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# RUTAS - ARCHIVOS ESTÁTICOS
# ============================================================================

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Sirve archivos estáticos"""
    return send_from_directory('static', filename)


# ============================================================================
# GESTIÓN DE ERRORES
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Maneja errores 404"""
    return jsonify({
        'success': False,
        'error': 'Página no encontrada'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Maneja errores 500"""
    logger.error(f"Error interno: {str(error)}")
    return jsonify({
        'success': False,
        'error': 'Error interno del servidor'
    }), 500


# ============================================================================
# SALUD Y DIAGNÓSTICO
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de salud del servidor"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'model_loaded': model_loader is not None
    }), 200


# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

if __name__ == '__main__':
    # Configuración para desarrollo
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
    # Para producción, usar:
    # gunicorn -w 4 -b 0.0.0.0:5000 app:app
