""" Module for show the viewer window """
import tkinter as tk
from tkinter import messagebox as tkmessagebox

import simimg.utils.pillowplus as PP


class Viewer(tk.Toplevel):
    "A viewer window to display the selected pictures"

    def __init__(self, Fileinfo=None, Controller=None):
        super().__init__()

        self._checksums, self._filenames = map(list, zip(*Fileinfo))

        self._Ctrl = Controller

        self.geometry(self._Ctrl.Cfg.get("viewergeometry"))
        self.protocol("WM_DELETE_WINDOW", self._exitViewer)

        self._ImgDict = {}
        self._ImgIndex = 0
        # the pillow image object (not scaled photoimage)
        self._Img = None

        self._zoomLevelDict = {
            1: 2,
            2: 3,
            3: 4,
            4: 10,
            5: 20,
            6: 100,
            }
        self._zoomLevel = 0
        self._zoomImg = None
        self._zoomImgId = None

        self._keyDict = {
            "space": self._showNext,
            "n": self._showNext,
            "Right": self._showNext,
            "p": self._showPrevious,
            "Left": self._showPrevious,
            "d": self._deleteFile,
            "Delete": self._deleteFile,
            "h": self._showHelp,
            "m": self._moveFile,
            "F1": self._showHelp,
            "q": self._exitViewer,
            "Escape": self._exitViewer
            }
        for i in range(1, self._Ctrl.Cfg.get("numfolders")+1):
            self._keyDict.update({str(i): lambda idx=i: self._moveFile(index=idx)})
        self.bind("<Key>", self._key)

        self._canvas = tk.Canvas(self)
        self._canvas.pack(fill="both", expand=True)
        self._canvas.update_idletasks()
        self._canvas.bind("<Button-1>", self._click)
        self._canvas.bind("<Button-3>", self._click)
        self._canvas.bind("<Button-4>", self._changeZoom)
        self._canvas.bind("<Button-5>", self._changeZoom)
        self._canvas.bind("<MouseWheel>", self._changeZoom)
        self._canvas.bind("<Motion>", self._showZoom)

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
        self._Img = Img
        W = Img.size[0]
        H = Img.size[1]
        # scale down if too large
        if W > maxW or H > maxH:
            Img = PP.imageResizeToFit(Img, maxW, maxH)
        self._ImgDict[Index] = (File, PP.TkPhotoImage(Img), W, H, maxW, maxH)

    # clicks
    def _click(self, event):
        if event.num == 1:
            self._showNext()
        else:
            self._showPrevious()

    # keys
    def _key(self, event):
        if event.keysym not in self._keyDict:
            return
        self._keyDict[event.keysym]()

    def _showImage(self, *args):
        self._canvas.delete("all")
        # unset the Image object
        self._Img = None
        # reset the zoom level
        self._zoomLevel = 0
        self._fillImgDict(self._ImgIndex)
        self._canvas.create_image(
            self._canvas.winfo_width()/2,
            self._canvas.winfo_height()/2,
            anchor="center",
            image=self._ImgDict[self._ImgIndex][1],
        )
        self.title(
            f"Similar Image Viewer: {self._ImgDict[self._ImgIndex][0]} --- Press F1 for Help"
        )

    def _showNext(self):
        self._ImgIndex += 1
        self._ImgIndex = self._ImgIndex % len(self._filenames)
        # if the filename is none skip to next
        if self._filenames[self._ImgIndex] is None:
            self._showNext()
        self._showImage()

    def _showPrevious(self):
        self._ImgIndex -= 1
        self._ImgIndex = self._ImgIndex % len(self._filenames)
        if self._filenames[self._ImgIndex] is None:
            self._showPrevious()
        self._showImage()

    def _deleteFile(self):
        checksum = self._checksums[self._ImgIndex]
        fo = [self._Ctrl.FODict[checksum][0]]
        if not self._Ctrl.deleteFOs(fo, Owner=self):
            return

        # remove the filename
        self._filenames[self._ImgIndex] = None
        self._checksums[self._ImgIndex] = None
        del self._ImgDict[self._ImgIndex]
        # check if all filenames are None
        if len(set(self._filenames)) > 1:
            self._showNext()
        else:
            self.destroy()

    def _moveFile(self, **kwargs):
        checksum = self._checksums[self._ImgIndex]
        fo = [self._Ctrl.FODict[checksum][0]]
        if not self._Ctrl.moveFOs(fo, **kwargs):
            return

        # remove the filename
        self._filenames[self._ImgIndex] = None
        self._checksums[self._ImgIndex] = None
        del self._ImgDict[self._ImgIndex]
        # check if all filenames are None
        if len(set(self._filenames)) > 1:
            self._showNext()
        else:
            self.destroy()

    def _changeZoom(self, event):
        if (event.delta > 0 or event.num == 4):
            if self._zoomLevel < len(self._zoomLevelDict):
                self._zoomLevel += 1
        elif (event.delta < 0 or event.num == 5):
            if self._zoomLevel > 0:
                self._zoomLevel -= 1
        self._showZoom(event)

    def _showZoom(self, event):

        # remove the old zoom
        if self._zoomImgId:
            self._canvas.delete(self._zoomImgId)

        # if no zoom requested return
        if not self._zoomLevel:
            return

        fName, pImage, imgW, imgH, canvasW, canvasH = self._ImgDict[self._ImgIndex]

        if not self._Img:
            self._Img = PP.imageOpen(fName)

        # size of the shown image in canvas units
        shownImgW = pImage.width()
        shownImgH = pImage.height()

        # in normalised units
        # taking care of possible empty space around the shown image
        # half above/below or left/right
        normX = (event.x - (canvasW - shownImgW)/2)/shownImgW
        normY = (event.y - (canvasH - shownImgH)/2)/shownImgH

        # size of the enlarged area in canvas pixels
        zoomSize = round(0.5*max(canvasW, canvasH))

        # the corresponding size of the enlarged area in normalised units
        normSizeX = zoomSize/shownImgW
        normSizeY = zoomSize/shownImgH

        # calculate the corners of the box we want
        X0 = imgW*(normX - normSizeX/2 / self._zoomLevelDict[self._zoomLevel])
        X1 = imgW*(normX + normSizeX/2 / self._zoomLevelDict[self._zoomLevel])
        Y0 = imgH*(normY - normSizeY/2 / self._zoomLevelDict[self._zoomLevel])
        Y1 = imgH*(normY + normSizeY/2 / self._zoomLevelDict[self._zoomLevel])

        # take ROI of the original image and scale it
        self._zoomImg = PP.TkPhotoImage(
            PP.imageResize(self._Img.crop((X0, Y0, X1, Y1)), zoomSize, zoomSize)
            )
        self._zoomImgId = self._canvas.create_image(
            event.x,
            event.y,
            anchor="center",
            image=self._zoomImg
        )

    def _showHelp(self):
        msg = """
SiMilar ImaGe viewer:

This windows show the selected images to be able to compare them.
The mouse allow to browse though the images:
Left button: forward
Right button: backward
The scrollwheel allow to zoom on part of the image

The following keys are defined:
i, F1: show this help
n, Right, Spacebar: show the next image
p, Left: show the previous images
d, Delete: delete the file from your hard disk!
m: move the file to the folder set in the main window
<n>: move the file to the folder #n move panel of the main window
q, Escape: quit the viewer
"""
        tkmessagebox.showinfo("Information", msg, parent=self)

    def _exitViewer(self):
        self._Ctrl.Cfg.set("viewergeometry", self.geometry())
        del self._ImgDict
        self.destroy()
