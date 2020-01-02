import tkinter as tk
from tkinter import messagebox as tkmessagebox
from PIL import ImageTk
from ..utils import pillowplus as PP

class viewer(tk.Toplevel):
    "A viewer window to display the selected pictures"
    def __init__(self, Fileinfo=None, Controller=None):
        super().__init__()

        self._MD5s, self._filenames = zip(*Fileinfo)
        self._MD5s = list(self._MD5s)
        self._filenames = list(self._filenames)
        
        self.Ctrl = Controller

        self.geometry(self.Ctrl.Cfg.get('viewergeometry'))
        self.bind("<Key>", self._key)
        self.protocol("WM_DELETE_WINDOW", self._exitViewer)

        self._ImgDict = {}
        self._ImgIndex = 0

        self._canvas = tk.Canvas(self, bg="white")
        self._canvas.pack(fill='both', expand=True)
        self._canvas.update_idletasks()
        self._canvas.bind("<Button>", self._click)

        self.bind("<Configure>", self._showImage)

    def _fillImgDict(self, Index):
        maxW = self._canvas.winfo_width()
        maxH = self._canvas.winfo_height()
        # check if this image already exists?
        if Index in self._ImgDict:
            File, Img, W, H, targetW, targetH = self._ImgDict[Index]
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
        File = self._filenames[Index]
        Img = PP.imageOpen(File)
        W = Img.size[0]
        H = Img.size[1]
        # scale down if too large
        if W > maxW or H > maxH:
            Img = PP.imageResizeToFit(Img, maxW, maxH)
        self._ImgDict[Index] = (File, ImageTk.PhotoImage(Img), W, H, maxW, maxH)

    # clicks
    def _click(self, event):
        if event.num in [1, 4]:
            self._showNext()
        else:
            self._showPrevious()

    # keys
    def _key(self, event):
        keyDict = {
            'space':self._showNext,
            'n':self._showNext,
            'Right':self._showNext,
            'p':self._showPrevious,
            'Left':self._showPrevious,
            'd':self._deleteFile,
            'Delete':self._deleteFile ,
            'h':self._showHelp,
            'F1':self._showHelp,
            'q':self._exitViewer,
            'Escape':self._exitViewer
            }
        if not event.keysym in keyDict:
            return
        keyDict[event.keysym]()

    def _showImage(self, *args):
        self._canvas.delete("all")
        self._fillImgDict(self._ImgIndex)
        self._canvas.create_image(
            self._canvas.winfo_width()/2,
            self._canvas.winfo_height()/2,
            anchor='center',
            image=self._ImgDict[self._ImgIndex][1]
        )
        self.title("Similar Image Viewer: %s --- Press F1 for Help" % self._ImgDict[self._ImgIndex][0])

    def _showNext(self):
        self._ImgIndex += 1
        self._ImgIndex = self._ImgIndex % len(self._filenames)
        #if the filename is none skip to next
        if self._filenames[self._ImgIndex] == None:
            self._showNext()
        self._showImage()

    def _showPrevious(self):
        self._ImgIndex -= 1
        self._ImgIndex = self._ImgIndex % len(self._filenames)
        if self._filenames[self._ImgIndex] == None:
            self._showPrevious()
        self._showImage()

    def _deleteFile(self):
        md5 = self._MD5s[self._ImgIndex]
        fo = [self.Ctrl.FODict[md5][0]]
        if not self.Ctrl.deleteFOs(fo, Owner=self):
            return

        # remove the filename
        self._filenames[self._ImgIndex] = None
        self._MD5s[self._ImgIndex] = None
        del self._ImgDict[self._ImgIndex]
        # check if all filenames are None
        if len(set(self._filenames)) > 1:
            self._showNext()
        else:
            self.destroy()

    def _showHelp(self):
        msg = '''
SiMilar ImaGe viewer:

This windows show the selected images to be able to compare them.
The mouse allow to browse though the images:
Left button: forward
Right button: backward
The scrollwheel should also work

The following keys are defined:
i, F1: show this help
n, Right, Spacebar: show the next image
p, Left: show the previous images
d, Delete: delete the file from your hard disk!
q, Escape: quit the viewer
'''
        tkmessagebox.showinfo("Information", msg, parent=self)

    def _exitViewer(self):
        self.Ctrl.Cfg.set('viewergeometry', self.geometry())
        self.destroy()
