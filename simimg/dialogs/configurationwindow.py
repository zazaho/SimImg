""" Modules that defines a oolbar with action items"""
import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as tkfiledialog

import simimg.classes.tooltip as TT
import simimg.utils.pillowplus as PP


class CfgWindow(tk.Toplevel):
    def __init__(self, parent, Controller=None):
        super().__init__()

        self.title("Settings")

        self.parent = parent
        self.transient(self.parent)

        self.Ctrl = Controller
        iconpath = self.Ctrl.Cfg.get("iconpath")

        self.recurse = tk.BooleanVar()
        self.recurse.set(self.Ctrl.Cfg.get("searchinsubfolders"))
        self.upscale = tk.BooleanVar()
        self.upscale.set(self.Ctrl.Cfg.get("upscalethumbnails"))
        self.confirmDel = tk.BooleanVar()
        self.confirmDel.set(self.Ctrl.Cfg.get("confirmdelete"))
        self.doGzip = tk.BooleanVar()
        self.doGzip.set(self.Ctrl.Cfg.get("gzipinsteadofdelete"))
        self.saveSettings = tk.BooleanVar()
        self.saveSettings.set(self.Ctrl.Cfg.get("savesettings"))
        self.startupDir = tk.StringVar()
        self.startupDir.set(self.Ctrl.Cfg.get("startupfolder"))
        self.restoreFolders = tk.BooleanVar()
        self.restoreFolders.set(self.Ctrl.Cfg.get("restoremovefolders"))

        startupFrame = ttk.Frame(self)
        startupFrame.pack(fill="x", padx=5)
        startlabel = ttk.Label(
            startupFrame,
            style="LargeText.TLabel",
            text="Startup Folder"
        )
        startentry = ttk.Entry(
            startupFrame,
            font=("", 11),
            textvariable=self.startupDir
        )
        self.openImg = PP.photoImageOpenAndResizeToFit(os.path.join(iconpath, "open.png"), 16 , 16)
        openbutton = ttk.Button(
            startupFrame,
            image=self.openImg,
            style="Picture.TButton",
            command=self._openFolder
        )
        startlabel.pack(pady=5, side="left")
        startentry.pack(pady=5, side="left")
        openbutton.pack(side="left", padx=5)
        msg = """Folder to read upon starting the application.

. Means the directory from which the script was started.

Leave empty to start without reading files"""
        TT.Tooltip(startlabel, text=msg)
        TT.Tooltip(startentry, text=msg)
        TT.Tooltip(openbutton, text="Select Startup Folder")

        clearDBFrame = ttk.Frame(self)
        clearDBFrame.pack(fill="x", padx=5)
        self.clearDBImg = PP.photoImageOpen(os.path.join(iconpath, "refresh.png"))
        clearDBbutton = ttk.Button(
            clearDBFrame,
            image=self.clearDBImg,
            text="Clear Database",
            style="LargeText.TButton",
            compound="left",
            command=self._clearDB
        )
        clearDBbutton.pack(side="left")
        msg = "Empty the database that holds the calculated image properties"
        TT.Tooltip(clearDBbutton, text=msg)

        toggleFrame = ttk.Frame(self)
        toggleFrame.pack(fill="x", padx=5)
        subdir = ttk.Checkbutton(
            toggleFrame,
            text="Search in Subfolders",
            style="LargeText.TCheckbutton",
            variable=self.recurse
        )
        msg = "Search recursively in the subfolders for image files"
        TT.Tooltip(subdir, text=msg)

        upscale = ttk.Checkbutton(
            toggleFrame,
            text="Zoom small images as thumbnails",
            style="LargeText.TCheckbutton",
            variable=self.upscale
        )
        msg = "While making thumbnail stretch small images to the thumbnail size"
        TT.Tooltip(upscale, text=msg)

        cnfrm = ttk.Checkbutton(
            toggleFrame,
            text="Confirm File Delete",
            style="LargeText.TCheckbutton",
            variable=self.confirmDel
        )
        msg = "Ask before deleting files"
        TT.Tooltip(cnfrm, text=msg)

        gzp = ttk.Checkbutton(
            toggleFrame,
            text="Gzip File Instead of Delete",
            style="LargeText.TCheckbutton",
            variable=self.doGzip
        )
        msg = "Instead of deleting the file gzip it (adds .gz to the filename)"
        TT.Tooltip(gzp, text=msg)

        svs = ttk.Checkbutton(
            toggleFrame,
            text="Save Settings on Exit",
            style="LargeText.TCheckbutton",
            variable=self.saveSettings
        )

        rfl = ttk.Checkbutton(
            toggleFrame,
            text="Remember Move Folders",
            style="LargeText.TCheckbutton",
            variable=self.restoreFolders
        )

        subdir.pack(pady=5, anchor="w")
        upscale.pack(pady=5, anchor="w")
        cnfrm.pack(pady=5, anchor="w")
        gzp.pack(pady=5, anchor="w")
        svs.pack(pady=5, anchor="w")
        rfl.pack(pady=5, anchor="w")

        btnFrame = ttk.Frame(self)
        btnFrame.pack(fill="x")
        ttk.Button(
            btnFrame,
            text="Ok",
            width=15,
            style="LargeText.TButton",
            command=self._ok
        ).pack(padx=10, side="left")
        ttk.Button(
            btnFrame,
            text="Cancel",
            width=15,
            style="LargeText.TButton",
            command=self._cancel
        ).pack(padx=10, side="right")

        self.bind("<Escape>", self._cancel)
        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self.geometry = self.parent.geometry()
        self.grab_set()
        self.wait_window(self)

    def _openFolder(self):
        selectedFolder = tkfiledialog.askdirectory()
        if not selectedFolder:
            return
        if not os.path.isdir(selectedFolder):
            return
        self.startupDir.set(selectedFolder)

    def _clearDB(self):
        self.Ctrl.stopDatabase()
        self.Ctrl.startDatabase(clear=True)

    def _ok(self, *args):
        self.Ctrl.Cfg.set("searchinsubfolders", self.recurse.get())
        self.Ctrl.Cfg.set("upscalethumbnails", self.upscale.get())
        self.Ctrl.Cfg.set("confirmdelete", self.confirmDel.get())
        self.Ctrl.Cfg.set("gzipinsteadofdelete", self.doGzip.get())
        self.Ctrl.Cfg.set("savesettings", self.saveSettings.get())
        self.Ctrl.Cfg.set("restoremovefolders", self.restoreFolders.get())
        self.Ctrl.Cfg.set("startupfolder", self.startupDir.get())
        self._returntoparent()

    def _cancel(self, *args):
        self._returntoparent()

    def _returntoparent(self):
        self.withdraw()
        self.update_idletasks()
        self.parent.focus_set()
        self.destroy()
