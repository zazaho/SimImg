import tkinter as tk
from tkinter import ttk

class ImageFrame(ttk.Frame):
    " A frame that holds one image thumbnail with its buttons"
    def __init__(self, parent, md5=None, Ctrl=None, X=None, Y=None):
        super().__init__(parent)

        self.Ctrl = Ctrl
        self._ThumbSize = Ctrl.Cfg.get('thumbnailsize')
        self.md5 = md5
        self.selected = False
        self.X = X
        self.Y = Y

        self._defaultBackgroundColor = Ctrl.TopWindow.cget('background')
        self._thumb_canvas = tk.Canvas(
            self,
            width=self._ThumbSize,
            height=self._ThumbSize
        )
        self._thumb_canvas.bind("<Button-1>", self._click)

        if self.md5:
            self._thumb_canvas.create_image(
                self._ThumbSize/2,
                self._ThumbSize/2,
                anchor='center',
                image=Ctrl.FODict[self.md5][0].Thumbnail()
            )
            if len(Ctrl.FODict[self.md5]) > 1:
                self._thumb_canvas.config(highlightbackground="green", highlightthickness=2)

        self._thumb_canvas.pack(side="top")
        self._hide_button = ttk.Button(
            self,
            text="Hide",
            command=self._hide,
            style="Thumb.TButton"
        )
        self._delete_button = ttk.Button(
            self,
            text="Delete",
            command=self._delete,
            style="Thumb.TButton"
        )
        self.showHideButtons()

    def showHideButtons(self):
        if self.Ctrl.Cfg.get('showbuttons'):
            self._hide_button.pack(side="left")
            self._delete_button.pack(side="right")
        else:
            self._hide_button.pack_forget()
            self._delete_button.pack_forget()

    def _hide(self):
        for fo in self.Ctrl.FODict[self.md5]:
            fo.active = False
            self.Ctrl.onChange()

    def _delete(self):
        self.Ctrl.deleteFOs(
            self.Ctrl.FODict[self.md5],
            Owner=self.Ctrl.TopWindow
        )

    def select(self, value):
        self.selected = value
        if self.selected:
            self._thumb_canvas.config(bg="blue")
            self.Ctrl.lastSelectedXY = (self.X, self.Y)
        else:
            self._thumb_canvas.config(bg=self._defaultBackgroundColor)
            self.Ctrl.lastSelectedXY = None
        self.focus_set()

    def _click(self, event):
        if (event.state & 0x4) != 0:
            self.Ctrl.toggleSelectRow(self.Y, not self.selected)
            return
        if (event.state & 0x1) != 0:
            self.Ctrl.selectRangeFromLastSelected(self.X, self.Y)
            return
        self.select(not self.selected)
