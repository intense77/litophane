// Variablen, die von Python via Kommandozeile (-D) übergeben werden
image_file = "";
text_id = "";

// Lithophane Einstellungen - NUR DAS INLAY
inlay_size = 42.0;       // Exakt 42mm (passt mit 0.4mm Spiel in den 42.4mm Schlitz)
max_height = 1.5;        // Maximale Gesamtdicke

// Da Python das Bild auf 150px verkleinert: 150 * 0.28 = 42mm
scale_xy = 0.28;

union() {
    // 1. Das eigentliche Lithophane
    // Die Bodenplatte (0.4mm) ist jetzt durch Python unsichtbar ins Bild "eingebrannt".
    // Dadurch ist das Dia EIN perfekter, solider Block ohne Slicer-Fehler!
    scale([scale_xy, scale_xy, max_height / 100])
    // center=false sorgt dafür, dass das Relief exakt bei Z=0 startet und nur nach OBEN wächst.
    // Da das Bild 150x150 px ist, zentrieren wir es manuell um die Hälfte (-75) auf X und Y.
    translate([-75, -75, 0])
    surface(file = image_file, center = false, invert = true);
    
    // 2. Die User-ID am oberen Rand
    // Wir starten bei Z=0.2mm (sicher im 0.4mm dicken Boden versenkt),
    // um coplanare Böden (Z-Fighting) komplett zu verhindern.
    translate([0, inlay_size/2 - 1.5, 0.2]) {
        difference() {
            // Flacher Balken, der das unebene Bild-Relief am Rand überschreibt
            translate([0, 0, (max_height - 0.2) / 2])
            cube([inlay_size - 4, 3, max_height - 0.2], center = true);
            
            // Die eingravierte ID (0.4mm tief von der Oberfläche)
            translate([0, 0, max_height - 0.2 - 0.4])
            linear_extrude(1) {
                text(text_id, size=2.5, halign="center", valign="center");
            }
        }
    }
}