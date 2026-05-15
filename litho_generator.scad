// Variablen (von Python via -D übergeben)
image_file = ""; 
text_id = ""; 

// Konstanten
inlay_size = 42.0;
max_height = 1.5;       

// surface() mit 120px erzeugt ein Grid von 0 bis 119.
scale_xy = inlay_size / 119;   

difference() {
    // 1. Das Lithophane-Relief
    // Die Bodenplatte (0.4mm) und der Steg (1.5mm) sind bereits
    // durch Python perfekt ins Bild gebrannt! Keine kaputten unions mehr!
    scale([scale_xy, scale_xy, max_height / 100])
    translate([-59.5, -59.5, 0])
    surface(file = image_file, center = false, invert = true);

    // 2. Textgravur in den Steg
    // Der Steg befindet sich im Bereich Y=17.8 bis 21.0
    translate([0, 19.4, max_height - 0.4])
    linear_extrude(height = 1.0) {
        text(text_id, size=2.5, halign="center", valign="center");
    }
}