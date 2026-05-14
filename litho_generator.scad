// Variablen (werden von Python via -D übergeben)
image_file = ""; 
text_id = ""; 

// Lithophane Einstellungen
inlay_size = 42.0;       
base_th = 0.4;           
max_height = 1.5;        
scale_xy = 41.8 / 150;   

union() {
    // 1. Bodenplatte (Massiv)
    translate([-inlay_size/2, -inlay_size/2, 0])
    cube([inlay_size, inlay_size, base_th]);

    // 2. Relief - WICHTIG: Start bei Z=0!
    // Wir lassen das Relief von GANZ UNTEN anfangen. 
    // Da es in einer union() mit der Platte (0.4mm) ist, 
    // verschmilzt alles, was dicker als 0.4mm ist, nach oben heraus.
    scale([scale_xy, scale_xy, max_height / 100])
    translate([-75, -75, 0])
    surface(file = image_file, center = false, invert = true);

    // 3. User-ID Steg
    // Auch den Steg lassen wir bei Z=0 starten
    translate([0, inlay_size/2 - 1.55, 0]) {
        difference() {
            translate([0, 0, max_height / 2])
            cube([inlay_size - 4, 3, max_height], center = true);

            // Gravur an der Oberkante
            translate([0, 0, max_height - 0.4])
            linear_extrude(height = 1) {
                text(text_id, size=2.5, halign="center", valign="center");
            }
        }
    }
}