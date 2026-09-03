import os
import sys

# Ensure root folder is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Execute Streamlit app from frontend package
with open(os.path.join(os.path.dirname(__file__), "frontend", "streamlit_app.py"), "r", encoding="utf-8") as f:
    code = f.read()

exec(compile(code, "frontend/streamlit_app.py", "exec"))
