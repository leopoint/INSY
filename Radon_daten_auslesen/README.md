# Radondaten auslesen (INSY, 5. Klasse)

Radon-Messdaten werden aus einer PDF ausgelesen, bereinigt und in einem Dashboard im Browser dargestellt.

- **Dashboard (im Browser, ohne Installation):** https://leopoint.github.io/INSY/Radon_daten_auslesen/dashboard/
- **Ausführliche Beschreibung:** [ARBEITSBERICHT.md](ARBEITSBERICHT.md)
- **Stand und KI-Nutzung:** [FORTSCHRITT.md](FORTSCHRITT.md)

## Inhalt

| Datei / Ordner | Inhalt |
|---|---|
| [`auslesen.py`](auslesen.py) | liest die PDF, repariert die Zeichenkodierung, entfernt ungültige Werte und speichert die Daten |
| [`daten/radon_daten.csv`](daten/radon_daten.csv) | die ausgelesene Tabelle (alle 29 Spalten, für Excel oder zum Nachprüfen) |
| [`dashboard/`](dashboard/) | `index.html` (Dashboard) und `daten.js` (die bereinigten Daten, von `auslesen.py` erzeugt) |

## Ablauf

```
PDF → Text (pypdf) → Tabelle (CSV) → bereinigen → daten/radon_daten.csv
                                               → dashboard/daten.js → Dashboard (index.html)
```

## Das zeigt das Dashboard

- Kennzahlen: Mittelwert mit Bewertung, Höchst- und Tiefstwert mit Uhrzeit, Anteil der Zeit über 300 Bq/m³, letzter Wert
- Radonverlauf mit den Grenzen 100 Bq/m³ (WHO) und 300 Bq/m³ (Referenzwert Österreich) und markiertem Sensor-Neustart
- Verteilung der Messzeit auf die Bereiche niedrig / erhöht / über Referenzwert
- Tagesverlauf (mittlerer Radonwert je Uhrzeit)
- automatisch erkannte Auffälligkeiten (Höchstwert, stärkster Abfall und Anstieg, längste Phase über 300)
- Wetterdaten (Außen- und Bodentemperatur, Luftdruck, Wind) auf derselben Zeitachse und deren Korrelation mit Radon
- Messwerte als Stundentabelle

## Selbst ausführen

Voraussetzung: Python 3.12 mit `pypdf` (`pip install pypdf`).

```
python auslesen.py
```

Danach `dashboard/index.html` doppelklicken. Eine andere PDF mit demselben Aufbau: `python auslesen.py andere.pdf`. Die Mess-PDF selbst liegt nicht im Repository.
