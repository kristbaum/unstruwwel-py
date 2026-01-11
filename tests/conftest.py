import json
from pathlib import Path
import pytest

DATA_RAW = Path(__file__).resolve().parents[1] / "data-raw"


@pytest.fixture(scope="session")
def lang_jsons():
    files = [DATA_RAW / "en.json", DATA_RAW / "de.json", DATA_RAW / "fr.json"]
    return {
        p.stem: json.loads(p.read_text(encoding="utf-8")) for p in files if p.exists()
    }
