import os
import sys
import runpy

# Ensure project root directory is in Python module search path
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Execute main Streamlit app script dynamically on every Streamlit script execution
app_path = os.path.join(root_dir, "app", "streamlit_app.py")
runpy.run_path(app_path, run_name="__main__")
