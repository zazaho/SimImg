""" The basic object that represents one file """
from functools import cached_property
import hashlib
import os
from datetime import datetime

from PIL import Image, ExifTags

import simimg.utils.pillowplus as PP


class FileObject():
    " File object that contains all information relating to one file on disk "

    def __init__(self, parent, FullPath=None, checksumFilenameDict=None):
        self._Ctrl = parent
        self._Cfg = parent.Cfg
        self.fullPath = FullPath
        self.dirName = os.path.dirname(self.fullPath)
        self.fileName = os.path.basename(self.fullPath)
        dummy, self.fileExtension = os.path.splitext(self.fileName)

        self.hashDict = {}

        self._checksum = (
            checksumFilenameDict[FullPath]
            if FullPath in checksumFilenameDict
            else None
        )
        self._size_ = None
        self._thumbnail = None
        # It this file active
        self.active = True

    @cached_property
    def isImage(self):
        " Set IsImage to True if the file can be read by PIL "
        img = PP.imageOpen(self.fullPath)
        if not img:
            return False
        self._size_ = img.size
        return True

    def checksum(self):
        if self._checksum is None:
            hasher = hashlib.sha1()
            with open(self.fullPath, "rb") as afile:
                hasher.update(afile.read())
                self._checksum = hasher.hexdigest()
        return self._checksum

    @cached_property
    def exifTags(self):
        # default to empty basic values
        exifTags = {
            "Make": "",
            "Model": "",
            "DateTimeOriginal": "",
            "DateTime": "",
            "DateTimeDigitized": ""
        }
        # Rotating in pillow removes exifTags
        image = PP.imageOpenNoRotate(self.fullPath)
        if not image or not hasattr(image, "_getexif") or not (exif := image._getexif()):
            return exifTags
        for key, value in exif.items():
            if (exif_label := ExifTags.TAGS.get(key)) in exifTags:
                exifTags[exif_label] = value
        return exifTags

    def cameraMake(self):
        return self.exifTags["Make"]

    def cameraModel(self):
        return self.exifTags["Model"]

    def date(self):
        if self.exifTags["DateTimeOriginal"]:
            return self.exifTags["DateTimeOriginal"]
        if self.exifTags["DateTime"]:
            return self.exifTags["DateTime"]
        if self.exifTags["DateTimeDigitized"]:
            return self.exifTags["DateTimeDigitized"]
        return ""

    @cached_property
    def dateTime(self):
        thisDateString = self.date()
        if thisDateString == "":
            return "Missing"
        try:
            dateTime = datetime.strptime(
                thisDateString,
                "%Y:%m:%d %H:%M:%S"
            )
        except:
            return "Missing"
        return dateTime

    @cached_property
    def size(self):
        if self._size_ is not None:
            return self._size_
        image = PP.imageOpen(self.fullPath)
        if not image:
            return (0, 0)
        return image.size

    def shapeParameter(self):
        w, h = self.size
        # (width-height)/(width+height)*100
        # positive for landscape, negative for portait
        return (w-h)/(w+h)*100

    def thumbnail(self):
        if self._thumbnail is None:
            ThumbSize = self._Cfg.get("thumbnailsize")
            self._thumbnail = PP.photoImageOpenAndResizeToFit(
               self.fullPath,
               ThumbSize,
               ThumbSize
           )
        return self._thumbnail
