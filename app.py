# Sentinel AI V2.0 - Streamlit Cloud Entry Point
# Starts the FastAPI backend in a background thread, then runs the Streamlit frontend.
# Allows single-process deployment on Streamlit Community Cloud.
import threading
import time
import os
import sys
import socket

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def ensure_data_ready():
    """Run setup pipeline on Streamlit Cloud if data/models are missing."""
    if not os.path.exists("datasets/processed/unified_intelligence.parquet") or not os.path.exists("models/trained_model.pkl"):
        import subprocess
        print("Data or models missing. Running setup_data_pipeline.py...")
        subprocess.run([sys.executable, "setup_data_pipeline.py"], check=True)
        print("Setup complete.")

def _start_api():
    import uvicorn
    ensure_data_ready()
    uvicorn.run(
        "api.main:app",
        host="127.0.0.1",
        port=8001,
        log_level="warning",
        reload=False,
    )


# Only launch if the port isn't already bound (Streamlit reruns this file on every interaction!)
if not is_port_in_use(8001):
    _thread = threading.Thread(target=_start_api, daemon=True)
    _thread.start()
    time.sleep(2)  # Give FastAPI time to bind to port

# Run the main Streamlit frontend
from frontend.app import *

