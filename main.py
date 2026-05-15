import os
import subprocess
import uuid
from flask import Flask, request, jsonify, send_from_directory
from PIL import Image, ImageOps, ImageFilter

app = Flask(__name__)

# Absolute Pfade für die Docker-Umgebung
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'outputs')
STATIC_FOLDER = os.path.join(BASE_DIR, 'static')
SCAD_FILE = os.path.join(BASE_DIR, 'litho_generator.scad')

# Verzeichnisse sicherstellen
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return send_from_directory(STATIC_FOLDER, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(STATIC_FOLDER, path)

@app.route('/generate', methods=['POST'])
def generate():
    img_path = None
    try:
        if 'image' not in request.files:
            return jsonify({"error": "Kein Bild"}), 400
        
        file = request.files['image']
        user_id = request.form.get('id', 'ID-' + str(uuid.uuid4())[:4])
        val = request.form.get('value', 'Dia')
        
        # Eindeutige Namen
        img_filename = f"img_{uuid.uuid4().hex}.png"
        img_path = os.path.join(UPLOAD_FOLDER, img_filename)
        stl_filename = f"{user_id}_{val}.stl"
        stl_path = os.path.join(OUTPUT_FOLDER, stl_filename)

        # 1. Bildverarbeitung
        img = Image.open(file.stream)
        img = ImageOps.exif_transpose(img)
        img = img.convert('L')
        img = ImageOps.fit(img, (150, 150), centering=(0.5, 0.2))
        img = ImageOps.flip(img)
        img = ImageOps.equalize(img)
        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        # Mapping: Sicherstellen, dass das Relief DEUTLICH über die 0.4mm Platte ragt
        # Werte zwischen 35 (ca. 0.52mm) und 100 (1.5mm)
        img = img.point(lambda p: int(100 - (p / 255.0) * 65))
        img.save(img_path)

        # 2. OpenSCAD Aufruf mit absoluten Pfaden
        # Wir erzwingen absolute Pfade, damit surface() das Bild sicher findet
        abs_img_path = os.path.abspath(img_path)
        
        cmd = [
            "openscad", "-o", stl_path,
            "-D", f'image_file="{abs_img_path}"',
            "-D", f'text_id="{user_id}"',
            SCAD_FILE
        ]

        # Rendering
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            print(f"OpenSCAD Error: {result.stderr}")
            return jsonify({"error": "Rendering failed", "details": result.stderr}), 500

        return jsonify({"id": user_id, "status": "Fertig", "file": stl_filename})

    except Exception as e:
        print(f"Python Error: {str(e)}")
        return jsonify({"error": str(e)}), 500
    # Finally-Block: Wir löschen das Bild vorerst NICHT, um Fehler auszuschließen
    finally:
        pass

@app.route('/outputs/<path:filename>')
def download(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

@app.route('/admin')
def admin():
    files = sorted([f for f in os.listdir(OUTPUT_FOLDER) if f.endswith('.stl')], reverse=True)
    links = "".join([f'<li><a href="/outputs/{f}">{f}</a></li>' for f in files])
    return f"<h1>STL Downloads</h1><ul>{links}</ul>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)