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
from . import awcc_fs
import os
def reconstruct(hash):
    if len(hash) < 40:
        hash = awcc_fs.short_to_long_hash(hash)
    register = awcc_fs.read_register()
    for i in register:
        entry = awcc_fs.read_register_entry(i)
        if entry[1] == hash:
            os.system(f'cp ./.awcc/blob/srcs/{hash[:2]}/{hash[2:]}.blob {entry[3]}')
