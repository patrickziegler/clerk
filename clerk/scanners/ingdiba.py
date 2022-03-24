# Copyright (C) 2022 Patrick Ziegler
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

from .scanner import StatementScanner as scanner

import re


@scanner.register_filt("ingdiba")
def ingdiba_filt(path):
    pattern = "Kontoauszug.*pdf$"
    return re.match(pattern, path) is not None


@scanner.register_conv("ingdiba")
def ingdiba_conv(path):
    print(">>> " + path)
    return [(3, 4, 5), (2, 3, 1), (1, 3, 4)]


@scanner.register_conv_update("ingdiba")
def ingdiba_conv_update(path):
    raise NotImplementedError
