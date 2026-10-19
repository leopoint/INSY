# Neural Network from Scratch (INSY, 4AHITS)

Ein neuronales Netz, das ohne KI-Bibliothek in Python selbst programmiert, trainiert und anschließend in C nachgebaut wurde. Es lernt XOR und einen 7-Segment-Decoder (Ziffer 0–9 als 4 Bit → Segmente a–g).

- **Visualisierung (im Browser, ohne Installation):** https://leopoint.github.io/INSY/NN_from_scratch/gui/
- **Ausführliche Beschreibung:** [ARBEITSBERICHT.md](ARBEITSBERICHT.md)
- **Status aller Parts und KI-Nutzung:** [FORTSCHRITT.md](FORTSCHRITT.md)

## Inhalt

| Ordner | Part | Inhalt |
|---|---|---|
| [`part1_2_python/`](part1_2_python/) | 1, 2 | `nn.py` (Neuron, Layer, NeuralNetwork, Export JSON/TXT/.h), `train_xor.py`, `train_7seg.py` |
| [`models/`](models/) | 2 | trainierte Netze: `xor.json`, `7seg.json`, `7seg.txt`, `7seg_net.h` |
| [`part3_tensorflow/`](part3_tensorflow/) | 3 | dieselben Netze mit TensorFlow/Keras, [`vergleich.md`](part3_tensorflow/vergleich.md) |
| [`part4_c_txt/`](part4_c_txt/) | 4 | C-Programm, nur Vorwärtsrechnung, Gewichte aus `7seg.txt` |
| [`part5_c_header/`](part5_c_header/) | 5 | C-Programm, Gewichte aus `7seg_net.h`, ohne Datei und ohne `malloc` |
| [`gui/`](gui/) | Zusatz | Weboberfläche zum Starten aller Programme und zum Ansehen des Netzes |

Part 6 (ESP32 mit 7-Segment-Anzeige) wurde nicht umgesetzt.

## Visualisierung

Die Online-Version zeigt im Reiter „Netz ansehen“, wie eine Eingabe Schicht für Schicht durch das trainierte Netz läuft. Gerechnet wird dabei live im Browser mit den gespeicherten Gewichten. In den anderen Reitern werden die Trainings- und C-Programme als Aufzeichnung eines echten Laufs abgespielt, mit Ausgabe und Lernkurve.

Lokal lassen sich alle Programme auch wirklich starten: `gui/start_gui.bat` ausführen oder `python gui/server.py`, danach öffnet sich `http://localhost:8000`.

## Selbst ausführen

Voraussetzungen: Python 3.12 mit NumPy, für Part 3 zusätzlich TensorFlow, für Part 4/5 gcc.

```
cd part1_2_python
python train_xor.py
python train_7seg.py

cd ../part3_tensorflow
python tf_xor.py
python tf_7seg.py

cd ../part4_c_txt
gcc -Wall -O2 -o nn_txt main.c nn.c -lm
./nn_txt

cd ../part5_c_header
gcc -Wall -O2 -o nn_header main.c nn.c -lm
./nn_header
```

Alle Skripte verwenden einen festen Zufalls-Seed, die Ergebnisse sind also bei jedem Lauf gleich.
