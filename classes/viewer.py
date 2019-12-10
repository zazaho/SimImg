import tkinter as tk
from PIL import Image,  ImageTk
import classes.tooltip as TT

class viewer(tk.Toplevel):
    "A viewer window to display the selected pictures"
    def __init__(self, Filenames=None, Controller=None):
        super().__init__()

        self.Filenames = Filenames
        self.Ctrl = Controller
        
        self.geometry(self.Ctrl.Cfg.get('ViewerGeometry'))

        self.canvas = tk.Canvas(self,bg="white")
        self.canvas.pack(fill='both', expand=True)
        self.canvas.update()
        self.canvas.bind("<Button>", self.clicked)
        self.bind("<Key>", self.key_press)
        TT.Tooltip(self, text='Press F1 for help')
        self.ImgDict = {}
        self.ImgIndex = 0
        self.showImage()
        self.protocol("WM_DELETE_WINDOW", self.exitViewer)

    def fillImgDict(self, Index):
        maxW = self.canvas.winfo_width()
        maxH = self.canvas.winfo_height()
        # check if this image already exists?
        if Index in self.ImgDict:
            File, Img, W, H, targetW, targetH = self.ImgDict[Index]
            # check if this image has the right dimensions.
            # if the max-dimensions did not change, fine!
            if targetW == maxW and targetH == maxH:
                return
            # if the dimensions did change,  but the image is:
            # small than the old target and smaller than the new target
            # no scaling was done and should be done, fine!
            if W <= maxW and W <= targetW and H <= maxH and H <= targetH:
                return

        # if we get here, we need to create and image tuple
        File = self.Filenames[Index]
        Img = Image.open(File)
        W = Img.size[0]
        H = Img.size[1]
        # scale down if too large
        if W > maxW or H > maxH:
            ratioX = W/maxW
            ratioY = H/maxH
            ratio = max(ratioX, ratioY)
            Img = Img.resize((round(W/ratio), round(H/ratio)),Image.ANTIALIAS)
        self.ImgDict[Index] = (File, ImageTk.PhotoImage(Img), W, H, maxW, maxH)
        
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
        self.fillImgDict(self.ImgIndex)
        self.canvas.create_image(
            self.canvas.winfo_width()/2,
            self.canvas.winfo_height()/2,
            anchor='center',
            image=self.ImgDict[self.ImgIndex][1]
        )
        self.title("SIMilar IMaGe viewer: %s" % self.ImgDict[self.ImgIndex][0])

    def showNext(self):
        self.ImgIndex += 1
        self.ImgIndex = self.ImgIndex % len(self.Filenames)
        self.showImage()
        
    def showPrevious(self):
        self.ImgIndex -= 1
        self.ImgIndex = self.ImgIndex % len(self.Filenames)
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
        self.Ctrl.Cfg.set('ViewerGeometry', self.geometry())
        self.destroy()
