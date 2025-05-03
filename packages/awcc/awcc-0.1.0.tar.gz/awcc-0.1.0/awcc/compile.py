from . import hasher
from . import awcc_fs
import sys
import os
import hashlib



def compile(file, flags="", gcc="clang"):
    hash = hasher.getHashOfFile(file)
    if awcc_fs.blob_exists(hash):
        print(f"[FILE:{hash[:8]}] {file} already in blob")
    else:
        os.makedirs(f"./.awcc/blob/objs/{hash[:2]}", exist_ok=True)
        os.makedirs(f"./.awcc/blob/srcs/{hash[:2]}", exist_ok=True)
        
        print(f"[FILE:{hash[:8]}] {file} -> awcc:{hash}")
        cmd = f"{gcc} -c {file} -o {awcc_fs.blob_getfile(hash)} {flags}"
        os.system(cmd)
        os.system(f"cp {file} ./.awcc/blob/srcs/{hash[:2]}/{hash[2:]}.blob")

        awcc_fs.register_file(file, "C", hash)
    return hash

def link(hashes: list, flags="", ld="clang"):
    fhash = hashlib.sha1("".join(hashes).encode("utf-8")).hexdigest()
    if awcc_fs.blob_exists(fhash):
        print(f"[LINK:{fhash[:8]}] already in blob")
    else: 
        os.makedirs(f"./.awcc/blob/objs/{fhash[:2]}", exist_ok=True)
        print(f"[LINK:{fhash[:8]}] -> awcc:{fhash}")
        cmd = [ld, "-o", awcc_fs.blob_getfile(fhash), flags]
        for h in hashes:
            if len(h) < 40:
                h = awcc_fs.short_to_long_hash(h)
            cmd.append(awcc_fs.blob_getfile(h))
        os.system(" ".join(cmd))
        awcc_fs.register_file("", "LINKED", fhash)
    return hash

    
