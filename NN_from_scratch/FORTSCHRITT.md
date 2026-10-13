# Arbeitsfortschritt – Neural Network from Scratch (INSY, 4AHITS)

Diese Datei wird laufend aktualisiert und zeigt, woran ich gerade arbeite.

## Stand

| Part | Inhalt | Status |
|------|--------|--------|
| 1 | Netz in Python (Neuron, Layer, NeuralNetwork, Export JSON/TXT/.h) | ✅ fertig |
| 2 | Training XOR (2-2-1) und 7-Segment-Decoder (4-16-7), Speichern/Laden | ✅ fertig |
| 3 | Vergleich mit TensorFlow/Keras | ✅ fertig |
| 4 | C-Programm, nur Forward, Gewichte aus `7seg.txt` | ✅ fertig |
| 5 | C-Programm, Gewichte aus `7seg_net.h` | ✅ fertig |
| 6 | ESP32 mit 7-Segment-Anzeige (PlatformIO) | ⬜ offen |

## Verlauf

- **29.09.2026** – Projekt angelegt, eigene Vorarbeit (Neuron, Layer, Netz mit NumPy) übernommen, Speichern/Laden als JSON eingebaut.
- **29.09.2026** – XOR-Netz (2-2-1) trainiert und gespeichert. 7-Segment-Decoder (4-16-7) trainiert, alle 10 Ziffern korrekt, Export als JSON, TXT und C-Header (.h).
- **29.09.2026** – Grafische Ausgabe der 10 vorhergesagten Ziffern mit Matplotlib.
- **30.09.2026** – Fortschrittsdatei auf GitHub angelegt.
- **13.10.2026** – XOR und 7-Segment-Decoder mit TensorFlow/Keras trainiert (gleiche Netzgröße 4-16-7 für einen fairen Vergleich). Beide Umsetzungen erreichen 100 % Genauigkeit. Der Vergleich von Endfehler und Trainingszeit ist dokumentiert.
- **13.10.2026** – Vorwärtsrechnung des 7-Segment-Netzes in C umgesetzt. Die Gewichte werden aus `7seg.txt` gelesen, und das Programm erkennt alle 10 Ziffern mit denselben Ausgabewerten wie Python.
- **13.10.2026** – C-Variante ohne Datei und ohne dynamischen Speicher erstellt. Die Gewichte stammen aus dem automatisch erzeugten Header `7seg_net.h`, der jetzt auch eine Init-Funktion enthält. Alle 10 Ziffern werden korrekt erkannt.

## Nächster Schritt

Part 6: Das Netz auf dem ESP32 ausführen. Eine über den Serial Monitor eingegebene Ziffer wird über eine 7-Segment-Anzeige ausgegeben.
