import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT in sys.path:
    sys.path.remove(ROOT)
sys.path.insert(0, ROOT)
