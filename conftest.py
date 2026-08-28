import os
import sys
from pathlib import Path

os.environ.setdefault("TAVILY_API_KEY", "test-key")

# Add the root directory to the Python path so pytest can find modules
root = Path(__file__).parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))
