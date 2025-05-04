from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class _Config:
    DATA_PATH = Path(__file__).parent / "data"


CONFIG = _Config()
