// Variablen, die von Python via Kommandozeile (-D) übergeben werden
image_file = "";
text_id = "";

// Hier kommt dein eigentlicher Code für das Dia-Inlay hin!
// Als Platzhalter generieren wir hier nur einen einfachen Block mit der ID.

union() {
    cube([50, 50, 2], center=true);
    translate([-15, 0, 1]) linear_extrude(2) text(text_id, size=5);
}