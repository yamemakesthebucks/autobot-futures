from tkinter import Tk, Label, Button
from src.utils.logger import get_logger

def launch_dashboard():
    log = get_logger("Dashboard")
    root = Tk()
    root.title("Trading Bot Dashboard")
    status = Label(root, text="Status: Idle")
    status.pack()
    def start(): log.info("Start clicked")
    def stop():  log.info("Stop clicked")
    Button(root, text="Start Bot", command=start).pack()
    Button(root, text="Stop Bot", command=stop).pack()
    root.mainloop()
