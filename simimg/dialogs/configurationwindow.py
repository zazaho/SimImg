''' Modules that defines a oolbar with action items'''
import os
import tkinter as tk
from tkinter import font as tkfont
from tkinter import filedialog as tkfiledialog
import simimg.classes.tooltip as TT
import simimg.utils.pillowplus as PP

class CfgWindow(tk.Toplevel):
    def __init__(self, parent, Controller=None):
        super().__init__()

        myfont = tkfont.Font(family='Helvetica', size=11)
        self.title("Settings")

        self.parent = parent
        self.transient(self.parent)

        self.Ctrl = Controller
        self.Cfg = Controller.Cfg
        iconpath = self.Cfg.get('iconpath')

        self.recurse = tk.BooleanVar()
        self.recurse.set(self.Cfg.get('searchinsubfolders'))
        self.confirmDel = tk.BooleanVar()
        self.confirmDel.set(self.Cfg.get('confirmdelete'))
        self.doGzip = tk.BooleanVar()
        self.doGzip.set(self.Cfg.get('gzipinsteadofdelete'))
        self.saveSettings = tk.BooleanVar()
        self.saveSettings.set(self.Cfg.get('savesettings'))
        self.showButtons = tk.BooleanVar()
        self.showButtons.set(self.Cfg.get('showbuttons'))
        self.thumbSize = tk.IntVar()
        self.thumbSize.set(self.Cfg.get('thumbnailsize'))
        self.startupDir = tk.StringVar()
        self.startupDir.set(self.Cfg.get('startupfolder'))

        startupFrame = tk.Frame(self)
        startupFrame.pack(fill='x', padx=5)
        startlabel = tk.Label(
            startupFrame,
            font=myfont,
            text="Startup Folder"
        )
        startentry = tk.Entry(
            startupFrame,
            font=myfont,
            textvariable=self.startupDir
        )
        self.openImg = PP.photoImageOpen(os.path.join(iconpath, "open.png"))
        openbutton = tk.Button(
            startupFrame,
            image=self.openImg,
            relief="flat",
            command=self._openFolder
        )
        startlabel.pack(pady=5,side="left")
        startentry.pack(pady=5,side="left")
        openbutton.pack(side="left")
        msg = '''Folder to read upon starting the application.

. Means the directory from which the script was started.

Leave empty to start without reading files.'''
        TT.Tooltip(startlabel, text=msg)
        TT.Tooltip(startentry, text=msg)
        TT.Tooltip(openbutton, text='Select Startup Folder')

        thumbSizeFrame = tk.Frame(self)
        thumbSizeFrame.pack(fill='x', padx=5)

        tk.Label(
            thumbSizeFrame,
            font=myfont,
            text="Thumbnail Size"
        ).pack(pady=5,side="left")
        tk.Entry(
            thumbSizeFrame,
            font=myfont,
            textvariable=self.thumbSize
        ).pack(pady=5,side="left")

        clearDBFrame = tk.Frame(self)
        clearDBFrame.pack(fill='x', padx=5)
        self.clearDBImg = PP.photoImageOpen(os.path.join(iconpath, "refresh.png"))
        clearDBbutton = tk.Button(
            clearDBFrame,
            image=self.clearDBImg,
            text="Clear Database",
            compound="left",
            command=self._clearDB
        )
        clearDBbutton.pack(side="left")
        msg = '''Empty the database that holds the calculated image properties.'''
        TT.Tooltip(clearDBbutton, text=msg)

        toggleFrame = tk.Frame(self)
        toggleFrame.pack(fill='x', padx=5)
        subdir = tk.Checkbutton(toggleFrame,
                                text="Search in Subfolders",
                                font=myfont,
                                variable=self.recurse
        )
        msg = '''Search recursively in the subfolders for image files.'''
        TT.Tooltip(subdir, text=msg)

        cnfrm = tk.Checkbutton(toggleFrame,
                               text="Confirm File Delete",
                               font=myfont,
                               variable=self.confirmDel
        )
        msg = '''Ask before deleting files.'''
        TT.Tooltip(cnfrm, text=msg)

        gzp = tk.Checkbutton(toggleFrame,
                             text="Gzip File Instead of Delete",
                             font=myfont,
                             variable=self.doGzip
        )
        msg = '''Instead of deleting the file gzip it (adds .gz to the filename).'''
        TT.Tooltip(gzp, text=msg)

        svs = tk.Checkbutton(toggleFrame,
                             text="Save Settings on Exit",
                             font=myfont,
                             variable=self.saveSettings
        )

        shb = tk.Checkbutton(toggleFrame,
                             text="Show Hide/Delete buttons",
                             font=myfont,
                             variable=self.showButtons
        )
        msg = '''Show the individual Hide/Delete buttons with each thumbnail.'''
        TT.Tooltip(shb, text=msg)

        subdir.pack(pady=5, anchor='w')
        cnfrm.pack(pady=5, anchor='w')
        gzp.pack(pady=5, anchor='w')
        svs.pack(pady=5, anchor='w')
        shb.pack(pady=5, anchor='w')

        btnFrame = tk.Frame(self)
        btnFrame.pack(fill='x')
        tk.Button(
            btnFrame,
            text="Ok",
            width=15,
            command=self._ok
        ).pack(padx=10, side="left")
        tk.Button(
            btnFrame,
            text="Cancel",
            width=15,
            command=self._cancel
        ).pack(padx=10, side="right")

        self.bind("<Escape>", self._cancel)
        self.protocol("WM_DELETE_WINDOW", self._cancel)
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
        self.Cfg.set('searchinsubfolders', self.recurse.get())
        self.Cfg.set('confirmdelete', self.confirmDel.get())
        self.Cfg.set('gzipinsteadofdelete', self.doGzip.get())
        self.Cfg.set('savesettings', self.saveSettings.get())
        self.Cfg.set('showbuttons', self.showButtons.get())
        try:
            ts = self.thumbSize.get()
        except tk.TclError:
            ts = self.Cfg.get('thumbnailsize')
        self.Cfg.set('thumbnailsize', ts)
        self.Cfg.set('startupfolder', self.startupDir.get())
        self._returntoparent()

    def _cancel(self, *args):
        self._returntoparent()

    def _returntoparent(self):
        self.withdraw()
        self.update_idletasks()
        self.parent.focus_set()
        self.destroy()
