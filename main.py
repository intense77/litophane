import os
import subprocess
import uuid
from flask import Flask, request, jsonify, send_from_directory
from PIL import Image, ImageOps, ImageFilter

# Konfiguriere Flask für statische Dateien
app = Flask(__name__, static_url_path='', static_folder='static')

# Pfade definieren
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
SCAD_FILE = 'litho_generator.scad'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        # 1. Daten aus dem Request holen
        if 'image' not in request.files:
            return "Kein Bild gefunden", 400
        
        file = request.files['image']
        # Das Javascript sendet 'id' und 'value'
        user_id = request.form.get('id', 'ID-0000')
        val = request.form.get('value', 'Segen')
        
        img_path = os.path.join(UPLOAD_FOLDER, f"img_{user_id}.png")
        stl_path = os.path.join(OUTPUT_FOLDER, f"{user_id}_{val}.stl")

        # 2. Bildverarbeitung (Vorbereitung für Lithophane)
        img = Image.open(file.stream)
        img = ImageOps.exif_transpose(img) # WICHTIG: Verhindert 90-Grad gedrehte Bilder vom Smartphone!
        img = img.convert('L') # In Graustufen umwandeln
        
        # Bild zuschneiden (damit das Gesicht bleibt) und vertikal spiegeln (für OpenSCAD)
        img = ImageOps.fit(img, (150, 150), centering=(0.5, 0.2))
        img = ImageOps.flip(img)
        
        # WICHTIG: Equalize zwingt das Bild, die maximale Höhe (1.5mm) auch wirklich auszunutzen!
        # Ohne diese Zeile ist das 3D-Relief dünner als eine Druckschicht und der Slicer radiert es weg.
        img = ImageOps.equalize(img)
        
        # NEU: Ein leichter Weichzeichner glättet die Geometrie!
        # 1 Pixel entspricht 0.28mm (kleiner als die 0.4mm Düse). Ohne Blur stottert der 
        # Drucker bei harten Kontrasten, fördert kein Plastik und erzeugt physische Löcher.
        img = img.filter(ImageFilter.GaussianBlur(radius=1))
        
        # WICHTIG: Das Relief startet nun bei Z=0. Die 0.4mm Bodenplatte "verschluckt" alles, was dünner ist.
        # Wir müssen das Bild komprimieren: Das dunkelste Schwarz (0) bleibt 0 (= 1.5mm Höhe).
        # Das hellste Weiß (255) wird auf 187 abgedunkelt. 187 ergibt in OpenSCAD exakt 0.4mm Höhe!
        # Das "int()" ist extrem wichtig, damit keine Kommazahlen (Floats) Löcher im 3D-Modell verursachen.
        img = img.point(lambda p: int((p / 255.0) * 187))
        
        img.save(img_path)
        print(f"[{user_id}] Bild verarbeitet und gespeichert.", flush=True)

        # 3. OpenSCAD Befehl ausführen
        # Wir übergeben die Variablen via -D an OpenSCAD
        cmd = [
            "openscad",
            "-o", stl_path,
            "-D", f'image_file="{img_path}"',
            "-D", f'text_id="{user_id}"',
            SCAD_FILE
        ]

        print(f"[{user_id}] Starte OpenSCAD Rendering...", flush=True)
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"[{user_id}] OpenSCAD Fehler:\n{result.stderr}", flush=True)
            return jsonify({"error": "OpenSCAD Rendering fehlgeschlagen", "details": result.stderr}), 500

        # 4. JSON Antwort an das Smartphone senden (NICHT direkt die Datei!)
        return jsonify({"id": user_id, "status": "In Schlange"})

    except Exception as e:
        print(f"Allgemeiner Fehler: {str(e)}", flush=True)
        return jsonify({"error": str(e)}), 500
    finally:
        # Optional: Temporäre Dateien aufräumen
        if os.path.exists(img_path): os.remove(img_path)

# Admin-Route, um die STLs später gesammelt herunterzuladen
@app.route('/outputs/<filename>')
def download_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

@app.route('/admin', strict_slashes=False)
def admin():
    files = [f for f in os.listdir(OUTPUT_FOLDER) if f.endswith('.stl')]
    links = "".join([f'<li><a href="/outputs/{f}">{f}</a></li>' for f in files])
    return f"<h1>Fertige Dia-Inlays</h1><ul>{links}</ul><p><a href='/'>Zurück zur Fotobox</a></p>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)