"""Write the app's OpenAPI schema to openapi.json (gitignored; regenerate any time)."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.main import app  # noqa: E402

(ROOT / "openapi.json").write_text(json.dumps(app.openapi(), indent=2) + "\n")
print("wrote openapi.json")
