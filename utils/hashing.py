import math
import statistics as stats
from multiprocessing import Pool
from PIL import Image
from imagehash import dhash
from imagehash import average_hash
from imagehash import phash
from imagehash import whash
from utils import jumbling as JU
from utils import database as DB

def hexstring_to_array(hexstring):
    return [int(hexstring[i:i+2],16) for i in range(0, len(hexstring), 2)]

def array_to_hexstring(array):
    return ''.join(format(round(i), 'x').zfill(2) for i in array)

def array_to_array_distance(array1, array2):
    narray = len(array1)
    distance = 0.0
    for i in range(narray):
        distance += math.sqrt(((array1[i]-array2[i])/256.)**2)
    distance *= 100.0/narray
    return distance

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
        if hashvalue:
            HashValueDict[md5] = hashvalue
            continue

        hashvalue = DB.GetHashValueFromDataBase(md5, hashname, db_connection=db_connection)
        if hashvalue:
            HashValueDict[md5] = hashvalue
            continue

        needcalculating.append((md5, FirstImageFileObject.FullPath, hashname))

    ## For the md5 with None calculate the hashvalue in a pool of workers
    ## Returning (md5, imagehash)
    if needcalculating:
        # calculatedhashes = []
        # for need in needcalculating:
        #     calculatedhashes.append(CalculateImageHash(need))

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

    hashvalue = funcdict[hashname](Image.open(FullPath), hash_size=8)

    return (md5, str(hashvalue))

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

    x = 0.3
    boxes = [
        (0.0, 0.0,  x,    x),
        (0.0, 1-x,  x,  1.0),
        (1-x, 0.0, 1.0,   x),
        (1-x, 1-x, 1.0, 1.0),
        (0.5-x/2.0, 0.5-x/2.0, 0.5+x/2.0, 0.5+x/2.0)
    ]

    # open and convert to HSV
    HSV = Img.convert("HSV")
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

    return array_to_hexstring(values)

def hsvhash(Img, **kwargs):
    ''' Calculate a hash that stores info about the colour histogram'''

    # open and convert to HSV
    HSV = Img.convert("HSV")
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

    return array_to_hexstring(values)
