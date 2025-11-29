/*
    AutoDocVision - JavaScript Principal
    Lógica de la interfaz web para detección de documentos vehiculares
*/

// ============================================================================
// VARIABLES GLOBALES
// ============================================================================

let selectedFile = null;
let detectionHistory = JSON.parse(localStorage.getItem('detectionHistory')) || [];
let cameraStream = null;
let cameraActive = false;

// ============================================================================
// FUNCIONALIDAD DE CARGAS
// ============================================================================

// Configurar área de drag & drop
const dragDropArea = document.getElementById('dragDropArea');

dragDropArea.addEventListener('click', () => {
    document.getElementById('fileInput').click();
});

dragDropArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    dragDropArea.classList.add('dragover');
});

dragDropArea.addEventListener('dragleave', () => {
    dragDropArea.classList.remove('dragover');
});

dragDropArea.addEventListener('drop', (e) => {
    e.preventDefault();
    dragDropArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

document.getElementById('fileInput').addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

// Manejo de selección de archivo
function handleFileSelect(file) {
    if (!file.type.startsWith('image/')) {
        showError('Por favor selecciona un archivo de imagen válido');
        return;
    }

    if (file.size > 16 * 1024 * 1024) {
        showError('El archivo es demasiado grande (máximo 16MB)');
        return;
    }

    selectedFile = file;
    
    // Mostrar vista previa
    const reader = new FileReader();
    reader.onload = (e) => {
        const previewSection = document.getElementById('previewSection');
        const previewImage = document.getElementById('previewImage');
        previewImage.src = e.target.result;
        previewSection.style.display = 'block';
        document.getElementById('resultSection').style.display = 'none';
        document.getElementById('errorSection').style.display = 'none';
    };
    reader.readAsDataURL(file);
}

// Cargar y procesar imagen
async function uploadImage() {
    if (!selectedFile) {
        showError('Por favor selecciona una imagen primero');
        return;
    }

    const confidence = parseInt(document.getElementById('confidenceSlider').value) / 100;
    
    const formData = new FormData();
    formData.append('image', selectedFile);
    formData.append('confidence', confidence);

    showLoader(true);

    try {
        const response = await fetch('/api/detect', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        showLoader(false);

        if (data.success) {
            displayResult(data);
            addToHistory(data);
        } else {
            showError(data.error || 'Error al procesar imagen');
        }
    } catch (error) {
        showLoader(false);
        showError('Error de conexión: ' + error.message);
    }
}

// Mostrar resultado
function displayResult(result) {
    document.getElementById('resultClass').textContent = result.class;
    document.getElementById('resultConfidence').textContent = (result.confidence * 100).toFixed(2) + '%';
    document.getElementById('resultStatus').textContent = result.above_threshold ? '✅ Válido' : '⚠️ Bajo Umbral';
    document.getElementById('resultTime').textContent = (result.processing_time * 1000).toFixed(0) + 'ms';

    // Actualizar barra de confianza
    const confidenceBar = document.getElementById('confidenceBar');
    const percentage = result.confidence * 100;
    confidenceBar.style.width = percentage + '%';
    confidenceBar.style.background = percentage >= 90 ? 'linear-gradient(90deg, #16a34a, #15803d)' : 
                                     percentage >= 75 ? 'linear-gradient(90deg, #ea580c, #c2410c)' :
                                     'linear-gradient(90deg, #dc2626, #b91c1c)';
    confidenceBar.textContent = percentage.toFixed(1) + '%';

    document.getElementById('errorSection').style.display = 'none';
    document.getElementById('resultSection').style.display = 'block';
}

// Mostrar error
function showError(message) {
    document.getElementById('errorMessage').textContent = message;
    document.getElementById('errorSection').style.display = 'block';
    document.getElementById('resultSection').style.display = 'none';
}

// ============================================================================
// FUNCIONALIDAD DE CÁMARA
// ============================================================================

async function startCamera() {
    try {
        cameraStream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'environment' },
            audio: false
        });

        const video = document.getElementById('cameraVideo');
        video.srcObject = cameraStream;
        video.onloadedmetadata = () => {
            video.play();
            cameraActive = true;
            updateCameraUI();
            startCameraDetection();
        };
    } catch (error) {
        showError('No se pudo acceder a la cámara: ' + error.message);
    }
}

function stopCamera() {
    if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop());
        cameraActive = false;
        updateCameraUI();
    }
}

function updateCameraUI() {
    document.getElementById('startCameraBtn').style.display = cameraActive ? 'none' : 'block';
    document.getElementById('stopCameraBtn').style.display = cameraActive ? 'block' : 'none';
    document.getElementById('captureBtn').style.display = cameraActive ? 'block' : 'none';
}

async function startCameraDetection() {
    const video = document.getElementById('cameraVideo');
    const canvas = document.getElementById('cameraCanvas');
    const ctx = canvas.getContext('2d');

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const detectFrame = async () => {
        if (!cameraActive) return;

        try {
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            const imageData = canvas.toDataURL('image/jpeg');

            const response = await fetch('/api/detect-camera', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    frame_data: imageData
                })
            });

            const data = await response.json();

            if (data.success) {
                document.getElementById('cameraResultClass').textContent = data.class;
                document.getElementById('cameraResultConfidence').textContent = (data.confidence * 100).toFixed(2) + '%';
                document.getElementById('cameraResultSection').style.display = 'block';
            }
        } catch (error) {
            console.error('Error en detección de cámara:', error);
        }

        setTimeout(detectFrame, 500); // Detectar cada 500ms
    };

    detectFrame();
}

function captureFrame() {
    const video = document.getElementById('cameraVideo');
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);

    canvas.toBlob((blob) => {
        const file = new File([blob], 'camera-capture.jpg', { type: 'image/jpeg' });
        handleFileSelect(file);
    }, 'image/jpeg');
}

// ============================================================================
// HISTORIAL
// ============================================================================

function addToHistory(result) {
    const entry = {
        id: Date.now(),
        class: result.class,
        confidence: result.confidence,
        timestamp: new Date().toLocaleTimeString(),
        date: new Date().toLocaleDateString()
    };

    detectionHistory.unshift(entry);
    
    // Mantener máximo 50 elementos
    if (detectionHistory.length > 50) {
        detectionHistory.pop();
    }

    localStorage.setItem('detectionHistory', JSON.stringify(detectionHistory));
    displayHistory();
}

function displayHistory() {
    const historyContainer = document.getElementById('historyContainer');

    if (detectionHistory.length === 0) {
        historyContainer.innerHTML = '<p class="empty-state">📭 No hay detecciones aún</p>';
        return;
    }

    historyContainer.innerHTML = detectionHistory.map(entry => `
        <div class="history-item">
            <div class="history-item-info">
                <div class="history-item-class">${entry.class}</div>
                <div class="history-item-confidence">
                    ${entry.date} ${entry.timestamp} - ${(entry.confidence * 100).toFixed(2)}%
                </div>
            </div>
            <div class="history-item-badge">${(entry.confidence * 100).toFixed(0)}%</div>
        </div>
    `).join('');
}

function clearHistory() {
    if (confirm('¿Seguro que quieres limpiar todo el historial?')) {
        detectionHistory = [];
        localStorage.removeItem('detectionHistory');
        displayHistory();
    }
}

// ============================================================================
// INTERFAZ DE USUARIO
// ============================================================================

function switchTab(tabName) {
    // Ocultar todos los tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });

    // Mostrar tab seleccionado
    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');

    // Si es historial, actualizar
    if (tabName === 'history') {
        displayHistory();
    }
}

// Actualizar valor de confianza en tiempo real
document.getElementById('confidenceSlider').addEventListener('input', (e) => {
    document.getElementById('confidenceValue').textContent = e.target.value + '%';
});

function showLoader(show) {
    document.getElementById('loader').style.display = show ? 'flex' : 'none';
}

// ============================================================================
// INICIALIZACIÓN
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    displayHistory();
    console.log('AutoDocVision inicializado correctamente');
});

// Limpiar recursos al cerrar
window.addEventListener('beforeunload', () => {
    if (cameraStream) {
        stopCamera();
    }
});
