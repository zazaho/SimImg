from multiprocessing import Pool
from PIL import Image, ImageTk

def GetMD5Thumbnails(FODict, Thumbsize=(150, 150)):
    '''return thumbnail for each md5 in FODict.'''
    args = [(md5, fo[0].FullPath, Thumbsize) for md5, fo in FODict.items()]
    ThumbDict = {} ## md5, thumbnail
    with Pool() as pool:
        calculatedthumbs = pool.map(getOneThumb, args)
    ThumbDict.update(calculatedthumbs)
    return ThumbDict
    
def getOneThumb(arg):
    md5, filename, tsize = arg
    img = Image.open(filename)
    ratio = max(img.size[0]/tsize[0], img.size[1]/tsize[1])
    img = img.resize(
        (int(img.size[0]/ratio), int(img.size[1]/ratio)),
        Image.ANTIALIAS
    )
    return (md5, img)
