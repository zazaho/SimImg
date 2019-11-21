import tkinter as tk
from PIL import ImageTk, Image

class ImageFrame(tk.Frame):
    " A frame that holds one image thumbnail with its buttons"
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.image = None
        self.FileObject = None
        self.ThumbSize = parent.ThumbImageSize
        self.BorderWidth = parent.ThumbBorderWidth
        self.config(relief="groove",borderwidth=self.BorderWidth)
        self.make_widgets()
        
    def make_widgets(self):
        self.thumb_canvas = tk.Canvas(self,
                                      width=self.ThumbSize[0],
                                      height=self.ThumbSize[1],
                                      bg="white",
                                      relief="groove",
                                      borderwidth=self.BorderWidth)
        self.thumb_canvas.bind("<Button-1>", self.thumb_click)
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

    def resize_aspect_fit(self, image):
        resize_ratio_x = image.size[0]/self.ThumbSize[0]
        resize_ratio_y = image.size[1]/self.ThumbSize[1]
        resize_ratio = max(resize_ratio_x,resize_ratio_y)
        new_image_height = int(image.size[0] / resize_ratio)
        new_image_length = int(image.size[1] / resize_ratio)
        return image.resize((new_image_height, new_image_length), Image.ANTIALIAS)

    def thumb_load_image(self):
        image = Image.open(self.FileObject.FullPath)
        self.image = ImageTk.PhotoImage(
            self.resize_aspect_fit(image)
        )
        self.thumb_canvas.create_image(
            self.BorderWidth+self.ThumbSize[0]/2,
            self.BorderWidth+self.ThumbSize[1]/2,
            anchor='center',
            image=self.image
        )
