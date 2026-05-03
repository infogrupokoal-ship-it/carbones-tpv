# local_print_bridge.py
# Bridge local Windows: recibe JSON {ticket, raw} y manda a impresora
import os
import tempfile
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

PRINTER_NAME = os.getenv("PRINTER_NAME", "").strip()
PORT = int(os.getenv("BRIDGE_PORT", "8181"))

def print_text_windows(text: str, printer_name: str = ""):
    """
    Estrategia:
    1) Guarda ticket a .txt temporal (UTF-8)
    2) Usa PowerShell + Notepad /p para imprimir texto plano
    Nota: para tickets térmicos, mejor driver Generic/Text.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as f:
        f.write(text)
        path = f.name

    try:
        if printer_name:
            # Imprimir a impresora concreta con Start-Process (notepad /p)
            ps = (
                f'$p="{path}"; '
                f'$printer="{printer_name}"; '
                f'Start-Process -FilePath notepad.exe -ArgumentList "/p `"$p`"" -WindowStyle Hidden; '
                f'Start-Sleep -Milliseconds 800; '
                f'"OK"'
            )
        else:
            # Impresora por defecto
            ps = (
                f'$p="{path}"; '
                f'Start-Process -FilePath notepad.exe -ArgumentList "/p `"$p`"" -WindowStyle Hidden; '
                f'Start-Sleep -Milliseconds 800; '
                f'"OK"'
            )

        completed = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
            capture_output=True, text=True, timeout=15
        )

        if completed.returncode != 0:
            return False, f"PowerShell error: {completed.stderr.strip()}"

        return True, "Printed"
    except Exception as e:
        return False, str(e)
    finally:
        try:
            os.remove(path)
        except Exception:
            pass


@app.get("/health")
def health():
    return jsonify({
        "ok": True,
        "service": "local-print-bridge",
        "printer": PRINTER_NAME or "(default)",
        "port": PORT
    })


@app.post("/print")
def print_endpoint():
    data = request.get_json(silent=True) or {}
    ticket = data.get("ticket", "")
    if not ticket:
        return jsonify({"ok": False, "message": "Missing 'ticket' text"}), 400

    ok, detail = print_text_windows(ticket, PRINTER_NAME)
    status = 200 if ok else 500
    return jsonify({"ok": ok, "message": detail}), status


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=PORT, debug=False)
