"""
Camera Detection - Detección en tiempo real desde cámara web
"""

import cv2
import numpy as np
import argparse
import logging
from datetime import datetime
import os

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from utils.model_loader import ModelLoader
from utils.image_processor import ImageProcessor
from utils.predictor import Predictor


class CameraDetector:
    """Detector de documentos en tiempo real desde cámara"""
    
    def __init__(self, camera_id=0, confidence_threshold=0.7):
        """
        Inicializa detector de cámara
        
        Args:
            camera_id (int): ID de la cámara (0=predeterminada)
            confidence_threshold (float): Umbral de confianza
        """
        logger.info("Inicializando CameraDetector...")
        
        self.camera_id = camera_id
        self.confidence_threshold = confidence_threshold
        self.model_loader = ModelLoader()
        self.image_processor = ImageProcessor()
        self.predictor = Predictor(self.model_loader, confidence_threshold)
        
        # Inicializar cámara
        self.cap = cv2.VideoCapture(camera_id)
        if not self.cap.isOpened():
            raise RuntimeError(f"No se pudo acceder a la cámara {camera_id}")
        
        # Configurar propiedades de cámara
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        self.running = True
        self.frame_count = 0
        self.detections_count = 0
        
        logger.info("CameraDetector inicializado correctamente")
    
    def run(self, save_detections=False, output_dir='detections'):
        """
        Ejecuta detección en tiempo real
        
        Args:
            save_detections (bool): Guardar imágenes detectadas
            output_dir (str): Directorio para guardar imágenes
        
        Controles:
            q - Salir
            s - Guardar captura actual
            c - Limpiar pantalla
            t - Mostrar estadísticas
        """
        
        if save_detections:
            os.makedirs(output_dir, exist_ok=True)
        
        logger.info("Iniciando captura de cámara...")
        logger.info("Controles: q=salir, s=guardar, c=limpiar, t=estadísticas")
        
        fps_start_time = datetime.now()
        fps_counter = 0
        
        while self.running:
            ret, frame = self.cap.read()
            
            if not ret:
                logger.error("Error al leer frame de cámara")
                break
            
            self.frame_count += 1
            fps_counter += 1
            
            # Redimensionar para procesamiento
            display_frame = cv2.resize(frame, (1280, 720))
            
            # Procesar y predecir
            try:
                processed = self.image_processor.process(frame)
                prediction = self.predictor.predict(processed)
                
                # Verificar si cumple threshold
                if prediction['confidence'] >= self.confidence_threshold:
                    self.detections_count += 1
                    
                    # Preparar etiqueta
                    label = f"{prediction['class']}: {prediction['confidence']:.1%}"
                    color = (0, 255, 0) if prediction['confidence'] >= 0.9 else (0, 165, 255)
                    
                    # Dibujar en frame
                    cv2.rectangle(display_frame, (10, 10), (550, 100), color, 2)
                    cv2.putText(display_frame, label, (20, 50),
                               cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 2)
                    cv2.putText(display_frame, 
                               f"Presiona 's' para guardar",
                               (20, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1)
            
            except Exception as e:
                logger.error(f"Error en predicción: {e}")
            
            # Mostrar información
            fps_elapsed = (datetime.now() - fps_start_time).total_seconds()
            if fps_elapsed >= 1:
                fps = fps_counter / fps_elapsed
                fps_start_time = datetime.now()
                fps_counter = 0
            else:
                fps = 0
            
            # Dibujar FPS y contador
            cv2.putText(display_frame, f"FPS: {fps:.1f}", (10, 700),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(display_frame, f"Frames: {self.frame_count} | Detecciones: {self.detections_count}", 
                       (10, 750), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Mostrar frame
            cv2.imshow('AutoDocVision - Detección en Tiempo Real', display_frame)
            
            # Manejo de teclas
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                logger.info("Saliendo...")
                break
            elif key == ord('s'):
                self._save_frame(display_frame, prediction, output_dir)
            elif key == ord('c'):
                cv2.destroyAllWindows()
                cv2.namedWindow('AutoDocVision - Detección en Tiempo Real')
            elif key == ord('t'):
                self._print_stats()
        
        self.cleanup()
    
    def _save_frame(self, frame, prediction, output_dir):
        """Guarda frame actual con información de predicción"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{output_dir}/detection_{timestamp}_{prediction['class']}.jpg"
            cv2.imwrite(filename, frame)
            logger.info(f"Frame guardado: {filename}")
        except Exception as e:
            logger.error(f"Error al guardar frame: {e}")
    
    def _print_stats(self):
        """Imprime estadísticas de sesión"""
        accuracy = (self.detections_count / self.frame_count * 100) if self.frame_count > 0 else 0
        print(f"\n{'='*50}")
        print(f"ESTADÍSTICAS DE SESIÓN")
        print(f"{'='*50}")
        print(f"Frames procesados: {self.frame_count}")
        print(f"Detecciones: {self.detections_count}")
        print(f"Tasa de detección: {accuracy:.1f}%")
        print(f"{'='*50}\n")
    
    def cleanup(self):
        """Limpia recursos"""
        logger.info("Limpiando recursos...")
        self.running = False
        self.cap.release()
        cv2.destroyAllWindows()
        logger.info("Recursos liberados")
        self._print_stats()


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description='Detección de documentos vehiculares en tiempo real'
    )
    parser.add_argument('--camera', type=int, default=0,
                       help='ID de la cámara (default: 0)')
    parser.add_argument('--confidence', type=float, default=0.7,
                       help='Umbral de confianza (0-1, default: 0.7)')
    parser.add_argument('--save', action='store_true',
                       help='Guardar detecciones en archivos')
    parser.add_argument('--output', type=str, default='detections',
                       help='Directorio de salida para detecciones')
    
    args = parser.parse_args()
    
    try:
        detector = CameraDetector(
            camera_id=args.camera,
            confidence_threshold=args.confidence
        )
        detector.run(save_detections=args.save, output_dir=args.output)
    except Exception as e:
        logger.error(f"Error fatal: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
