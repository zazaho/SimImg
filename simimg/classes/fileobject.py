''' The basic object that represents one file '''
import hashlib
from datetime import datetime
from PIL import Image, ExifTags
import simimg.utils.pillowplus as PP

class FileObject():
    ' File object that contains all information relating to one file on disk '
    def __init__(self, parent, FullPath=None, MD5HashesDict=None):

        self.Cfg = parent.Cfg
        self.FullPath = FullPath
        #self.DirName = os.path.dirname(self.FullPath)
        #self.FileName = os.path.basename(self.FullPath)
        #dummy, self.FileExtension = os.path.splitext(self.FileName)

        self.hashDict = {}

        # These are private variables that allow to call the corresponding method
        # If the variable is None we calculate the value
        # otherwise we return the value of this private variable
        self._IsImage = None
        self._md5 = MD5HashesDict[FullPath] if FullPath in MD5HashesDict else None
        self._ExifTags = None
        self._Thumbnail = None
        self._DateTime = None
        self._Size = None

        #It this file active
        self.active = True

    def IsImage(self):
        ' Set IsImage to True if the file can be read by PIL '
        if self._IsImage is None:
            try:
                img = Image.open(self.FullPath)
                self._IsImage = True
                # do this here to save time
                self._Size = img.size
            except IOError:
                self._IsImage = False
        return self._IsImage

    def md5(self):
        if self._md5 is None:
            hasher = hashlib.md5()
            with open(self.FullPath, 'rb') as afile:
                hasher.update(afile.read())
                self._md5 = hasher.hexdigest()
        return self._md5

    def ExifTags(self):
        if self._ExifTags is None:
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

    def DateTime(self):
        if self._DateTime is None:
            thisDateString = self.Date()
            if thisDateString == '':
                self._DateTime = 'Missing'
                return self._DateTime
            try:
                self._DateTime = datetime.strptime(thisDateString ,'%Y:%m:%d %H:%M:%S')
            except ValueError:
                self._DateTime = 'Missing'
        return self._DateTime

    def Size(self):
        if self._Size is None:
            self._Size = (0, 0)
            with Image.open(self.FullPath) as image:
                self._Size = image.size
        return self._Size

    def ShapeParameter(self):
        w, h = self.Size()
        # (width-height)/(width+height)*100
        # positive for landscape, negative for portait
        return (w-h)/(w+h)*100

    def Thumbnail(self):
        if self._Thumbnail is None:
            ThumbSize = self.Cfg.get('thumbnailsize')
            self._Thumbnail = PP.photoImageOpenAndResizeToFit(self.FullPath, ThumbSize, ThumbSize)
        return self._Thumbnail
