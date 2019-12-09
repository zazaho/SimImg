import tkinter as tk
from PIL import Image,  ImageTk
import classes.tooltip as TT

class viewer(tk.Toplevel):
    "A viewer window to display the selected pictures"
    def __init__(self, parent, Filenames=None):
        super().__init__()

        self.Filenames = Filenames

        self.geometry("%dx%d+0+0" %
                      (self.winfo_screenwidth()*0.9, self.winfo_screenheight()*0.9)
        )

        self.canvas = tk.Canvas(self,bg="white")
        self.canvas.pack(fill='both', expand=True)
        self.canvas.update()
        self.maxImgWidth = self.canvas.winfo_width()
        self.maxImgHeight = self.canvas.winfo_height()
        self.canvas.bind("<Button>", self.clicked)
        self.bind("<Key>", self.key_press)
        TT.Tooltip(self, text='Press F1 for help')
        self.ImgDict = {}
        self.makeImgDict()
        self.ImgIndex = 0
        self.showImage()
        
    def makeImgDict(self):
        for i, file in enumerate(self.Filenames):
            Img = Image.open(file)
            if (Img.size[0] > self.maxImgWidth or Img.size[1] > self.maxImgHeight):
                ratio_x = Img.size[0]/self.maxImgWidth
                ratio_y = Img.size[1]/self.maxImgHeight
                ratio = max(ratio_x, ratio_y)
                Img = Img.resize(
                    (int(Img.size[0]/ratio), int(Img.size[1]/ratio)),
                    Image.ANTIALIAS
            )
            self.ImgDict[i] = (file, ImageTk.PhotoImage(Img))

    # clicks
    def clicked(self, event):
        if event.num in [1,4]:
            self.showNext()
        else:
            self.showPrevious()

    # keys
    def key_press(self, event):
        keyDict = {
            'n':self.showNext,
            'Right':self.showNext,
            'p':self.showPrevious,
            'Left':self.showPrevious,
            'd':self.deleteFile,
            'Delete':self.deleteFile ,
            'h':self.showHelp,
            'F1':self.showHelp,
            'q':self.exitViewer,
            'Escape':self.exitViewer
            }
        if not event.keysym in keyDict:
            return
        keyDict[event.keysym]()

    def showImage(self):
        self.canvas.delete(tk.ALL)
        self.canvas.create_image(
            self.maxImgWidth/2,
            self.maxImgHeight/2,
            anchor='center',
            image=self.ImgDict[self.ImgIndex][1]
        )
        self.title("SIMilar IMaGe viewer: %s" % self.ImgDict[self.ImgIndex][0])

    def showNext(self):
        self.ImgIndex += 1
        self.ImgIndex = self.ImgIndex % len(self.ImgDict)
        self.showImage()
        
    def showPrevious(self):
        self.ImgIndex -= 1
        self.ImgIndex = self.ImgIndex % len(self.ImgDict)
        self.showImage()

    def deleteFile(self):
        pass
    
    def showHelp(self):
        msg = '''
SiMilar ImaGe viewer:

This windows show the selected images to be able to compare them.
The mouse allow to browse though the images:
Left button: forward
Right button: backward
The scrollwheel should also work

The following keys are defined:
i, F1: show this help
n, Right: show the next image
p, Left: show the previous images
d, Delete: delete the file from your hard disk!
q, Escape: quit the viewer
'''
        tk.messagebox.showinfo("Information", msg, parent=self)
        
    def exitViewer(self):
        self.destroy()
