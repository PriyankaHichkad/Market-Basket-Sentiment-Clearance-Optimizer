import os
import sys

# Ensure project root directory is included in Python search path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Delegate execution to the Streamlit app module
from app.streamlit_app import *
