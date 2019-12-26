import tkinter as tk

class ImageFrame(tk.Frame):
    " A frame that holds one image thumbnail with its buttons"
    def __init__(self, parent, md5=None, Ctrl=None, X=None, Y=None):
        super().__init__(parent)

        self.Ctrl = Ctrl
        self.ThumbSize = Ctrl.Cfg.get('thumbnailsize')
        BorderWidth = Ctrl.Cfg.get('thumbnailborderwidth')
        self.md5 = md5
        self.selected = False
        self.X = X
        self.Y = Y

        #self.config(relief="groove",borderwidth=BorderWidth)
        self.thumb_canvas = tk.Canvas(self,
                                      width=self.ThumbSize,
                                      height=self.ThumbSize,
                                      bg="white",
                                      relief="groove",
                                      borderwidth=BorderWidth)
        self.thumb_canvas.bind("<Button-1>", self._click)

        if self.md5:
            self.thumb_canvas.create_image(
                BorderWidth+self.ThumbSize/2,
                BorderWidth+self.ThumbSize/2,
                anchor='center',
                image=Ctrl.FODict[self.md5][0].Thumbnail()
            )
            if len(Ctrl.FODict[self.md5]) > 1:
                self.thumb_canvas.config(highlightbackground="green", highlightthickness=2)

        self.thumb_canvas.pack(side="top")
        if Ctrl.Cfg.get('showbuttons'):
            hide_button = tk.Button(self, text="Hide", command=self._hide, pady=0)
            delete_button = tk.Button(self, text="Delete", command=self._delete, pady=0)
            hide_button.pack(side="left")
            delete_button.pack(side="right")

    def _hide(self):
        for fo in self.Ctrl.FODict[self.md5]:
            fo.active = False
            self.Ctrl.onFileListChanged()

    def _delete(self):
        self.Ctrl.deleteFOs(
            self.Ctrl.FODict[self.md5],
            Owner=self.Ctrl.TopWindow
        )

    def select(self, value):
        self.selected = value
        if self.selected:
            self.thumb_canvas.config(bg="blue")
            self.Ctrl.lastSelectedXY = (self.X, self.Y)
        else:
            self.thumb_canvas.config(bg="white")
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
