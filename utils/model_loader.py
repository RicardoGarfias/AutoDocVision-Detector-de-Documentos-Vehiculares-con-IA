"""
Model Loader - Carga y gestión del modelo de IA
"""

import json
import os
import logging

logger = logging.getLogger(__name__)


class ModelLoader:
    """
    Cargador de modelo Teachable Machine
    Gestiona la carga y caché del modelo de IA
    """
    
    # Caché global para evitar recargar modelo
    _model_cache = {}
    
    def __init__(self, model_path='RECONOCIMIENTO DE DOCUMENTOS'):
        """
        Inicializa el cargador de modelo
        
        Args:
            model_path (str): Ruta a la carpeta del modelo
        
        Raises:
            FileNotFoundError: Si no encuentra los archivos del modelo
        """
        self.model_path = model_path
        self.model = None
        self.metadata = None
        self.weights = None
        self.class_names = None
        
        logger.info(f"Inicializando ModelLoader con ruta: {model_path}")
        self._load()
    
    def _load(self):
        """Carga el modelo y sus metadatos"""
        
        # Validar que la carpeta existe
        if not os.path.isdir(self.model_path):
            raise FileNotFoundError(f"Carpeta del modelo no encontrada: {self.model_path}")
        
        logger.info(f"Cargando modelo desde: {self.model_path}")
        
        # Cargar metadata.json
        metadata_path = os.path.join(self.model_path, 'metadata.json')
        if not os.path.exists(metadata_path):
            raise FileNotFoundError(f"Archivo metadata.json no encontrado en {self.model_path}")
        
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
            logger.info(f"Metadata cargada: {self.metadata.get('name', 'N/A')}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Error al decodificar metadata.json: {e}")
        
        # Cargar model.json
        model_json_path = os.path.join(self.model_path, 'model.json')
        if not os.path.exists(model_json_path):
            logger.warning(f"Archivo model.json no encontrado en {self.model_path}")
        
        # Cargar weights.bin
        weights_path = os.path.join(self.model_path, 'weights.bin')
        if not os.path.exists(weights_path):
            logger.warning(f"Archivo weights.bin no encontrado en {self.model_path}")
        
        # Extraer clases del metadata
        if 'labels' in self.metadata:
            self.class_names = self.metadata['labels']
            logger.info(f"Clases cargadas: {self.class_names}")
        else:
            logger.warning("No se encontró lista de clases en metadata")
            self.class_names = []
    
    def get_model(self):
        """
        Obtiene el modelo cargado
        
        Returns:
            dict: Diccionario con información del modelo
        """
        if self.model is None:
            logger.warning("Modelo aún no inicializado")
        return self.model
    
    def get_metadata(self):
        """
        Obtiene los metadatos del modelo
        
        Returns:
            dict: Metadatos completos del modelo
        """
        return self.metadata if self.metadata else {}
    
    def get_class_names(self):
        """
        Obtiene la lista de nombres de clases
        
        Returns:
            list: Lista de nombres de clases
        """
        return self.class_names if self.class_names else []
    
    def get_model_info(self):
        """
        Obtiene información completa del modelo
        
        Returns:
            dict: Información detallada del modelo
        """
        return {
            'path': self.model_path,
            'name': self.metadata.get('name', 'Desconocido') if self.metadata else 'N/A',
            'classes': self.class_names,
            'num_classes': len(self.class_names) if self.class_names else 0,
            'metadata': self.metadata if self.metadata else {}
        }
    
    @classmethod
    def get_cached_model(cls, model_path):
        """
        Obtiene modelo del caché o lo carga si no existe
        
        Args:
            model_path (str): Ruta del modelo
        
        Returns:
            ModelLoader: Instancia del cargador
        """
        if model_path not in cls._model_cache:
            cls._model_cache[model_path] = ModelLoader(model_path)
            logger.info(f"Modelo cacheado para: {model_path}")
        return cls._model_cache[model_path]
    
    @classmethod
    def clear_cache(cls):
        """Limpia el caché de modelos"""
        cls._model_cache.clear()
        logger.info("Caché de modelos limpiado")
    
    def __repr__(self):
        return f"ModelLoader(path='{self.model_path}', classes={len(self.class_names)})"
