''' library of little function to make code more readable'''
import os
import gzip
import shutil

def hexstring2array(hexstring):
    '''convert a hexstring (each pair of letters represents one element) <255 to an array'''
    return [int(hexstring[i:i+2], 16) for i in range(0, len(hexstring), 2)]

def array2hexstring(array):
    '''convert an array to a hexstring (each pair of letters represents one element)'''
    return ''.join(format(round(i), 'x').zfill(2) for i in array)

def str2bool(S, default=False):
    '''convert a string to a boolean '''
    if S[0] in [0, 'n', 'N', 'f', 'F']:
        return False
    if S[0] in [1, 'y', 'Y', 't', 'T']:
        return True
    return default

def existsAsSubGroup(E, GL):
    '''Test whether E exists as a subgroup in any of the groups in the group list'''
    for G in GL:
        if set(E) - set(G) == set():
            return True
    return False

def pairlist2dict(lst):
    '''take a list containing key,values pairs and return
    a dict where each key hold a list of matching values.
    '''
    dct = {}
    for ky, vle in lst:
        if ky in dct:
            dct[ky].append(vle)
        else:
            dct[ky] = [vle]
    return dct

def stringlist2commonunique(sl):
    '''convert a list of strings (filenames) into a common part and unique part.
    like ["/home/user/pictures/pic1.jpg", "/home/user/pictures/pic2.jpg"]
    =>
    ("/home/user/pictures/pic", ["1.jpg","2.jpg"])
    '''

    letterTupleList = list(zip(*sl))
    common = ''
    for letterTuple in letterTupleList:
        if len(set(letterTuple)) > 1:
            break
        common += letterTuple[0]
    unique = [s[len(common):] for s in sl ]
    return (common, unique)

def gzipfile(file):
    try:
        f_in = open(file, 'rb')
        f_out = gzip.open(file+'.gz', 'wb')
        shutil.copyfileobj(f_in, f_out)
        f_out.close()
        f_in.close()
        os.remove(file)
    except:
        f_out.close()
        f_in.close()

def mergeGroupLists(ListGList):
    ''' this routine takes a list of group lists 
    each element containing a list of matching images 
    returned by a condition modules.

    So if for example the date module returned:
    GL1 = [ [1,2,3], [2,3,6], [3], [4] [5,6] [6] ]
    and the hash module returned:
    GL2 = [ [1] , [2,3,4], [3], [4], [5,6], [6] ]
    the ListGList will be [G1, G2]

    This function should return the union of each by element:
    GL = [ [1,2,3], [2,3,4,6], [3], [4], [5,6], [6] ]
    '''
    if not ListGList:
        return None

    lenListGList = len(ListGList)
    if lenListGList == 1:
        return ListGList[0]

    lenGList = len(ListGList[0])
    GList = []
    for i in range(lenGList):
        dummy = set()
        for j in range(lenListGList):
            dummy = dummy | set(ListGList[j][i])
        dummy = list(dummy)
        dummy.sort()
        GList.append(dummy)

    return GList

def applyMMGroupLists(GList, ListGList):
    ''' this routine take a group list and a list of group lists
    The first list contains for groups of images that matched at least one 
    active condition.
    The list of list contains group that statisfy an mustmatch condition.
    We want to keep only the intersection of both element by element
    '''
    if not GList:
        return None

    if not ListGList:
        return GList

    lenListGList = len(ListGList)
    lenGList = len(GList)

    for i in range(lenGList):
        dummy = set(GList[i])
        for j in range(lenListGList):
            dummy = dummy & set(ListGList[j][i])
        dummy = list(dummy)
        dummy.sort()
        GList[i] = dummy

    return GList

def sortMd5sByFilename(md5s, FilenameMd5Dict):
    #get md5s sorted by filename:
    # only one time
    result = []
    for f in sorted(FilenameMd5Dict):
        md5 = FilenameMd5Dict[f]
        if md5 in result:
            continue
        if not md5 in md5s:
            continue
        result.append(md5)
    return result

def sortMd5ListsByFilename(md5Lists, FilenameMd5Dict):
    ''' return the lists of list of md5s sorted by filename
    for the first md5 in each list '''
    result = []
    firstmd5sDict = {ml[0]:ml for ml in md5Lists}
    for f in sorted(FilenameMd5Dict):
        md5 = FilenameMd5Dict[f]
        if not md5 in firstmd5sDict:
            continue
        result.append(firstmd5sDict[md5])
    return result
