"""Production entry point (works on Windows and Linux): python serve.py"""
import os

from waitress import serve

from app import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    print(f"Serving MultiWire on http://0.0.0.0:{port}")
    serve(app, host="0.0.0.0", port=port, threads=8)
