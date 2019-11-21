from operator import itemgetter
import itertools
from imagehash import hex_to_hash

def HashDistances(fodict,hashname):
    ihashdict = {}
    for k, v in fodict.items():
        ihashdict[k] = hex_to_hash(getattr(v[0], hashname))
        
    allmd5pairs = itertools.combinations(fodict.keys(),2)

    distances = [ (md5a, md5b, ihashdict[md5a] - ihashdict[md5b])
                  for md5a, md5b in allmd5pairs ]

    distances.sort(key=itemgetter(2))
    return distances
    

def puzzle(file1,file2):
    try:
        puzzle = Puzzle()
        sign1 = puzzle.from_filename(file1)
        sign2 = puzzle.from_filename(file2)
        return sign1.distance(sign2)
    except PuzzleError:
        return -666.666

def phash(file1,file2):
    return 1.0/(photohash.distance(file1,file2)+1.0)

def image_similarity(files):
    "build the matrix of image similarity"

    similarity_function = puzzle
    files1 = []
    files2 = []
    values = []

    for idx1, file1 in enumerate(files):
        for idx2, file2 in enumerate(files[idx1+1:]):
            #print("comparing %s with %s" % (file1,file2))
            similarity = similarity_function(file1,file2)
            files1.append(file1)
            files2.append(file2)
            values.append(similarity)
            # add entry also repeated for the file2,file1 pair
            files1.append(file2)
            files2.append(file1)
            values.append(similarity)
    return files1,files2,values

def images_most_similar_to(file,files1,files2,sims,N):
    sub_files2 = [ files2[i] for i, x in enumerate(files1) if x == file ]
    sub_sims = [ sims[i] for i, x in enumerate(files1) if x == file ]

    sub_files2_sorted = [y for x,y in sorted(zip(sub_sims,sub_files2))]
    return sub_files2_sorted[:-1*(N+1):-1]

