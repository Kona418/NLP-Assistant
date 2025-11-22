import pytest
import json
from pathlib import Path

# Pfad relativ zum tests/-Ordner berechnen, um systemunabhängig zu bleiben
# Pfad: src/nlp_assistant/data/deviceList.json
BASE_DIR = Path(__file__).parent.parent
JSON_FILE = BASE_DIR / "src" / "nlp_assistant" / "data" / "deviceList.json"

@pytest.fixture(scope="session")
def real_device_list():
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
