import tkinter as tk
from tkinter import font

class CDDialog(tk.Toplevel):
    def __init__(self, parent, Filename="", simple=False):
        super().__init__()

        self.title("Delete File?")

        self.parent = parent
        self.transient(self.parent)

        self.result = None
        boldfont = font.Font(family='Helvetica', size=12, weight='bold')
        tk.Label(
            self,
            text=Filename,
            font=boldfont
        ).grid(column=0, row=0, columnspan=4, padx=10, pady=10)
        tk.Button(
            self,
            text="Yes",
            width=10,
            command=self._yes,
            default="active"
        ).grid(column=0, row=1, padx=10)
        tk.Button(
            self,
            text="No",
            width=10,
            command=self._no
        ).grid(column=1, row=1, padx=10)
        if not simple:
            tk.Button(
                self,
                text="Yes to All",
                width=10,
                command=self._yes_to_all
            ).grid(column=2, row=1, padx=10)
            tk.Button(
                self,
                text="Abort",
                width=10,
                command=self._abort
            ).grid(column=3, row=1, padx=10)

        self.bind("<Return>", self._yes)
        self.bind("<Escape>", self._abort)
        self.protocol("WM_DELETE_WINDOW", self._abort)

        self.grab_set()
        self.wait_window(self)

    def _yes(self, *args):
        self.result = "yes"
        self._returntoparent()

    def _yes_to_all(self, *args):
        self.result = "yestoall"
        self._returntoparent()

    def _no(self, *args):
        self.result = "no"
        self._returntoparent()

    def _abort(self, *args):
        self.result = "abort"
        self._returntoparent()

    def _returntoparent(self):
        self.withdraw()
        self.update_idletasks()
        self.parent.focus_set()
        self.destroy()
