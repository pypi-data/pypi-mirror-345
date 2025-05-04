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

import sys
import os
import argparse
from . import compile
from . import awcc_fs
from . import recipes
from . import reconstruct

def main():
    parser = argparse.ArgumentParser("awcc")

    subparsers = parser.add_subparsers(required=False, dest='command')


    compile_subparser = subparsers.add_parser("compile")
    
    compile_subparser.add_argument("input", type=str, nargs='*', default=[])
    compile_subparser.add_argument("-O", default=3, dest="opt_level", type=int, choices=(0, 1, 2, 3))
    compile_subparser.add_argument("-g", dest='debug', action="store_true", default=False)
    compile_subparser.add_argument("-ggdb", dest='debug_gdb', action="store_true", default=False)
    compile_subparser.add_argument("-I", type=str, dest='include', nargs='*', default=[])
    compile_subparser.add_argument("-l", type=str, dest='lib', nargs='*', default=[])
    compile_subparser.add_argument("-L", type=str, dest='libpath', nargs='*', default=[])
    compile_subparser.set_defaults(func=compile_subcommand)
    
    link_subparser = subparsers.add_parser('link')
    link_subparser.add_argument("input", type=str, nargs='*',default=[])
    link_subparser.add_argument("-O", default=3, dest="opt_level", type=int, choices=(0, 1, 2, 3))
    link_subparser.add_argument("-g", dest='debug', action="store_true", default=False)
    link_subparser.add_argument("-ggdb", dest='debug_gdb', action="store_true", default=False)
    link_subparser.add_argument("-l", type=str, dest='lib', nargs='*', default=[])
    link_subparser.add_argument("-L", type=str, dest='libpath', nargs='*', default=[])
    link_subparser.set_defaults(func=link_subcommmand)
    
    list_subparser = subparsers.add_parser('list')
    list_subparser.add_argument('list', choices=('objs',))
    list_subparser.set_defaults(func=list_subcommand)

    get_subparser = subparsers.add_parser('get')
    get_subparser.add_argument('hash')
    get_subparser.add_argument('-o', dest='output')
    get_subparser.set_defaults(func=get_subcommand)

    reconstruct_subparser = subparsers.add_parser('reconstruct')
    reconstruct_subparser.add_argument('hash')
    reconstruct_subparser.set_defaults(func=reconstruct_subcommand)

    recipe_subparser = subparsers.add_parser('recipe')
    recipe_subparsers= recipe_subparser.add_subparsers(required=True, dest='recipe_command')

    add_recipe_subparser = recipe_subparsers.add_parser('add')
    add_recipe_subparser.add_argument('recipe', type=str, nargs=1)
    add_recipe_subparser.add_argument('needs', type=str, nargs='+')

    new_recipe_subparser = recipe_subparsers.add_parser('new')
    new_recipe_subparser.add_argument('recipe', type=str, nargs=1)
    recipe_subparser.set_defaults(func=recipe_subcommand)

    help_subparser = subparsers.add_parser('help')
    help_subparser.add_argument('cmd', choices=('compile', 'link', 'list', 'recipe'))

    init_subparser = subparsers.add_parser('init')
    init_subparser.set_defaults(func=init_subcommand)
    if len(sys.argv[1:]) == 0:
        parser.print_help()
        exit()
    args = parser.parse_args(sys.argv[1:])
    if args.command == 'help':
        if args.cmd == 'compile':
            compile_subparser.print_help()
        elif args.cmd == 'link':
            link_subparser.print_help()
        elif args.cmd == 'list':
            list_subparser.print_help()
        elif args.cmd == 'recipe':
            recipe_subparser.print_help()

        exit()
    args.func(args)


def reconstruct_subcommand(args):
    reconstruct.reconstruct(args.hash)



def init_subcommand(args):
    os.makedirs('.awcc/blob/objs', exist_ok=True)
    os.makedirs('.awcc/blob/srcs', exist_ok=True)
    os.makedirs('.awcc/blob/incl', exist_ok=True)
    os.makedirs('.awcc/blob/deps', exist_ok=True)
    os.makedirs('.awcc/recipes', exist_ok=True)
    open('.awcc/register', 'w').close()
def get_subcommand(args):
    fhash = args.hash
    if len(fhash) < 40:
        fhash = awcc_fs.short_to_long_hash(fhash)
    os.system(f"cp ./.awcc/blob/objs/{fhash[:2]}/{fhash[2:]}.blob {args.output}")
    os.system(f"chmod 775 {args.output}")    

def list_subcommand(args):
    if args.list =='objs':
        table = []
        for i in awcc_fs.read_register():
            entry = awcc_fs.read_register_entry(i)
            table.append(entry)
        print(      f"{"Type":<8} {"Hash\t\t\t\t":<15}   {"Created At":<15} {"Filename":<25}")
        for row in table:
            print(  f"{row[0]:<8} {row[1]:<15} {row[2]:<15} {row[3]:<25}".replace('\n', ''))


def recipe_subcommand(args):
    print(args)
    if args.recipe_command == 'add':
        recipes.recipe_add(args.recipe[0], args.needs)
    elif args.recipe_command == 'new':
        recipes.new_recipe(args.recipe[0])

def link_subcommmand(args):
    if len(args.input) == 0:
        print("No input files")
        exit(1)
    _flags=[f"-O{args.opt_level}",
            '-g' if args.debug else '',
            '-ggdb' if args.debug_gdb else '',
            *[f'-l{l}'for l in args.lib],
            *[f'-L{L}'for L in args.libpath],
            ]
    flags = []
    for i in _flags:
        if i != '':
            flags.append(i)
    del _flags
    flags = " ".join(flags) + '-std=c++17 -no-pie'

    compile.link(args.input, flags)
def compile_subcommand(args):
    if len(args.input) == 0:
        print("No input files")
        exit(1)
    _flags=[f"-O{args.opt_level}",
            '-g' if args.debug else '',
            '-ggdb' if args.debug_gdb else '',
            *[f'-l{l}'for l in args.lib],
            *[f'-I{I}'for I in args.include],
            *[f'-L{L}'for L in args.libpath],

        ]
    flags = []
    for i in _flags:
        if i != '':
            flags.append(i)
    del _flags
    flags = " ".join(flags)
    
    for i in args.input:
        compile.compile(i, flags=flags)
    


