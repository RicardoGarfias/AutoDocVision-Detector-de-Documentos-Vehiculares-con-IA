# Contribuyendo a AutoDocVision

¡Gracias por interesarte en contribuir a AutoDocVision! Este documento proporciona pautas y instrucciones para contribuir.

## 🤝 Cómo Contribuir

### Reportar Bugs

Si encuentras un bug, crea un issue incluyendo:

1. **Descripción clara** del problema
2. **Pasos para reproducir** el problema
3. **Comportamiento esperado** vs **comportamiento actual**
4. **Screenshots o logs** si es aplicable
5. **Tu entorno** (SO, versión de Python, etc.)

### Sugerencias de Mejoras

Para sugerir mejoras:

1. Usa el título descriptivo
2. Proporciona una descripción detallada de la mejora sugerida
3. Explica por qué esta mejora sería útil
4. Lista algunos ejemplos de cómo se usaría

### Pull Requests

#### Preparación

1. Fork el repositorio
2. Clona tu fork localmente
3. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
4. Instala las dependencias: `pip install -r requirements.txt`

#### Desarrollo

1. Realiza tus cambios
2. Asegúrate de que el código sigue el estilo del proyecto
3. Añade tests si es aplicable
4. Documenta cambios importantes

#### Antes de hacer Push

```bash
# Formatea el código
black app.py utils/ detect_image.py camera_detection.py

# Verifica errores de linting
flake8 app.py utils/ detect_image.py camera_detection.py

# Ejecuta tests (si existen)
pytest
```

#### Hacer Push

1. Commit tus cambios con mensaje descriptivo:
   ```bash
   git commit -m "Add feature: descripción clara del cambio"
   ```

2. Push a tu fork:
   ```bash
   git push origin feature/AmazingFeature
   ```

3. Abre un Pull Request en GitHub con:
   - Título descriptivo
   - Descripción detallada de cambios
   - Referencias a issues relacionados
   - Screenshots/videos si es aplicable

## 📋 Directrices de Código

### Style Guide

- **Python**: Sigue [PEP 8](https://pep8.org/)
- **Docstrings**: Usa formato NumPy/Google
- **Nombres**: 
  - Funciones/variables: `snake_case`
  - Clases: `PascalCase`
  - Constantes: `UPPER_CASE`

### Ejemplo de Función Documentada

```python
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
            'class': str,
            'confidence': float,
            'above_threshold': bool
        }
    
    Raises:
        ValueError: Si la imagen tiene formato inválido
    """
```

## 🧪 Testing

```bash
# Instalar herramientas de testing
pip install pytest pytest-cov

# Ejecutar tests
pytest

# Con cobertura
pytest --cov=./ --cov-report=html
```

## 📚 Documentación

- Actualiza README.md si cambias funcionalidad
- Mantén REPORTE.md con información técnica actual
- Comenta código complejo
- Usa docstrings en todas las funciones públicas

## 🔄 Proceso de Review

1. Tu PR será revisado por mantenedores
2. Pueden solicitar cambios
3. Actualiza tu PR según feedback
4. Una vez aprobado, será mergeado

## 💬 Comunicación

- Sé respetuoso y constructivo
- Incluye contexto en discusiones
- Proporciona ejemplos cuando sea posible
- Responde a feedback de manera oportuna

## 📄 Licencia

Al contribuir, aceptas que tu código será licenciado bajo MIT License.

## 🙏 Agradecimientos

¡Gracias por contribuir a hacer AutoDocVision mejor!

---

**Para preguntas, contacta a:** Ricardo Garfias (GitHub: @RicardoGarfias)
