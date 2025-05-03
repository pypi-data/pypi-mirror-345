import hashlib



def getHashOfFile(file):
    return hashlib.sha1(open(file, 'r').read().replace(" ", "").replace("\n", "").replace("\t", "").encode('utf8')).hexdigest()