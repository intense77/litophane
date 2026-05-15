import os
import subprocess
import uuid
from flask import Flask, request, jsonify, send_from_directory
from PIL import Image, ImageOps, ImageFilter

app = Flask(__name__)

# Absolute Pfade für die Docker-Umgebung (Coolify)
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
        
        # Eindeutige Namen generieren
        img_filename = f"img_{uuid.uuid4().hex}.png"
        img_path = os.path.join(UPLOAD_FOLDER, img_filename)
        stl_filename = f"{user_id}_{val}.stl"
        stl_path = os.path.join(OUTPUT_FOLDER, stl_filename)

        # 1. Bildverarbeitung (Vorbereitung für Lithophane)
        img = Image.open(file.stream)
        img = ImageOps.exif_transpose(img) # Handy-Rotation korrigieren
        img = img.convert('L') # Graustufen
        img = ImageOps.fit(img, (120, 120), centering=(0.5, 0.2)) # RAM sparen, aber detailreich bleiben!
        img = ImageOps.flip(img) # Spiegeln für OpenSCAD
        img = ImageOps.equalize(img) # Kontrast-Spreizung
        img = img.filter(ImageFilter.GaussianBlur(radius=0.5)) # Glättung
        
        # Werte leicht kappen (1 bis 254), um absolut extreme Spitzen (0 und 100 in OpenSCAD) 
        # zu vermeiden. Das schützt vor kaputten Geometrien an den Rändern.
        img = img.point(lambda p: max(1, min(p, 254)))
        
        # WICHTIG: Die Bodenplatte wird jetzt in OpenSCAD als echter massiver Block (Cube) erzeugt!
        # Das Bild nutzt den vollen Kontrast (0=Schwarz, 255=Weiß).
        # Weiß (255) wird in OpenSCAD zu 0mm Höhe, was unsichtbar in der Bodenplatte versinkt.
        # Schwarz (0) wird in OpenSCAD zu 1.11mm Höhe, was perfekt aus der Platte herausragt.
        # Keine künstliche Begrenzung mehr nötig -> Keine Löcher!
        
        img.save(img_path)

        # 2. OpenSCAD Aufruf mit ABSOLUTEN Pfaden
        # Das ist entscheidend, damit surface() die Datei findet.
        abs_img_path = os.path.abspath(img_path)
        abs_scad_path = os.path.abspath(SCAD_FILE)
        abs_stl_path = os.path.abspath(stl_path)
        
        cmd = [
            "openscad", "-o", abs_stl_path,
            "-D", f'image_file="{abs_img_path}"',
            "-D", f'text_id="{user_id}"',
            abs_scad_path
        ]

        # Rendering starten (Timeout 60s)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            print(f"OpenSCAD Error: {result.stderr}", flush=True)
            return jsonify({"error": "Rendering failed", "details": result.stderr}), 500

        print(f"Erfolgreich generiert: {stl_filename}", flush=True)
        return jsonify({"id": user_id, "status": "Fertig", "file": stl_filename})

    except Exception as e:
        print(f"Python Error: {str(e)}", flush=True)
        return jsonify({"error": str(e)}), 500
    finally:
        # Speicherplatz auf dem Netcup Server freigeben!
        if img_path and os.path.exists(img_path): os.remove(img_path)

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