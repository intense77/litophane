// Variablen (von Python via -D übergeben)
image_file = ""; 
text_id = ""; 

// Konstanten
inlay_size = 42.0;
max_height = 1.5;       
base_th = 0.4; // Massive Basisplatte
scale_xy = inlay_size / 150;   

union() {
    // 1. Die Bodenplatte (Immer vorhanden)
    translate([-inlay_size/2, -inlay_size/2, 0])
    cube([inlay_size, inlay_size, base_th]);

    // 2. Das Relief (Start bei Z=0 für perfekte Verschmelzung)
    // Die surface() Funktion nutzt das von Python vorbereitete Bild
    scale([scale_xy, scale_xy, max_height / 100])
    translate([-75, -75, 0])
    surface(file = image_file, center = false, invert = true);

    // 3. User-ID Steg oben
    translate([0, inlay_size/2 - 1.55, 0]) {
        difference() {
            translate([0, 0, max_height / 2])
            cube([inlay_size - 4, 3, max_height], center = true);

            // Textgravur (0.4mm tief von der Oberkante)
            translate([0, 0, max_height - 0.4])
            linear_extrude(height = 1.1) {
                text(text_id, size=2.5, halign="center", valign="center");
            }
        }
    }
}