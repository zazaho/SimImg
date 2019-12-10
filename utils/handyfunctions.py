''' library of little function to make code more readable'''

def hexstring_to_array(hexstring):
    '''convert a hexstring (each pair of letters represents one element) <255 to an array'''
    return [int(hexstring[i:i+2], 16) for i in range(0, len(hexstring), 2)]

def array_to_hexstring(array):
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

def pairListToDict(lst):
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
