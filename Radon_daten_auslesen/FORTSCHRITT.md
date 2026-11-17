# Arbeitsfortschritt – Radondaten auslesen (INSY, 5. Klasse)

Diese Datei wird laufend aktualisiert und zeigt, woran ich gerade arbeite.

- **Projekt (Code, Daten, Dokumente):** https://github.com/leopoint/INSY/tree/main/Radon_daten_auslesen
- **Dashboard im Browser:** https://leopoint.github.io/INSY/Radon_daten_auslesen/dashboard/

## Stand

| Teil | Inhalt | Status |
|------|--------|--------|
| 1 | Daten aus der PDF auslesen und bereinigen (`auslesen.py`) | ✅ fertig |
| 2 | Dashboard mit Kennzahlen, Verlauf, Tagesverlauf, Auffälligkeiten und Wetter | ✅ erste Version |
| 3 | Raumplan mit Farbskala und Zeitregler | ✅ fertig |
| 4 | Dokumentation und Veröffentlichung über GitHub Pages | ✅ fertig |

## Verlauf

- **17.11.2026** – Projekt angelegt. Die Mess-PDF enthält eine CSV-Tabelle mit 236 Messzeilen (24.03.2026, 20:37 bis 25.03.2026, 14:59) und 29 Spalten. Werte gibt es für den Radonsensor in der Küche und für stündliche Wetterdaten, die übrigen Räume sind in dieser Datei leer.
- **17.11.2026** – Auslese-Skript erstellt. Es repariert die fehlerhafte Zeichenkodierung der PDF, erkennt einen Sensor-Neustart und entfernt die drei Anlaufwerte mit 0 Bq/m³ danach.
- **17.11.2026** – Erste Version des Dashboards erstellt. Ergebnis für die Küche: Mittelwert 350 Bq/m³, Höchstwert 707 Bq/m³, 61 % der Messzeit über dem österreichischen Referenzwert von 300 Bq/m³.
- **17.11.2026** – Raumplan ergänzt: Ein schematischer Grundriss zeigt jeden Raum in der Farbe seines Radonwerts, mit Zeitregler und den Wetterwerten draußen.
- **17.11.2026** – Projekt auf GitHub hochgeladen, das Dashboard ist über GitHub Pages online.

## KI-Nutzung: Token-Verbrauch und Kosten

Das Projekt wird mit Claude Code (Modell Claude Opus 5.5) als Tutor und Programmierpartner umgesetzt. Die Werte stammen aus den lokalen Sitzungsprotokollen und werden mit `token_verbrauch.py` ausgewertet.

| Sitzung | Dauer | Antworten | Eingabe | Ausgabe | Cache geschrieben | Cache gelesen | Kosten (API-Preis) |
|---|---|---|---|---|---|---|---|
| 17.11.2026 15:24 | 13 min | 70 | 150 | 74.505 | 170.673 | 11.774.402 | 5,21 $ |
| **Summe** | | 70 | 150 | 74.505 | 170.673 | 11.774.402 | **5,21 $** |

Die Kosten sind mit den Listenpreisen der Claude-API berechnet: 4 $ pro Million Eingabe-Tokens, 20 $ pro Million Ausgabe-Tokens, 8 $ pro Million in den Cache geschriebener Tokens (1-Stunden-Cache) und 0,20 $ pro Million aus dem Cache gelesener Tokens. Bei einem Claude-Abo wird nicht pro Token abgerechnet; die Kosten zeigen dann den Gegenwert zu API-Preisen. Stand der Zahlen: 17.11.2026, 15:38.
