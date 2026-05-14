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
    // 1. Die Bodenplatte (0.4mm dick) [cite: 2, 6]
    translate([-inlay_size/2, -inlay_size/2, 0])
    cube([inlay_size, inlay_size, base_th]);

    // 2. Das Lithophane [cite: 7]
    // Wir lassen das Relief bei Z = 0.1 starten (0.3mm tief in der Bodenplatte versenkt)
    // Das eliminiert den Deckel-Bug in Bambu Studio komplett.
    translate([0, 0, 0.1]) 
    scale([scale_xy, scale_xy, (max_height - 0.1) / 100]) [cite: 5, 9]
    translate([-75, -75, 0]) [cite: 10]
    surface(file = image_file, center = false, invert = true); [cite: 10]

    // 3. Die User-ID [cite: 11]
    translate([0, inlay_size/2 - 1.55, 0.1]) { [cite: 12]
        difference() {
            translate([0, 0, (max_height - 0.1) / 2])
            cube([inlay_size - 4, 3, max_height - 0.1], center = true); [cite: 12]

            // Gravur
            translate([0, 0, max_height - 0.1 - 0.4]) [cite: 13]
            linear_extrude(1) {
                text(text_id, size=2.5, halign="center", valign="center"); [cite: 13]
            }
        }
    }
}