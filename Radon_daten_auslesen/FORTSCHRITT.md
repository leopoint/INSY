# Arbeitsfortschritt – Radondaten auslesen (INSY, 5. Klasse)

Diese Datei wird laufend aktualisiert und zeigt, woran ich gerade arbeite.

- **Projekt (Code, Daten, Dokumente):** https://github.com/leopoint/INSY/tree/main/Radon_daten_auslesen
- **Dashboard im Browser:** https://leopoint.github.io/INSY/Radon_daten_auslesen/dashboard/

## Stand

| Teil | Inhalt | Status |
|------|--------|--------|
| 1 | Daten aus der PDF auslesen und bereinigen (`auslesen.py`) | ✅ fertig |
| 2 | Dashboard mit Kennzahlen, Verlauf, Tagesverlauf, Auffälligkeiten und Wetter | ✅ fertig |
| 3 | Raumplan mit Farbskala und Zeitregler | ✅ fertig |
| 4 | Dokumentation und Veröffentlichung über GitHub Pages | ✅ fertig |
| 5 | Vollständige Daten aller Räume (CSV, März bis Oktober 2026) | ✅ fertig |
| 6 | Automatische Erkennung, wann gelüftet wurde | ✅ fertig |

## Verlauf

- **17.11.2026** – Projekt angelegt. Die Mess-PDF enthält eine CSV-Tabelle mit 236 Messzeilen (24.03.2026, 20:37 bis 25.03.2026, 14:59) und 29 Spalten. Werte gibt es für den Radonsensor in der Küche und für stündliche Wetterdaten, die übrigen Räume sind in dieser Datei leer.
- **17.11.2026** – Auslese-Skript erstellt. Es repariert die fehlerhafte Zeichenkodierung der PDF, erkennt einen Sensor-Neustart und entfernt die drei Anlaufwerte mit 0 Bq/m³ danach.
- **17.11.2026** – Erste Version des Dashboards erstellt. Ergebnis für die Küche: Mittelwert 350 Bq/m³, Höchstwert 707 Bq/m³, 61 % der Messzeit über dem österreichischen Referenzwert von 300 Bq/m³.
- **17.11.2026** – Raumplan ergänzt: Ein schematischer Grundriss zeigt jeden Raum in der Farbe seines Radonwerts, mit Zeitregler und den Wetterwerten draußen.
- **17.11.2026** – Projekt auf GitHub hochgeladen, das Dashboard ist über GitHub Pages online.
- **17.11.2026** – Vollständige Messdaten als CSV übernommen: 229.403 Zeilen vom 24.03. bis 13.10.2026 mit 7 Radonsensoren, Raumklima in Küche und Schlafzimmer und Wetterdaten. Das Auslese-Skript bildet jetzt Stundenmittel. Das Dashboard wurde für mehrere Monate und alle Räume erweitert: Zeitraumauswahl, automatische Erkenntnisse, Raumvergleich, Monatsübersicht, Tag-Uhrzeit-Bild je Raum, Raumklima, Zusammenhänge mit Wetter und CO₂, Ereignisse und Datenqualität. Ergebnis: Das Haus liegt im Mittel bei 52 Bq/m³ und damit deutlich unter dem Referenzwert. Anfang August lagen jedoch alle Räume mehrere Tage gleichzeitig über 300 Bq/m³.
- **17.11.2026** – Lüftungserkennung ergänzt: Ein schneller Abfall von CO₂ oder Radon wird als Lüften gewertet (338 Lüftungen erkannt). Das Lüften ist jetzt in allen Ansichten des Dashboards eingetragen. Ergebnis: Am häufigsten wird um 6 Uhr gelüftet. In der Küche wurde vom 31.07. bis 06.08.2026 fast eine Woche lang nicht gelüftet, genau in der Zeit mit den höchsten Radonwerten.
- **17.11.2026** – Weitere Auswertungen ergänzt: Tag-Nacht-Vergleich je Raum, Wochentage und Kennzahlen zum Raumklima (z. B. Stunden mit CO₂ über 1000 ppm).
- **17.11.2026** – Raumplan auf drei Stockwerke aufgeteilt (Keller, Erdgeschoss, 1. Stock), jeweils mit Mittelwert des Stockwerks.
- **17.11.2026** – Erkennung von Abwesenheit ergänzt: Steigt CO₂ in Küche und Schlafzimmer mindestens 36 Stunden lang nicht an, war vermutlich niemand zu Hause. Gefunden wurde genau eine solche Phase, vom 31.07. bis 06.08.2026 (Urlaub). In dieser Zeit lag Radon im Mittel bei 283 Bq/m³ statt 44 Bq/m³.
- **17.11.2026** – Feld „Wie schlimm ist Radon?“ ergänzt: Einordnung des Lungenkrebsrisikos nach den Zahlen der WHO, mit Regler, Nichtraucher/Raucher-Umschalter und einer Darstellung als 1000 Menschen. Für dieses Haus (52 Bq/m³) ergibt sich etwa +8 % Risiko gegenüber einem Haus ohne Radon.

## KI-Nutzung: Token-Verbrauch und Kosten

Das Projekt wird mit Claude Code (Modell Claude Opus 5.5) als Tutor und Programmierpartner umgesetzt. Die Werte stammen aus den lokalen Sitzungsprotokollen und werden mit `token_verbrauch.py` ausgewertet.

| Sitzung | Dauer | Antworten | Eingabe | Ausgabe | Cache geschrieben | Cache gelesen | Kosten (API-Preis) |
|---|---|---|---|---|---|---|---|
| 17.11.2026 15:24 | 67 min | 225 | 492 | 251.313 | 439.937 | 66.931.983 | 21,93 $ |
| **Summe** | | 225 | 492 | 251.313 | 439.937 | 66.931.983 | **21,93 $** |

Die Kosten sind mit den Listenpreisen der Claude-API berechnet: 4 $ pro Million Eingabe-Tokens, 20 $ pro Million Ausgabe-Tokens, 8 $ pro Million in den Cache geschriebener Tokens (1-Stunden-Cache) und 0,20 $ pro Million aus dem Cache gelesener Tokens. Bei einem Claude-Abo wird nicht pro Token abgerechnet; die Kosten zeigen dann den Gegenwert zu API-Preisen. Stand der Zahlen: 17.11.2026, 16:31.
