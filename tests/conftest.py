import os
import sys

# database.py (and future test targets like communication.py/chat.py) live at
# the project root, not inside a package - make them importable from tests/.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
