// Variablen, die von Python via Kommandozeile (-D) übergeben werden
image_file = "";
text_id = "";

// Lithophane Einstellungen
max_width = 40;  // Breite des Bildes in mm
thickness = 2.5; // Maximale Dicke des Reliefs (schwarze Stellen)
base_th = 0.5;   // Grunddicke, damit weiße Stellen keine Löcher werden

// Da Python das Bild auf max 100px verkleinert: 100 * 0.40 = 40mm
scale_xy = 0.40;

union() {
    // 1. Das eigentliche Lithophane
    // invert=true macht dunkle Pixel dick (lichtundurchlässig) und helle dünn
    translate([0, 0, base_th]) 
    // WICHTIG: surface() generiert Höhen bis 100. Daher: thickness / 100
    scale([scale_xy, scale_xy, thickness / 100]) {
        surface(file = image_file, center = true, invert = true);
    }
    
    // 2. Grundboden (die Trägerschicht)
    translate([0, 0, base_th / 2])
    cube([max_width, max_width, base_th], center = true);

    // 3. Äußerer Dia-Rahmen (z.B. 50x50 mm)
    translate([0, 0, (base_th + thickness) / 2])
    difference() {
        cube([50, 50, base_th + thickness], center = true);
        cube([max_width, max_width, base_th + thickness + 1], center = true);
    }

    // 4. Die User-ID auf den Rahmen prägen
    translate([0, -22, base_th + thickness - 0.5]) {
        linear_extrude(1) {
            text(text_id, size=4, halign="center", valign="center");
        }
    }
}