image_file = "input.png"; 
text_id = "MZ-XXXX"; 
size_x = 42; size_y = 45; // Dia-Maße

union() {
    translate([2, 5, 0]) scale([38/100, 38/100, 1])
    surface(file = image_file, center = false, convexity = 5);
    difference() {
        cube([size_x, 5, 1.2]);
        translate([size_x/2, 1.5, 0.4])
        linear_extrude(1) text(text_id, size=2, halign="center"); // ID im Fenster[cite: 2]
    }
}
