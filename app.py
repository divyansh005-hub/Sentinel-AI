# Sentinel AI V2.0 - Streamlit Cloud Entry Point
# Starts the FastAPI backend in a background thread, then runs the Streamlit frontend.
# Allows single-process deployment on Streamlit Community Cloud.
import threading
import time
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _start_api():
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="127.0.0.1",
        port=8001,
        log_level="warning",
        reload=False,
    )


# Launch FastAPI in a background daemon thread
_thread = threading.Thread(target=_start_api, daemon=True)
_thread.start()
time.sleep(2)  # Give FastAPI time to bind to port

# Run the main Streamlit frontend
from frontend.app import *
