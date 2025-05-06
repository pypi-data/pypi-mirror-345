<!--
This file is part of Awesome compiler collection.

Copyright (C) 2025 TrollMii

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
-->


# AWesome Compiler Collection
The awesome compiler collection does compile files to objects, and put it into a blob filesystem
That means you will save time at compiling, because some objects was already compiled

## Installation
To install `awcc` use pip:
```shell
pip install awcc
```
or you can use on nixos pipx
```shell
pipx install awcc
```
(note: in future awcc will be applied to nixpkgs)

## How to use
### init
First you have to initialize an awcc repository
```shell
awcc init
```
### compiling
Than you can compile files

```shell
awcc compile file.c [flags]
```
because you have a blob system of object files, you dont need `-o`, you will get a hash
### listing
If you want to see you files, use the `list` command
```shell
awcc list objs
```
That will output
```
FILETYPE SHA1_HASH CREATED_AT FILENAME_OF_SRC
```
example:
```
C        f7bdf8d0191d26a95e4073d8a153731fc465e499   2025-05-03 07:59:05.075623  test.c
C        485fa9594b9394833fafafacafe3943549349483   2025-05-03 08:49:04.075494  test.c
```


### Linking
So, if you want to link something, you have to use
```shell
awcc link [hash1] [hash2] [...] [flags]
```

so, example

```shell 
awcc link 485fa9594b9394833fafafacafe3943549349483 f7bd cafe -lm
```

the len of the hash must be less equals 40.
if the len is less than 40 (short hash), awcc searches for the long hash
if it is equals 40, you have the long hash.
so, the lenght of the hash is not important, you can also only use one character as hash, awcc will find the correct hash

### How to use the program?
So, awcc linked your program to an executable, or library, and put it into the blob.
you can use it like this:

```shell
awcc get [HASH] -o [output]
```

for example:

```shell
awcc get 58f -o test.exe
```

### Reconstructing
so, you want a source file from a older version, use `awcc reconstruct`\
usage:
```shell
awcc reconstruct [hash]
```
here is an example of using reconstruct:
```shell
awcc reconstruct faceb00k15dead
```
and your `file.c` will be reconstructed