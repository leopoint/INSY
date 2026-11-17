# Arbeitsbericht – Radondaten auslesen

**Fach:** INSY, 5. Klasse · **Beginn:** 17.11.2026 · **Stand:** 17.11.2026

Dieser Bericht beschreibt, wie echte Radon-Messdaten eines Hauses ausgelesen, bereinigt und in einem Dashboard dargestellt werden. Den kurzen Status zeigt [`FORTSCHRITT.md`](FORTSCHRITT.md). Das Dashboard ist online unter https://leopoint.github.io/INSY/Radon_daten_auslesen/dashboard/ erreichbar.

---

## 1. Ziel und Gesamtablauf

In einem Haus messen sieben Radonsensoren, zwei Raumklima-Sensoren und eine Wetterstation. Ziel ist, diese Daten maschinell auszulesen und so darzustellen, dass man auf einen Blick sieht, wie hoch die Radonbelastung in jedem Raum ist, wann sie hoch ist und womit sie zusammenhängen könnte.

```
CSV oder PDF → Text → Tabelle → bereinigen → Lüften erkennen → Stundenwerte → daten/radon_stuendlich.csv
                                                                         → dashboard/daten.js → Dashboard (index.html)
```

Das Projekt besteht aus zwei Teilen:

- **Auslesen in Python (`auslesen.py`).** Liest die Datei, macht daraus eine Tabelle, bereinigt sie, fasst die Werte zu Stundenwerten zusammen und speichert das Ergebnis.
- **Dashboard im Browser (`dashboard/index.html`).** Liest die Stundenwerte, berechnet alle Kennzahlen selbst und zeichnet die Diagramme. Es läuft ohne Server, auch direkt per Doppelklick.

## 2. Die Daten

Zuerst lag nur eine PDF vor (18 Stunden, nur Küche und Wetter). Danach kam der vollständige Export als CSV-Datei mit allen Räumen. Beide haben denselben Aufbau: Jede Zeile ist eine Messung, die Werte sind durch Kommas getrennt, die Kopfzeile hat 29 Spalten wie `Kueche – Radon (Bq/m³)` oder `Wetter – Luftdruck (hPa)`. Die ersten beiden Spalten sind der Zeitpunkt in UTC und in Wiener Zeit.

| Eigenschaft | Wert |
|---|---|
| Messzeilen | 229.403 |
| Zeitraum | 24.03.2026 bis 13.10.2026 (203 Tage) |
| Radonsensoren | Wohnzimmer, Küche, Küche (Sockel), Schlafzimmer, Büro, Werkstatt, Technikraum (etwa alle 5–10 Minuten) |
| Raumklima | Küche und Schlafzimmer: Temperatur, CO₂, Luftfeuchte, Luftdruck |
| Wetter | Außentemperatur, Luftdruck, Wind, Bodentemperatur in 0, 6 und 54 cm (einmal pro Stunde) |

In jeder Zeile ist nur ein Teil der Spalten gefüllt, weil jeder Sensor zu seinem eigenen Zeitpunkt sendet. Die Sensoren wurden nicht alle gleichzeitig in Betrieb genommen, das Schlafzimmer zum Beispiel erst am 13.05.2026.

## 3. Auslesen und Bereinigen (`auslesen.py`)

1. **Text holen.** Eine CSV-Datei wird direkt gelesen. Bei einer PDF holt die Bibliothek `pypdf` den Text aus der Seite.
2. **Zeichenkodierung reparieren (nur PDF).** Die PDF wurde mit einer falschen Zeichenkodierung erzeugt, aus `³` wurde `Â³`. Der Text wurde ursprünglich als UTF-8 gespeichert, aber als Windows-1252 gelesen. Das Skript macht diesen Schritt rückgängig.
3. **Tabelle bilden.** Jede Zeile wird beim Komma getrennt. Gültig ist eine Zeile nur, wenn sie gleich viele Spalten hat wie die Kopfzeile. Alle 229.403 Zeilen waren gültig.
4. **Spaltennamen zerlegen.** Aus `Kueche (Luft) – CO₂ (ppm)` werden Ort (`Kueche`), Messgröße (`CO₂`) und Einheit (`ppm`). So ordnet das Dashboard alle Spalten automatisch dem richtigen Raum zu.
5. **Sensor-Neustarts erkennen.** Zu jedem Radonsensor gibt es eine Spalte „Betriebszeit“ in Minuten. Wird sie kleiner, wurde der Sensor neu gestartet. Insgesamt gab es 65 Neustarts.
6. **Anlaufwerte entfernen.** Direkt nach einem Neustart meldet der Sensor 0 Bq/m³, obwohl er noch nicht misst. Werte von 0 in den ersten 10 Betriebsminuten werden entfernt (99 Werte). Nullwerte während des normalen Betriebs bleiben, weil sie zwischen Werten wie 1 oder 2 Bq/m³ liegen und damit echte, sehr niedrige Messungen sind.
7. **Lüften erkennen.** Beim Lüften kommt frische Außenluft herein. Deshalb gilt als Lüften, wenn CO₂ innerhalb von 30 Minuten um mindestens 150 ppm fällt (nur Küche und Schlafzimmer haben CO₂-Sensoren, ab 08.05.2026) oder Radon innerhalb einer Stunde von mindestens 100 um mindestens 60 Bq/m³ auf höchstens 65 % fällt. Abfälle durch einen Sensor-Neustart zählen nicht. Mehrere Treffer im selben Raum innerhalb einer Stunde gelten als ein Lüften. So wurden 338 Lüftungen erkannt. In Räumen ohne CO₂-Sensor wird Lüften nur erkannt, wenn Radon vorher hoch war.
8. **Stundenwerte bilden.** Alle Messungen einer Stunde werden gemittelt. Aus etwa 200.000 Radon-Einzelwerten werden rund 4.900 Stunden pro Sensor. Das macht die Datenmenge für den Browser etwa 40-mal kleiner, ohne dass im Verlauf etwas Wichtiges verloren geht. Höchst- und Tiefstwerte der Einzelmessungen werden zusätzlich gespeichert.
9. **Speichern.** `daten/radon_stuendlich.csv` enthält die Stundenwerte aller Messgrößen (für Excel). `dashboard/daten.js` enthält dieselben Werte für das Dashboard. Es ist eine JavaScript-Datei statt JSON, damit der Browser sie auch ohne Server laden kann. Die Rohdatei (20 MB) liegt nicht im Repository.

## 4. Das Dashboard

Oben wählt man den Zeitraum: gesamt, die letzten 7 oder 30 Tage, einen Monat oder ein eigenes Datum von–bis. Alle Bereiche rechnen dann nur mit diesem Zeitraum. Bei mehr als 21 Tagen zeigen die Verlaufsdiagramme Tagesmittel, sonst Stundenwerte.

| Bereich | Inhalt |
|---|---|
| Kennzahlen | Mittelwert des ganzen Hauses mit Bewertung, höchster Raum-Mittelwert, höchster Stundenwert, Stunden über 300 Bq/m³, Anteil der Zeit unter 100 Bq/m³ |
| Wichtigste Erkenntnisse | automatisch formulierte Sätze: Gesamtbewertung, höchster und niedrigster Raum, Monatsvergleich, Tageszeit, Phasen mit mehreren Räumen über 300, stärkster Zusammenhang |
| Raumplan | schematischer Grundriss eines quadratischen Hauses, jeder Raum in der Farbe seines Radonwerts (grün → gelb → rot), mit Zeitregler und Abspielfunktion; wahlweise Wert zum Zeitpunkt, Mittelwert, höchster Wert oder Stunden über 300; dazu Temperatur und CO₂ in Küche und Schlafzimmer und das Wetter draußen |
| Lüften | erkannte Lüftungen mit Anzahl, häufigster Uhrzeit, Wirkung auf Radon und längster Zeit ohne Lüften; Diagramm „Wann wird gelüftet?“, Tabelle je Raum und Liste aller Lüftungen. Lüften wird zusätzlich überall eingetragen: im Raumplan („gerade gelüftet“, „zuletzt gelüftet“), als Striche im Zeitverlauf, als weiße Punkte im Fingerabdruck, in den Erkenntnissen, bei den Ereignissen und in der Tagestabelle |
| Räume im Vergleich | Balkendiagramm der Mittelwerte und Tabelle mit Bewertung, höchstem Stundenwert, Stunden über 300, Zeit unter 100 und Datenabdeckung |
| Zeitverlauf | Radonkurve je Raum (einzeln ein- und ausblendbar) mit den Grenzen 100 Bq/m³ (WHO) und 300 Bq/m³ (Referenzwert Österreich) |
| Monatsübersicht | Tabelle Raum × Monat, jede Zelle in der Farbe ihres Mittelwerts |
| Tagesverlauf | mittlerer Radonwert je Uhrzeit für jeden Raum |
| Tag und Nacht | Mittelwert je Raum nachts (22–6 Uhr) und tagsüber (6–22 Uhr) |
| Wochentage | Mittelwert des ganzen Hauses und Lüftungen pro Tag je Wochentag |
| Fingerabdruck | Bild eines Raums: jede Spalte ein Tag, jede Zeile eine Uhrzeit, Farbe = Radonwert |
| Raumklima | Kennzahlen (CO₂-Mittel und -Maximum, Stunden über 1000 ppm, Temperaturbereich, Anteil der Zeit mit Luftfeuchte außerhalb 30–60 %) und Verläufe von CO₂, Temperatur, Luftfeuchte und Luftdruck in Küche und Schlafzimmer |
| Wetter | Außen- und Bodentemperatur, Luftdruck, Wind |
| Zusammenhänge | Korrelation zwischen Radon in jedem Raum und Außentemperatur, Temperaturunterschied innen–außen, Luftdruck, Wind, Bodentemperatur und CO₂ |
| Ereignisse | höchste Spitzen, längste Phasen über 300 Bq/m³ und gleichzeitige Neustarts mehrerer Sensoren (vermutlich Stromausfälle) |
| Datenqualität | je Sensor: Anzahl Messungen, Messbeginn, Neustarts, Lücken, längste Lücke, Minimum und Maximum der Einzelwerte |
| Tabelle | Tagesmittelwerte aller Räume, dazu der Download der Stundenwerte |

Jede Messgröße hat ihr eigenes Diagramm, damit nie zwei Einheiten auf einer Achse landen. Alle Zeitachsen sind gleich breit und liegen untereinander. Jeder Raum hat überall dieselbe Farbe. Das Dashboard hat einen hellen und einen dunklen Modus und funktioniert auch am Handy.

## 5. Ergebnisse (gesamter Zeitraum)

- **Gesamtbewertung:** Das ganze Haus liegt im Mittel bei **52 Bq/m³**. Das ist niedrig und liegt klar unter dem österreichischen Referenzwert von 300 Bq/m³. 94 % der Stunden lagen unter der WHO-Empfehlung von 100 Bq/m³.
- **Räume:** Am höchsten ist der Sensor am Küchensockel (60 Bq/m³), am niedrigsten das Büro (37 Bq/m³). Der Sockel liegt nahe am Boden, wo das Radon ins Haus kommt.
- **Jahreszeit:** August hatte die höchsten Werte (101 Bq/m³), September die niedrigsten (30 Bq/m³).
- **Anfang August:** Vom 2. bis 6.08. lagen bis zu alle sieben Räume gleichzeitig über 300 Bq/m³, teilweise mehrere Tage am Stück (Küchensockel 94 Stunden). Wenn alle Räume zugleich steigen, liegt die Ursache im ganzen Haus, zum Beispiel weil längere Zeit nicht gelüftet wurde.
- **Lüften:** 338 Lüftungen erkannt (etwa 1,7 pro Tag), am häufigsten um 6 Uhr, im Schlafzimmer meist um 22 Uhr. In der Küche wurde vom 31.07. bis 06.08.2026 fast 7 Tage lang kein Lüften erkannt, genau in der Zeit mit den höchsten Werten. Am 06.08. gegen 20 Uhr wurde in fast allen Räumen gleichzeitig gelüftet, danach fielen die Werte. War Radon vorher über 100 Bq/m³, lag es 2 Stunden nach dem Lüften im Schnitt um etwa die Hälfte niedriger.
- **Tag und Nacht:** In fast allen Räumen ist Radon nachts höher als tagsüber, am deutlichsten im Wohnzimmer, in der Küche und im Büro.
- **Raumklima:** Im Schlafzimmer lag CO₂ 117 Stunden über 1000 ppm (verbrauchte Luft), in der Küche nur 12 Stunden.
- **Tageszeit:** Am höchsten ist Radon um 6 Uhr früh, am niedrigsten um 18 Uhr. Nachts sammelt es sich an, tagsüber wird gelüftet.
- **März:** In der ersten Woche (24.03.) wurden in der Küche bis zu 707 Bq/m³ gemessen (Einzelwert). Danach sanken die Werte deutlich.
- **Zusammenhänge:** Am deutlichsten hängen Werkstatt und Technikraum mit der Bodentemperatur in 54 cm Tiefe zusammen (r ≈ 0,5). Die übrigen Räume zeigen nur schwache Zusammenhänge mit dem Wetter.
- **Stromausfälle:** Mehrmals starteten sechs Sensoren gleichzeitig neu, zum Beispiel am 16.04., 30.04. und 06.07.2026. Das deutet auf Stromausfälle hin.

Hinweis: Das Dashboard bewertet Messwerte. Es ersetzt keine offizielle Radonmessung nach Norm.

## 6. Probleme und Lösungen

| Problem | Lösung |
|---|---|
| Sonderzeichen in der PDF kaputt (`Â³`, `â€“`) | Text als Windows-1252 kodieren und als UTF-8 lesen |
| Werte von 0 Bq/m³ nach einem Neustart verfälschen Tiefst- und Mittelwerte | Neustart über die Betriebszeit erkennen, Anlaufwerte entfernen |
| Ein Neustart wurde doppelt erkannt (Betriebszeit sprang erst von 185 auf 180, dann auf 0) | Rücksprünge innerhalb von 15 Minuten zählen als ein Neustart |
| Hunderte Nullwerte auch im normalen Betrieb | Untersucht: sie liegen zwischen Werten wie 1–2 Bq/m³, sind also echte niedrige Messungen und bleiben |
| 229.403 Zeilen sind zu viel für ein flüssiges Dashboard | Stundenmittel bilden (rund 550 KB statt 20 MB) |
| Die Uhrzeit für den Tagesverlauf wurde falsch gelesen („20 Uhr“ statt „20“) | Uhrzeit mit einem eigenen Zahlenformat bestimmen |
| Beim Browser ist das Laden einer JSON-Datei ohne Server blockiert | Daten als JavaScript-Datei (`daten.js`) speichern |
| Der März hatte nur 8 Tage Daten und wirkte deshalb als „höchster Monat“ | Monatsvergleich nur für Monate mit mindestens 14 Tagen Daten |
