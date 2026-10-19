"""Trainiert XOR und prueft das gespeicherte Modell."""

from pathlib import Path

import numpy as np

from nn import NeuralNetwork


# Trainingsdaten: XOR ist 1, wenn genau einer der beiden Eingänge 1 ist.
XOR_X = [[0, 0], [0, 1], [1, 0], [1, 1]]
XOR_Y = [[0], [1], [1], [0]]
ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "models"


# Trainiert das 2-2-1-Netz, speichert es als JSON, lädt es neu und prüft, ob das
# geladene Netz dieselben Ergebnisse liefert.
def main():
    np.random.seed(42)  # fester Seed -> bei jedem Start dieselben Zufallsgewichte
    MODEL_DIR.mkdir(exist_ok=True)

    # Mit nur 2 Hidden-Neuronen kann XOR in einem lokalen Minimum hängen bleiben
    # (z. B. nur 3/4 richtig). Dann einfach mit neuen Zufallsgewichten neu starten.
    for attempt in range(1, 6):
        print(f"\nXOR Versuch {attempt}")
        network = NeuralNetwork([2, 2, 1], learning_rate=0.1)
        network.train(XOR_X, XOR_Y, epochs=20000, print_every=2000)
        # Ausgabe mit Schwelle 0,5 runden (0,97 -> 1) und mit dem Ziel vergleichen.
        correct = sum(
            np.array_equal((network.predict(x) >= 0.5).astype(int), np.array(y))
            for x, y in zip(XOR_X, XOR_Y)
        )
        print(f"Genauigkeit: {correct}/{len(XOR_X)}")
        if correct == len(XOR_X):
            # Erfolgreich -> speichern, wieder laden und das geladene Netz testen.
            # So sieht man, dass Speichern/Laden die Gewichte nicht verändert.
            json_path = MODEL_DIR / "xor.json"
            network.dump_json(json_path)
            print(f"Gespeichert: {json_path}")
            loaded = NeuralNetwork.load(json_path)
            for x, y in zip(XOR_X, XOR_Y):
                output = loaded.predict(x)[0]
                print(f"  {x} -> {output:.3f} (erwartet {y[0]})")
            return
        print("Lokales Minimum, starte mit neuen Gewichten neu.")

    raise RuntimeError("XOR wurde in fuenf Versuchen nicht korrekt gelernt.")


if __name__ == "__main__":
    main()
