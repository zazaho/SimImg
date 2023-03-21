""" class related to the display of one thumbnail """
import tkinter as tk
from tkinter import ttk


class ImageFrame(ttk.Frame):
    " A frame that holds one image thumbnail with its buttons"

    def __init__(self, parent, checksum=None, Ctrl=None, X=None, Y=None):
        super().__init__(parent)

        self.checksum = checksum
        self.selected = False
        self.X = X
        self.Y = Y

        self._Ctrl = Ctrl
        self._tSize = Ctrl.Cfg.get("thumbnailsize")
        self._text = None
        self._backtext = None

        self._thumbCanvas = tk.Canvas(
            self,
            width=self._tSize,
            height=self._tSize
        )
        self._thumbCanvas.defBgClr = self._thumbCanvas.cget("background")
        self._thumbCanvas.selBgClr = "blue"
        self._thumbCanvas.bind("<Button-1>", self._click)

        self._thumbCanvas.pack(side="top")
        self._thumbCanvas.config(highlightthickness=1)
        self._hideButton = ttk.Button(
            self,
            text="Hide",
            command=self._hide,
            style="Thumb.TButton"
        )
        self._moveButton = ttk.Button(
            self,
            text="Move",
            command=self._move,
            style="Thumb.TButton"
        )
        self._deleteButton = ttk.Button(
            self,
            text="Delete",
            command=self._delete,
            style="Thumb.TButton"
        )
        self.createThumbContent()
        self.showOptionalElements()

    def createThumbContent(self):
        self._tSize = self._Ctrl.Cfg.get("thumbnailsize")
        self._thumbCanvas.delete("all")
        self._thumbCanvas.config(width=self._tSize, height=self._tSize)
        if self.checksum:
            self._thumbCanvas.create_image(
                self._tSize/2,
                self._tSize/2,
                anchor="center",
                image=self._Ctrl.FODict[self.checksum][0].thumbnail()
            )
            self._text = self._thumbCanvas.create_text(
                self._tSize/2,
                self._tSize,
                anchor="s",
                text=self._Ctrl.FODict[self.checksum][0].fileName,
            )
            self._backtext = self._thumbCanvas.create_rectangle(
                self._thumbCanvas.bbox(self._text),
                fill=self._thumbCanvas.defBgClr,
                width=0,
            )
            self._thumbCanvas.tag_lower(self._backtext, self._text)

            if len(self._Ctrl.FODict[self.checksum]) > 1:
                self._thumbCanvas.config(highlightbackground="green", highlightthickness=1)

    def showOptionalElements(self):
        if self._Ctrl.Cfg.get("filenameonthumbnail"):
            self._thumbCanvas.itemconfigure(self._text, state="normal")
            self._thumbCanvas.itemconfigure(self._backtext, state="normal")
        else:
            self._thumbCanvas.itemconfigure(self._text, state="hidden")
            self._thumbCanvas.itemconfigure(self._backtext, state="hidden")

        if self._Ctrl.Cfg.get("showbuttons"):
            self._hideButton.pack(side="left")
            self._moveButton.pack(side="left")
            self._deleteButton.pack(side="left")
        else:
            self._hideButton.pack_forget()
            self._moveButton.pack_forget()
            self._deleteButton.pack_forget()

    def _hide(self):
        for fo in self._Ctrl.FODict[self.checksum]:
            fo.active = False
            self._Ctrl.onChange()

    def _move(self):
        self._Ctrl.moveFOs(self._Ctrl.FODict[self.checksum])

    def _delete(self):
        self._Ctrl.deleteFOs(self._Ctrl.FODict[self.checksum])

    def select(self, value):
        self.selected = value
        if self.selected:
            self._thumbCanvas.config(bg=self._thumbCanvas.selBgClr)
            self._Ctrl.lastSelectedXY = (self.X, self.Y)
        else:
            self._thumbCanvas.config(bg=self._thumbCanvas.defBgClr)
            self._Ctrl.lastSelectedXY = None
        self.focus_set()

    def _click(self, event):
        if (event.state & 0x4) != 0:
            self._Ctrl.toggleSelectRow(self.Y, not self.selected)
            return
        if (event.state & 0x1) != 0:
            self._Ctrl.selectRangeFromLastSelected(self.X, self.Y)
            return
        self.select(not self.selected)
