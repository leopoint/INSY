"""Liest die Radon-Messdaten aus der PDF und bereitet sie fuer das Dashboard auf.

Die PDF enthaelt eine CSV-Tabelle als Text (eine Zeile pro Messung, Werte durch Kommas getrennt).
Ablauf:  PDF -> Text -> Tabelle -> bereinigen -> daten/radon_daten.csv + dashboard/daten.js
Start:   python auslesen.py                (nimmt daten/radon_sample_data.pdf)
         python auslesen.py andere.pdf     (beliebige PDF mit demselben Aufbau)
"""

import csv
import io
import json
import os
import sys
from datetime import datetime, timezone

from pypdf import PdfReader

ORDNER = os.path.dirname(os.path.abspath(__file__))
STANDARD_PDF = os.path.join(ORDNER, "daten", "radon_sample_data.pdf")
CSV_AUSGABE = os.path.join(ORDNER, "daten", "radon_daten.csv")
JS_AUSGABE = os.path.join(ORDNER, "dashboard", "daten.js")

# Ein Radonsensor braucht nach dem Einschalten ein paar Minuten, bis er echte Werte liefert.
# Werte mit 0 Bq/m³ in den ersten 10 Betriebsminuten sind deshalb keine Messung, sondern Anlaufphase.
ANLAUF_MINUTEN = 10


def pdf_zu_text(pfad):
    """Holt den Text aus allen Seiten der PDF."""
    seiten = PdfReader(pfad).pages
    text = "\n".join(seite.extract_text() for seite in seiten)
    return zeichen_reparieren(text)


def zeichen_reparieren(text):
    """Die PDF wurde mit falscher Zeichenkodierung erzeugt: aus '³' wird 'Â³', aus '–' wird 'â€“'.
    Zurueckverwandeln (Text als Windows-1252 auffassen und als UTF-8 lesen) repariert das.
    Klappt das nicht, war der Text schon richtig und bleibt unveraendert."""
    try:
        return text.encode("cp1252").decode("utf-8")
    except UnicodeError:
        return text


def text_zu_tabelle(text):
    """Macht aus dem Text eine Tabelle: Kopfzeile + Liste von Zeilen.
    Eine Zeile gilt nur, wenn sie gleich viele Spalten wie die Kopfzeile hat."""
    zeilen = [z for z in text.splitlines() if z.strip()]
    tabelle = list(csv.reader(zeilen))
    kopf = tabelle[0]
    gueltig = [z for z in tabelle[1:] if len(z) == len(kopf)]
    kaputt = len(tabelle) - 1 - len(gueltig)
    return kopf, gueltig, kaputt


def spalte_zerlegen(name):
    """'Kueche – Radon (Bq/m³)' -> ('Kueche', 'Radon', 'Bq/m³')."""
    ort, _, rest = name.partition(" – ")
    groesse, _, einheit = rest.rpartition(" (")
    return ort.strip(), groesse.strip(), einheit.rstrip(")")


def zahl(text):
    """Text in Zahl umwandeln, leere Felder werden zu None."""
    return float(text) if text.strip() else None


def bereinigen(kopf, zeilen):
    """Baut pro Messgroesse eine Liste von Punkten (Zeit, Wert) und wirft Anlaufwerte weg."""
    reihen = {}
    entfernt = []
    neustarts = []       # Zeitpunkte, an denen ein Sensor neu gestartet wurde
    letzte_betriebszeit = {}
    for i, name in enumerate(kopf[2:], start=2):
        ort, groesse, einheit = spalte_zerlegen(name)
        reihen[name] = {"ort": ort, "groesse": groesse, "einheit": einheit, "punkte": []}

    for z in zeilen:
        utc = datetime.fromisoformat(z[0].replace("Z", "+00:00")).astimezone(timezone.utc)
        ms = int(utc.timestamp() * 1000)
        for i, name in enumerate(kopf[2:], start=2):
            wert = zahl(z[i])
            if wert is None:
                continue
            reihe = reihen[name]
            if reihe["groesse"] == "Radon":
                betrieb = zahl(z[i + 1]) if i + 1 < len(kopf) and "Betriebszeit" in kopf[i + 1] else None
                # Betriebszeit wird kleiner -> der Sensor hat neu gestartet
                if betrieb is not None:
                    vorher = letzte_betriebszeit.get(name)
                    if vorher is not None and betrieb < vorher:
                        # mehrere Ruecksprunge innerhalb von 15 Minuten zaehlen als ein Neustart
                        frueher = [n for n in neustarts if n["ort"] == reihe["ort"] and ms - n["zeit"] < 15 * 60000]
                        if not frueher:
                            neustarts.append({"ort": reihe["ort"], "zeit": ms})
                    letzte_betriebszeit[name] = betrieb
                if wert == 0 and betrieb is not None and betrieb < ANLAUF_MINUTEN:
                    entfernt.append((z[1], reihe["ort"], betrieb))
                    continue
            reihe["punkte"].append([ms, wert])

    # Spalten ganz ohne Werte (z. B. Raeume ohne Sensor in diesem Zeitraum) weglassen
    leer = [n for n, r in reihen.items() if not r["punkte"]]
    reihen = {n: r for n, r in reihen.items() if r["punkte"]}
    return reihen, entfernt, leer, neustarts


def csv_schreiben(kopf, zeilen, pfad):
    """Speichert die ausgelesene Tabelle unveraendert als CSV (zum Nachpruefen und fuer Excel)."""
    with open(pfad, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(kopf)
        w.writerows(zeilen)


def js_schreiben(reihen, neustarts, entfernt, quelle, anzahl, pfad):
    """Speichert die Daten als JavaScript-Datei. So kann das Dashboard sie auch ohne Server laden
    (einfach index.html doppelklicken) und genauso auf GitHub Pages."""
    daten = {
        "quelle": os.path.basename(quelle),
        "erzeugt": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "zeilen": anzahl,
        "entfernt": len(entfernt),
        "neustarts": neustarts,
        "reihen": list(reihen.values()),
    }
    with open(pfad, "w", encoding="utf-8") as f:
        f.write("// Automatisch erzeugt von auslesen.py, nicht von Hand aendern\n")
        f.write("const DATEN = ")
        json.dump(daten, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")


def zusammenfassung(reihen, entfernt, leer, kaputt, neustarts):
    """Gibt die wichtigsten Kennzahlen im Terminal aus, damit man das Ergebnis sofort sieht."""
    print(f"Ungueltige Zeilen: {kaputt}")
    print(f"Leere Spalten (kein Sensor/keine Werte): {len(leer)}")
    print(f"Sensor-Neustarts: {len(neustarts)}")
    print(f"Entfernte Anlaufwerte (0 Bq/m³ kurz nach Neustart): {len(entfernt)}")
    for zeit, ort, betrieb in entfernt:
        print(f"   {zeit}  {ort}  Betriebszeit {betrieb:.0f} min")
    print()
    print(f"{'Messgroesse':<45} {'Anzahl':>6} {'Min':>8} {'Mittel':>8} {'Max':>8}")
    for name, r in reihen.items():
        werte = [p[1] for p in r["punkte"]]
        mittel = sum(werte) / len(werte)
        print(f"{name:<45} {len(werte):>6} {min(werte):>8.1f} {mittel:>8.1f} {max(werte):>8.1f}")


def main():
    pdf = sys.argv[1] if len(sys.argv) > 1 else STANDARD_PDF
    print(f"Lese {pdf} ...")
    kopf, zeilen, kaputt = text_zu_tabelle(pdf_zu_text(pdf))
    print(f"{len(zeilen)} Messzeilen, {len(kopf)} Spalten, "
          f"von {zeilen[0][1]} bis {zeilen[-1][1]} (Wiener Zeit)\n")

    reihen, entfernt, leer, neustarts = bereinigen(kopf, zeilen)
    # Betriebszeit ist nur eine Hilfsspalte zum Bereinigen, im Dashboard braucht man sie nicht
    reihen = {n: r for n, r in reihen.items() if r["groesse"] != "Betriebszeit"}
    zusammenfassung(reihen, entfernt, leer, kaputt, neustarts)

    csv_schreiben(kopf, zeilen, CSV_AUSGABE)
    js_schreiben(reihen, neustarts, entfernt, pdf, len(zeilen), JS_AUSGABE)
    print(f"\nGespeichert: {os.path.relpath(CSV_AUSGABE, ORDNER)} und {os.path.relpath(JS_AUSGABE, ORDNER)}")


if __name__ == "__main__":
    main()
