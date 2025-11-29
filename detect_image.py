"""
Detect Image - Detección de documentos en imágenes estáticas
"""

import argparse
import logging
import json
import os
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from utils.model_loader import ModelLoader
from utils.image_processor import ImageProcessor
from utils.predictor import Predictor


class ImageDetector:
    """Detector de documentos en imágenes estáticas"""
    
    def __init__(self, confidence_threshold=0.5):
        """
        Inicializa detector de imágenes
        
        Args:
            confidence_threshold (float): Umbral de confianza
        """
        logger.info("Inicializando ImageDetector...")
        
        self.confidence_threshold = confidence_threshold
        self.model_loader = ModelLoader()
        self.image_processor = ImageProcessor()
        self.predictor = Predictor(self.model_loader, confidence_threshold)
        
        logger.info("ImageDetector inicializado correctamente")
    
    def detect(self, image_path, return_all_probs=False):
        """
        Detecta documento en imagen
        
        Args:
            image_path (str): Ruta a la imagen
            return_all_probs (bool): Retorna probabilidades de todas las clases
        
        Returns:
            dict: Resultado de detección
        """
        
        try:
            # Validar archivo
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Archivo no encontrado: {image_path}")
            
            logger.info(f"Procesando imagen: {image_path}")
            
            # Procesar imagen
            image = self.image_processor.process(image_path)
            
            # Hacer predicción
            prediction = self.predictor.predict(image, return_all_probs)
            
            # Agregar información adicional
            result = {
                'file': os.path.basename(image_path),
                'success': True,
                'class': prediction['class'],
                'class_index': prediction['class_index'],
                'confidence': round(prediction['confidence'], 4),
                'above_threshold': prediction['confidence'] >= self.confidence_threshold,
                'threshold': self.confidence_threshold,
                'timestamp': datetime.now().isoformat()
            }
            
            if return_all_probs:
                result['all_probabilities'] = prediction['all_probabilities']
                result['all_classes'] = self.model_loader.get_class_names()
            
            logger.info(f"Detección exitosa: {result['class']} ({result['confidence']})")
            
            return result
            
        except Exception as e:
            logger.error(f"Error en detección: {e}")
            return {
                'file': os.path.basename(image_path),
                'success': False,
                'error': str(e)
            }
    
    def detect_batch(self, image_paths, return_all_probs=False):
        """
        Detecta documentos en múltiples imágenes
        
        Args:
            image_paths (list): Lista de rutas a imágenes
            return_all_probs (bool): Retorna probabilidades de todas las clases
        
        Returns:
            list: Lista de resultados
        """
        
        results = []
        for image_path in image_paths:
            result = self.detect(image_path, return_all_probs)
            results.append(result)
        
        return results


def print_result_text(result):
    """Imprime resultado en formato texto"""
    print(f"\n{'='*60}")
    print(f"RESULTADO DE DETECCIÓN - AutoDocVision")
    print(f"{'='*60}")
    
    if result['success']:
        print(f"Archivo: {result['file']}")
        print(f"Clase: {result['class']}")
        print(f"Confianza: {result['confidence']:.1%}")
        print(f"Índice de clase: {result['class_index']}")
        print(f"Encima del umbral ({result['threshold']}): {result['above_threshold']}")
        
        if 'all_probabilities' in result:
            print(f"\nProbabilidades por clase:")
            for class_name, prob in zip(result['all_classes'], result['all_probabilities']):
                print(f"  {class_name}: {prob:.4f} ({prob*100:.2f}%)")
    else:
        print(f"ERROR: {result['error']}")
    
    print(f"{'='*60}\n")


def main():
    """Función principal"""
    
    parser = argparse.ArgumentParser(
        description='Detección de documentos vehiculares en imágenes'
    )
    parser.add_argument('--image', type=str, required=True,
                       help='Ruta a la imagen a procesar')
    parser.add_argument('--confidence', type=float, default=0.5,
                       help='Umbral de confianza (0-1, default: 0.5)')
    parser.add_argument('--output', type=str, default=None,
                       help='Ruta para guardar imagen con resultado')
    parser.add_argument('--json', action='store_true',
                       help='Salida en formato JSON')
    parser.add_argument('--all-probs', action='store_true',
                       help='Mostrar probabilidades de todas las clases')
    parser.add_argument('--batch', nargs='+', default=None,
                       help='Procesar múltiples imágenes')
    
    args = parser.parse_args()
    
    try:
        # Validar confianza
        if not 0 <= args.confidence <= 1:
            logger.error("Confianza debe estar entre 0 y 1")
            return 1
        
        # Inicializar detector
        detector = ImageDetector(confidence_threshold=args.confidence)
        
        # Procesar imagen(s)
        if args.batch:
            logger.info(f"Procesando lote de {len(args.batch)} imágenes...")
            results = detector.detect_batch(args.batch, args.all_probs)
        else:
            result = detector.detect(args.image, args.all_probs)
            results = [result]
        
        # Mostrar resultados
        if args.json:
            # Salida JSON
            output = {'results': results, 'count': len(results)}
            json_str = json.dumps(output, indent=2, ensure_ascii=False)
            print(json_str)
            
            # Guardar a archivo si se especifica
            if args.output and args.output.endswith('.json'):
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(output, f, indent=2, ensure_ascii=False)
                logger.info(f"Resultados guardados en: {args.output}")
        else:
            # Salida texto
            for result in results:
                print_result_text(result)
        
        # Guardar imagen con resultado (solo para una imagen)
        if args.output and not args.output.endswith('.json') and len(results) == 1:
            import cv2
            try:
                img = cv2.imread(args.image)
                if img is not None:
                    # Dibujar resultado
                    result = results[0]
                    if result['success']:
                        label = f"{result['class']}: {result['confidence']:.1%}"
                        color = (0, 255, 0) if result['confidence'] >= 0.9 else (0, 165, 255)
                        cv2.rectangle(img, (10, 10), (400, 80), color, 2)
                        cv2.putText(img, label, (20, 55),
                                   cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                    
                    cv2.imwrite(args.output, img)
                    logger.info(f"Imagen guardada en: {args.output}")
            except Exception as e:
                logger.error(f"Error al guardar imagen: {e}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error fatal: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
