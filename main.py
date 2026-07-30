import tkinter

from src.application_window import DCAExtractorApplicationWindow

if __name__ == "__main__":
    root_window = tkinter.Tk()
    application_window = DCAExtractorApplicationWindow(root_window)
    root_window.mainloop()
