// Variablen, die von Python via Kommandozeile (-D) übergeben werden
image_file = "";
text_id = "";

// Lithophane Einstellungen - NUR DAS INLAY
inlay_size = 42.0;       // Exakt 42mm (passt mit 0.4mm Spiel in den 42.4mm Schlitz)
base_th = 0.6;           // Flache Trägerschicht für gute Druckbetthaftung
thickness = 0.9;         // Reliefhöhe (0.6 + 0.9 = 1.5mm Gesamtdicke. Passt in den 1.6mm Schlitz!)

// Da Python das Bild auf max 100px verkleinert: 100 * 0.42 = 42mm
scale_xy = 0.42;

union() {
    // 1. Grundboden (die absolut flache Trägerschicht für das Druckbett)
    translate([0, 0, base_th / 2])
    cube([inlay_size, inlay_size, base_th], center = true);

    // 2. Das eigentliche Lithophane (Bild-Relief)
    translate([0, 0, base_th]) 
    // WICHTIG: surface() generiert Höhen bis 100. Daher: thickness / 100
    scale([scale_xy, scale_xy, thickness / 100]) {
        surface(file = image_file, center = true, invert = true);
    }
    
    // 3. Die User-ID am oberen Rand (wird später vom Rahmen-Schlitz verdeckt)
    // Bei 42mm Inlay und 38mm Fenster verschwinden exakt 2mm Rand im Rahmen.
    translate([0, inlay_size/2 - 1.5, base_th]) {
        difference() {
            // Flacher Balken, der das unebene Bild-Relief am Rand überschreibt
            translate([0, 0, thickness / 2])
            cube([inlay_size - 4, 3, thickness], center = true);
            
            // Die eingravierte ID (0.4mm tief)
            translate([0, 0, thickness - 0.4])
            linear_extrude(1) {
                text(text_id, size=2.5, halign="center", valign="center");
            }
        }
    }
}