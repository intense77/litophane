// Variablen (von Python via -D übergeben)
image_file = ""; 
text_id = ""; 

// Konstanten
inlay_size = 42.0;
max_height = 1.5;       
base_th = 0.4; // Massive Basisplatte

// WICHTIG: Das Relief muss minimal kleiner sein als die 42mm Bodenplatte!
// Wir nehmen 41.8mm. Teilen sich beide Objekte die exakt selbe Außenwand,
// erzeugt OpenSCAD kaputte Geometrien, die der Slicer als "flache Platte" flickt.
scale_xy = 41.8 / 120;   

union() {
    // 1. Die echte Bodenplatte (garantiert zu 100% eine solide, löcherfreie Basis!)
    translate([-inlay_size/2, -inlay_size/2, 0])
    cube([inlay_size, inlay_size, base_th]);

    // 2. Das Relief (sitzt auf der Bodenplatte)
    // Wir starten bei Z=0.39 (0.01mm tief in der Bodenplatte versenkt, um perfekt zu verschmelzen)
    translate([0, 0, base_th - 0.01])
    // WICHTIG: Wir skalieren die Höhe nur bis 1.49mm (statt 1.50mm)!
    // Dadurch sind die höchsten Bergspitzen nicht EXAKT auf derselben Z-Höhe wie der Steg.
    // Coplanare Flächen an der Oberseite sind der Hauptgrund für den oberen Slicer-"Deckel"!
    scale([scale_xy, scale_xy, (max_height - base_th) / 100])
    translate([-60, -60, 0])
    surface(file = image_file, center = false, invert = true);

    // 3. User-ID Steg oben (startet ebenfalls massiv bei Z=0)
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