// Variablen, die von Python via Kommandozeile (-D) übergeben werden
image_file = "";
text_id = "";

// Lithophane Einstellungen - NUR DAS INLAY
inlay_size = 42.0;       // Exakt 42mm (passt mit 0.4mm Spiel in den 42.4mm Schlitz)
base_th = 0.4;           // Reduziert auf 0.4mm, um mehr Tiefe fürs Bild zu gewinnen
thickness = 1.1;         // Reliefhöhe auf 1.1mm erhöht für stärkere Kontraste! (0.4 + 1.1 = 1.5mm)

// Da Python das Bild auf 150px verkleinert: 150 * 0.28 = 42mm
scale_xy = 0.28;

union() {
    // 1. Grundboden (die absolut flache Trägerschicht für das Druckbett)
    // Von Z=0 bis base_th, exakt flach aufliegend
    translate([-inlay_size/2, -inlay_size/2, 0])
    cube([inlay_size, inlay_size, base_th]);

    // 2. Das eigentliche Lithophane (Bild-Relief)
    translate([0, 0, base_th]) 
    // WICHTIG: surface() generiert Höhen bis 100. Daher: thickness / 100
    scale([scale_xy, scale_xy, thickness / 100])
    // center=false sorgt dafür, dass das Relief exakt bei Z=0 startet und nur nach OBEN wächst.
    // Da das Bild 150x150 px ist, zentrieren wir es manuell um die Hälfte (-75) auf X und Y.
    translate([-75, -75, 0])
    surface(file = image_file, center = false, invert = true);
    
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