from flask import Flask, request, jsonify
import subprocess, os, uuid
from werkzeug.utils import secure_filename

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
        request.files['image'].save(img_path)
    
    stl_path = f"outputs/{user_id}_{val}.stl"
    
    try:
        # OpenSCAD Aufruf für das Dia-Inlay (check=True wirft Fehler bei Fehlschlag)
        subprocess.run(["openscad", "-o", stl_path, "-D", f'image_file="{img_path}"', "-D", f'text_id="{user_id}"', "litho_generator.scad"], check=True)
    finally:
        if os.path.exists(img_path): os.remove(img_path) # Löschen nach Erfolg oder Fehler
        
    return jsonify({"id": user_id, "status": "In Schlange"})
