""" library of little function to make code more readable"""
import gzip
import os
import shutil


def hexstring2array(hexstring):
    """convert a hexstring to an array
    (each pair of letters represents one element) <255"""
    return [int(hexstring[i:i+2], 16) for i in range(0, len(hexstring), 2)]


def array2hexstring(array):
    """convert an array to a hexstring
    (each pair of letters represents one element)"""
    return "".join(format(round(i), "x").zfill(2) for i in array)


def pairlist2dict(lst):
    """take a list containing key,values pairs and return
    a dict where each key holds a list of matching values.
    """
    dct = {}
    for ky, vle in lst:
        if ky in dct:
            dct[ky].append(vle)
        else:
            dct[ky] = [vle]
    return dct


def stringlist2commonunique(sl):
    """split list of strings (filenames) into a common part and unique part
    like ["/home/user/pictures/pic1.jpg", "/home/user/pictures/pic2.jpg"]
    =>
    ("/home/user/pictures/pic", ["1.jpg","2.jpg"])
    """

    # break the list of string into tuples of letters for each position
    letterTupleList = map(list, zip(*sl))
    common = ""
    for letterTuple in letterTupleList:
        # if there is more than one letter in the set of letters
        # it means that the filenames start to differ at this position.
        if len(set(letterTuple)) > 1:
            break
        common += letterTuple[0]
    unique = [s[len(common):] for s in sl]
    return (common, unique)


def gzipfile(file):
    with open(file, "rb") as f_in:
        with gzip.open(file+".gz", "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
            os.remove(file)


def mergeGroupDicts(ListGDict):
    """ this routine takes a list of group dicts
    each element containing a dict of matching images
    returned by a condition modules.

    So if for example the date module returned:
    GL1 = { 1:{1,2,3}, 2:{2,3,6}, 5:{5,6} }
    and the hash module returned:
    GL2 = { 2:{2,3,4}, 5:{5,6}, 6:{6,7} }
    the ListGDict will be [G1, G2]

    This function should return the union of each by element:
    GL = { 1:{1,2,3}, 2:{2,3,4,6}, 5:{5,6}, 6:{6,7} }
    """
    GDict = {}
    for d in ListGDict:
        for m, g in d.items():
            previous = GDict[m] if m in GDict else set()
            GDict[m] = previous | g
    return GDict


def applyMMGroupDicts(GDict, ListGDict):
    """ this routine take a group dict and a list of group dicts
    The first list contains groups of images that matched at least one
    active condition.
    The list of dicts contains groups that statisfy an mustmatch condition.
    We want to keep only the intersection of both element by element
    """
    for k in GDict:
        for mmDict in ListGDict:
            mmSet = mmDict[k] if k in mmDict else set()
            GDict[k] = GDict[k] & mmSet
    # remove sets with less than two element
    return {k: v for k, v in GDict.items() if len(v) > 1}


def removeRedunantSubgroups(GDict):
    """ Remove groups that exists entirely as subgroups elsewhere"""
    # We sort by reverse length of the groups so we know that
    # subgroups can only be found later in the list
    checksums_sorted_by_length_of_group = sorted(
        GDict,
        key=lambda k: len(GDict[k]),
        reverse=True
    )
    cleanedGDict = {}
    for m in checksums_sorted_by_length_of_group:
        # if this set exists as a subgroup already pass to the next
        if existsAsSubGroup(GDict[m], cleanedGDict.values()):
            continue
        cleanedGDict[m] = GDict[m]
    return cleanedGDict


def existsAsSubGroup(g, GL):
    "Test whether G exists as a subgroup in any of the groups in GL"
    for G in GL:
        if g - G == set():
            return True
    return False


def sortMatchingGroupsByFilename(GDict, filenameChecksumDict):
    # sort each line
    sortedLines = [sortChecksumsByFilename(c, filenameChecksumDict) for c in GDict.values()]
    # sort the final list of lists by the first element of each list
    return sorted(sortedLines, key=lambda k: filenameChecksumDict[k[0]])


def sortChecksumsByFilename(checksums, filenameChecksumDict):
    return sorted(checksums, key=lambda k: filenameChecksumDict[k])
