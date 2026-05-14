import os
import subprocess
import uuid
from flask import Flask, request, send_file, jsonify
from PIL import Image, ImageOps

app = Flask(__name__)

# Pfade definieren
UPLOAD_FOLDER = '/tmp'
SCAD_FILE = 'litho_generator.scad'

@app.route('/generate', methods=['POST'])
def generate():
    try:
        # 1. Daten aus dem Request holen
        if 'image' not in request.files:
            return "Kein Bild gefunden", 400
        
        file = request.files['image']
        text_id = request.form.get('text_id', 'ID-0000')
        
        # Eindeutiger Dateiname für diesen Durchgang
        job_id = str(uuid.uuid4())[:8]
        img_path = os.path.join(UPLOAD_FOLDER, f"img_{job_id}.png")
        stl_path = os.path.join(UPLOAD_FOLDER, f"litho_{job_id}.stl")

        # 2. Bildverarbeitung (Vorbereitung für Lithophane)
        img = Image.open(file.stream).convert('L') # In Graustufen umwandeln
        
        # Bild auf 150x150 Pixel skalieren (passend zur scale_xy in .scad)
        img = img.resize((150, 150), Image.Resampling.LANCZOS)
        
        # Kontrast optimieren (extremes Schwarz/Weiß vermeiden für bessere Druckbarkeit)
        img = img.point(lambda p: max(5, min(p, 245)))
        
        img.save(img_path)
        print(f"[{job_id}] Bild verarbeitet und gespeichert.")

        # 3. OpenSCAD Befehl ausführen
        # Wir übergeben die Variablen via -D an OpenSCAD
        cmd = [
            "openscad",
            "-o", stl_path,
            "-D", f'image_file="{img_path}"',
            "-D", f'text_id="{text_id}"',
            SCAD_FILE
        ]

        print(f"[{job_id}] Starte OpenSCAD Rendering...")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"[{job_id}] OpenSCAD Fehler:\n{result.stderr}")
            return jsonify({"error": "OpenSCAD Rendering fehlgeschlagen", "details": result.stderr}), 500

        # 4. STL Datei zurückgeben
        return send_file(stl_path, as_attachment=True, download_name=f"litho_{text_id}.stl")

    except Exception as e:
        print(f"Allgemeiner Fehler: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        # Optional: Temporäre Dateien aufräumen
        # if os.path.exists(img_path): os.remove(img_path)
        pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)