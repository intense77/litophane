// 1. Variablen (werden von Python via -D übergeben)
image_file = ""; 
text_id = ""; 

// 2. Lithophane Einstellungen
inlay_size = 42.0;       // Exakt 42mm [cite: 2]
base_th = 0.4;           // Bodenplatte Dicke [cite: 2]
max_height = 1.5;        // Maximale Gesamtdicke [cite: 3]
scale_xy = 41.8 / 150;   // Skalierung für 150px Bild auf 41.8mm [cite: 5]

union() {
    // 3. Die Bodenplatte (Garantierte Basis)
    translate([-inlay_size/2, -inlay_size/2, 0])
    cube([inlay_size, inlay_size, base_th]); [cite: 6]

    // 4. Das Lithophane (Relief)
    // Wir starten bei Z=0, damit es voll in der Bodenplatte verankert ist.
    // Das verhindert den Deckel-Bug in Bambu Studio.
    scale([scale_xy, scale_xy, max_height / 100])
    translate([-75, -75, 0])
    surface(file = image_file, center = false, invert = true); [cite: 10]

    // 5. Die User-ID am oberen Rand
    translate([0, inlay_size/2 - 1.55, 0]) { [cite: 12]
        difference() {
            // Balken zur Stabilisierung und für den Text
            translate([0, 0, max_height / 2])
            cube([inlay_size - 4, 3, max_height], center = true); [cite: 12]

            // Eingravierte ID (0.4mm tief von der Oberkante)
            translate([0, 0, max_height - 0.4])
            linear_extrude(height = 1) {
                text(text_id, size=2.5, halign="center", valign="center"); [cite: 13]
            }
        }
    }
}