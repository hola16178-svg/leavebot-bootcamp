from dataclasses import dataclass
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    db_path: Path


def load_settings(*, db_path=None):
    selected = db_path if db_path is not None else os.environ.get(
        "LEAVEBOT_DB", "backend/data/leavebot.db"
    )
    path = Path(selected)
    return Settings(path if path.is_absolute() else ROOT / path)
