import tkinter as tk
from tkinter import ttk

class ImageFrame(ttk.Frame):
    " A frame that holds one image thumbnail with its buttons"
    def __init__(self, parent, md5=None, Ctrl=None, X=None, Y=None):
        super().__init__(parent)

        self.md5 = md5
        self.selected = False
        self.X = X
        self.Y = Y

        self._Ctrl = Ctrl
        self._ThumbSize = Ctrl.Cfg.get('thumbnailsize')

        self._defaultBackgroundColor = Ctrl.TopWindow.cget('background')
        self._thumb_canvas = tk.Canvas(
            self,
            width=self._ThumbSize,
            height=self._ThumbSize
        )
        self._thumb_canvas.bind("<Button-1>", self._click)

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
        self.createThumbContent()
        self.showOptionalElements()

    def createThumbContent(self):
        self._ThumbSize = self._Ctrl.Cfg.get('thumbnailsize')
        self._thumb_canvas.delete('all')
        self._thumb_canvas.config(width=self._ThumbSize, height=self._ThumbSize)
        if self.md5:
            self._thumb_canvas.create_image(
                self._ThumbSize/2,
                self._ThumbSize/2,
                anchor='center',
                image=self._Ctrl.FODict[self.md5][0].Thumbnail()
            )
            self.text = self._thumb_canvas.create_text(
                self._ThumbSize/2,
                self._ThumbSize,
                anchor='s',
                text=self._Ctrl.FODict[self.md5][0].FileName,
            )
            self.backtext = self._thumb_canvas.create_rectangle(
                self._thumb_canvas.bbox(self.text),
                fill=self._defaultBackgroundColor,
                width=0,
            )
            self._thumb_canvas.tag_lower(self.backtext, self.text)

            if len(self._Ctrl.FODict[self.md5]) > 1:
                self._thumb_canvas.config(highlightbackground="green", highlightthickness=2)
                
    def showOptionalElements(self):
        if self._Ctrl.Cfg.get('filenameonthumbnail'):
            self._thumb_canvas.itemconfigure(self.text, state='normal')
            self._thumb_canvas.itemconfigure(self.backtext, state='normal')
        else:
            self._thumb_canvas.itemconfigure(self.text, state='hidden')
            self._thumb_canvas.itemconfigure(self.backtext, state='hidden')

        if self._Ctrl.Cfg.get('showbuttons'):
            self._hide_button.pack(side="left")
            self._delete_button.pack(side="right")
        else:
            self._hide_button.pack_forget()
            self._delete_button.pack_forget()

    def _hide(self):
        for fo in self._Ctrl.FODict[self.md5]:
            fo.active = False
            self._Ctrl.onChange()

    def _delete(self):
        self._Ctrl.deleteFOs(
            self._Ctrl.FODict[self.md5],
            Owner=self._Ctrl.TopWindow
        )

    def select(self, value):
        self.selected = value
        if self.selected:
            self._thumb_canvas.config(bg="blue")
            self._Ctrl.lastSelectedXY = (self.X, self.Y)
        else:
            self._thumb_canvas.config(bg=self._defaultBackgroundColor)
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
