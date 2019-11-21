def PairListToDict(list):
    'take a list containing key,values pairs and return a dict where each key hold a list of matching values'
    dict = { }
    for key, value in list:
        if key in dict:
            dict[key].append(value)
        else:
            dict[key] = [value]
    return dict

