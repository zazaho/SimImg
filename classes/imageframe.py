import tkinter as tk

class ImageFrame(tk.Frame):
    " A frame that holds one image thumbnail with its buttons"
    def __init__(self, parent, md5=None, Ctrl=None, X=None, Y=None):
        super().__init__(parent)

        self.Ctrl = Ctrl
        self.ThumbSize = Ctrl.Cfg.get('ThumbImageSize')
        self.BorderWidth = Ctrl.Cfg.get('ThumbBorderWidth')
        self.md5 = md5
        self.selected = False
        self.X = X
        self.Y = Y
        
        #self.config(relief="groove",borderwidth=self.BorderWidth)
        self.thumb_canvas = tk.Canvas(self,
                                      width=self.ThumbSize[0],
                                      height=self.ThumbSize[1],
                                      bg="white",
                                      relief="groove",
                                      borderwidth=self.BorderWidth)
        self.thumb_canvas.bind("<Button-1>", self.thumb_click)

        if self.md5:
            self.thumb_canvas.create_image(
                self.BorderWidth+self.ThumbSize[0]/2,
                self.BorderWidth+self.ThumbSize[1]/2,
                anchor='center',
                image=Ctrl.FODict[self.md5][0].Thumbnail()
            )
            if len(Ctrl.FODict[self.md5]) > 1:
                self.thumb_canvas.config(highlightbackground="green", highlightthickness=2)

        self.hide_button = tk.Button(self, text="Hide", command=self.button_hide, pady=0)
        self.delete_button = tk.Button(self, text="Delete", command=self.button_delete, pady=0)

        self.thumb_canvas.pack(side=tk.TOP)
        self.hide_button.pack(side=tk.LEFT)
        self.delete_button.pack(side=tk.RIGHT)

    def button_hide(self):
        for fo in self.Ctrl.FODict[self.md5]:
            fo.Active = False
            self.Ctrl.onThumbnailChanged()

    def button_delete(self):
        pass

    def setSelected(self, value):
        self.selected = value
        if self.selected:
            self.thumb_canvas.config(bg="blue")
            self.Ctrl.lastSelectedXY = (self.X, self.Y)
        else:
            self.thumb_canvas.config(bg="white")
            self.Ctrl.lastSelectedXY = None

    def thumb_click(self, event):
        if (event.state & 0x4) != 0:
            self.Ctrl.toggleSelectRow(self.Y, not self.selected)
            return
        if (event.state & 0x1) != 0:
            self.Ctrl.selectRangeFromLastSelected(self.X, self.Y)
            return
        self.setSelected(not self.selected)
