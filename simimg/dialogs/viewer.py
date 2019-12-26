import tkinter as tk
from PIL import ImageTk
import simimg.utils.pillowplus as PP

class viewer(tk.Toplevel):
    "A viewer window to display the selected pictures"
    def __init__(self, Fileinfo=None, Controller=None):
        super().__init__()

        self.Filenames = [f for _, f in Fileinfo]
        self.MD5s = [m for m, _ in Fileinfo]
        self.Ctrl = Controller

        self.geometry(self.Ctrl.Cfg.get('viewergeometry'))

        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(fill='both', expand=True)
        self.canvas.update_idletasks()
        self.canvas.bind("<Button>", self._click)
        self.bind("<Key>", self._key)
        self.ImgDict = {}
        self.ImgIndex = 0
        self.protocol("WM_DELETE_WINDOW", self._exitViewer)
        self.bind("<Configure>", self._showImage)

    def _fillImgDict(self, Index):
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
        Img = PP.imageOpen(File)
        W = Img.size[0]
        H = Img.size[1]
        # scale down if too large
        if W > maxW or H > maxH:
            Img = PP.imageResizeToFit(Img, maxW, maxH)
        self.ImgDict[Index] = (File, ImageTk.PhotoImage(Img), W, H, maxW, maxH)

    # clicks
    def _click(self, event):
        if event.num in [1, 4]:
            self._showNext()
        else:
            self._showPrevious()

    # keys
    def _key(self, event):
        keyDict = {
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
        self.canvas.delete("all")
        self._fillImgDict(self.ImgIndex)
        self.canvas.create_image(
            self.canvas.winfo_width()/2,
            self.canvas.winfo_height()/2,
            anchor='center',
            image=self.ImgDict[self.ImgIndex][1]
        )
        self.title("Similar Image Viewer: %s --- Press F1 for Help" % self.ImgDict[self.ImgIndex][0])

    def _showNext(self):
        self.ImgIndex += 1
        self.ImgIndex = self.ImgIndex % len(self.Filenames)
        #if the filename is none skip to next
        if self.Filenames[self.ImgIndex] == None:
            self._showNext()
        self._showImage()

    def _showPrevious(self):
        self.ImgIndex -= 1
        self.ImgIndex = self.ImgIndex % len(self.Filenames)
        if self.Filenames[self.ImgIndex] == None:
            self._showPrevious()
        self._showImage()

    def _deleteFile(self):
        md5 = self.MD5s[self.ImgIndex]
        fo = [self.Ctrl.FODict[md5][0]]
        if not self.Ctrl.deleteFOs(fo, Owner=self):
            return

        # remove the filename
        self.Filenames[self.ImgIndex] = None
        self.MD5s[self.ImgIndex] = None
        del self.ImgDict[self.ImgIndex]
        # check if all filenames are None
        if len(set(self.Filenames)) > 1:
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
n, Right: show the next image
p, Left: show the previous images
d, Delete: delete the file from your hard disk!
q, Escape: quit the viewer
'''
        tk.messagebox.showinfo("Information", msg, parent=self)

    def _exitViewer(self):
        self.Ctrl.Cfg.set('viewergeometry', self.geometry())
        self.destroy()
