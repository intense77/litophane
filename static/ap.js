// Konfiguration & ID-Generierung
const userId = "MZ-" + Math.random().toString(36).substr(2, 4).toUpperCase();
let queuePosition = 0;

// Three.js Vorschau-Logik (Minimal-Setup)
function init3DPreview(imageSrc) {
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, 1, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(300, 300);
    document.getElementById('preview-container').innerHTML = '';
    document.getElementById('preview-container').appendChild(renderer.domElement);

    // Das "Dia"-Inlay simulieren
    const geometry = new THREE.PlaneGeometry(3.8, 3.8, 64, 64);
    const texture = new THREE.TextureLoader().load(imageSrc);
    const material = new THREE.MeshStandardMaterial({ 
        map: texture, 
        displacementMap: texture, 
        displacementScale: 0.5 
    });
    
    const mesh = new THREE.Mesh(geometry, material);
    scene.add(mesh);
    scene.add(new THREE.AmbientLight(0xffffff, 1));
    camera.position.z = 5;

    function animate() {
        requestAnimationFrame(animate);
        mesh.rotation.y += 0.01;
        renderer.render(scene, camera);
    }
    animate();
}

// Upload & Datensparsamkeit
async function uploadPhoto(blob, imageSrc) {
    const formData = new FormData();
    formData.append('image', blob);
    formData.append('id', userId);
    formData.append('value', document.getElementById('value-select').value);

    try {
        const response = await fetch('/generate', { method: 'POST', body: formData });
        
        if (!response.ok) {
            throw new Error(`Server meldet Fehlercode ${response.status}`);
        }
        
        const result = await response.json();
        
        // UI Update: HTML-Status anzeigen und anpassen
        document.getElementById('status-display').classList.remove('hidden');
        document.getElementById('user-id-display').innerText = result.id;
        document.getElementById('queue-info').innerText = 'Dein Dia ist in Arbeit und wird bald gedruckt!';
        if (typeof updateQueueTime === 'function') updateQueueTime();
        
    } catch (error) {
        console.error("Upload-Fehler:", error);
        alert("Es gab ein Problem beim Generieren des Dias. Überprüfe die Server-Logs in Coolify!");
    } finally {
        // Button nach Erfolg oder Fehler wieder zurücksetzen
        const uploadBtn = document.getElementById('upload-btn');
        uploadBtn.innerText = "An Drucker senden";
        uploadBtn.disabled = false;

        // Lokale Daten "vergessen" (Browser-Cache)
        if (imageSrc) URL.revokeObjectURL(imageSrc); 
    }
}

// --- Event Listeners für Smartphone Workflow ---
let currentBlob = null;
let currentImageSrc = null;

document.addEventListener('DOMContentLoaded', () => {
    const photoInput = document.getElementById('photo-input');
    const uploadBtn = document.getElementById('upload-btn');
    
    // Sobald die Kamera ein Foto liefert
    photoInput.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            currentBlob = file;
            if (currentImageSrc) URL.revokeObjectURL(currentImageSrc);
            currentImageSrc = URL.createObjectURL(file);
            
            // 3D Vorschau aktualisieren und Senden-Button aktivieren
            init3DPreview(currentImageSrc);
            uploadBtn.disabled = false;
        }
    });
    
    // Upload Button Klick-Logik
    uploadBtn.addEventListener('click', () => {
        if (currentBlob) {
            uploadBtn.disabled = true; // Verhindert Doppel-Uploads durch nervöses Klicken
            uploadBtn.innerText = "Wird hochgeladen...";
            uploadPhoto(currentBlob, currentImageSrc);
        }
    });
});
