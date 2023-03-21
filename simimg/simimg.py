""" Project to display similar images from an image catalog """
import os
import tkinter as tk
from tkinter import ttk

import simimg.classes.configuration as CONF
import simimg.classes.controller as CTRL
import simimg.classes.scrollframe as SF


class simim_app(tk.Tk):
    """ Main window for sorting and managing pictures"""

    def __init__(self, ScriptPath=None):
        # do what any TK app does
        super().__init__()

        # Do nothing much but creating the objects
        # it is those objects that will implement the
        # working of the App.

        # Object that hold configuration database
        self.Cfg = CONF.Configuration(ScriptPath=ScriptPath)

        self.title("Similar Image Finder")
        self.tk.call("wm", "iconphoto", self._w,
                     tk.PhotoImage(
                         file=os.path.join(self.Cfg.get("iconpath"), "simimg.png")
                     )
                     )
        self.geometry(self.Cfg.get("findergeometry"))

        # ttk widget style section
        style = ttk.Style()
        style.configure("LargeText.TButton", font=("", 11))
        style.configure("LargeText.TLabel", font=("", 11))
        style.configure(
            "HeaderText.TLabel",
            font=("", 11),
            foreground=self.cget("background"),
            background="darkblue",
            anchor="center",
        )
        style.configure("LargeText.TCheckbutton", font=("", 11))
        style.configure("BoldText.TLabel", font=("", 12, "bold"))

        style.configure("Picture.TButton", relief="flat", padding=0)
        style.configure(
            "Thumb.TButton",
            relief="flat",
            padding=0,
            font=("", 8),
            width=-1
        )

        style.configure("Tooltip.TLabel",
                        background="#FFFFE1",
                        padding=3,
                        relief="solid",
                        borderwidth=1,
                        font=("", 11),
                        )

        self.Statusbar = ttk.Label(self, text="...", relief="sunken")
        self.Statusbar.pack(side="bottom", fill="x")
        self.ModulePane = ttk.Frame(self)
        self.ModulePane.pack(side="left", fill="y")
        self.ThumbPane = SF.ScrollFrame(self)
        self.ThumbPane.pack(side="right", fill="both", expand=True)
        # The object responsible for dealing with the data
        # and the display of those data
        self.Ctrl = CTRL.Controller(self)


def main():
    scriptpath = os.path.join(os.path.dirname(os.path.realpath(__file__)))
    app = simim_app(ScriptPath=scriptpath)
    app.mainloop()


if __name__ == "__main__":
    main()
