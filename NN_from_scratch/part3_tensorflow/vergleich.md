# Vergleich: eigenes NumPy-Netz vs. TensorFlow/Keras

Beide Varianten verwenden dieselben Einstellungen: Sigmoid in allen Schichten, MSE als Fehler, SGD mit einem Beispiel pro Update, Lernrate 0,1 und 20.000 Epochen.
Gemessen am 13.10.2026 auf demselben Windows-PC (nur CPU).

**Hinweis zur Netzgröße:** Im PDF steht für TensorFlow „Hidden e.g. 10“. Für einen fairen Vergleich wurden auch in TensorFlow **16** Hidden-Neuronen verwendet, also dieselbe Größe 4-16-7 wie im eigenen Netz.

## Ergebnisse

| Netz | Variante | Richtig | End-Fehler (MSE) | Trainingszeit |
|------|----------|---------|------------------|---------------|
| XOR 2-2-1 | NumPy (eigenes Netz) | 4/4 (erst im 2. Versuch) | 0,001770 | ca. 1,9 s pro Versuch |
| XOR 2-2-1 | TensorFlow | 4/4 | 0,000382 | ca. 8,7 s |
| 7-Segment 4-16-7 | NumPy (eigenes Netz) | 70/70 Segmente, 10/10 Ziffern | 0,000122 | ca. 22,5 s |
| 7-Segment 4-16-7 | TensorFlow | 70/70 Segmente, 10/10 Ziffern | 0,000654 | ca. 21,8 s |

Der MSE ist hier für beide gleich gerechnet: Mittelwert von (Ausgabe − Ziel)² über alle Beispiele und alle Ausgaben.
Das eigene Netz gibt beim Training einen anders skalierten Loss aus (½ · Summe pro Beispiel). Deshalb steht im Lernprotokoll für den 7-Segment-Decoder `0.000429`; das entspricht demselben Netz.

## Was ist gleich?

- Beide Netze lösen beide Aufgaben vollständig: Nach dem Runden mit Schwelle 0,5 stimmen alle Ausgaben.
- Der Fehler sinkt in beiden Fällen ähnlich: zuerst schnell, dann immer langsamer.
- Das mathematische Verfahren ist identisch: Forward-Pass, Fehler über MSE, Backpropagation mit Kettenregel und Gewichtsanpassung über Gradient Descent.

## Was ist anders und warum?

- **Endfehler:** Die Werte sind nicht genau gleich, weil beide Netze mit anderen Zufallsgewichten starten und die Beispiele in anderer Reihenfolge sehen. Bei XOR war TensorFlow genauer, beim 7-Segment-Decoder das eigene Netz. Beide Fehler sind aber so klein, dass das Ergebnis nach dem Runden gleich ist.
- **Startgewichte:** Keras startet mit der Glorot-Initialisierung und Bias 0. Das eigene Netz verwendet einfache Zufallswerte zwischen −1 und 1 für Gewichte und Bias. Deshalb blieb das eigene XOR-Netz mit Seed 42 im ersten Versuch in einem lokalen Minimum (3/4), TensorFlow nicht.
- **Geschwindigkeit:** Bei so winzigen Netzen ist TensorFlow nicht schneller. Jedes Update hat bei TensorFlow einen festen Verwaltungsaufwand; seine Stärke sind große Netze und große Datenmengen, die als Batches auf einmal gerechnet werden. Beim XOR-Netz ist das eigene Python-Netz deshalb sogar schneller. Beim 7-Segment-Netz sind beide etwa gleich schnell, weil das eigene Netz jedes Neuron einzeln in Python berechnet.
- **Aufwand beim Programmieren:** Mit TensorFlow sind es nur wenige Zeilen (`Sequential`, `Dense`, `compile`, `fit`). Das eigene Netz braucht eigene Klassen, aber dafür ist jeder Rechenschritt sichtbar und lässt sich später 1:1 nach C übertragen.

## Fazit

TensorFlow und das eigene Netz liefern für diese Aufgaben gleichwertige Ergebnisse. Das zeigt, dass die eigene Implementierung von Forward-Pass und Backpropagation korrekt ist. Für den ESP32 verwenden wir weiter die Gewichte des eigenen Netzes, weil dafür der Export als `.txt` und `.h` schon vorhanden ist.
