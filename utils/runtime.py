# utils/runtime.py
import sys
from pathlib import Path

def resource_path(relative: str) -> str:
    """
    Retorna o caminho absoluto de um recurso, funcionando em dev e no PyInstaller.
    Ex.: resource_path("resources/dummy/dummy.feature")
    """
    if hasattr(sys, "_MEIPASS"):  # PyInstaller extrai para pasta temporária
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).resolve().parents[1]  # raiz do projeto
    return str(base / relative)
