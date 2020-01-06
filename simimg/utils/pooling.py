''' Functions on the image files that take time.
    Like file-hasing and image-hashing
    They are organised to be done in multiprocessing.'''
import hashlib
from operator import add
import functools
from multiprocessing import Pool
from PIL import Image
from . import database as DB
from . import pillowplus as PP

# box that contains the whole image
onebox = [(0.0, 0.0, 1.0, 1.0)]

# size of boxes that has ~equal amount over overlap between the boxes
# and the amount of unsampled area
fiveboxsize = 0.46
fiveboxes = [
    (0.0, 0.0,  fiveboxsize,    fiveboxsize),
    (0.0, 1-fiveboxsize,  fiveboxsize,  1.0),
    (1-fiveboxsize, 0.0, 1.0,   fiveboxsize),
    (1-fiveboxsize, 1-fiveboxsize, 1.0, 1.0),
    (0.5-fiveboxsize/2.0, 0.5-fiveboxsize/2.0, 0.5+fiveboxsize/2.0, 0.5+fiveboxsize/2.0)
]

# not very careful but quick median function
def statsmedian(a):
    aa = sorted(a)
    return aa[round(len(aa)*0.50)]

# not very careful but quick 4-quantiles function
def statsquantiles(a):
    aa = sorted(a)
    return [aa[round(len(aa)*i)] for i in [0.25, 0.5, 0.75]]

def CalculateMD5Hash(file):
    hasher = hashlib.md5()
    with open(file, 'rb') as afile:
        hasher.update(afile.read())
    return (file, hasher.hexdigest())

def GetMD5Hashes(filelist, hashValueDict):
    '''return md5 hashing value for each file the list.'''
    missingfilelist = list(set(filelist) - set(hashValueDict.keys()))
    with Pool() as pool:
        calculatedHashes = pool.map(CalculateMD5Hash, missingfilelist)
    hashValueDict.update(calculatedHashes)
    return hashValueDict

def subImage(Img, FracBox):
    ''' return a subImage from Image based on coordinates in dimensionless units'''
    width, height = Img.size
    left = round(width*FracBox[0])
    right = round(width*FracBox[2])
    bottom = round(height*FracBox[1])
    top = round(height*FracBox[3])
    return Img.crop((left, bottom, right, top))

def colhash(Img, colorspace=None, five=False):
    ''' Regrouped colour hashing function to avoid repeating code.'''

    #requested colorspace defaults to HSV
    cspace = colorspace if colorspace else 'HSV'
    # one box or five boxes requested
    boxes = fiveboxes if five else onebox

    # The image is not in the requested mode, convert
    if not Img.mode == cspace:
        Img = Img.convert(cspace)

    # resample to speed up the calculation
    Img = Img.resize((100,100), Image.BOX)

    # split in bands
    channels = [ch.getdata() for ch in Img.split()]

    values = []
    # get measurements for each box
    for bx in boxes:
        # get a measurement for each channel
        for idx, ch in enumerate(channels):
            data = subImage(ch, bx)
            if cspace == 'HSV' and idx == 1:
                data = list(data)
                medianH = statsmedian(data)
                quant = statsquantiles([(h-medianH+128) % 255 for h in data])
                values.append(round(medianH))
                values.append(round(quant[2] - quant[0]))
            else:
                quant = statsquantiles(data)
                values.append(round(quant[1]))
                values.append(round(quant[2] - quant[0]))
    return values

def hsvhash(Img):
    return colhash(Img, colorspace='HSV', five=False)

def hsv5hash(Img):
    return colhash(Img, colorspace='HSV', five=True)

def rgbhash(Img):
    return colhash(Img, colorspace='RGB', five=False)

def rgb5hash(Img):
    return colhash(Img, colorspace='RGB', five=True)

def lhash(Img):
    return colhash(Img, colorspace='L', five=False)

def l5hash(Img):
    return colhash(Img, colorspace='L', five=True)

def dhash(Img, doVertical=False):
    if doVertical:
        i8x8 = Img.convert('L').resize((8, 9), Image.BOX).transpose(Image.ROTATE_90)
    else:
        i8x8 = Img.convert('L').resize((9, 8), Image.BOX)

    values = []
    for y in range(8):
        val = functools.reduce(
            add,
            [(i8x8.getpixel((x+1, y)) > i8x8.getpixel((x, y)))*(2**x) for x in range(8)]
        )
        values.append(val)
    return values

def dhash_horizontal(Img):
    return dhash(Img)

def dhash_vertical(Img):
    return dhash(Img, doVertical=True)

def CalculateImageHash(args):
    md5, FullPath, hashName = args
    funcdict = {
        'HSV': hsvhash,
        'HSV (5 regions)': hsv5hash,
        'RGB': rgbhash,
        'RGB (5 regions)': rgb5hash,
        'Luminosity': lhash,
        'Luminosity (5 regions)': l5hash,
        'Horizontal': dhash_horizontal,
        'Vertical': dhash_vertical,
        }
    return (md5, funcdict[hashName](PP.imageOpen(FullPath)))

def GetImageHashes(FODict, hashName, db_connection=None):
    '''return hashing value according to selected hashName method
    for each file the (file,md5) list.'''

    ## create an empty dict to hold the results
    hashValueDict = {} ## md5:hashValue

    ## create an empty list to hold md5,file,hashName tuples that need to be calculated
    needCalculating = []

    ## for each uniq md5 in the requested file in FODict
    ## check if the FileObject has the hash value already list.
    ## if yes take it
    #
    ## if none:
    ## get the hash value for this method and this md5 from the database or None
    #
    ## if none add the info to the needCalculating list

    for md5, imageFileObjectList in FODict.items():
        firstFO = imageFileObjectList[0]
        if hashName in firstFO.hashDict:
            hashValueDict[md5] = firstFO.hashDict[hashName]
            continue

        hashValue = DB.GetHashValueFromDataBase(md5, hashName, db_connection=db_connection)
        if hashValue is None:
            needCalculating.append((md5, firstFO.FullPath, hashName))
        else:
            hashValueDict[md5] = hashValue

    ## For the md5 with None calculate the hashValue in a pool of workers
    ## Returning (md5, imagehash)
    if needCalculating:

        with Pool() as pool:
            calculatedHashes = pool.map(CalculateImageHash, needCalculating)

        hashValueDict.update(calculatedHashes)

        ## update the database with the new md5, method, hashValueDict
        DB.SetHashValues(calculatedHashes, hashName, db_connection=db_connection)

    # write everything back to each fileobject
    # behind every md5 key in the FODict is a list of fileobjects with corresponding md5
    for md5, hashValue in hashValueDict.items():
        for FO in FODict[md5]:
            FO.hashDict[hashName] = hashValue

def getOneThumb(arg):
    md5, filename, tsize, channel = arg
    img = PP.thumbnailOpen(filename, tsize, tsize, channel=channel)
    return (md5, img)

def GetMD5Thumbnails(FODict, Thumbsize=None, channel='Default'):
    '''return thumbnail for each md5 in FODict.'''
    args = [(md5, fo[0].FullPath, Thumbsize, channel) for md5, fo in FODict.items()]
    ThumbDict = {} ## md5, thumbnail
    with Pool() as pool:
        calculatedthumbs = pool.map(getOneThumb, args)
    ThumbDict.update(calculatedthumbs)
    return ThumbDict
