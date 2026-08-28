import sys
from pathlib import Path

# Add the root directory to the Python path so pytest can find modules
root = Path(__file__).parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))
