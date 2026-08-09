import ctypes
import sys
import tkinter

from src.application_window import DCAExtractorApplicationWindow


def enable_windows_dpi_awareness():
    if sys.platform != "win32":
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError):
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except (AttributeError, OSError):
            pass


if __name__ == "__main__":
    enable_windows_dpi_awareness()
    root_window = tkinter.Tk()
    application_window = DCAExtractorApplicationWindow(root_window)
    root_window.mainloop()
