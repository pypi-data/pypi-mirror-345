# This file is part of Awesome compiler collection.
#
# Copyright (C) 2025 TrollMii
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
    _ = entry.split(" ", 4)
    type = _[0]
    hash = _[1]
    date = _[2] + ' ' + _[3]
    filename = _[4][:-1]
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







