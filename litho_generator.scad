// Variablen (werden von Python via -D übergeben) [cite: 1]
image_file = ""; 
text_id = ""; 

// Lithophane Einstellungen
inlay_size = 42.0;
max_height = 1.5; [cite: 2]       
base_th = 0.4; // Die wichtige Basis-Dicke
scale_xy = inlay_size / 150;   

union() {
    // 1. Die Bodenplatte (Sorgt für Stabilität)
    translate([-inlay_size/2, -inlay_size/2, 0])
    cube([inlay_size, inlay_size, base_th]);

    // 2. Das Lithophane-Relief
    // Wir lassen es bei Z=0 starten, damit es mit der Platte verschmilzt.
    // Das verhindert Löcher und den "Deckel-Bug" in Bambu Studio.
    scale([scale_xy, scale_xy, max_height / 100]) [cite: 4]
    translate([-75, -75, 0])
    surface(file = image_file, center = false, invert = true);

    // 3. User-ID Steg [cite: 5]
    translate([0, inlay_size/2 - 1.55, 0]) {
        difference() {
            translate([0, 0, max_height / 2])
            cube([inlay_size - 4, 3, max_height], center = true);

            // Gravur an der Oberkante [cite: 6]
            translate([0, 0, max_height - 0.4])
            linear_extrude(height = 1) {
                text(text_id, size=2.5, halign="center", valign="center"); [cite: 7]
            }
        }
    }
}