from flask import Flask, request, jsonify, send_from_directory
import subprocess, os, uuid
from werkzeug.utils import secure_filename
from PIL import Image, ImageOps

# Konfiguriere Flask so, dass statische Dateien direkt aus dem 'static'-Ordner ausgeliefert werden
app = Flask(__name__, static_url_path='', static_folder='static')

# Sicherstellen, dass die Zielordner existieren
os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    # Die vom Frontend generierte ID übernehmen oder eine neue erstellen
    client_id = request.form.get('id')
    user_id = secure_filename(client_id) if client_id else f"MZ-{uuid.uuid4().hex[:4].upper()}"
    
    # Input sanitizen, um Path Traversal Attacken zu verhindern
    val = secure_filename(request.form.get('value', 'Segen'))
    
    img_path = f"uploads/{user_id}.png"
    if 'image' in request.files:
        print(f"[{user_id}] Bild empfangen, verarbeite...", flush=True)
        # Bild laden, richtig drehen, in Graustufen umwandeln und verkleinern
        img = Image.open(request.files['image'])
        img = ImageOps.exif_transpose(img)
        img = img.convert('L')
        
        # NEU: Histogramm-Ausgleich (Equalize) bringt extrem viele Details in Gesichtern zum Vorschein!
        img = ImageOps.equalize(img)
        
        # Auflösung auf 150x150 erhöhen (für mehr Details, ohne den Server zu crashen)
        # Zentrierung 0.2 behält weiterhin den Kopf bei Hochformat-Fotos
        img = ImageOps.fit(img, (150, 150), centering=(0.5, 0.2))
        # Vertikal spiegeln, da OpenSCAD das Bild sonst auf dem Kopf einliest
        img = ImageOps.flip(img)
        
        # NEU: Wir brennen die Bodenplatte (0.4mm) direkt in die Pixel ein!
        # Das verhindert den "Slicer-Deckel-Bug" (Z-Fighting) zu 100%.
        # Weiß (255) wird auf 187 abgedunkelt. Das ergibt in OpenSCAD exakt 0.4mm Höhe.
        img = img.point(lambda p: p * (187 / 255.0))
        
        img.save(img_path, format="PNG")
        print(f"[{user_id}] Bild für den 3D-Druck gespeichert.", flush=True)
    else:
        print(f"[{user_id}] FEHLER: Kein Bild hochgeladen!", flush=True)
    
    stl_path = f"outputs/{user_id}_{val}.stl"
    
    try:
        print(f"[{user_id}] Starte OpenSCAD Rendering...", flush=True)
        # OpenSCAD Aufruf für das Dia-Inlay (check=True wirft Fehler bei Fehlschlag)
        subprocess.run(["openscad", "-o", stl_path, "-D", f'image_file="{img_path}"', "-D", f'text_id="{user_id}"', "litho_generator.scad"], capture_output=True, text=True, check=True)
        print(f"[{user_id}] 3D-Modell erfolgreich generiert: {stl_path}", flush=True)
    except subprocess.CalledProcessError as e:
        print(f"[{user_id}] OpenSCAD Fehler:\n{e.stderr}", flush=True)
        return jsonify({"error": "OpenSCAD Rendering fehlgeschlagen"}), 500
    finally:
        if os.path.exists(img_path): os.remove(img_path) # Löschen nach Erfolg oder Fehler
        
    return jsonify({"id": user_id, "status": "In Schlange"})

@app.route('/outputs/<filename>')
def download_file(filename):
    return send_from_directory("outputs", filename, as_attachment=True)

@app.route('/admin', strict_slashes=False)
def admin():
    files = [f for f in os.listdir("outputs") if f.endswith('.stl')]
    links = "".join([f'<li><a href="/outputs/{f}">{f}</a></li>' for f in files])
    return f"<h1>Fertige Dia-Inlays</h1><ul>{links}</ul><p><a href='/'>Zurück zur Fotobox</a></p>"
