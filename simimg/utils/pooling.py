"""Functions on the image files that take time. Like file-hashing and
image-hashing They are organised to be done in multiprocessing.

"""
import functools
import hashlib
from multiprocessing import Pool
from operator import add

from PIL import Image

import simimg.utils.database as DB
import simimg.utils.pillowplus as PP

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
def statsMedian(a):
    aa = sorted(a)
    return aa[round(len(aa)*0.50)]


# not very careful but quick 4-quantiles function
def statsQuantiles(a):
    aa = sorted(a)
    return [aa[round(len(aa)*i)] for i in [0.25, 0.5, 0.75]]


def calculateChecksum(file):
    hasher = hashlib.sha1()
    with open(file, "rb") as afile:
        hasher.update(afile.read())
    return (file, hasher.hexdigest())


def getChecksums(filelist, hashValueDict):
    """return checksum hashing value for each file the list."""
    missingfilelist = list(set(filelist) - set(hashValueDict.keys()))
    with Pool() as pool:
        calculatedHashes = pool.map(calculateChecksum, missingfilelist)
    hashValueDict.update(calculatedHashes)
    return hashValueDict


def subImage(Img, FracBox):
    "return a subImage from Image based on coordinates in dimensionless units"
    width, height = Img.size
    left = round(width*FracBox[0])
    right = round(width*FracBox[2])
    bottom = round(height*FracBox[1])
    top = round(height*FracBox[3])
    return Img.crop((left, bottom, right, top))


def colorHash(Img, colorspace=None, five=False):
    """ Regrouped colour hashing function to avoid repeating code."""

    # requested colorspace defaults to HSV
    cspace = colorspace if colorspace else "HSV"
    # one box or five boxes requested
    boxes = fiveboxes if five else onebox

    # The image is not in the requested mode, convert
    if not Img.mode == cspace:
        Img = Img.convert(cspace)

    # resample to speed up the calculation
    Img = Img.resize((100, 100), Image.BOX)

    # split in bands
    channels = [ch.getdata() for ch in Img.split()]

    values = []
    # get measurements for each box
    for bx in boxes:
        # get a measurement for each channel
        for idx, ch in enumerate(channels):
            data = subImage(ch, bx)
            if cspace == "HSV" and idx == 1:
                data = list(data)
                medianH = statsMedian(data)
                quant = statsQuantiles([(h-medianH+128) % 255 for h in data])
                values.append(round(medianH))
                values.append(round(quant[2] - quant[0]))
            else:
                quant = statsQuantiles(data)
                values.append(round(quant[1]))
                values.append(round(quant[2] - quant[0]))
    return values


def hsvHash(Img):
    return colorHash(Img, colorspace="HSV", five=False)


def hsv5Hash(Img):
    return colorHash(Img, colorspace="HSV", five=True)


def rgbHash(Img):
    return colorHash(Img, colorspace="RGB", five=False)


def rgb5Hash(Img):
    return colorHash(Img, colorspace="RGB", five=True)


def lHash(Img):
    return colorHash(Img, colorspace="L", five=False)


def l5Hash(Img):
    return colorHash(Img, colorspace="L", five=True)


def dHash(Img, doVertical=False):
    if doVertical:
        i8x8 = Img.convert("L").resize((8, 9), Image.BOX).transpose(Image.ROTATE_90)
    else:
        i8x8 = Img.convert("L").resize((9, 8), Image.BOX)

    values = []
    for y in range(8):
        val = functools.reduce(
            add,
            [(i8x8.getpixel((x+1, y)) > i8x8.getpixel((x, y)))*(2**x) for x in range(8)]
        )
        values.append(val)
    return values


def dHashHorizontal(Img):
    return dHash(Img)


def dHashVertical(Img):
    return dHash(Img, doVertical=True)


def calculateHash(args):
    checksum, fullPath, hashName = args
    funcdict = {
        "HSV": hsvHash,
        "HSV (5 regions)": hsv5Hash,
        "RGB": rgbHash,
        "RGB (5 regions)": rgb5Hash,
        "Luminosity": lHash,
        "Luminosity (5 regions)": l5Hash,
        "Horizontal": dHashHorizontal,
        "Vertical": dHashVertical,
    }
    return (checksum, funcdict[hashName](PP.imageOpen(fullPath)))


def getHashes(FODict, hashName, db_connection=None):
    """return hashing value according to selected hashName method
    for each file the (file,checksum) list."""

    # create an empty dict to hold the results
    hashValueDict = {} # checksum:hashValue

    # create an empty list to hold checksum,file,hashName tuples
    # that need to be calculated
    needCalculating = []

    # for each uniq checksum in the requested file in FODict
    # check if the FileObject has the hash value already list.
    # if yes take it
    #
    # if none:
    # get the hash value for this method and this checksum from the database or None
    #
    # if none add the info to the needCalculating list

    for checksum, fileObjectList in FODict.items():
        firstFO = fileObjectList[0]
        if hashName in firstFO.hashDict:
            hashValueDict[checksum] = firstFO.hashDict[hashName]
            continue

        hashValue = DB.getHash(checksum, hashName, db_connection=db_connection)
        if hashValue is None:
            needCalculating.append((checksum, firstFO.fullPath, hashName))
        else:
            hashValueDict[checksum] = hashValue

    # For the checksum with None calculate the hashValue in a pool of workers
    # Returning (checksum, imagehash)
    if needCalculating:

        with Pool() as pool:
            calculatedHashes = pool.map(calculateHash, needCalculating)

        hashValueDict.update(calculatedHashes)

        # update the database with the new checksum, method, hashValueDict
        DB.setHash(calculatedHashes, hashName, db_connection=db_connection)

    # write everything back to each fileobject
    # every checksum key in the FODict contains a list of fileobjects
    # that match this checksum
    for checksum, hashValue in hashValueDict.items():
        for FO in FODict[checksum]:
            FO.hashDict[hashName] = hashValue


def getOneThumb(arg):
    checksum, filename, tsize, channel, upscale = arg
    img = PP.thumbnailOpen(
        filename,
        tsize,
        tsize,
        channel=channel,
        upscale=upscale
    )
    return (checksum, img)


def getThumbnails(FODict, Thumbsize=None, channel="Default", upscale=False):
    """return thumbnail for each checksum in FODict."""
    args = [
        (checksum, fo[0].fullPath, Thumbsize, channel, upscale)
        for checksum, fo in FODict.items()
    ]
    with Pool() as pool:
        calculatedthumbs = pool.map(getOneThumb, args)
    ThumbDict = {}
    ThumbDict.update(calculatedthumbs)
    return ThumbDict
