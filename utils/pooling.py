import hashlib
import statistics as stats
from multiprocessing import Pool
from PIL import Image
from imagehash import dhash
from imagehash import average_hash
from imagehash import phash
from imagehash import whash
from utils import database as DB

def CalculateMD5Hash(file):
    hasher = hashlib.md5()
    with open(file, 'rb') as afile:
        hasher.update(afile.read())
    return (file, hasher.hexdigest())

def GetMD5Hashes(filelist):
    '''return md5 hashing value for each file the list.'''
    HashValueDict = {} ## filename,md5
    with Pool() as pool:
        calculatedhashes = pool.map(CalculateMD5Hash, filelist)
    HashValueDict.update(calculatedhashes)
    return HashValueDict

def subImage(Img, FracBox):
    ''' return a subImage from Image based on coordinates in dimensionless units'''
    width, height = Img.size
    left = round(width*FracBox[0])
    right = round(width*FracBox[2])
    bottom = round(height*FracBox[1])
    top = round(height*FracBox[3])
    return Img.crop((left, bottom, right, top))

def hsv5hash(Img, **kwargs):
    ''' Calculate a hash that stores info about the colour histogram 
    after having split the image in 5 regions'''

    # size of boxes that has ~equal amount over overlap between the boxes
    # and the amount of unsampled area
    x = 0.46
    boxes = [
        (0.0, 0.0,  x,    x),
        (0.0, 1-x,  x,  1.0),
        (1-x, 0.0, 1.0,   x),
        (1-x, 1-x, 1.0, 1.0),
        (0.5-x/2.0, 0.5-x/2.0, 0.5+x/2.0, 0.5+x/2.0)
    ]

    # open and convert to HSV
    # resample to speed up the calculation
    HSV = Img.convert("HSV").resize((100,100), Image.NEAREST)
    H = HSV.getchannel('H').getdata()
    S = HSV.getchannel('S').getdata()
    V = HSV.getchannel('V').getdata()

    values = []
    for box in boxes:
        Hsub = subImage(H, box)
        Ssub = subImage(S, box)
        Vsub = subImage(V, box)
        quantH = stats.quantiles(Hsub)
        quantS = stats.quantiles(Ssub)
        quantV = stats.quantiles(Vsub)
        values.extend(quantH)
        values.extend(quantS)
        values.extend(quantV)

    return values

def hsvhash(Img, **kwargs):
    ''' Calculate a hash that stores info about the colour histogram'''

    # open and convert to HSV
    # resample to speed up the calculation
    HSV = Img.convert("HSV").resize((100,100), Image.NEAREST)
    H = HSV.getchannel('H').getdata()
    S = HSV.getchannel('S').getdata()
    V = HSV.getchannel('V').getdata()
    # for each LAYER (H,S,L) record quantiles (three x three values)
    quantH = stats.quantiles(H)
    quantS = stats.quantiles(S)
    quantV = stats.quantiles(V)

    values = []
    values.extend(quantH)
    values.extend(quantS)
    values.extend(quantV)

    return values

def CalculateImageHash(args):
    md5, FullPath, hashname = args
    funcdict = {
        'ahash': average_hash,
        'dhash': dhash,
        'phash': phash,
        'whash': whash,
        'hsvhash': hsvhash,
        'hsv5hash': hsv5hash
        }
    return (md5, funcdict[hashname](Image.open(FullPath), hash_size=8))

def GetImageHashes(fodict, hashname, db_connection=None):
    '''return hashing value according to selected hashname method
    for each file the (file,md5) list.'''

    ## the logic to apply is:
    ## create an empty dict to hold the results
    HashValueDict = {} ## md5:hashvalue

    ## create an empty list to hold md5,file,hashname tuples that need to be calculated
    needcalculating = []

    ## for each uniq md5 in the requested fileinfodict
    ## check if the FileObject has the hash value already list.
    ## if yes take it
    #
    ## if none:
    ## get the hash value for this method and this md5 from the database or None
    #
    ## if none add the info to the needcalculating list

    for md5, ImageFileObjectList in fodict.items():
        FirstImageFileObject = ImageFileObjectList[0]
        hashvalue = getattr(FirstImageFileObject, hashname)
        if hashvalue is not None:
            HashValueDict[md5] = hashvalue
            continue

        hashvalue = DB.GetHashValueFromDataBase(md5, hashname, db_connection=db_connection)
        if hashvalue is not None:
            HashValueDict[md5] = hashvalue
            continue

        needcalculating.append((md5, FirstImageFileObject.FullPath, hashname))

    ## For the md5 with None calculate the hashvalue in a pool of workers
    ## Returning (md5, imagehash)
    if needcalculating:

        with Pool() as pool:
            calculatedhashes = pool.map(CalculateImageHash, needcalculating)

        HashValueDict.update(calculatedhashes)

        ## update the database with the new md5, method, HashValueDict
        DB.SetHashValues(calculatedhashes, hashname, db_connection=db_connection)

    # write everything back to each fileobject
    # behind every md5 key in the fodict is a list of fileobjects with corresponding md5
    for md5, hashvalue in HashValueDict.items():
        for fo in fodict[md5]:
            setattr(fo, hashname, hashvalue)
def getOneThumb(arg):
    md5, filename, tsize = arg
    img = Image.open(filename)
    ratio = max(img.size[0]/tsize, img.size[1]/tsize)
    img = img.resize(
        (int(img.size[0]/ratio), int(img.size[1]/ratio)),
        Image.ANTIALIAS
    )
    return (md5, img)

def GetMD5Thumbnails(FODict, Thumbsize=150):
    '''return thumbnail for each md5 in FODict.'''
    args = [(md5, fo[0].FullPath, Thumbsize) for md5, fo in FODict.items()]
    ThumbDict = {} ## md5, thumbnail
    with Pool() as pool:
        calculatedthumbs = pool.map(getOneThumb, args)
    ThumbDict.update(calculatedthumbs)
    return ThumbDict
