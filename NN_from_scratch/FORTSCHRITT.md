# Arbeitsfortschritt – Neural Network from Scratch (INSY, 4AHITS)

Diese Datei wird laufend aktualisiert und zeigt, woran ich gerade arbeite.

- **Projekt (Code, Modelle, Dokumente):** https://github.com/leopoint/INSY/tree/main/NN_from_scratch
- **Visualisierung im Browser:** https://leopoint.github.io/INSY/NN_from_scratch/gui/

## Stand

| Part | Inhalt | Status |
|------|--------|--------|
| 1 | Netz in Python (Neuron, Layer, NeuralNetwork, Export JSON/TXT/.h) | ✅ fertig |
| 2 | Training XOR (2-2-1) und 7-Segment-Decoder (4-16-7), Speichern/Laden | ✅ fertig |
| 3 | Vergleich mit TensorFlow/Keras | ✅ fertig |
| 4 | C-Programm, nur Forward, Gewichte aus `7seg.txt` | ✅ fertig |
| 5 | C-Programm, Gewichte aus `7seg_net.h` | ✅ fertig |
| 6 | ESP32 mit 7-Segment-Anzeige (PlatformIO) | ➖ entfällt |

## Verlauf

- **29.09.2026** – Projekt angelegt, eigene Vorarbeit (Neuron, Layer, Netz mit NumPy) übernommen, Speichern/Laden als JSON eingebaut.
- **29.09.2026** – XOR-Netz (2-2-1) trainiert und gespeichert. 7-Segment-Decoder (4-16-7) trainiert, alle 10 Ziffern korrekt, Export als JSON, TXT und C-Header (.h).
- **29.09.2026** – Grafische Ausgabe der 10 vorhergesagten Ziffern mit Matplotlib.
- **30.09.2026** – Fortschrittsdatei auf GitHub angelegt.
- **13.10.2026** – XOR und 7-Segment-Decoder mit TensorFlow/Keras trainiert (gleiche Netzgröße 4-16-7 für einen fairen Vergleich). Beide Umsetzungen erreichen 100 % Genauigkeit. Der Vergleich von Endfehler und Trainingszeit ist dokumentiert.
- **13.10.2026** – Vorwärtsrechnung des 7-Segment-Netzes in C umgesetzt. Die Gewichte werden aus `7seg.txt` gelesen, und das Programm erkennt alle 10 Ziffern mit denselben Ausgabewerten wie Python.
- **13.10.2026** – C-Variante ohne Datei und ohne dynamischen Speicher erstellt. Die Gewichte stammen aus dem automatisch erzeugten Header `7seg_net.h`, der jetzt auch eine Init-Funktion enthält. Alle 10 Ziffern werden korrekt erkannt.
- **13.10.2026** – Code durchgehend kommentiert. Lokale Weboberfläche erstellt, mit der sich alle Programme starten lassen und die Lernkurve sowie den Weg einer Eingabe durch das Netz live anzeigt. Ungenutzte Dateien entfernt, darunter die grafische Ausgabe vom 29.09.
- **13.10.2026** – Ausführlicher [Arbeitsbericht](ARBEITSBERICHT.md) mit Erklärung aller Parts, Ergebnissen und Problemen angelegt.
- **19.10.2026** – Entscheidung, Part 6 (ESP32) nicht umzusetzen. Alle Programme aus Part 1 bis 5 wurden erneut geprüft und liefern weiterhin korrekte Ergebnisse. Das Projekt ist damit abgeschlossen; der Arbeitsbericht enthält eine Zusammenfassung des gesamten Ablaufs.
- **19.10.2026** – Das gesamte Projekt (Code, trainierte Modelle, Weboberfläche) liegt jetzt auf GitHub. Die Weboberfläche ist zusätzlich über GitHub Pages online erreichbar. Dort rechnet die Netz-Ansicht direkt im Browser, und die Programmläufe werden als Aufzeichnung eines echten Laufs abgespielt.

## KI-Nutzung: Token-Verbrauch und Kosten

Das Projekt wird mit Claude Code (Modell Claude Opus 5.5) als Tutor und Programmierpartner umgesetzt. Die Werte stammen aus den lokalen Sitzungsprotokollen und werden mit `token_verbrauch.py` ausgewertet.

| Sitzung | Dauer | Antworten | Eingabe | Ausgabe | Cache geschrieben | Cache gelesen | Kosten (API-Preis) |
|---|---|---|---|---|---|---|---|
| 30.09.2026 08:12 | 25 min | 40 | 80 | 25.493 | 59.002 | 2.273.884 | 1,44 $ |
| 13.10.2026 09:47 | 406 min | 135 | 274 | 175.862 | 349.126 | 26.302.502 | 11,57 $ |
| 19.10.2026 19:34 | 15 min | 36 | 72 | 40.699 | 142.839 | 4.565.430 | 2,87 $ |
| **Summe** | | 211 | 426 | 242.054 | 550.967 | 33.141.816 | **15,88 $** |

Die Kosten sind mit den Listenpreisen der Claude-API berechnet: 4 $ pro Million Eingabe-Tokens, 20 $ pro Million Ausgabe-Tokens, 8 $ pro Million in den Cache geschriebener Tokens (1-Stunden-Cache) und 0,20 $ pro Million aus dem Cache gelesener Tokens. Den Großteil machen die Cache-Lesezugriffe aus, weil bei jeder Antwort der bisherige Gesprächsverlauf erneut eingelesen wird. Bei einem Claude-Abo wird nicht pro Token abgerechnet; die Kosten zeigen dann den Gegenwert zu API-Preisen. Für die Arbeit vom 29.09.2026 liegt kein Sitzungsprotokoll vor, sie ist deshalb nicht enthalten. Stand der Zahlen: 19.10.2026, 19:50.

## Abschluss

Das Projekt ist mit Part 5 abgeschlossen. Part 6 (ESP32 mit 7-Segment-Anzeige) wird nicht umgesetzt. Die Grundlage dafür wäre vorhanden: Die C-Variante aus Part 5 kommt ohne Datei und ohne dynamischen Speicher aus und könnte auf einen Mikrocontroller übertragen werden.
