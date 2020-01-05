import tkinter as tk
from tkinter import ttk
from ..classes import tooltip as TT
from . import customscales as CS

class ThumbOptions(ttk.Frame):
    " A frame that holds some options for the thumbnail panels"
    def __init__(self, parent, Controller=None):
        super().__init__(parent)
        self.config(borderwidth=1, relief="raised")

        # keep a handle of the controller object
        self.Ctrl = Controller

        label = ttk.Label(self, text="Output channel")
        label.pack(fill='x')
        self.channeltoshow = "Default"
        self._Combo = ttk.Combobox(
            self,
            values=["Default", "Hue", "Saturation", "Value"],
            width=15,
        )
        self._Combo.set(self.channeltoshow)
        self._Combo.bind("<<ComboboxSelected>>", self._comboChanged)
        self._Combo.pack()

        self.showfilename = tk.BooleanVar()
        self.showfilename.set(self.Ctrl.Cfg.get('filenameonthumbnail'))
        sfn = ttk.Checkbutton(
            self,
            text="Filenames",
            variable=self.showfilename,
            command=self._showOptionChanged
        )
        sfn.pack(fill='x')
        msg = '''Show the filename on each thumbnail.'''
        TT.Tooltip(sfn, text=msg)

        self.showbuttons = tk.BooleanVar()
        self.showbuttons.set(self.Ctrl.Cfg.get('showbuttons'))
        shb = ttk.Checkbutton(
            self,
            text="Hide/Delete buttons",
            variable=self.showbuttons,
            command=self._showOptionChanged
        )
        shb.pack(fill='x')
        msg = '''Show the individual Hide/Delete buttons with each thumbnail.'''
        TT.Tooltip(shb, text=msg)

        label = ttk.Label(self, text="Thumbnail size")
        label.pack(fill='x')

        self._thumbsizeVar = tk.IntVar()
        self._thumbsizeVar.set(self.Ctrl.Cfg.get('thumbnailsize'))
        
        self._Scale = CS.DelayedScale(self,
                                      from_= 50, to=500,
                                      resolution=10,
                                      variable=self._thumbsizeVar,
                                      takefocus=1,
                                      command=self._scaleChanged,
                                      orient="horizontal",
        )
        self._Scale.bind("<Control-a>", self._doSelectAll)
        self._Scale.pack()

    def _comboChanged(self, *args):
        self._Combo.focus_set()
        if self.channeltoshow != self._Combo.get():
            self.channeltoshow = self._Combo.get()
            self.Ctrl.Cfg.set('channeltoshow', self.channeltoshow)
            self.Ctrl.onThumbParamsChanged()

    def _showOptionChanged(self, *args):
        self.Ctrl.Cfg.set('showbuttons', self.showbuttons.get())
        self.Ctrl.Cfg.set('filenameonthumbnail', self.showfilename.get())
        self.Ctrl.onThumbElementsChanged()

    def _scaleChanged(self, *args):
        self.Ctrl.Cfg.set('thumbnailsize', self._thumbsizeVar.get())
        self._Scale.focus_set()
        self.Ctrl.onThumbParamsChanged()

    def _doSelectAll(self, *args):
        self.Ctrl.selectAllThumbnails()
        return "break"
