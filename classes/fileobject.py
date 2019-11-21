' The basic object that represents one file '

import os
import hashlib
from PIL import ImageTk, Image

class FileObject(object):
    ' File object that contains all information relating to one file on disk '
    def __init__(self, parent, FullPath=None, *args, **kwargs):

        self.FullPath = FullPath
        self.DirName = os.path.dirname(self.FullPath)
        self.FileName = os.path.basename(self.FullPath)
        dummy, self.FileExtension = os.path.splitext(self.FileName)

        self.ahash = None
        self.dhash = None
        self.phash = None
        self.whash = None

        # These are private variables that allow to call the corresponding method
        # If the variable is None we calculate the value
        # otherwise we return the value of this private variable

        self._IsImage = None
        self._md5 = None

        #thumbnail object
        self.ThumbFrame = None

        #Is the thumbnail shown
        self.ThumbFrameHidden = True
        self.ThumbFramePosition = (-1,-1)
        
        #It this file active
        self.Active = True
        self.Selected = False

    def IsImage(self):
        ' Set IsImage to True if the file can be read by PIL '
        if not self._IsImage:
            try:
                Image.open(self.FullPath)
                self._IsImage = True
            except IOError:
                self._IsImage = False
        return self._IsImage


    def md5(self):
        if not self._md5:
            hasher = hashlib.md5()
            with open(self.FullPath, 'rb') as afile:
                buf = afile.read()
                hasher.update(buf)
            self._md5 = hasher.hexdigest()
        return self._md5
            
    def MakeThumbnail(self):
        self.ThumbFrame.thumb_load_image()
