import sys
from pathlib import Path


def get_path() -> Path:
    if getattr(sys, "frozen", False):
        file_dir = Path(getattr(sys, "_MEIPASS"))
    else:
        file_dir = Path(__file__).parent.parent
    return file_dir.joinpath("pre_edited_cs")
