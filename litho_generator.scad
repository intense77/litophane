// Variablen, die von Python via Kommandozeile (-D) übergeben werden
image_file = "";
text_id = "";

// Lithophane Einstellungen - NUR DAS INLAY
inlay_size = 42.0;       // Exakt 42mm (passt mit 0.4mm Spiel in den 42.4mm Schlitz)
base_th = 0.4;           // Garantiertes Minimum (Bodenplatte)
max_height = 1.5;        // Maximale Gesamtdicke (0.4 + 1.1 = 1.5mm)

// Da Python das Bild auf 150px verkleinert: 150 * 0.28 = 42mm
scale_xy = 0.28;

union() {
    // 1. Grundboden (die absolut flache Trägerschicht für das Druckbett)
    // Von Z=0 bis base_th, exakt flach aufliegend.
    // Verhindert Löcher an den hellsten (weißen) Stellen des Bildes.
    translate([-inlay_size/2, -inlay_size/2, 0])
    cube([inlay_size, inlay_size, base_th]);

    // 2. Das eigentliche Lithophane (Bild-Relief)
    // Wir lassen das Relief direkt bei Z=0 starten und bis auf Z=1.5 wachsen!
    // Dadurch überlappt es gigantisch mit dem Boden und Bambu Studio erzeugt KEINE internen Deckel mehr.
    scale([scale_xy, scale_xy, max_height / 100])
    // center=false sorgt dafür, dass das Relief exakt bei Z=0 startet und nur nach OBEN wächst.
    // Da das Bild 150x150 px ist, zentrieren wir es manuell um die Hälfte (-75) auf X und Y.
    translate([-75, -75, 0])
    surface(file = image_file, center = false, invert = true);
    
    // 3. Die User-ID am oberen Rand (wird später vom Rahmen-Schlitz verdeckt)
    // Bei 42mm Inlay und 38mm Fenster verschwinden exakt 2mm Rand im Rahmen.
    translate([0, inlay_size/2 - 1.5, 0]) {
        difference() {
            // Massiver Block von Z=0 bis Z=1.5, der das Relief überschreibt
            translate([0, 0, max_height / 2])
            cube([inlay_size - 4, 3, max_height], center = true);
            
            // Die eingravierte ID (0.4mm tief)
            translate([0, 0, max_height - 0.4])
            linear_extrude(1) {
                text(text_id, size=2.5, halign="center", valign="center");
            }
        }
    }
}