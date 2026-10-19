"""Lokale Weboberflaeche: startet alle Projekt-Programme und zeigt live, was passiert.

Start:  python gui/server.py   ->  im Browser http://localhost:8000 oeffnen
Nur Python-Standardbibliothek + NumPy (fuer die Netz-Vorschau), keine Installation noetig.
"""

import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
GUI_DIR = ROOT / "gui"
MODEL_DIR = ROOT / "models"
PY_DIR = ROOT / "part1_2_python"
PORT = 8000
BUILD_DIR = Path(tempfile.gettempdir()) / "nn_from_scratch_build"  # .exe landen hier, nicht im Projekt

sys.dont_write_bytecode = True  # keine __pycache__-Ordner im Projekt anlegen
sys.path.insert(0, str(PY_DIR))
from nn import NeuralNetwork  # noqa: E402  (eigenes Netz fuer die Live-Vorschau)


def find_gcc():
    """Sucht gcc im PATH oder im winget-Installationsordner von WinLibs."""
    found = shutil.which("gcc")
    if found:
        return found
    pattern = os.path.join(
        os.environ.get("LOCALAPPDATA", ""),
        "Microsoft", "WinGet", "Packages", "BrechtSanders.WinLibs*", "mingw64", "bin", "gcc.exe",
    )
    matches = glob.glob(pattern)
    return matches[0] if matches else None


# Alle Programme, die die Oberflaeche starten darf (feste Liste -> nichts Beliebiges ausfuehrbar).
# Jede Aufgabe ist eine Folge von Befehlen; schlaegt einer fehl, wird abgebrochen.
def build_tasks():
    py = sys.executable
    gcc = find_gcc() or "gcc"
    c4 = ROOT / "part4_c_txt"
    c5 = ROOT / "part5_c_header"
    exe4 = str(BUILD_DIR / "nn_txt.exe")
    exe5 = str(BUILD_DIR / "nn_header.exe")
    return {
        "train_xor": {
            "title": "XOR trainieren (2-2-1)", "part": "Part 1/2",
            "steps": [([py, "-u", "train_xor.py"], PY_DIR)],
        },
        "train_7seg": {
            "title": "7-Segment trainieren (4-16-7)", "part": "Part 1/2",
            "steps": [([py, "-u", "train_7seg.py"], PY_DIR)],
        },
        "tf_xor": {
            "title": "XOR mit TensorFlow", "part": "Part 3",
            "steps": [([py, "-u", "tf_xor.py"], ROOT / "part3_tensorflow")],
        },
        "tf_7seg": {
            "title": "7-Segment mit TensorFlow", "part": "Part 3",
            "steps": [([py, "-u", "tf_7seg.py"], ROOT / "part3_tensorflow")],
        },
        "c_txt": {
            "title": "C: Gewichte aus 7seg.txt", "part": "Part 4",
            "steps": [
                ([gcc, "-Wall", "-O2", "-o", exe4, "main.c", "nn.c", "-lm"], c4),
                ([exe4], c4),
            ],
        },
        "c_header": {
            "title": "C: Gewichte aus 7seg_net.h", "part": "Part 5",
            "steps": [
                ([gcc, "-Wall", "-O2", "-o", exe5, "main.c", "nn.c", "-lm"], c5),
                ([exe5], c5),
            ],
        },
    }


TASKS = build_tasks()


class Job:
    """Merkt sich das gerade laufende Programm und seine Ausgabe (immer nur eins gleichzeitig)."""

    def __init__(self):
        self.lock = threading.Lock()
        self.task = None
        self.lines = []
        self.status = "idle"      # idle | running | done | error | stopped
        self.started = None
        self.finished = None
        self.proc = None

    def start(self, task_id):
        with self.lock:
            if self.status == "running":
                return False
            self.task = task_id
            self.lines = []
            self.status = "running"
            self.started = time.time()
            self.finished = None
        threading.Thread(target=self._run, args=(task_id,), daemon=True).start()
        return True

    def _run(self, task_id):
        """Fuehrt die Befehle der Aufgabe nacheinander aus und sammelt jede Ausgabezeile."""
        env = dict(os.environ, PYTHONUNBUFFERED="1", PYTHONIOENCODING="utf-8",
                   PYTHONDONTWRITEBYTECODE="1", TF_CPP_MIN_LOG_LEVEL="2")
        BUILD_DIR.mkdir(exist_ok=True)
        gcc = find_gcc()
        if gcc:
            env["PATH"] = os.path.dirname(gcc) + os.pathsep + env.get("PATH", "")
        result = "done"
        for cmd, cwd in TASKS[task_id]["steps"]:
            self.lines.append(f"$ {' '.join(Path(c).name if i == 0 else c for i, c in enumerate(cmd))}")
            try:
                self.proc = subprocess.Popen(
                    cmd, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
            except OSError as error:
                self.lines.append(f"Fehler beim Start: {error}")
                result = "error"
                break
            for raw in self.proc.stdout:
                self.lines.append(raw.decode("utf-8", errors="replace").rstrip("\r\n"))
            code = self.proc.wait()
            if self.status == "stopped":
                result = "stopped"
                break
            if code != 0:
                self.lines.append(f"(Programm beendet mit Code {code})")
                result = "error"
                break
        with self.lock:
            if self.status != "stopped":
                self.status = result
            self.finished = time.time()
            self.proc = None

    def stop(self):
        with self.lock:
            if self.status == "running" and self.proc:
                self.status = "stopped"
                self.proc.kill()
                self.lines.append("(vom Benutzer abgebrochen)")

    def snapshot(self, since):
        end = self.finished or time.time()
        return {
            "task": self.task,
            "status": self.status,
            "lines": self.lines[since:],
            "total": len(self.lines),
            "elapsed": round(end - self.started, 1) if self.started else 0,
        }


JOB = Job()


def model_info(name):
    """Liefert Netzgroesse, Gewichte und Biases eines gespeicherten Modells (fuer die Netz-Grafik)."""
    data = json.loads((MODEL_DIR / f"{name}.json").read_text(encoding="utf-8"))
    return {"layer_sizes": data["layer_sizes"], "layers": data["layers"]}


def predict(name, inputs):
    """Schickt eine Eingabe durchs gespeicherte Netz und gibt die Werte JEDER Schicht zurueck."""
    network = NeuralNetwork.load(MODEL_DIR / f"{name}.json")
    activations = [list(map(float, inputs))]
    current = inputs
    for layer in network.layers:
        current = layer.forward(current)
        activations.append([float(v) for v in current])
    return {"activations": activations}


class Handler(BaseHTTPRequestHandler):
    """Beantwortet die Anfragen der Webseite (HTML-Seite und die /api/...-Befehle)."""

    def log_message(self, *args):
        pass  # Konsole des Servers ruhig halten

    def send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, path, content_type):
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urlparse(self.path)
        query = parse_qs(url.query)
        try:
            if url.path == "/":
                self.send_file(GUI_DIR / "index.html", "text/html; charset=utf-8")
            elif url.path == "/api/tasks":
                self.send_json({
                    "tasks": [{"id": k, "title": v["title"], "part": v["part"]}
                              for k, v in TASKS.items()],
                    "gcc": find_gcc() is not None,
                })
            elif url.path == "/api/log":
                self.send_json(JOB.snapshot(int(query.get("since", ["0"])[0])))
            elif url.path == "/api/model":
                name = query.get("name", ["7seg"])[0]
                if name not in ("xor", "7seg"):
                    raise ValueError("unbekanntes Modell")
                self.send_json(model_info(name))
            elif url.path == "/api/predict":
                name = query.get("name", ["7seg"])[0]
                if name not in ("xor", "7seg"):
                    raise ValueError("unbekanntes Modell")
                inputs = [float(v) for v in query.get("x", [""])[0].split(",")]
                self.send_json(predict(name, inputs))
            else:
                self.send_json({"error": "nicht gefunden"}, 404)
        except FileNotFoundError:
            self.send_json({"error": "Modell noch nicht trainiert"}, 404)
        except (ValueError, KeyError) as error:
            self.send_json({"error": str(error)}, 400)

    def do_POST(self):
        url = urlparse(self.path)
        if url.path.startswith("/api/run/"):
            task_id = url.path.rsplit("/", 1)[-1]
            if task_id not in TASKS:
                self.send_json({"error": "unbekannte Aufgabe"}, 400)
            elif JOB.start(task_id):
                self.send_json({"ok": True})
            else:
                self.send_json({"error": "Es laeuft schon ein Programm"}, 409)
        elif url.path == "/api/stop":
            JOB.stop()
            self.send_json({"ok": True})
        else:
            self.send_json({"error": "nicht gefunden"}, 404)


def main():
    # Nur 127.0.0.1 -> die Seite ist ausschliesslich von diesem PC aus erreichbar.
    try:
        server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    except OSError:
        print(f"Port {PORT} ist belegt - laeuft die Oberflaeche schon? Sonst http://localhost:{PORT} oeffnen.")
        return
    print(f"Oberflaeche laeuft: http://localhost:{PORT}  (Beenden mit Strg+C)")
    if "--no-browser" not in sys.argv:
        webbrowser.open(f"http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer beendet.")


if __name__ == "__main__":
    main()
