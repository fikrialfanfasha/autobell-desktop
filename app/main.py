import tkinter as tk
from pathlib import Path

from .storage import load_or_init_config
from .audio import AudioEngine
from .scheduler import BellScheduler
from .ui import AppUI

def resource_path(rel: str) -> Path:
    # aman untuk mode source & PyInstaller
    import sys, os
    base = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return Path(base) / rel

def main():
    cfg = load_or_init_config(resource_path("assets/config_default.json"))
    audio = AudioEngine()
    bell = BellScheduler(cfg, audio)
    bell.start()

    root = tk.Tk()
    ui = AppUI(root, cfg, on_config_changed=lambda new_cfg: bell.reload(new_cfg))
    root.protocol("WM_DELETE_WINDOW", root.withdraw)  # close -> minimize (biar scheduler tetap jalan)
    root.mainloop()

if __name__ == "__main__":
    main()
