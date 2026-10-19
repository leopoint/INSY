"""Trainiert einen 4-16-7-Decoder fuer eine 7-Segment-Anzeige."""

from pathlib import Path

import numpy as np

from nn import NeuralNetwork


# Trainingsdaten: Eingabe = Ziffer als 4 Bits (BCD), Ziel = welche Segmente a..g leuchten.
# Beispiel Ziffer 1 = [0,0,0,1] -> nur b und c an -> [0,1,1,0,0,0,0].
DIGITS = list(range(10))
INPUTS = [
    [0, 0, 0, 0],
    [0, 0, 0, 1],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 1, 0, 0],
    [0, 1, 0, 1],
    [0, 1, 1, 0],
    [0, 1, 1, 1],
    [1, 0, 0, 0],
    [1, 0, 0, 1],
]
TARGETS = [
    [1, 1, 1, 1, 1, 1, 0],
    [0, 1, 1, 0, 0, 0, 0],
    [1, 1, 0, 1, 1, 0, 1],
    [1, 1, 1, 1, 0, 0, 1],
    [0, 1, 1, 0, 0, 1, 1],
    [1, 0, 1, 1, 0, 1, 1],
    [1, 0, 1, 1, 1, 1, 1],
    [1, 1, 1, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 0, 1, 1],
]
ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "models"


def render_digit(segments):
    """Zeigt die sieben Segmentwerte als ASCII-Ziffer an."""
    a, b, c, d, e, f, g = segments
    on = lambda value: "---" if value else "   "
    side = lambda value: "|" if value else " "
    return "\n".join(
        [
            f" {on(a)} ",
            f"{side(f)}   {side(b)}",
            f" {on(g)} ",
            f"{side(e)}   {side(c)}",
            f" {on(d)} ",
        ]
    )


# Ablauf: trainieren -> in drei Formaten speichern -> JSON neu laden -> alle Ziffern testen.
def main():
    np.random.seed(7)  # fester Seed -> reproduzierbares Ergebnis
    MODEL_DIR.mkdir(exist_ok=True)

    # 1. Training: 4 Eingänge, 16 Hidden-Neuronen, 7 Ausgänge (ein Ausgang pro Segment).
    network = NeuralNetwork([4, 16, 7], learning_rate=0.1)
    network.train(INPUTS, TARGETS, epochs=20000, print_every=1000)

    # 2. Speichern: JSON für Python, TXT für das C-Programm (Part 4),
    #    .h-Header für C ohne Dateisystem bzw. den ESP32 (Part 5/6).
    json_path = MODEL_DIR / "7seg.json"
    txt_path = MODEL_DIR / "7seg.txt"
    header_path = MODEL_DIR / "7seg_net.h"
    network.dump_json(json_path)
    network.dump_txt(txt_path)
    network.dump_initfile(header_path, model_name="7seg_net")

    # 3. Test mit dem NEU GELADENEN Netz: jede Ziffer vorhersagen, mit 0,5 runden,
    #    mit der Tabelle vergleichen und als ASCII-Bild zeigen.
    loaded = NeuralNetwork.load(json_path)
    correct_segments = 0
    print("\nTestergebnisse des geladenen 7-Segment-Modells:")
    for digit, inputs, target in zip(DIGITS, INPUTS, TARGETS):
        output = loaded.predict(inputs)
        rounded = (output >= 0.5).astype(int).tolist()
        correct = rounded == target
        correct_segments += sum(a == b for a, b in zip(rounded, target))
        print(f"\nZiffer {digit}: {'OK' if correct else 'FALSCH'}")
        print(f"  Ausgabe: {rounded}")
        print(render_digit(rounded))

    total = len(DIGITS) * 7
    print(f"\nSegment-Genauigkeit: {correct_segments}/{total}")
    print(f"Gespeichert: {json_path}, {txt_path}, {header_path}")


if __name__ == "__main__":
    main()
