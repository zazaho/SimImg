""" Some modules to be put in the left panel that are not related to image matching"""
import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as tkfiledialog

import simimg.classes.tooltip as TT
import simimg.classes.customscales as CS


class ThumbOptions(ttk.Frame):
    " A frame that holds some options for the thumbnail panels"

    def __init__(self, parent, Controller=None):
        super().__init__(parent)
        self.config(borderwidth=1, relief="raised")

        # keep a handle of the controller object
        self._Ctrl = Controller

        label = ttk.Label(self, text="Output channel")
        label.pack(fill="x")
        self.channeltoshow = "Default"
        self._Combo = ttk.Combobox(
            self,
            values=["Default", "Hue", "Saturation", "Value"],
            width=15,
        )
        self._Combo.set(self.channeltoshow)
        self._Combo.config(state="normal")
        self._Combo.bind("<<ComboboxSelected>>", self._comboChanged)
        self._Combo.pack()

        self.showfilename = tk.BooleanVar()
        self.showfilename.set(self._Ctrl.Cfg.get("filenameonthumbnail"))
        sfn = ttk.Checkbutton(
            self,
            text="Filenames",
            variable=self.showfilename,
            command=self._showOptionChanged
        )
        sfn.pack(fill="x")
        msg = """Show the filename on each thumbnail."""
        TT.Tooltip(sfn, text=msg)

        self.showbuttons = tk.BooleanVar()
        self.showbuttons.set(self._Ctrl.Cfg.get("showbuttons"))
        shb = ttk.Checkbutton(
            self,
            text="Show buttons",
            variable=self.showbuttons,
            command=self._showOptionChanged
        )
        shb.pack(fill="x")
        msg = "Show the individual Hide/Move/Delete buttons with each thumbnail"
        TT.Tooltip(shb, text=msg)

        label = ttk.Label(self, text="Thumbnail size")
        label.pack(fill="x")

        sizeVar = tk.IntVar()
        sizeVar.set(self._Ctrl.Cfg.get("thumbnailsize"))
        self._Scale = CS.LabelScale(
            self,
            from_=50,
            to=250,
            resolution=10,
            takefocus=1,
            command=self._scaleChanged,
            variable=sizeVar,
            orient="horizontal",
        )
        self._Scale.bind("<Control-a>", self._doSelectAll)
        self._Scale.pack()

    def _comboChanged(self, *args):
        self._Combo.focus_set()
        if self.channeltoshow != self._Combo.get():
            self.channeltoshow = self._Combo.get()
            self._Ctrl.Cfg.set("channeltoshow", self.channeltoshow)
            self._Ctrl.onThumbParamsChanged()

    def _showOptionChanged(self, *args):
        self._Ctrl.Cfg.set("showbuttons", self.showbuttons.get())
        self._Ctrl.Cfg.set("filenameonthumbnail", self.showfilename.get())
        self._Ctrl.onThumbElementsChanged()

    def _scaleChanged(self, *args):
        self._Ctrl.Cfg.set("thumbnailsize", self._Scale.get())
        self._Scale.focus_set()
        self._Ctrl.onThumbParamsChanged()

    def _doSelectAll(self, *args):
        self._Ctrl.toggleSelectAllThumbnails()
        return "break"

class MovePanel(ttk.Frame):
    " A frame that holds a list of target folders for moving files"

    def __init__(self, parent, Controller=None):
        super().__init__(parent)
        self.config(borderwidth=1, relief="raised")

        # keep a handle of the controller object
        self._Ctrl = Controller

        self._activeFolder = ""
        self._folderDict = {}
        self._activeFolderIdx = tk.IntVar()

        for i in range(1, self._Ctrl.Cfg.get("numfolders")+1):
            txt = "right-click to set"
            if self._Ctrl.Cfg.get("restoremovefolders"):
                fld = self._Ctrl.Cfg.get("folder"+str(i))
                if fld:
                    self._folderDict[i] = fld
                    txt = os.path.basename(fld)
            RB = ttk.Radiobutton(
                self,
                variable=self._activeFolderIdx,
                text=txt,
                command=self._setActiveFolder,
                value=i
            )
            RB.pack(anchor="w")
            RB.bind("<Button-3>", self._changeFolder)

    def _setActiveFolder(self):
        if self._activeFolderIdx.get() in self._folderDict:
            self._activeFolder = self._folderDict[self._activeFolderIdx.get()]

    def _changeFolder(self, event):
        thisWidgetId = event.widget.cget("value")
        selectedFolder = tkfiledialog.askdirectory(mustexist=False)
        if not selectedFolder:
            return
        # try to create the directory
        if not os.path.isdir(selectedFolder):
            os.mkdir(selectedFolder)
        if not os.path.isdir(selectedFolder):
            return
        self._folderDict[thisWidgetId] = selectedFolder
        event.widget.config(text=os.path.basename(selectedFolder))
        # set this button active if none are active
        if self._activeFolderIdx.get() == 0:
            self._activeFolderIdx.set(thisWidgetId)
        # make sure the folder string is updated
        self._setActiveFolder()
        self._Ctrl.Cfg.set("folder"+str(thisWidgetId), self._activeFolder)

    def get(self, index=None):
        if not index:
            return self._activeFolder
        if index not in self._folderDict:
            return None
        return self._folderDict[index]
