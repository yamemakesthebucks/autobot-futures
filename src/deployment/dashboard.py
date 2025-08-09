# src/deployment/deployment.py (headless-safe dashboard)
from __future__ import annotations
import os
from typing import NoReturn

def _enabled() -> bool:
    """Return True if dashboard is explicitly enabled via env."""
    flag = os.getenv("DASHBOARD", "").strip().lower()
    return flag in ("1", "true", "yes", "on")

def launch_dashboard() -> None | NoReturn:
    """
    Start a tiny Tk dashboard *only* when enabled and Tk is available.

    In headless environments (containers/Kubernetes) or when Tk is missing,
    this function will just log and return without raising.
    """
    if not _enabled():
        print("[dashboard] Disabled (set DASHBOARD=1 to enable).")
        return

    try:
        # Import Tkinter *inside* the function so importing this module
        # does not require libtk on headless systems.
        from tkinter import Tk, Label, Button  # type: ignore
    except Exception as e:  # pragma: no cover
        print(f"[dashboard] Tk not available; skipping dashboard: {e}")
        return

    root = Tk()
    root.title("Autobot Futures")
    Label(root, text="Autobot Futures running").pack(padx=10, pady=10)
    Button(root, text="Quit", command=root.destroy).pack(pady=10)
    root.mainloop()
