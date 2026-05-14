// Variablen (werden von Python via -D übergeben)
image_file = ""; 
text_id = ""; 

// Lithophane Einstellungen
inlay_size = 42.0;       
base_th = 0.4;           
max_height = 1.5;        
scale_xy = 41.8 / 150;   

union() {
    // 1. Bodenplatte (Massiv von Z=0 bis Z=0.4)
    translate([-inlay_size/2, -inlay_size/2, 0])
    cube([inlay_size, inlay_size, base_th]);

    // 2. Relief (Gepackt AUF die Bodenplatte)
    // Wir starten bei Z=0.39. So ist das Relief nicht mehr im Boden versenkt.
    translate([0, 0, base_th - 0.01])
    scale([scale_xy, scale_xy, (max_height - base_th + 0.01) / 100])
    translate([-75, -75, 0])
    surface(file = image_file, center = false, invert = true);

    // 3. User-ID Steg (Ebenfalls auf die Bodenplatte gesetzt)
    translate([0, inlay_size/2 - 1.55, base_th - 0.01]) {
        difference() {
            // Der Steg geht jetzt von Z=0.39 bis Z=1.5
            translate([0, 0, (max_height - base_th + 0.01) / 2])
            cube([inlay_size - 4, 3, max_height - base_th + 0.01], center = true);

            // Die Schriftgravur (0.4mm tief)
            translate([0, 0, (max_height - base_th + 0.01) - 0.4])
            linear_extrude(height = 1) {
                text(text_id, size=2.5, halign="center", valign="center");
            }
        }
    }
}