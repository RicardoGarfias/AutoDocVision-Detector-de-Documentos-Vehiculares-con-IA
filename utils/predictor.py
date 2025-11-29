"""
Predictor - Motor de predicción usando modelo cargado
"""

import numpy as np
import logging
import time

logger = logging.getLogger(__name__)


class Predictor:
    """
    Motor de predicción que utiliza el modelo cargado
    Realiza predicciones y post-procesamiento de resultados
    """
    
    def __init__(self, model_loader, confidence_threshold=0.7):
        """
        Inicializa el predictor
        
        Args:
            model_loader (ModelLoader): Cargador del modelo
            confidence_threshold (float): Umbral mínimo de confianza (0-1)
        
        Raises:
            ValueError: Si threshold no está en rango [0, 1]
        """
        
        if not 0 <= confidence_threshold <= 1:
            raise ValueError("Confidence threshold debe estar entre 0 y 1")
        
        self.model = model_loader.get_model()
        self.metadata = model_loader.get_metadata()
        self.class_names = model_loader.get_class_names()
        self.confidence_threshold = confidence_threshold
        
        logger.info(f"Predictor inicializado con threshold={confidence_threshold}")
        logger.info(f"Clases disponibles: {self.class_names}")
    
    def predict(self, image, return_all_probabilities=False, verbose=False):
        """
        Realiza predicción sobre imagen
        
        Args:
            image (np.array): Imagen procesada (H, W, C) o (1, H, W, C)
            return_all_probabilities (bool): Si retornar todas las probabilidades
            verbose (bool): Si mostrar logs detallados
        
        Returns:
            dict: Resultado con formato:
            {
                'class': str,              # Nombre de la clase predicha
                'class_index': int,        # Índice de la clase
                'confidence': float,       # Confianza (0-1)
                'above_threshold': bool,   # Si supera el threshold
                'all_probabilities': list  # (opcional) Probabilidades de todas las clases
            }
        
        Raises:
            ValueError: Si la imagen tiene formato inválido
        """
        
        start_time = time.time()
        
        # Validar entrada
        if image is None or not isinstance(image, np.ndarray):
            raise ValueError("Imagen debe ser un array de numpy")
        
        if image.size == 0:
            raise ValueError("Imagen vacía")
        
        # Agregar dimensión batch si es necesario
        if image.ndim == 3:
            if verbose:
                logger.info("Agregando dimensión batch")
            image = np.expand_dims(image, axis=0)
        
        if verbose:
            logger.info(f"Forma de entrada: {image.shape}")
        
        try:
            # Realizar predicción
            # Nota: La implementación exacta depende del formato del modelo
            # (TFLite, ONNX, TensorFlow, etc.)
            # Esta es una estructura genérica
            
            if self.model is None:
                # Fallback: predicción simulada para demostración
                logger.warning("Modelo no disponible, usando predicción simulada")
                probabilities = self._simulate_prediction(image.shape[0])
            else:
                # Predicción real con el modelo
                predictions = self.model.predict(image)
                probabilities = predictions[0].numpy() if hasattr(predictions[0], 'numpy') else predictions[0]
            
            # Asegurar que es un array numpy
            if not isinstance(probabilities, np.ndarray):
                probabilities = np.array(probabilities)
            
            # Validar dimensiones
            if probabilities.ndim == 1:
                probabilities = np.expand_dims(probabilities, 0)
            
            probabilities = probabilities[0]  # Tomar primer resultado del batch
            
            if verbose:
                logger.info(f"Probabilidades: {probabilities}")
            
            # Encontrar clase con máxima probabilidad
            max_index = int(np.argmax(probabilities))
            max_confidence = float(probabilities[max_index])
            
            # Validar índice
            if max_index >= len(self.class_names):
                max_index = 0
            
            class_name = self.class_names[max_index] if self.class_names else f"Clase {max_index}"
            
            # Construir resultado
            result = {
                'class': class_name,
                'class_index': max_index,
                'confidence': max_confidence,
                'above_threshold': max_confidence >= self.confidence_threshold
            }
            
            if return_all_probabilities:
                result['all_probabilities'] = probabilities.tolist()
            
            # Tiempo de procesamiento
            elapsed_time = time.time() - start_time
            result['processing_time'] = elapsed_time
            
            if verbose:
                logger.info(f"Predicción completada en {elapsed_time:.3f}s")
                logger.info(f"Resultado: {class_name} ({max_confidence:.1%})")
            
            return result
            
        except Exception as e:
            logger.error(f"Error en predicción: {e}")
            raise
    
    def predict_batch(self, images, return_all_probabilities=False, verbose=False):
        """
        Realiza predicción en lote
        
        Args:
            images (list): Lista de arrays de imagen
            return_all_probabilities (bool): Si retornar todas las probabilidades
            verbose (bool): Si mostrar logs detallados
        
        Returns:
            list: Lista de resultados de predicción
        """
        
        results = []
        
        for i, image in enumerate(images):
            try:
                if verbose:
                    logger.info(f"Prediciendo imagen {i+1}/{len(images)}")
                
                result = self.predict(image, return_all_probabilities, verbose=False)
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error prediciendo imagen {i}: {e}")
                results.append({
                    'class': 'Error',
                    'confidence': 0.0,
                    'error': str(e)
                })
        
        return results
    
    def set_threshold(self, threshold):
        """
        Establece nuevo umbral de confianza
        
        Args:
            threshold (float): Nuevo umbral (0-1)
        
        Raises:
            ValueError: Si threshold no está en rango válido
        """
        
        if not 0 <= threshold <= 1:
            raise ValueError("Threshold debe estar entre 0 y 1")
        
        self.confidence_threshold = threshold
        logger.info(f"Threshold actualizado a {threshold}")
    
    def get_statistics(self, predictions):
        """
        Calcula estadísticas de un conjunto de predicciones
        
        Args:
            predictions (list): Lista de resultados de predicción
        
        Returns:
            dict: Estadísticas incluidas promedio de confianza, distribución de clases, etc.
        """
        
        if not predictions:
            return {}
        
        confidences = [p.get('confidence', 0) for p in predictions]
        classes = [p.get('class', 'Unknown') for p in predictions]
        
        # Contar ocurrencias de clases
        class_counts = {}
        for cls in classes:
            class_counts[cls] = class_counts.get(cls, 0) + 1
        
        stats = {
            'total_predictions': len(predictions),
            'average_confidence': np.mean(confidences),
            'min_confidence': np.min(confidences),
            'max_confidence': np.max(confidences),
            'std_confidence': np.std(confidences),
            'class_distribution': class_counts,
            'above_threshold_count': sum(1 for p in predictions if p.get('above_threshold', False))
        }
        
        return stats
    
    def _simulate_prediction(self, batch_size):
        """
        Simula predicción cuando el modelo no está disponible
        Usado para propósitos de demostración/testing
        
        Args:
            batch_size (int): Tamaño del batch
        
        Returns:
            np.array: Probabilidades simuladas
        """
        
        logger.warning("Usando predicción simulada (modo demostración)")
        num_classes = len(self.class_names)
        
        # Generar probabilidades aleatorias
        probabilities = np.random.dirichlet(np.ones(num_classes), batch_size)
        
        return probabilities
    
    def __repr__(self):
        return f"Predictor(classes={len(self.class_names)}, threshold={self.confidence_threshold})"
