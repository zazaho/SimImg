' The basic object that represents one file '

import os
import hashlib
from datetime import datetime
from dateutil.parser import parse as dateutil_parse
from dateutil.parser import ParserError as dateutil_parserError
from PIL import ImageTk, Image, ExifTags

class FileObject(object):
    ' File object that contains all information relating to one file on disk '
    def __init__(self, parent, FullPath=None, serial=None):

        self.Cfg = parent.Cfg
        self.FullPath = FullPath
        self.DirName = os.path.dirname(self.FullPath)
        self.FileName = os.path.basename(self.FullPath)
        dummy, self.FileExtension = os.path.splitext(self.FileName)

        self.serial = serial

        self.ahash = None
        self.dhash = None
        self.phash = None
        self.whash = None

        # These are private variables that allow to call the corresponding method
        # If the variable is None we calculate the value
        # otherwise we return the value of this private variable

        self._IsImage = None
        self._md5 = None
        self._ExifTags = None
        self._Thumbnail = None
        self._DateUTC = None

        #It this file active
        self.Active = True
        self.Selected = False

    def IsImage(self):
        ' Set IsImage to True if the file can be read by PIL '
        if self._IsImage is not None:
            return self._IsImage

        try:
            Image.open(self.FullPath)
            self._IsImage = True
        except IOError:
            self._IsImage = False
        return self._IsImage


    def md5(self):
        if self._md5 is not None:
            return self._md5

        hasher = hashlib.md5()
        with open(self.FullPath, 'rb') as afile:
            buf = afile.read()
            hasher.update(buf)
            self._md5 = hasher.hexdigest()
        return self._md5
            
    def ExifTags(self):
        if self._ExifTags is not None:
            return self._ExifTags

        # default to empty basic values
        self._ExifTags = {
            'Make': '',
            'Model': '',
            'DateTimeOriginal': '',
            'DateTime': '',
            'DateTimeDigitized': ''
        }
        with Image.open(self.FullPath) as image:
            # image does not have method to get tags
            if not hasattr(image,'_getexif'):
                return self._ExifTags

            exif = image._getexif()
            # image does not have tags
            if not exif:
                return self._ExifTags

            for key, value in exif.items():
                if key in ExifTags.TAGS:
                    self._ExifTags[ExifTags.TAGS[key]] = value
        return self._ExifTags

    def CameraMake(self):
        return self.ExifTags()['Make']

    def CameraModel(self):
        return self.ExifTags()['Model']

    def Date(self):
        if self.ExifTags()['DateTimeOriginal']:
            return self.ExifTags()['DateTimeOriginal']
        if self.ExifTags()['DateTime']:
            return self.ExifTags()['DateTime']
        if self.ExifTags()['DateTimeDigitized']:
            return self.ExifTags()['DateTimeDigitized']
        return ''

    def DateUTC(self):
        if self._DateUTC is not None :
            return self._DateUTC

        thisDateString = self.Date()
        if not thisDateString:
            self._DateUTC = 'Missing'
            return self._DateUTC

        try:
            self._DateUTC = dateutil_parse(thisDateString).timestamp()
        except dateutil_parserError:
            self._DateUTC = 'Missing'

        return self._DateUTC

    def Thumbnail(self):
        if self._Thumbnail:
            return self._Thumbnail

        ThumbSize = self.Cfg.get('ThumbImageSize')
        image = Image.open(self.FullPath)
        resize_ratio_x = image.size[0]/ThumbSize[0]
        resize_ratio_y = image.size[1]/ThumbSize[1]
        resize_ratio = max(resize_ratio_x,resize_ratio_y)
        new_image_height = int(image.size[0] / resize_ratio)
        new_image_length = int(image.size[1] / resize_ratio)
        image = image.resize(
            (new_image_height, new_image_length),
            Image.ANTIALIAS
        )
        self._Thumbnail = ImageTk.PhotoImage(image)
        return self._Thumbnail
