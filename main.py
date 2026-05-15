# ... (Vorheriger Code bleibt gleich)

@app.route('/generate', methods=['POST'])
def generate():
    img_path = None # Wichtig für den finally Block
    try:
        # ... (Request Handling bleibt gleich)
        
        file = request.files['image']
        user_id = request.form.get('id', 'ID-0000')
        val = request.form.get('value', 'Segen')
        
        # Absolute Pfade nutzen (sicherer in Docker/Coolify)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(base_dir, UPLOAD_FOLDER, f"img_{uuid.uuid4().hex}.png")
        stl_path = os.path.join(base_dir, OUTPUT_FOLDER, f"{user_id}_{val}.stl")

        # 2. Bildverarbeitung
        img = Image.open(file.stream)
        img = ImageOps.exif_transpose(img)
        img = img.convert('L')
        img = ImageOps.fit(img, (150, 150), centering=(0.5, 0.2))
        img = ImageOps.flip(img)
        
        # Kontrast-Spreizung
        img = ImageOps.equalize(img)
        
        # Glättung gegen "Zappeln" der Düse
        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        # MATHEMATIK-FIX:
        # OpenSCAD skaliert 0-100 auf 0-1.5mm (max_height).
        # Wir wollen: Weiß (255) = 0.4mm (Bodenplatte) -> Wert 26.6
        # Schwarz (0) = 1.5mm (Maximum) -> Wert 100
        img = img.point(lambda p: int(100 - (p / 255.0) * 73.4))
        
        img.save(img_path)

        # 3. OpenSCAD Befehl
        cmd = [
            "openscad",
            "-o", stl_path,
            "-D", f'image_file="{img_path}"',
            "-D", f'text_id="{user_id}"',
            os.path.join(base_dir, SCAD_FILE)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            return jsonify({"error": "OpenSCAD Fehler", "details": result.stderr}), 500

        return jsonify({"id": user_id, "status": "Fertig", "file": f"{user_id}_{val}.stl"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Erst löschen, wenn wir sicher sind
        if img_path and os.path.exists(img_path):
            try:
                os.remove(img_path)
            except:
                pass