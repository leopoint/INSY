# Arbeitsbericht – Neural Network from Scratch

**Fach:** INSY, 4AHITS · **Zeitraum:** 29.09.2026 – 19.10.2026 · **Stand:** 19.10.2026 (abgeschlossen)

Dieser Bericht beschreibt, was im Projekt umgesetzt wurde, wie die einzelnen Teile funktionieren und welche Ergebnisse erzielt wurden. Den kurzen Status aller Parts zeigt die Datei [`FORTSCHRITT.md`](FORTSCHRITT.md). Die Visualisierung ist online unter https://leopoint.github.io/INSY/NN_from_scratch/gui/ erreichbar.

---

## 1. Ziel und Gesamtablauf

Ziel der Übung ist ein neuronales Netz, das ohne fertige KI-Bibliothek selbst programmiert und anschließend in C nachgebaut wird. Das Netz lernt, eine Ziffer von 0 bis 9 (als 4 Bit) in die sieben Segmente a–g einer 7-Segment-Anzeige zu übersetzen. Die Angabe sieht als letzten Teil die Ansteuerung einer echten Anzeige mit einem ESP32-Mikrocontroller vor; dieser Teil (Part 6) wurde nicht umgesetzt. Das Projekt endet mit der C-Variante aus Part 5.

Das Projekt ist in zwei Phasen geteilt:

- **Training am PC (Python).** Das Lernen braucht viele tausend Wiederholungen und ist rechenintensiv. Es läuft deshalb am PC.
- **Vorhersage in C.** Das fertige Netz muss nur noch rechnen: multiplizieren, addieren und die Sigmoid-Funktion anwenden. Dafür reicht ein einfaches C-Programm, grundsätzlich sogar ein kleiner Mikrocontroller.

```
Training (Python, PC) → Gewichte speichern (7seg.json / 7seg.txt / 7seg_net.h)
                      → Vorhersage in C mit 7seg.txt (Part 4)
                      → Vorhersage in C mit 7seg_net.h (Part 5)
```

## 2. Grundlagen des Netzes

**Neuron.** Jedes Neuron bildet eine gewichtete Summe seiner Eingänge, addiert einen Bias und wendet die Sigmoid-Funktion an. Sigmoid drückt jeden Wert in den Bereich 0 bis 1.
Beispiel: Eingabe [0, 1], Gewichte [0,5; −0,3], Bias 0,1 → z = 0·0,5 + 1·(−0,3) + 0,1 = −0,2 → sigmoid(−0,2) ≈ 0,45.

**Schichten.** Mehrere Neuronen nebeneinander bilden eine Schicht, und die Ausgaben einer Schicht sind die Eingaben der nächsten. Die Netzgröße wird als Neuronenzahl pro Schicht angegeben: „4-16-7“ bedeutet 4 Eingänge, 16 Neuronen in der versteckten Schicht (Hidden Layer) und 7 Ausgänge.

**Lernen.**
- **Fehlermaß:** Der Fehler wird mit dem mittleren quadratischen Fehler (MSE) gemessen.
- **Backpropagation:** Über die Kettenregel wird bestimmt, wie stark jedes Gewicht zum Fehler beigetragen hat. Der Fehler wird dabei von der Ausgabeschicht rückwärts durch das Netz gereicht.
- **Gradientenabstieg:** Jedes Gewicht wird ein kleines Stück in die Richtung verschoben, die den Fehler verkleinert. Die Schrittgröße ist die Lernrate 0,1.
- **Stochastic Gradient Descent:** Die Gewichte werden nach jedem einzelnen Trainingsbeispiel angepasst.
- **Epoche:** Ein Durchlauf über alle Beispiele. Trainiert wurde jeweils 20 000 Epochen.

**Vorhersage.** Die Ausgaben liegen zwischen 0 und 1. Ab der Schwelle 0,5 gilt ein Segment als „an“.

**Reproduzierbarkeit.** Alle Skripte verwenden einen festen Zufalls-Seed. Dadurch liefert jeder Lauf exakt dieselben Gewichte.

## 3. Umsetzung nach Parts

### Part 1 – Netz in Python (`part1_2_python/nn.py`)

Das Netz besteht aus drei Klassen:

| Klasse | Aufgabe |
|---|---|
| `Neuron` | Gewichte und Bias, Vorwärtsrechnung, Anpassung der eigenen Werte beim Lernen |
| `Layer` | Liste von Neuronen; `forward()` berechnet alle Ausgaben, `backward()` gibt den Fehler an die vorherige Schicht weiter |
| `NeuralNetwork` | Liste von Schichten; `train()`, `predict()` sowie Speichern und Laden |

Für die späteren Teile wird das trainierte Netz in drei Formaten gespeichert:

- **JSON** (`dump_json()` / `load()`): zum Speichern und Wiederladen in Python.
- **TXT** (`dump_txt()`): ein lesbares Format, das ein C-Programm einfach Wort für Wort einlesen kann. Jede Zeile beginnt mit einem Schlüsselwort, und vor jeder Liste steht ihre Größe. So weiß das C-Programm vorher, wie viel Speicher es braucht:
  ```
  LAYERS 2
  SIZES 4 16 7
  LAYER 0 16 4        (Schicht 0: 16 Neuronen mit je 4 Eingängen)
  NEURON 0
  BIAS 0.571...
  WEIGHTS -0.198 2.007 -3.809 4.948
  ```
- **C-Header** (`dump_initfile()`): Gewichte und Biases als `static const float`-Arrays plus eine Init-Funktion, die ein C-Netz mit diesen Konstanten verbindet.

### Part 2 – Training und Speichern (`train_xor.py`, `train_7seg.py`)

**XOR (Netz 2-2-1).**
- **Lokales Minimum:** Mit nur zwei Hidden-Neuronen blieb der erste Trainingsversuch bei 3 von 4 richtigen Ausgaben hängen. Weitere Gewichtsänderungen verbessern den Fehler dort kaum noch.
- **Neustart:** Das Skript startet in diesem Fall mit neuen Zufallsgewichten. Der zweite Versuch erreichte 4/4.
- **Speichern und Laden:** Das Netz wird als `xor.json` gespeichert, neu geladen und erneut getestet. Das geladene Netz liefert dieselben Werte, zum Beispiel [0,1] → 0,961 und [1,1] → 0,047.

**7-Segment-Decoder (Netz 4-16-7).**
- **Ergebnis:** Nach 20 000 Epochen sind alle 70 Segmentwerte (10 Ziffern × 7 Segmente) korrekt.
- **Speichern und Prüfen:** Das Netz wird als JSON, TXT und C-Header gespeichert. Danach wird es aus der JSON-Datei neu geladen und für jede Ziffer zusätzlich als ASCII-7-Segment-Bild im Terminal ausgegeben.
- **Fehlerverlauf:** Der Fehler wird alle 1000 Epochen ausgegeben und sinkt bis auf einen Endfehler von 0,00012 (MSE).

### Part 3 – Vergleich mit TensorFlow (`part3_tensorflow/`)

Beide Netze wurden zusätzlich mit TensorFlow/Keras gebaut, mit denselben Einstellungen: Sigmoid, MSE, SGD mit einem Beispiel pro Update, Lernrate 0,1 und 20 000 Epochen. Die Angabe schlägt für TensorFlow 10 Hidden-Neuronen vor. Für einen fairen Vergleich wurden aber ebenfalls 16 verwendet.

| Netz | Variante | Richtig | Endfehler (MSE) | Trainingszeit |
|---|---|---|---|---|
| XOR 2-2-1 | eigenes Netz | 4/4 (2. Versuch) | 0,00177 | ca. 1,9 s |
| XOR 2-2-1 | TensorFlow | 4/4 | 0,00038 | ca. 8,7 s |
| 7-Segment 4-16-7 | eigenes Netz | 70/70 | 0,00012 | ca. 22,5 s |
| 7-Segment 4-16-7 | TensorFlow | 70/70 | 0,00065 | ca. 21,8 s |

Beide Umsetzungen lösen die Aufgaben vollständig. Das bestätigt, dass Vorwärtsrechnung und Backpropagation im eigenen Netz korrekt sind.

- **Endfehler:** Die Werte unterscheiden sich, weil die Startgewichte verschieden gewählt werden. Keras verwendet die Glorot-Initialisierung, das eigene Netz Zufallswerte zwischen −1 und 1.
- **Geschwindigkeit:** TensorFlow ist bei so kleinen Netzen nicht schneller. Der Verwaltungsaufwand pro Rechenschritt überwiegt, und die Stärke der Bibliothek zeigt sich erst bei großen Netzen und Datenmengen.

Details stehen in `vergleich.md`.

### Part 4 – C-Programm mit Gewichten aus `7seg.txt` (`part4_c_txt/`)

Die Vorwärtsrechnung wurde in C nachgebaut. Trainiert wird in C nicht.

- **Datenstrukturen:** Die Structs `Neuron`, `Layer` und `Network` stehen in `nn.h`.
- **Funktionen:** `nn_load_txt()` liest die Textdatei ein, `nn_forward()` rechnet vorwärts, `nn_predict()` rundet mit der Schwelle 0,5, und `nn_free()` gibt den Speicher wieder frei.
- **Ergebnis:** Alle 10 Ziffern sind richtig, und die Rohwerte stimmen mit Python überein (z. B. Ziffer 0, Segment a: 0,985).

Unterschiede zu Python:
- **Speicher:** Der Speicher wird mit `malloc` angefordert und muss mit `free` wieder freigegeben werden. In Python passiert das automatisch.
- **Arrays:** C-Arrays kennen ihre eigene Länge nicht. Deshalb speichern die Structs die Anzahl der Eingänge und Neuronen extra.
- **Genauigkeit:** C rechnet mit `float` (ca. 7 Stellen), NumPy mit `double`. Für das Ergebnis macht das keinen Unterschied.

### Part 5 – C-Programm mit Gewichten aus `7seg_net.h` (`part5_c_header/`)

Die Structs und Funktionen sind dieselben wie in Part 4. Das Netz wird aber über die Init-Funktion aus dem Header aufgebaut, ohne Datei und ohne `malloc`:
- **Gewichte:** Sie stehen als Konstanten im Programm. Jedes Neuron zeigt nur auf seine Zeile im Header, kopiert wird nichts.
- **Speicher:** Die Structs haben feste Maximalgrößen und brauchen deshalb keinen dynamischen Speicher.
- **Ergebnis:** Alle 10 Ziffern sind richtig, mit denselben Rohwerten wie in Part 4.

**Warum diese Variante für den Mikrocontroller:** Ein ESP32 hat kein Dateisystem, aus dem `7seg.txt` gelesen werden könnte, und nur wenig Arbeitsspeicher. Konstanten aus dem Header legt der Compiler direkt in den Flash-Speicher. Das Netz ist damit sofort nach dem Einschalten einsatzbereit.

### Part 6 – ESP32 mit 7-Segment-Anzeige

Dieser Teil wurde nicht umgesetzt. Laut Angabe wäre eine Ziffer über den Serial Monitor empfangen, in 4 Bit umgewandelt, durch das Netz gerechnet und mit der Schwelle 0,5 an die sieben Segment-Pins ausgegeben worden. Die nötige Grundlage ist mit Part 5 vorhanden: `nn.c` und `7seg_net.h` brauchen weder ein Dateisystem noch dynamischen Speicher und könnten in ein ESP32-Projekt übernommen werden.

## 4. Zusatz: Weboberfläche (`gui/`)

Als Ergänzung zur Angabe gibt es eine lokale Weboberfläche (`http://localhost:8000`). Damit lassen sich alle Programme aus Part 1 bis 5 starten.

- **Aufbau:** Pro Part gibt es einen Reiter mit kurzer Erklärung, Start-Buttons und einer Live-Ausgabe.
- **Lernkurve:** Bei den Trainings wird die Lernkurve live aus der Programmausgabe gezeichnet.
- **Grafischer Vergleich (Reiter „TensorFlow“):** Lernkurven des eigenen Netzes und des TensorFlow-Netzes für XOR und den 7-Segment-Decoder übereinander, dazu Balkendiagramme für Endfehler und Trainingszeit. Der Fehler des eigenen Netzes ist dafür auf denselben MSE umgerechnet.
- **Reiter „Netz ansehen“:** Hier sieht man, wie eine gewählte Ziffer Schicht für Schicht durch das gespeicherte Netz läuft und welche Segmente aufleuchten.

Der Server verwendet nur die Python-Standardbibliothek und NumPy. Er ist ausschließlich vom eigenen PC aus erreichbar und kann nur die fest eingetragenen Programme starten.

**Online-Version (GitHub Pages).** Dieselbe Seite liegt unter https://leopoint.github.io/INSY/NN_from_scratch/gui/. Dort gibt es keinen Server, der Python oder gcc ausführen könnte. Die Seite erkennt das und schaltet um:
- **Netz ansehen:** Die gespeicherten Gewichte (`models/*.json`) werden direkt geladen, und die Vorwärtsrechnung läuft in JavaScript im Browser. Die Formel ist dieselbe wie in `nn.py`.
- **Programme:** Die Buttons spielen eine Aufzeichnung (`gui/aufzeichnung.json`) eines echten Laufs aller sechs Programme vom 19.10.2026 ab, mit Ausgabe, Lernkurve und gemessener Laufzeit.

## 5. Probleme und Lösungen

| Problem | Lösung |
|---|---|
| XOR-Training blieb im ersten Versuch in einem lokalen Minimum (3/4) | Automatischer Neustart mit neuen Zufallsgewichten |
| TensorFlow war mit 20 000 einzeln gestarteten Epochen sehr langsam | Daten gebündelt übergeben; weiterhin ein Update pro Beispiel |
| Eigenes Netz und TensorFlow geben den Fehler unterschiedlich skaliert aus | Für den Vergleich wurde bei beiden derselbe MSE nachgerechnet |
| Ursprünglicher C-Header enthielt keine Init-Funktion | `dump_initfile()` ergänzt, Header aus dem gespeicherten Modell neu erzeugt (Gewichte unverändert) |
| Kein C-Compiler auf dem PC | gcc (WinLibs) über winget installiert |

## 6. Werkzeuge

- **Programmierung:** Python 3.12 mit NumPy (eigenes Netz) und TensorFlow/Keras (nur Part 3), C mit gcc.
- **Umgebung:** Windows und VS Code.
- **KI-Unterstützung:** Die Umsetzung erfolgte mit Claude als Tutor und Programmierpartner. Die Arbeitsregeln dafür stehen in [`CLAUDE.md`](CLAUDE.md). Token-Verbrauch und Kosten der KI-Nutzung werden mit `token_verbrauch.py` aus den Sitzungsprotokollen ermittelt und in [`FORTSCHRITT.md`](FORTSCHRITT.md) laufend aktualisiert.

## 7. Projektstruktur

```
NN_from_scratch/
├── part1_2_python/    nn.py, train_xor.py, train_7seg.py
├── models/            xor.json, 7seg.json, 7seg.txt, 7seg_net.h
├── part3_tensorflow/  tf_xor.py, tf_7seg.py, vergleich.md
├── part4_c_txt/       nn.h, nn.c, main.c
├── part5_c_header/    nn.h, nn.c, main.c
└── gui/               server.py, index.html, start_gui.bat, aufzeichnung.json
```

Der gesamte Ordner liegt auf GitHub (https://github.com/leopoint/INSY/tree/main/NN_from_scratch). Nur das private Lernprotokoll und lokale Editor-Einstellungen bleiben auf dem eigenen PC.

## 8. Verlauf

| Datum | Arbeit |
|---|---|
| 29.09.2026 | Projekt angelegt, eigene Vorarbeit übernommen, Speichern/Laden (JSON, TXT, C-Header) ergänzt |
| 29.09.2026 | XOR- und 7-Segment-Netz trainiert, gespeichert und geprüft (Part 1 und 2 fertig) |
| 30.09.2026 | GitHub-Repository mit Fortschrittsdatei eingerichtet |
| 13.10.2026 | TensorFlow-Vergleich (Part 3), C-Programme mit TXT- und Header-Gewichten (Part 4 und 5) |
| 13.10.2026 | Code kommentiert, Weboberfläche erstellt, ungenutzte Dateien entfernt, Arbeitsbericht angelegt |
| 19.10.2026 | Entscheidung gegen Part 6 (ESP32), Schlussprüfung aller Programme, Projekt abgeschlossen |
| 19.10.2026 | Gesamtes Projekt auf GitHub hochgeladen, Weboberfläche als Online-Version über GitHub Pages |
| 17.11.2026 | Grafischer Vergleich eigenes Netz vs. TensorFlow in der Weboberfläche ergänzt |

## 9. Zusammenfassung

Am PC wurde in Python ein neuronales Netz aus den Klassen `Neuron`, `Layer` und `NeuralNetwork` selbst programmiert. Es lernt mit Backpropagation und Stochastic Gradient Descent: Nach jedem Beispiel wird der Fehler rückwärts durch das Netz gereicht, und jedes Gewicht wird ein kleines Stück verbessert. Als erster Test lernte ein 2-2-1-Netz die XOR-Funktion. Danach lernte ein 4-16-7-Netz, eine Ziffer als 4 Bit in die sieben Segmente einer Anzeige zu übersetzen, und erkennt alle 10 Ziffern richtig. Das trainierte Netz wurde in drei Formaten gespeichert: JSON zum Wiederladen in Python, TXT zum Einlesen in C und ein C-Header mit den Gewichten als Konstanten. Ein Vergleich mit TensorFlow/Keras bei gleicher Netzgröße und gleichen Einstellungen ergab dieselbe Genauigkeit und bestätigt so die eigene Umsetzung. In C wurde nur die Vorwärtsrechnung nachgebaut, einmal mit Gewichten aus der Textdatei und einmal mit Gewichten aus dem Header. Beide C-Programme liefern dieselben Ausgabewerte wie Python und erkennen alle 10 Ziffern. Die Header-Variante braucht weder Datei noch dynamischen Speicher und wäre damit für einen Mikrocontroller geeignet. Der ESP32-Teil wurde nicht mehr umgesetzt.

```
Trainingsdaten → Training in Python (nn.py) → 7seg.json / 7seg.txt / 7seg_net.h
                                                  │           │            │
                                        Python laden    C (Part 4)   C (Part 5)
```
