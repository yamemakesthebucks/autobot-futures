# src/deployment/dashboard.py
from __future__ import annotations
import os
from typing import NoReturn

def _enabled() -> bool:
    flag = os.getenv("DASHBOARD", "").strip().lower()
    return flag in ("1", "true", "yes", "on")

def launch_dashboard() -> None | NoReturn:
    if not _enabled():
        print("[dashboard] Disabled (set DASHBOARD=1 to enable).")
        return
    try:
        from tkinter import Tk, Label, Button  # imported only if enabled
    except Exception as e:
        print(f"[dashboard] Tk not available; skipping dashboard: {e}")
        return

    root = Tk()
    root.title("Autobot Futures")
    Label(root, text="Autobot Futures running").pack(padx=10, pady=10)
    Button(root, text="Quit", command=root.destroy).pack(pady=10)
    root.mainloop()
