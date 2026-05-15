import os
import subprocess
import uuid
from flask import Flask, request, jsonify, send_from_directory
from PIL import Image, ImageOps, ImageFilter

app = Flask(__name__)

# Absolute Pfade für Coolify/Docker Umgebungen
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'outputs')
SCAD_FILE = os.path.join(BASE_DIR, 'litho_generator.scad')

# Verzeichnisse beim Start erstellen
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/generate', methods=['POST'])
def generate():
    img_path = None
    try:
        if 'image' not in request.files:
            return jsonify({"error": "Kein Bild empfangen"}), 400
        
        file = request.files['image']
        user_id = request.form.get('id', 'ID-' + str(uuid.uuid4())[:4])
        val = request.form.get('value', 'Dia')
        
        img_path = os.path.join(UPLOAD_FOLDER, f"img_{uuid.uuid4().hex}.png")
        stl_filename = f"{user_id}_{val}.stl"
        stl_path = os.path.join(OUTPUT_FOLDER, stl_filename)

        # Bildverarbeitung
        img = Image.open(file.stream)
        img = ImageOps.exif_transpose(img)
        img = img.convert('L')
        img = ImageOps.fit(img, (150, 150), centering=(0.5, 0.2))
        img = ImageOps.flip(img)
        
        # Kontrast optimieren
        img = ImageOps.equalize(img)
        
        # Leichte Glättung für bessere Druckbarkeit (Arachne-freundlich)
        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        # Mapping: Weiß (255) soll 0.4mm (Boden) ergeben, Schwarz (0) 1.5mm (Max)
        # In OpenSCAD surface() entspricht 100 = max_height
        img = img.point(lambda p: int(100 - (p / 255.0) * 73.3))
        img.save(img_path)

        # OpenSCAD Befehl
        cmd = [
            "openscad",
            "-o", stl_path,
            "-D", f'image_file="{img_path}"',
            "-D", f'text_id="{user_id}"',
            SCAD_FILE
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            return jsonify({"error": "Rendering-Fehler", "details": result.stderr}), 500

        return jsonify({"id": user_id, "status": "Fertig", "file": stl_filename})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Bild erst nach dem Rendering löschen
        if img_path and os.path.exists(img_path):
            try:
                os.remove(img_path)
            except:
                pass

@app.route('/outputs/<path:filename>')
def download(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)