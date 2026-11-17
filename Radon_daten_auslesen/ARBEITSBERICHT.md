# Arbeitsbericht – Radondaten auslesen

**Fach:** INSY, 5. Klasse · **Beginn:** 17.11.2026 · **Stand:** 17.11.2026 (erste Version)

Dieser Bericht beschreibt, wie die Radon-Messdaten aus einer PDF ausgelesen, bereinigt und in einem Dashboard dargestellt werden. Den kurzen Status zeigt [`FORTSCHRITT.md`](FORTSCHRITT.md). Das Dashboard ist online unter https://leopoint.github.io/INSY/Radon_daten_auslesen/dashboard/ erreichbar.

---

## 1. Ziel und Gesamtablauf

Gegeben ist eine PDF mit echten Messdaten mehrerer Sensoren in einem Haus: Radon in verschiedenen Räumen, Raumklima und Wetterdaten. Ziel ist, diese Daten maschinell auszulesen und so darzustellen, dass man auf einen Blick sieht, wie hoch die Radonbelastung ist, wann sie hoch ist und womit sie zusammenhängen könnte.

```
PDF → Text (pypdf) → Tabelle (CSV) → bereinigen → daten/radon_daten.csv
                                               → dashboard/daten.js → Dashboard (index.html)
```

Das Projekt besteht aus zwei Teilen:

- **Auslesen in Python (`auslesen.py`).** Holt den Text aus der PDF, macht daraus eine Tabelle, bereinigt sie und speichert das Ergebnis.
- **Dashboard im Browser (`dashboard/index.html`).** Liest die bereinigten Daten, berechnet Kennzahlen und zeichnet die Diagramme. Es läuft ohne Server, auch direkt per Doppelklick.

## 2. Die Daten

Die PDF ist eine einzige Seite, auf der eine CSV-Tabelle als Text in sehr kleiner Schrift steht. Jede Zeile ist eine Messung, die Werte sind durch Kommas getrennt. Die Kopfzeile hat 29 Spalten, zum Beispiel `Kueche – Radon (Bq/m³)` oder `Wetter – Luftdruck (hPa)`. Die ersten beiden Spalten sind der Zeitpunkt in UTC und in Wiener Zeit.

| Eigenschaft | Wert |
|---|---|
| Messzeilen | 236 |
| Zeitraum | 24.03.2026, 20:37 bis 25.03.2026, 14:59 (18,4 Stunden) |
| Spalten mit Werten | Küche: Radon und Betriebszeit (etwa alle 5 Minuten), Wetter: 6 Werte (einmal pro Stunde) |
| leere Spalten | 19 (Büro, Schlafzimmer, Wohnzimmer, Technikraum, Werkstatt, Raumklima der Küche) |

In jeder Zeile ist meistens nur ein Teil der Spalten gefüllt, weil die Sensoren zu unterschiedlichen Zeiten senden. Der Radonwert ändert sich nur etwa alle 10 Minuten, dazwischen wird derselbe Wert noch einmal gemeldet.

## 3. Auslesen und Bereinigen (`auslesen.py`)

1. **Text aus der PDF holen.** Mit der Bibliothek `pypdf` wird der Text jeder Seite gelesen.
2. **Zeichenkodierung reparieren.** Die PDF wurde mit einer falschen Zeichenkodierung erzeugt. Aus `³` wurde `Â³`, aus dem Gedankenstrich `–` wurde `â€“`. Der Text wurde ursprünglich als UTF-8 gespeichert, aber als Windows-1252 gelesen. Das Skript macht genau diesen Schritt rückgängig.
3. **Tabelle bilden.** Jede Textzeile wird beim Komma getrennt. Gültig ist eine Zeile nur, wenn sie gleich viele Spalten hat wie die Kopfzeile. In der PDF waren alle 236 Zeilen gültig.
4. **Spaltennamen zerlegen.** Aus `Kueche – Radon (Bq/m³)` werden Ort (`Kueche`), Messgröße (`Radon`) und Einheit (`Bq/m³`). So kann das Dashboard die Spalten automatisch zuordnen, auch wenn später mehr Räume dazukommen.
5. **Sensor-Neustart erkennen.** Zu jedem Radonsensor gibt es eine Spalte „Betriebszeit“ in Minuten. Wird sie kleiner, wurde der Sensor neu gestartet. Das war am 24.03. um 21:14 der Fall.
6. **Anlaufwerte entfernen.** Direkt nach dem Neustart meldet der Sensor 0 Bq/m³, obwohl er noch nicht misst. Werte von 0 in den ersten 10 Betriebsminuten werden deshalb entfernt (3 Werte).
7. **Speichern.** `daten/radon_daten.csv` enthält die ausgelesene Tabelle unverändert, zum Nachprüfen oder für Excel. `dashboard/daten.js` enthält nur die bereinigten Messreihen. Es ist eine JavaScript-Datei statt JSON, damit der Browser sie auch ohne Server laden kann.

Zum Schluss gibt das Skript eine Übersicht im Terminal aus (Anzahl, Minimum, Mittelwert und Maximum je Messgröße).

## 4. Das Dashboard

Das Dashboard berechnet alle Kennzahlen selbst aus `daten.js`. Mit einer neuen PDF muss also nur `auslesen.py` erneut laufen. Gibt es Werte für mehrere Räume, erscheinen automatisch Schaltflächen zur Auswahl.

| Bereich | Inhalt |
|---|---|
| Kennzahlen | Mittelwert mit Bewertung, Höchst- und Tiefstwert mit Uhrzeit, Anteil der Zeit über 300 Bq/m³, letzter Wert |
| Zeitverlauf | Radonkurve mit den Grenzen 100 Bq/m³ (WHO-Empfehlung) und 300 Bq/m³ (Referenzwert in Österreich), Sensor-Neustart markiert |
| Verteilung | Anteil der Messzeit unter 100, zwischen 100 und 300 und ab 300 Bq/m³ |
| Tagesverlauf | mittlerer Radonwert je Uhrzeit |
| Auffälligkeiten | automatisch erkannt: Höchstwert, stärkster Abfall und Anstieg innerhalb einer Stunde, längste Phase über 300, Sensor-Neustart |
| Radon und Wetter | Außentemperatur, Bodentemperatur in drei Tiefen, Luftdruck und Wind auf derselben Zeitachse |
| Zusammenhang | Korrelation zwischen jedem Wetterwert und dem Radonwert zur selben Stunde |
| Tabelle | alle Werte stündlich zusammengefasst, dazu ein Link auf die CSV-Datei |

Die Diagramme werden mit der Bibliothek Chart.js gezeichnet. Jede Messgröße wird in einem eigenen Diagramm gezeigt, damit keine zwei unterschiedlichen Einheiten auf einer Achse landen. Alle Zeitachsen sind gleich breit und liegen genau untereinander. Das Dashboard hat einen hellen und einen dunklen Modus und funktioniert auch am Handy.

## 5. Ergebnisse (Küche)

- **Mittelwert:** 350 Bq/m³, also über dem österreichischen Referenzwert von 300 Bq/m³.
- **Höchstwert:** 707 Bq/m³ am 24.03. um 22:00. **Tiefstwert:** 123 Bq/m³ am 25.03. um 14:53.
- **Zeit über 300 Bq/m³:** 61 % der Messzeit, etwa 11 von 18 Stunden. Kein Messwert lag unter 100 Bq/m³.
- **Stärkster Abfall:** von 673 auf 185 Bq/m³ zwischen 22:15 und 23:11. So ein schneller Rückgang spricht für Lüften.
- **Längste Phase über 300:** 4,7 Stunden in der Nacht (02:03 bis 06:47). In der Nacht wird nicht gelüftet, das Radon sammelt sich an.
- **Wetter:** Die Korrelationen liegen zwischen −0,23 und +0,34, es gibt also nur schwache Zusammenhänge. Mit 14 Stundenwerten lässt sich daraus keine sichere Aussage ableiten.

Hinweis: Der Referenzwert bezieht sich auf das Jahresmittel. Eine Messung über 18 Stunden zeigt nur, dass die Belastung in diesem Raum genauer beobachtet werden sollte.

## 6. Probleme und Lösungen

| Problem | Lösung |
|---|---|
| Sonderzeichen in der PDF kaputt (`Â³`, `â€“`) | Text als Windows-1252 kodieren und als UTF-8 lesen |
| Werte von 0 Bq/m³ nach einem Neustart verfälschen Tiefstwert und Mittelwert | Neustart über die Betriebszeit erkennen, Anlaufwerte entfernen |
| Der Neustart wurde zuerst doppelt erkannt (Betriebszeit sprang erst von 185 auf 180, dann auf 0) | Rücksprünge innerhalb von 15 Minuten zählen als ein Neustart |
| Die Uhrzeit für den Tagesverlauf wurde falsch gelesen („20 Uhr“ statt „20“) | Uhrzeit mit einem eigenen Zahlenformat bestimmen |
| Beim Browser ist das Laden einer JSON-Datei ohne Server blockiert | Daten als JavaScript-Datei (`daten.js`) speichern |
