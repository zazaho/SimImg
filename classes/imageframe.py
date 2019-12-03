import tkinter as tk
from PIL import ImageTk, Image

class ImageFrame(tk.Frame):
    " A frame that holds one image thumbnail with its buttons"
    def __init__(self, parent, md5=None, Ctrl=None):
        super().__init__(parent)

        self.Ctrl = Ctrl
        self.Cfg = Ctrl.Cfg
        self.md5 = md5
        self.ThumbSize = self.Cfg.get('ThumbImageSize')
        self.BorderWidth = self.Cfg.get('ThumbBorderWidth')

        self.config(relief="groove",borderwidth=self.BorderWidth)
        self.thumb_canvas = tk.Canvas(self,
                                      width=self.ThumbSize[0],
                                      height=self.ThumbSize[1],
                                      bg="white",
                                      relief="groove",
                                      borderwidth=self.BorderWidth)
        self.thumb_canvas.bind("<Button-1>", self.thumb_click)

        if md5:
            self.thumb_canvas.create_image(
                self.BorderWidth+self.ThumbSize[0]/2,
                self.BorderWidth+self.ThumbSize[1]/2,
                anchor='center',
                image=Ctrl.FODict[md5][0].Thumbnail()
            )

        self.select_button = tk.Button(self, text="Select", command=self.button_select)
        self.hide_button = tk.Button(self, text="Hide", command=self.button_hide)
        self.delete_button = tk.Button(self, text="Delete", command=self.button_delete)

        self.thumb_canvas.pack(side=tk.TOP)
        self.select_button.pack(side=tk.LEFT)
        self.hide_button.pack(side=tk.LEFT)
        self.delete_button.pack(side=tk.LEFT)

    def button_select(self):
        pass

    def button_hide(self):
        pass

    def button_delete(self):
        pass

    def thumb_click(self,event):
        print("clicked at", event.x, event.y)
