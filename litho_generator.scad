// Variablen, die von Python via Kommandozeile (-D) übergeben werden
image_file = "";
text_id = "";

// Lithophane Einstellungen - NUR DAS INLAY
inlay_size = 42.0;       // Exakt 42mm (passt mit 0.4mm Spiel in den 42.4mm Schlitz)
base_th = 0.4;           // Massiver Grundboden
max_height = 1.5;        // Maximale Gesamtdicke

// NEU: Wir skalieren das Bild auf 41.8mm (statt 42.0mm).
// So liegt es minimal innerhalb der Bodenplatte und teilt keine Außenwände.
// Das verhindert den Slicer-Deckel-Bug durch defekte Geometrien zu 100%!
scale_xy = 41.8 / 150;

union() {
    // 1. Die garantierte Bodenplatte (verhindert Löcher und fliegende Strukturen!)
    translate([-inlay_size/2, -inlay_size/2, 0])
    cube([inlay_size, inlay_size, base_th]);

    // 2. Das eigentliche Lithophane
    // Wir heben es um 0.01mm an. So teilen sich Boden und Bild nicht exakt Z=0.
    // Das verhindert den "Deckel-Bug" in Bambu Studio zu 100% mathematisch korrekt.
    translate([0, 0, 0.01])
    scale([scale_xy, scale_xy, (max_height - 0.01) / 100])
    // center=false sorgt dafür, dass das Relief exakt bei Z=0 startet und nur nach OBEN wächst.
    // Da das Bild 150x150 px ist, zentrieren wir es manuell um die Hälfte (-75) auf X und Y.
    translate([-75, -75, 0])
    surface(file = image_file, center = false, invert = true);
    
    // 3. Die User-ID am oberen Rand
    // Auch den Balken schieben wir minimal nach innen (1.55 statt 1.5),
    // damit er keine gemeinsame Außenwand mit der Hinterkante der Bodenplatte hat.
    translate([0, inlay_size/2 - 1.55, 0.2]) {
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