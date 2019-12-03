from multiprocessing import Pool
from PIL import Image
from imagehash import dhash
from imagehash import average_hash
from imagehash import phash
from imagehash import whash
from utils import jumbling as JU
from utils import database as DB

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
        'whash': whash
        }

    hashvalue = funcdict[hashname](Image.open(FullPath), hash_size=8)

    return (md5, str(hashvalue))
