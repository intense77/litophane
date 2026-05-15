import os
import subprocess
import uuid
from flask import Flask, request, jsonify, send_from_directory
from PIL import Image, ImageOps, ImageFilter

# Konfiguration
app = Flask(__name__)

# Pfade absolut definieren, damit sie in Docker/Coolify sicher gefunden werden
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'outputs')
STATIC_FOLDER = os.path.join(BASE_DIR, 'static')
SCAD_FILE = os.path.join(BASE_DIR, 'litho_generator.scad')

# Notwendige Ordner beim Start erstellen
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

# 1. ROUTEN FÜR DAS FRONTEND (Verhindert 404 Fehler)
@app.route('/')
def index():
    """Liefert die index.html aus dem static-Ordner aus."""
    return send_from_directory(STATIC_FOLDER, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Liefert CSS, JS und andere Dateien aus dem static-Ordner aus."""
    return send_from_directory(STATIC_FOLDER, path)

# 2. ROUTE FÜR DIE GENERIERUNG
@app.route('/generate', methods=['POST'])
def generate():
    img_path = None
    try:
        if 'image' not in request.files:
            return jsonify({"error": "Kein Bild empfangen"}), 400
        
        file = request.files['image']
        user_id = request.form.get('id', 'ID-' + str(uuid.uuid4())[:4])
        val = request.form.get('value', 'Dia')
        
        # Eindeutige Dateinamen erzeugen
        img_filename = f"img_{uuid.uuid4().hex}.png"
        img_path = os.path.join(UPLOAD_FOLDER, img_filename)
        stl_filename = f"{user_id}_{val}.stl"
        stl_path = os.path.join(OUTPUT_FOLDER, stl_filename)

        # BILDVERARBEITUNG
        img = Image.open(file.stream)
        img = ImageOps.exif_transpose(img) # Handy-Rotation korrigieren
        img = img.convert('L') # Graustufen
        
        # Auf 150x150px bringen (passend zum OpenSCAD-Setup)
        img = ImageOps.fit(img, (150, 150), centering=(0.5, 0.2))
        img = ImageOps.flip(img) # Spiegeln für Lithophane-Durchsicht
        
        # Kontrast spreizen & leichte Glättung (hilft dem Slicer/Arachne)
        img = ImageOps.equalize(img)
        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        # MATHEMATIK: 
        # Weiß (255) -> 0.4mm (entspricht Wert 26.6 in OpenSCAD surface 0-100)
        # Schwarz (0) -> 1.5mm (entspricht Wert 100 in OpenSCAD surface 0-100)
        img = img.point(lambda p: int(100 - (p / 255.0) * 73.4))
        
        img.save(img_path)

        # OPENSCAD AUFRUF
        cmd = [
            "openscad",
            "-o", stl_path,
            "-D", f'image_file="{img_path}"',
            "-D", f'text_id="{user_id}"',
            SCAD_FILE
        ]

        # Rendering starten (Timeout 60s für komplexe Bilder)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            print(f"OpenSCAD Fehler: {result.stderr}")
            return jsonify({"error": "OpenSCAD Rendering fehlgeschlagen", "details": result.stderr}), 500

        # Erfolg: Dateinamen zurückgeben
        return jsonify({
            "id": user_id, 
            "status": "Fertig", 
            "file": stl_filename
        })

    except Exception as e:
        print(f"Server-Fehler: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        # Temporäres Bild aufräumen
        if img_path and os.path.exists(img_path):
            try:
                os.remove(img_path)
            except:
                pass

# 3. ROUTE FÜR DEN DOWNLOAD
@app.route('/outputs/<path:filename>')
def download_stl(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

# 4. ADMIN-ÜBERSICHT
@app.route('/admin')
def admin_view():
    files = sorted([f for f in os.listdir(OUTPUT_FOLDER) if f.endswith('.stl')], reverse=True)
    links = "".join([f'<li><a href="/outputs/{f}">{f}</a></li>' for f in files])
    return f"""
    <html>
        <head><title>Admin - STL Übersicht</title></head>
        <body style="font-family:sans-serif; padding:20px;">
            <h1>Generierte Inlays</h1>
            <ul>{links}</ul>
        </body>
    </html>
    """

if __name__ == '__main__':
    # Lokal zum Testen, Gunicorn übernimmt im Deployment
    app.run(host='0.0.0.0', port=5000, debug=False)