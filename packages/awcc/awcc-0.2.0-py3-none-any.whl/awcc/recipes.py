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
import json






def new_recipe(name):
    os.makedirs('.awcc/recipes')
    with open(f'.awcc/recipes/{name}.json', 'w') as f:
        json.dump({
            'flags': [],
            'needs': []
        }, f)
def recipe_add(name, hashes):
    with open(f'.awcc/recipes/{name}.json','r') as f:
        obj = json.load(f)
    obj['needs'].extend(hashes)
    with open(f'.awcc/recipes/{name}.json', 'w') as f:
        json.dump(obj, f)

def recipe_set_flags(name, hashes):
    pass

