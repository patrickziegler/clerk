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

from .scanners import StatementScanner


def main():
    import os
    import sys

    if len(sys.argv) < 2:
        raise RuntimeError("Not enough arguments")

    scanner = StatementScanner(sys.argv[1])

    items = [item for root, _, files in os.walk(sys.argv[2])
           for doc in files if scanner.filt(doc)
           for item in scanner.conv(os.path.join(root, doc))]

    print(sorted(items))
