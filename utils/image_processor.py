"""
Image Processor - Procesamiento de imágenes para predicción
"""

import cv2
import numpy as np
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ImageProcessor:
    """
    Procesa imágenes para compatibilidad con modelo de IA
    Realiza redimensionamiento, normalización y aumento de datos
    """
    
    def __init__(self, target_size=(224, 224), normalize=True):
        """
        Inicializa el procesador de imágenes
        
        Args:
            target_size (tuple): Tamaño de salida (ancho, alto)
            normalize (bool): Si normalizar a [0, 1]
        """
        self.target_size = target_size
        self.normalize = normalize
        logger.info(f"ImageProcessor inicializado: target_size={target_size}")
    
    def process(self, image_input, verbose=False):
        """
        Procesa una imagen para predicción
        
        Args:
            image_input (np.array o str): Array de imagen o ruta al archivo
            verbose (bool): Si mostrar logs detallados
        
        Returns:
            np.array: Imagen procesada y normalizada
        
        Raises:
            FileNotFoundError: Si no encuentra el archivo
            ValueError: Si la imagen no es válida
        """
        
        # Cargar imagen si es ruta
        if isinstance(image_input, str):
            if verbose:
                logger.info(f"Cargando imagen desde archivo: {image_input}")
            
            if not Path(image_input).exists():
                raise FileNotFoundError(f"Archivo no encontrado: {image_input}")
            
            image = cv2.imread(image_input)
            if image is None:
                raise ValueError(f"No se pudo leer imagen: {image_input}")
        else:
            image = image_input
        
        # Validar imagen
        if image is None or not isinstance(image, np.ndarray):
            raise ValueError("Entrada inválida: debe ser un array de numpy o ruta a archivo")
        
        if image.size == 0:
            raise ValueError("Imagen vacía")
        
        # Redimensionar
        if verbose:
            logger.info(f"Redimensionando de {image.shape} a {self.target_size}")
        
        image = cv2.resize(image, self.target_size, interpolation=cv2.INTER_LINEAR)
        
        # Convertir BGR a RGB (OpenCV por defecto usa BGR)
        if len(image.shape) == 3 and image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Convertir a float32
        image = image.astype(np.float32)
        
        # Normalizar [0, 1]
        if self.normalize:
            image = image / 255.0
            if verbose:
                logger.info(f"Imagen normalizada a rango [0, 1]")
        
        return image
    
    def process_batch(self, image_inputs, verbose=False):
        """
        Procesa lote de imágenes
        
        Args:
            image_inputs (list): Lista de arrays o rutas
            verbose (bool): Si mostrar logs detallados
        
        Returns:
            np.array: Array 4D (N, H, W, C)
        """
        
        if verbose:
            logger.info(f"Procesando lote de {len(image_inputs)} imágenes")
        
        processed_images = []
        for i, img_input in enumerate(image_inputs):
            try:
                processed = self.process(img_input, verbose=False)
                processed_images.append(processed)
            except Exception as e:
                logger.error(f"Error procesando imagen {i}: {e}")
                continue
        
        return np.array(processed_images)
    
    def augment(self, image, num_augmentations=1, rotation_range=15, 
                shift_range=0.1, brightness_range=0.2):
        """
        Augmenta imagen con transformaciones aleatorias
        
        Args:
            image (np.array): Imagen a aumentar
            num_augmentations (int): Número de versiones generadas
            rotation_range (int): Rango de rotación en grados
            shift_range (float): Rango de desplazamiento (0-1)
            brightness_range (float): Rango de cambio de brillo (0-1)
        
        Yields:
            np.array: Imágenes aumentadas
        """
        
        for _ in range(num_augmentations):
            augmented = image.copy()
            
            # Rotación aleatoria
            if rotation_range > 0:
                angle = np.random.uniform(-rotation_range, rotation_range)
                h, w = augmented.shape[:2]
                M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1.0)
                augmented = cv2.warpAffine(augmented, M, (w, h))
            
            # Desplazamiento aleatorio
            if shift_range > 0:
                h, w = augmented.shape[:2]
                dx = int(w * np.random.uniform(-shift_range, shift_range))
                dy = int(h * np.random.uniform(-shift_range, shift_range))
                M = np.float32([[1, 0, dx], [0, 1, dy]])
                augmented = cv2.warpAffine(augmented, M, (w, h))
            
            # Cambio de brillo
            if brightness_range > 0:
                delta = int(255 * np.random.uniform(-brightness_range, brightness_range))
                augmented = cv2.convertScaleAbs(augmented, alpha=1, beta=delta)
            
            yield augmented
    
    def convert_to_input_shape(self, image):
        """
        Convierte imagen al formato exacto esperado por el modelo
        Agrega dimensión batch si es necesario
        
        Args:
            image (np.array): Imagen procesada
        
        Returns:
            np.array: Imagen con dimensión batch (1, H, W, C)
        """
        
        if image.ndim == 3:
            # Agregar dimensión batch
            image = np.expand_dims(image, axis=0)
        
        return image
    
    def resize_preserve_aspect(self, image, target_size, pad_color=(128, 128, 128)):
        """
        Redimensiona preservando aspecto ratio, rellena con padding si es necesario
        
        Args:
            image (np.array): Imagen a redimensionar
            target_size (tuple): Tamaño objetivo
            pad_color (tuple): Color de relleno (BGR)
        
        Returns:
            np.array: Imagen redimensionada
        """
        
        h, w = image.shape[:2]
        target_w, target_h = target_size
        
        # Calcular escala
        scale = min(target_w / w, target_h / h)
        
        # Redimensionar
        new_w = int(w * scale)
        new_h = int(h * scale)
        resized = cv2.resize(image, (new_w, new_h))
        
        # Crear canvas
        canvas = np.full((target_h, target_w, 3), pad_color, dtype=np.uint8)
        
        # Colocar imagen redimensionada en el centro
        y_offset = (target_h - new_h) // 2
        x_offset = (target_w - new_w) // 2
        canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
        
        return canvas
    
    def __repr__(self):
        return f"ImageProcessor(target_size={self.target_size}, normalize={self.normalize})"
