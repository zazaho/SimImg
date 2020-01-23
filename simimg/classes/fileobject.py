''' The basic object that represents one file '''
import os
import hashlib
from datetime import datetime
from PIL import Image, ExifTags
from ..utils import pillowplus as PP


class FileObject():
    ' File object that contains all information relating to one file on disk '

    def __init__(self, parent, FullPath=None, checksumFilenameDict=None):
        self._Ctrl = parent
        self._Cfg = parent.Cfg
        self.fullPath = FullPath
        self.dirName = os.path.dirname(self.fullPath)
        self.fileName = os.path.basename(self.fullPath)
        dummy, self.fileExtension = os.path.splitext(self.fileName)

        self.hashDict = {}

        # These are private variables that allow to call the
        # corresponding method for cheap
        # If the variable is None we calculate the value
        # otherwise we return the value of this private variable
        self._isImage = None
        self._checksum = checksumFilenameDict[FullPath] if FullPath in checksumFilenameDict else None
        self._exifTags = None
        self._thumbnail = None
        self._dateTime = None
        self._size = None
        # It this file active
        self.active = True

    def isImage(self):
        ' Set IsImage to True if the file can be read by PIL '
        if self._isImage is None:
            try:
                img = Image.open(self.fullPath)
                self._isImage = True
                # do this here to save time
                self._size = img.size
            except:
                self._isImage = False
        return self._isImage

    def checksum(self):
        if self._checksum is None:
            hasher = hashlib.sha1()
            with open(self.fullPath, 'rb') as afile:
                hasher.update(afile.read())
                self._checksum = hasher.hexdigest()
        return self._checksum

    def exifTags(self):
        if self._exifTags is None:
            # default to empty basic values
            self._exifTags = {
                'Make': '',
                'Model': '',
                'DateTimeOriginal': '',
                'DateTime': '',
                'DateTimeDigitized': ''
            }
            with Image.open(self.fullPath) as image:
                # image does not have method to get tags
                if not hasattr(image, '_getexif'):
                    return self._exifTags
                exif = image._getexif()
                # image does not have tags
                if not exif:
                    return self._exifTags
                for key, value in exif.items():
                    if key in ExifTags.TAGS:
                        self._exifTags[ExifTags.TAGS[key]] = value
        return self._exifTags

    def cameraMake(self):
        return self.exifTags()['Make']

    def cameraModel(self):
        return self.exifTags()['Model']

    def date(self):
        if self.exifTags()['DateTimeOriginal']:
            return self.exifTags()['DateTimeOriginal']
        if self.exifTags()['DateTime']:
            return self.exifTags()['DateTime']
        if self.exifTags()['DateTimeDigitized']:
            return self.exifTags()['DateTimeDigitized']
        return ''

    def dateTime(self):
        if self._dateTime is None:
            thisDateString = self.date()
            if thisDateString == '':
                self._dateTime = 'Missing'
                return self._dateTime
            try:
                self._dateTime = datetime.strptime(
                    thisDateString,
                    '%Y:%m:%d %H:%M:%S'
                )
            except:
                self._dateTime = 'Missing'
        return self._dateTime

    def size(self):
        if self._size is None:
            self._size = (0, 0)
            with Image.open(self.fullPath) as image:
                self._size = image.size
        return self._size

    def shapeParameter(self):
        w, h = self.size()
        # (width-height)/(width+height)*100
        # positive for landscape, negative for portait
        return (w-h)/(w+h)*100

    def thumbnail(self):
        if self._thumbnail is None:
            ThumbSize = self._Cfg.get('thumbnailsize')
            self._thumbnail = PP.photoImageOpenAndResizeToFit(
                self.fullPath,
                ThumbSize,
                ThumbSize
            )
        return self._thumbnail
