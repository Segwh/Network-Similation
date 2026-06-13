"""
servidor.py — Köprü sunucu
==========================
Çalıştır: python servidor.py
Tarayıcı: http://localhost:5050
"""

import sys
import io
import json
import threading
import time
import queue
import os
import hashlib
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# Windows encoding düzeltmesi
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ── Orijinal modülleri içe aktar ─────────────────────────────────────────────
from similasyon import ag_kur, gonder
from traversal import hamilton_yolu_bul, hamilton_dongusu_bul, tsp_en_yakin_komsu
from cyrpto import affine_sifrele, affine_coz

dugumler, komsular, kenarlar, dugum_kayitlari = ag_kur()

# SSE olay kuyruğu
event_queue = queue.Queue()


def push(data: dict):
    event_queue.put(json.dumps(data, ensure_ascii=False))


# ── HTML dosya yolu (PyInstaller uyumlu) ─────────────────────────────────────
def resource_path(relative):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)

HTML_FILE = resource_path("visualizer_live.html")


# ── HTTP Handler ──────────────────────────────────────────────────────────────
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/" or path == "/index.html":
            try:
                with open(HTML_FILE, "rb") as f:
                    body = f.read()
                self._respond(200, "text/html; charset=utf-8", body)
            except FileNotFoundError:
                self._respond(404, "text/plain", b"visualizer_live.html not found")

        elif path == "/events":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            try:
                while True:
                    try:
                        msg = event_queue.get(timeout=1)
                        self.wfile.write(f"data: {msg}\n\n".encode("utf-8"))
                        self.wfile.flush()
                    except queue.Empty:
                        self.wfile.write(b": ping\n\n")
                        self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
                pass

        else:
            self._respond(404, "text/plain", b"Not found")

    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length) or b"{}")

        if path == "/send":
            threading.Thread(target=handle_send, args=(body,), daemon=True).start()
            self._respond(200, "application/json", json.dumps({"ok": True}).encode())
        elif path == "/hamilton":
            threading.Thread(target=handle_hamilton, args=(body,), daemon=True).start()
            self._respond(200, "application/json", json.dumps({"ok": True}).encode())
        elif path == "/tsp":
            threading.Thread(target=handle_tsp, args=(body,), daemon=True).start()
            self._respond(200, "application/json", json.dumps({"ok": True}).encode())
        else:
            self._respond(404, "text/plain", b"Not found")

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _respond(self, code, ctype, body: bytes):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", len(body))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)


# ── Paket Gönderim ────────────────────────────────────────────────────────────
def handle_send(body: dict):
    kaynak  = body.get("kaynak", "Istanbul")
    hedef   = body.get("hedef",  "Antalya")
    mesaj   = body.get("mesaj",  "Test mesaji")
    yontem  = body.get("yontem", "dijkstra")
    oncelik = int(body.get("oncelik", 2))

    push({"type": "start", "kaynak": kaynak, "hedef": hedef,
          "yontem": yontem, "oncelik": oncelik, "mesaj": mesaj})
    time.sleep(0.2)

    paket = gonder(
        dugumler, komsular, kenarlar, dugum_kayitlari,
        kaynak=kaynak, hedef=hedef, mesaj=mesaj,
        yontem=yontem, oncelik=oncelik, ayrintili=False,
    )

    if paket is None:
        push({"type": "error", "msg": f"Rota bulunamadi: {kaynak} -> {hedef}"})
        return

    yol     = [h["dugum"] for h in paket["hop_kaydi"]]
    sifreli = ""
    dr      = dugum_kayitlari[hedef]

    for hop in paket["hop_kaydi"]:
        # Türkçe karakter encoding sorununu atlatmak için upper() + 'in' kullan
        eylem = hop["eylem"].upper()

        if "IFRELEN" in eylem:          # ŞİFRELENDİ
            sifreli = affine_sifrele(mesaj, dr["a"], dr["b"]) or ""
            push({
                "type":     "encrypt",
                "dugum":    hop["dugum"],
                "yol":      yol,
                "a":        dr["a"],
                "b":        dr["b"],
                "sifresiz": mesaj,
                "sifreli":  sifreli,
                "checksum": paket["checksum"],
                "km":       int(paket.get("maliyet", 0)),
            })
            time.sleep(0.6)

        elif "RANS" in eylem:           # TRANSİT
            push({
                "type":    "transit",
                "dugum":   hop["dugum"],
                "yol":     yol,
                "sifreli": sifreli,
            })
            time.sleep(0.7)

        elif "ESLIM" in eylem:          # TESLİM EDİLDİ
            cozulmus = paket["payload"]
            butun = (
                paket["checksum"] ==
                hashlib.sha256(cozulmus.encode()).hexdigest()[:12]
            )
            push({
                "type":     "deliver",
                "dugum":    hop["dugum"],
                "yol":      yol,
                "sifreli":  sifreli,
                "cozulmus": cozulmus,
                "butun":    butun,
                "pkt_id":   paket["id"],
            })
            time.sleep(0.3)

    push({"type": "done", "pkt_id": paket["id"]})


# ── Hamilton ──────────────────────────────────────────────────────────────────
def handle_hamilton(body: dict):
    baslangic = body.get("baslangic") or None
    mod       = body.get("mod", "yol")

    push({"type": "hamilton_start", "baslangic": baslangic, "mod": mod})
    time.sleep(0.2)

    if mod == "dongu":
        sonuc = hamilton_dongusu_bul(dugumler, komsular, baslangic)
    else:
        sonuc = hamilton_yolu_bul(dugumler, komsular, baslangic)

    if not sonuc["bulundu"]:
        push({"type": "hamilton_error", "msg": "Hamilton yolu/dongusu bulunamadi."})
        return

    yol = sonuc["yol"]
    for i, dugum in enumerate(yol):
        push({"type": "hamilton_step", "dugum": dugum, "yol": yol,
              "adim": i, "toplam": len(yol)})
        time.sleep(0.6)

    push({"type": "hamilton_done", "yol": yol, "mod": mod})


# ── TSP ───────────────────────────────────────────────────────────────────────
def handle_tsp(body: dict):
    baslangic = body.get("baslangic") or None

    push({"type": "tsp_start", "baslangic": baslangic})
    time.sleep(0.2)

    sonuc = tsp_en_yakin_komsu(dugumler, komsular, kenarlar, baslangic)

    if not sonuc["bulundu"]:
        push({"type": "tsp_error", "msg": "TSP turu tamamlanamadi."})
        return

    yol = sonuc["yol"]
    km  = int(sonuc["maliyet"])

    for i, dugum in enumerate(yol):
        push({"type": "tsp_step", "dugum": dugum, "yol": yol,
              "adim": i, "toplam": len(yol), "km": km})
        time.sleep(0.6)

    push({"type": "tsp_done", "yol": yol, "km": km})


# ── Başlat ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    PORT = 5050
    server = ThreadingHTTPServer(("localhost", PORT), Handler)
    print(f"  Sunucu calisiyor -> http://localhost:{PORT}")
    print(f"  Durdurmak icin:    Ctrl+C\n")
    threading.Timer(1.5, lambda: __import__("webbrowser").open("http://localhost:5050")).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Sunucu kapatildi.")