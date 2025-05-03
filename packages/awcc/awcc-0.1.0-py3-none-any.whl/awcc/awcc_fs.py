import os
from . import hasher
import io
import datetime

def register_file(filename: str, type, hash):
    with open("./.awcc/register", "a") as f:
        f.write(f"{type} {hash} {datetime.datetime.utcnow()} {filename}\n")

def read_register() -> list:
    with open("./.awcc/register", "r") as f:
        return f.readlines()
    
def short_to_long_hash(short: str):
    for i in read_register():
        entry = read_register_entry(i)
        if entry[1].startswith(short):
            return entry[1]
def read_register_entry(entry: str):
    _ = entry.split(" ", 3)
    type = _[0]
    hash = _[1]
    date = _[2]
    filename = _[3]
    return (type, hash, date, filename)
def get_filehash(filename):
    r = read_register()
    for i in r:
        entry = read_register_entry(i)
        if entry[2] == filename:
            return entry[0]
        
def get_hash(filename):
    return hasher.getHashOfFile(filename)
def blob_exists(hash):
    return os.path.exists(f'./.awcc/blob/objs/{hash[:2]}/{hash[2:]}.blob')

def blob_getfile(hash):
    return f'./.awcc/blob/objs/{hash[:2]}/{hash[2:]}.blob'







