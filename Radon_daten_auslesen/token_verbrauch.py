"""Zaehlt den Token-Verbrauch der Claude-Code-Sitzungen in diesem Projekt und schaetzt die Kosten.

Quelle: die lokalen Sitzungsprotokolle von Claude Code (~/.claude/projects/...).
Ausgabe: eine Markdown-Tabelle pro Sitzung + Summe, zum Einfuegen in FORTSCHRITT.md.
Start:   python token_verbrauch.py
"""

import glob
import json
import os
from datetime import datetime

# Ordner, in denen Claude Code die Sitzungen zu diesem Projekt ablegt
SESSION_DIRS = [
    os.path.expandvars(r"%USERPROFILE%\.claude\projects\c--Schule-5-Klasse-INSY-Radon-daten-auslesen"),
]

# API-Listenpreise in US-Dollar pro 1 Million Tokens (Stand 10/2026).
# Cache schreiben: 5 Minuten = 1,25x Eingabepreis, 1 Stunde = 2x Eingabepreis.
PRICES = {
    "claude-opus-5-5": {"input": 4.00, "output": 20.00, "cache_read": 0.20},
}


def read_session(path):
    """Liest eine Sitzungsdatei und summiert die Tokens aller Antworten (jede Antwort nur einmal)."""
    answers = {}
    first = last = None
    for line in open(path, encoding="utf-8"):
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        stamp = entry.get("timestamp")
        if stamp:
            first = first or stamp
            last = stamp
        message = entry.get("message") or {}
        usage = message.get("usage")
        # "<synthetic>" = von Claude Code selbst erzeugte Meldung (z. B. Abbruch), kein echter API-Aufruf
        if entry.get("type") == "assistant" and usage and message.get("model") != "<synthetic>":
            # Eine Antwort kann mehrfach protokolliert sein -> nach ihrer ID zusammenfassen
            answers[message.get("id") or entry.get("uuid")] = (message.get("model"), usage)

    total = {"answers": len(answers), "input": 0, "output": 0, "write_5m": 0, "write_1h": 0,
             "cache_read": 0, "cost": 0.0, "models": set()}
    for model, u in answers.values():
        created = u.get("cache_creation") or {}
        write_1h = created.get("ephemeral_1h_input_tokens", 0) or 0
        write_5m = (u.get("cache_creation_input_tokens") or 0) - write_1h
        row = {"input": u.get("input_tokens") or 0, "output": u.get("output_tokens") or 0,
               "write_5m": write_5m, "write_1h": write_1h,
               "cache_read": u.get("cache_read_input_tokens") or 0}
        for key, value in row.items():
            total[key] += value
        total["models"].add(model)
        price = PRICES.get(model)
        if price is None:
            total["cost"] = float("nan")   # unbekanntes Modell -> keine Kostenschaetzung
            continue
        total["cost"] += (row["input"] * price["input"] + row["output"] * price["output"]
                          + row["write_5m"] * price["input"] * 1.25
                          + row["write_1h"] * price["input"] * 2
                          + row["cache_read"] * price["cache_read"]) / 1_000_000
    total["start"], total["end"] = first, last
    return total


def fmt(n):
    """Zahl mit Tausenderpunkten, z. B. 1.234.567."""
    return f"{n:,}".replace(",", ".")


def money(value):
    """Dollarbetrag mit Komma, z. B. 1,44 $."""
    return f"{value:.2f} $".replace(".", ",")


def local_time(stamp):
    return datetime.fromisoformat(stamp.replace("Z", "+00:00")).astimezone()


def main():
    files = [f for d in SESSION_DIRS for f in glob.glob(os.path.join(d, "*.jsonl"))]
    sessions = sorted((read_session(f) for f in files), key=lambda s: s["start"] or "")
    sessions = [s for s in sessions if s["answers"]]

    print("| Sitzung | Dauer | Antworten | Eingabe | Ausgabe | Cache geschrieben | Cache gelesen | Kosten (API-Preis) |")
    print("|---|---|---|---|---|---|---|---|")
    sum_cost = 0.0
    keys = ("answers", "input", "output", "write_5m", "write_1h", "cache_read")
    sums = dict.fromkeys(keys, 0)
    for s in sessions:
        start, end = local_time(s["start"]), local_time(s["end"])
        minutes = round((end - start).total_seconds() / 60)
        print(f"| {start:%d.%m.%Y %H:%M} | {minutes} min | {s['answers']} | {fmt(s['input'])} | "
              f"{fmt(s['output'])} | {fmt(s['write_5m'] + s['write_1h'])} | {fmt(s['cache_read'])} | "
              f"{money(s['cost'])} |")
        sum_cost += s["cost"]
        for k in keys:
            sums[k] += s[k]
    print(f"| **Summe** | | {sums['answers']} | {fmt(sums['input'])} | {fmt(sums['output'])} | "
          f"{fmt(sums['write_5m'] + sums['write_1h'])} | {fmt(sums['cache_read'])} | **{money(sum_cost)}** |")
    models = sorted({m for s in sessions for m in s["models"] if m})
    print(f"\nModell(e): {', '.join(models)}")


if __name__ == "__main__":
    main()
