"""
Patches all Streamlit page files and frontend/app.py with a sys.path fix
so they work correctly on Streamlit Cloud.
"""
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
PAGES_DIR = os.path.join(ROOT, "frontend", "pages")
APP_PATH = os.path.join(ROOT, "frontend", "app.py")

# Path fix for pages (2 levels up from frontend/pages/ to get to root)
PAGES_FIX = (
    "import sys, os\n"
    "sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))\n"
)

# Path fix for frontend/app.py (1 level up from frontend/ to get to root)
APP_FIX = (
    "import sys, os\n"
    "sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))\n"
)

for fname in sorted(os.listdir(PAGES_DIR)):
    if fname.endswith(".py") and not fname.startswith("__"):
        fpath = os.path.join(PAGES_DIR, fname)
        with open(fpath, encoding="utf-8") as f:
            content = f.read()
        if "sys.path.insert" not in content:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(PAGES_FIX + content)
            print(f"Patched: frontend/pages/{fname}")
        else:
            print(f"Already patched: {fname}")

with open(APP_PATH, encoding="utf-8") as f:
    content = f.read()
if "sys.path.insert" not in content:
    with open(APP_PATH, "w", encoding="utf-8") as f:
        f.write(APP_FIX + content)
    print("Patched: frontend/app.py")
else:
    print("Already patched: frontend/app.py")

print("Done.")
