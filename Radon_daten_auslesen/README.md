# Radondaten auslesen (INSY, 5. Klasse)

Echte Radon-Messdaten eines Hauses (7 Räume, Raumklima, Wetter, 24.03. bis 13.10.2026) werden ausgelesen, bereinigt und in einem Dashboard im Browser dargestellt.

- **Dashboard (im Browser, ohne Installation):** https://leopoint.github.io/INSY/Radon_daten_auslesen/dashboard/
- **Ausführliche Beschreibung:** [ARBEITSBERICHT.md](ARBEITSBERICHT.md)
- **Stand und KI-Nutzung:** [FORTSCHRITT.md](FORTSCHRITT.md)

## Inhalt

| Datei / Ordner | Inhalt |
|---|---|
| [`auslesen.py`](auslesen.py) | liest die Messdaten (CSV oder PDF), entfernt ungültige Werte und bildet Stundenwerte |
| [`daten/radon_stuendlich.csv`](daten/radon_stuendlich.csv) | Stundenmittel aller Messgrößen (für Excel oder zum Nachprüfen) |
| [`dashboard/`](dashboard/) | `index.html` (Dashboard) und `daten.js` (die Stundenwerte, von `auslesen.py` erzeugt) |

## Ablauf

```
CSV oder PDF → Text → Tabelle → bereinigen → Stundenwerte → daten/radon_stuendlich.csv
                                                        → dashboard/daten.js → Dashboard (index.html)
```

## Das zeigt das Dashboard

- Zeitraum frei wählbar (gesamt, letzte 7/30 Tage, einzelne Monate, eigenes Datum)
- Kennzahlen und automatisch formulierte „Wichtigste Erkenntnisse“
- Raumplan: schematischer Grundriss, jeder Raum in der Farbe seines Radonwerts (grün bis rot), mit Zeitregler zum Abspielen
- Lüften: automatisch erkannt (schneller Abfall von CO₂ oder Radon) und überall eingetragen: Raumplan, Zeitverlauf, Fingerabdruck, Erkenntnisse, Ereignisse, Tagestabelle
- Räume im Vergleich, Zeitverlauf mit den Grenzen 100 Bq/m³ (WHO) und 300 Bq/m³ (Referenzwert Österreich)
- Monatsübersicht, Tagesverlauf, Tag/Nacht-Vergleich, Wochentage und „Fingerabdruck“ (Tag × Uhrzeit) je Raum
- Raumklima (CO₂, Temperatur, Feuchte, Luftdruck) und Wetter
- Zusammenhänge zwischen Radon, Wetter und CO₂ (Korrelation)
- Ereignisse (Spitzen, lange Phasen über 300, vermutete Stromausfälle), Datenqualität je Sensor, Tagesmittel als Tabelle

## Selbst ausführen

Voraussetzung: Python 3.12 (für PDFs zusätzlich `pip install pypdf`).

```
python auslesen.py daten/radon_alle_raeume.csv
```

Danach `dashboard/index.html` doppelklicken. Die Rohdatei (20 MB) liegt nicht im Repository, die bereinigten Stundenwerte schon.
