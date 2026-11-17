"""Liest die Radon-Messdaten (CSV oder PDF) ein und bereitet sie fuer das Dashboard auf.

Die Daten sind eine Tabelle: eine Zeile pro Messung, Werte durch Kommas getrennt.
Bei der PDF steht diese Tabelle als Text auf der Seite und muss erst herausgeholt werden.
Ablauf:  Datei -> Text -> Tabelle -> bereinigen -> Lueften erkennen -> Stundenwerte -> daten/radon_stuendlich.csv
                                                                 -> dashboard/daten.js
Start:   python auslesen.py                (nimmt daten/radon_alle_raeume.csv)
         python auslesen.py andere.pdf     (oder eine andere CSV/PDF mit demselben Aufbau)
"""

import csv
import json
import os
import sys
from datetime import datetime, timedelta, timezone

ORDNER = os.path.dirname(os.path.abspath(__file__))
STANDARD_DATEI = os.path.join(ORDNER, "daten", "radon_alle_raeume.csv")
CSV_AUSGABE = os.path.join(ORDNER, "daten", "radon_stuendlich.csv")
JS_AUSGABE = os.path.join(ORDNER, "dashboard", "daten.js")

STUNDE = 3600 * 1000          # eine Stunde in Millisekunden
# Ein Radonsensor braucht nach dem Einschalten ein paar Minuten, bis er echte Werte liefert.
# Werte mit 0 Bq/m³ in den ersten 10 Betriebsminuten sind deshalb keine Messung, sondern Anlaufphase.
ANLAUF_MINUTEN = 10


def datei_zu_text(pfad):
    """Holt den Text aus einer CSV- oder PDF-Datei."""
    if pfad.lower().endswith(".pdf"):
        from pypdf import PdfReader          # nur noetig, wenn wirklich eine PDF gelesen wird
        text = "\n".join(seite.extract_text() for seite in PdfReader(pfad).pages)
        return zeichen_reparieren(text)
    with open(pfad, encoding="utf-8-sig") as f:
        return f.read()


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
    tabelle = list(csv.reader(z for z in text.splitlines() if z.strip()))
    kopf = tabelle[0]
    gueltig = [z for z in tabelle[1:] if len(z) == len(kopf)]
    kaputt = len(tabelle) - 1 - len(gueltig)
    return kopf, gueltig, kaputt


def spalte_zerlegen(name):
    """'Kueche (Luft) – CO₂ (ppm)' -> ('Kueche', 'CO₂', 'ppm'). Der Zusatz '(Luft)' bezeichnet nur
    das Messgeraet fuer das Raumklima, der Raum ist derselbe."""
    ort, _, rest = name.partition(" – ")
    groesse, _, einheit = rest.rpartition(" (")
    return ort.replace(" (Luft)", "").strip(), groesse.strip(), einheit.rstrip(")")


def zahl(text):
    """Text in Zahl umwandeln, leere Felder werden zu None."""
    return float(text) if text.strip() else None


def bereinigen(kopf, zeilen):
    """Baut pro Messgroesse eine Liste von Punkten (Zeit, Wert), erkennt Sensor-Neustarts
    und wirft Anlaufwerte weg."""
    reihen = {}
    entfernt = []
    neustarts = []       # Zeitpunkte, an denen ein Sensor neu gestartet wurde
    letzte_betriebszeit = {}
    for name in kopf[2:]:
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
                wert = abs(wert)          # "-0.0" kommt vor und ist einfach 0
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

    # Spalten ganz ohne Werte weglassen, Betriebszeit wird nur zum Bereinigen gebraucht
    leer = [n for n, r in reihen.items() if not r["punkte"]]
    reihen = {n: r for n, r in reihen.items() if r["punkte"] and r["groesse"] != "Betriebszeit"}
    return reihen, entfernt, leer, neustarts


def lueften_erkennen(reihen, neustarts):
    """Erkennt, wann gelueftet wurde. Beim Lueften kommt frische Aussenluft herein, deshalb faellt
    - CO₂ schnell: mindestens 150 ppm innerhalb von 30 Minuten (nur Kueche und Schlafzimmer haben CO₂), oder
    - Radon schnell: von mindestens 100 Bq/m³ um mindestens 60 Bq/m³ und auf hoechstens 65 % innerhalb von 1 Stunde.
    Ereignisse im selben Raum, die weniger als 1 Stunde auseinanderliegen, gelten als ein Lueften."""
    REGELN = {"CO₂": (30, lambda a, m: a - m >= 150, 2),
              "Radon": (60, lambda a, m: a >= 100 and a - m >= 60 and m <= 0.65 * a, 3)}
    ereignisse = []
    for r in reihen.values():
        if r["groesse"] not in REGELN:
            continue
        minuten, faellt, abstand_h = REGELN[r["groesse"]]
        raum = r["ort"].replace(" - Sockel", "")          # Sockel-Sensor steht in der Kueche
        p, letztes = r["punkte"], None
        ende = 0
        for j, (ms, wert) in enumerate(p):
            if letztes is not None and ms - letztes < abstand_h * STUNDE:
                continue
            ende = max(ende, j)
            while ende + 1 < len(p) and p[ende + 1][0] - ms <= minuten * 60000:
                ende += 1
            tief = min(x[1] for x in p[j:ende + 1])
            if not faellt(wert, tief):
                continue
            # Abfall durch einen Sensor-Neustart ist kein Lueften
            if any(n["ort"] == r["ort"] and ms <= n["zeit"] <= p[ende][0] for n in neustarts):
                continue
            ereignisse.append({"ort": raum, "zeit": ms, "groesse": r["groesse"], "von": wert, "bis": tief})
            letztes = ms

    # gleiches Lueften, das von mehreren Sensoren im selben Raum erkannt wurde, zusammenfassen
    ereignisse.sort(key=lambda e: (e["ort"], e["zeit"]))
    zusammen = []
    for e in ereignisse:
        vorher = zusammen[-1] if zusammen else None
        if vorher and vorher["ort"] == e["ort"] and e["zeit"] - vorher["zeit"] < STUNDE:
            vorher["hinweis"].append(f"{e['groesse']} {e['von']:.0f}→{e['bis']:.0f}")
        else:
            zusammen.append({"ort": e["ort"], "zeit": e["zeit"], "hinweis": [f"{e['groesse']} {e['von']:.0f}→{e['bis']:.0f}"]})
    return sorted(zusammen, key=lambda e: e["zeit"])


def statistik(reihe):
    """Kennzahlen aus den Rohwerten: Anzahl, Mittel, Min/Max mit Zeitpunkt, erster/letzter Messzeitpunkt."""
    p = reihe["punkte"]
    werte = [x[1] for x in p]
    mx = max(p, key=lambda x: x[1])
    mn = min(p, key=lambda x: x[1])
    # Luecken: Zeitraeume ueber 2 Stunden ohne Messwert (Sensor aus, kein WLAN, ...)
    luecken = [b[0] - a[0] for a, b in zip(p, p[1:]) if b[0] - a[0] > 2 * STUNDE]
    return {"anzahl": len(p), "mittel": round(sum(werte) / len(werte), 2),
            "max": mx[1], "maxZeit": mx[0], "min": mn[1], "minZeit": mn[0],
            "von": p[0][0], "bis": p[-1][0],
            "luecken": len(luecken), "laengsteLuecke": max(luecken, default=0)}


def stundenwerte(reihen):
    """Fasst alle Messungen zu Stundenmittelwerten zusammen (gemeinsames Zeitraster fuer alle Groessen).
    Aus z. B. 12 Radonwerten zwischen 14:00 und 15:00 wird ein Mittelwert. Das macht die Datenmenge
    fuer das Dashboard etwa 40-mal kleiner, ohne dass im Verlauf etwas Wichtiges verloren geht."""
    start = min(r["punkte"][0][0] for r in reihen.values()) // STUNDE * STUNDE
    ende = max(r["punkte"][-1][0] for r in reihen.values()) // STUNDE * STUNDE
    anzahl = (ende - start) // STUNDE + 1
    for r in reihen.values():
        summe = [0.0] * anzahl
        zaehler = [0] * anzahl
        for ms, wert in r["punkte"]:
            k = (ms - start) // STUNDE
            summe[k] += wert
            zaehler[k] += 1
        stellen = 1 if r["groesse"] == "Radon" else 2
        r["werte"] = [round(s / n, stellen) if n else None for s, n in zip(summe, zaehler)]
    return start, anzahl


def wiener_zeit(ms):
    """UTC -> Wiener Zeit. Sommerzeit gilt vom letzten Sonntag im Maerz bis zum letzten Sonntag
    im Oktober, jeweils ab 01:00 UTC."""
    utc = datetime.fromtimestamp(ms / 1000, timezone.utc)

    def letzter_sonntag(monat):
        tag = datetime(utc.year, monat, 31, 1, tzinfo=timezone.utc)
        return tag - timedelta(days=(tag.weekday() + 1) % 7)

    sommer = letzter_sonntag(3) <= utc < letzter_sonntag(10)
    return utc + timedelta(hours=2 if sommer else 1)


def csv_schreiben(reihen, start, anzahl, pfad):
    """Speichert die Stundenwerte als CSV (eine Spalte pro Messgroesse), z. B. fuer Excel."""
    namen = list(reihen)
    with open(pfad, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["Stunde (Europe/Vienna)"] + namen)
        for k in range(anzahl):
            werte = [reihen[n]["werte"][k] for n in namen]
            if any(v is not None for v in werte):
                zeit = wiener_zeit(start + k * STUNDE).strftime("%Y-%m-%d %H:00")
                w.writerow([zeit] + ["" if v is None else v for v in werte])


def js_schreiben(reihen, start, neustarts, lueften, entfernt, quelle, anzahl_zeilen, pfad):
    """Speichert die Daten als JavaScript-Datei. So kann das Dashboard sie auch ohne Server laden
    (einfach index.html doppelklicken) und genauso auf GitHub Pages."""
    daten = {
        "quelle": os.path.basename(quelle),
        "erzeugt": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "zeilen": anzahl_zeilen,
        "entfernt": len(entfernt),
        "start": start,
        "schritt": STUNDE,
        "neustarts": neustarts,
        "lueften": lueften,
        "reihen": [{"ort": r["ort"], "groesse": r["groesse"], "einheit": r["einheit"],
                    "stat": r["stat"], "werte": r["werte"]} for r in reihen.values()],
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
    print()
    print(f"{'Messgroesse':<42} {'Anzahl':>7} {'Min':>8} {'Mittel':>8} {'Max':>8}")
    for name, r in reihen.items():
        s = r["stat"]
        print(f"{name:<42} {s['anzahl']:>7} {s['min']:>8.1f} {s['mittel']:>8.1f} {s['max']:>8.1f}")


def main():
    datei = sys.argv[1] if len(sys.argv) > 1 else STANDARD_DATEI
    print(f"Lese {datei} ...")
    kopf, zeilen, kaputt = text_zu_tabelle(datei_zu_text(datei))
    print(f"{len(zeilen)} Messzeilen, {len(kopf)} Spalten, "
          f"von {zeilen[0][1]} bis {zeilen[-1][1]} (Wiener Zeit)\n")

    reihen, entfernt, leer, neustarts = bereinigen(kopf, zeilen)
    for r in reihen.values():
        r["stat"] = statistik(r)
        r["stat"]["entfernt"] = sum(1 for e in entfernt if e[1] == r["ort"] and r["groesse"] == "Radon")
    zusammenfassung(reihen, entfernt, leer, kaputt, neustarts)
    lueften = lueften_erkennen(reihen, neustarts)
    print(f"Erkannte Lueftungen: {len(lueften)}")
    for ort in sorted({e['ort'] for e in lueften}):
        print(f"   {ort:<14} {sum(1 for e in lueften if e['ort'] == ort)}")

    start, anzahl = stundenwerte(reihen)
    csv_schreiben(reihen, start, anzahl, CSV_AUSGABE)
    js_schreiben(reihen, start, neustarts, lueften, entfernt, datei, len(zeilen), JS_AUSGABE)
    print(f"\n{anzahl} Stunden. Gespeichert: {os.path.relpath(CSV_AUSGABE, ORDNER)} "
          f"und {os.path.relpath(JS_AUSGABE, ORDNER)}")


if __name__ == "__main__":
    main()
