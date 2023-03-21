import tkinter as tk
from tkinter import ttk


class CDDialog(tk.Toplevel):
    def __init__(self, parent, Filename="", simple=False):
        super().__init__()

        self.title("Delete File?")

        self.parent = parent
        self.transient(self.parent)

        self.result = None
        ttk.Label(
            self,
            text=Filename,
            style="BoldText.TLabel",
        ).grid(column=0, row=0, columnspan=4, padx=10, pady=10)
        ttk.Button(
            self,
            text="Yes",
            width=10,
            command=self._yes,
            style="LargeText.TButton",
            default="active"
        ).grid(column=0, row=1, padx=10)
        ttk.Button(
            self,
            text="No",
            width=10,
            style="LargeText.TButton",
            command=self._no
        ).grid(column=1, row=1, padx=10)
        if not simple:
            ttk.Button(
                self,
                text="Yes to All",
                width=10,
                style="LargeText.TButton",
                command=self._yes_to_all
            ).grid(column=2, row=1, padx=10)
            ttk.Button(
                self,
                text="Abort",
                width=10,
                style="LargeText.TButton",
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
