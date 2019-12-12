import tkinter as tk
from tkinter import font
import classes.tooltip as TT

class CfgWindow(tk.Toplevel):
    def __init__(self, parent, Controller=None):
        super().__init__()

        myfont = font.Font(family='Helvetica', size=11)
        self.title("Settings")

        self.parent = parent
        self.transient(self.parent)

        self.Cfg = Controller.Cfg

        self.recurse = tk.BooleanVar()
        self.confirmDel = tk.BooleanVar()
        self.doGzip = tk.BooleanVar()
        self.saveSettings = tk.BooleanVar()
        self.thumbSize = tk.IntVar()
        self.startupDir = tk.StringVar()

        frame3 = tk.Frame(self)
        frame3.pack(fill='x', padx=5)
        startlabel = tk.Label(
            frame3,
            font=myfont,
            text="Startup Folder"
        )
        startlabel.pack(pady=5,side=tk.LEFT)
        startentry = tk.Entry(
            frame3,
            font=myfont,
            textvariable=self.startupDir
        )
        startentry.pack(pady=5,side=tk.LEFT)
        self.startupDir.set(self.Cfg.get('startupfolder'))
        msg = '''Folder to read upon starting the application.
. means the directory from which the script was started
leave empty to start without reading files.'''
        TT.Tooltip(startlabel, text=msg)
        TT.Tooltip(startentry, text=msg)

        frame1 = tk.Frame(self)
        frame1.pack(fill='x', padx=5)
        subdir = tk.Checkbutton(frame1,
                                text="Search in Subfolders",
                                font=myfont,
                                variable=self.recurse
        )
        subdir.pack(pady=5, anchor='w')
        self.recurse.set(self.Cfg.get('searchinsubfolders'))
        msg = '''Search recursively in the subfolders for image files.'''
        TT.Tooltip(subdir, text=msg)

        cnfrm = tk.Checkbutton(frame1,
                               text="Confirm File Delete",
                               font=myfont,
                               variable=self.confirmDel
        )
        cnfrm.pack(pady=5, anchor='w')
        self.confirmDel.set(self.Cfg.get('confirmdelete'))
        msg = '''Ask before deleting files.'''
        TT.Tooltip(subdir, text=msg)

        gzp = tk.Checkbutton(frame1,
                             text="Gzip File Instead of Delete",
                             font=myfont,
                             variable=self.doGzip
        )
        gzp.pack(pady=5, anchor='w')
        self.doGzip.set(self.Cfg.get('gzipinsteadofdelete'))
        msg = '''Instead of deleting the file gzip it (adds .gz to the filename).'''
        TT.Tooltip(gzp, text=msg)

        tk.Checkbutton(frame1,
                       text="Save Settings on Exit",
                       font=myfont,
                       variable=self.saveSettings
        ).pack(pady=5, anchor='w')
        self.saveSettings.set(self.Cfg.get('savesettings'))

        frame2 = tk.Frame(self)
        frame2.pack(fill='x', padx=5)
        
        tk.Label(
            frame2,
            font=myfont,
            text="Thumbnail Size"
        ).pack(pady=5,side=tk.LEFT)
        tk.Entry(
            frame2,
            font=myfont,
            textvariable=self.thumbSize
        ).pack(pady=5,side=tk.LEFT)
        self.thumbSize.set(self.Cfg.get('thumbnailsize'))

        frame4 = tk.Frame(self)
        frame4.pack(fill='x')
        tk.Button(
            frame4,
            text="Ok",
            width=15,
            command=self._ok
        ).pack(padx=10, side=tk.LEFT)
        tk.Button(
            frame4,
            text="Cancel",
            width=15,
            command=self._cancel
        ).pack(padx=10, side=tk.RIGHT)

        self.bind("<Escape>", self._cancel)
        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self.grab_set()
        self.wait_window(self)
        
    def _ok(self, *args):
        self.Cfg.set('searchinsubfolders', self.recurse.get())
        self.Cfg.set('confirmdelete', self.confirmDel.get())
        self.Cfg.set('gzipinsteadofdelete', self.doGzip.get())
        self.Cfg.set('savesettings', self.saveSettings.get())
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
