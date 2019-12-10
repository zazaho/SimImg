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


