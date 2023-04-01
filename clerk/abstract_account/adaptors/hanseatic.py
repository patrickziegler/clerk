# Copyright (C) 2023 Patrick Ziegler
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

from clerk.abstract_account.abstract_account import AbstractAccount as scanner

import datetime
import os
import re
import tempfile


@scanner.register_filt("hanseatic")
def hanseatic_filt(path):
    """Return true if file with given path should be parsed with *_conv function"""

    pattern = "Kontoauszug-.*pdf$"
    return re.match(pattern, path)


@scanner.register_conv("hanseatic")
def hanseatic_conv(path, verbose=False):
    """Yield tuples like (<date>, <description>, <amount>) as found in the given bank statement (pdf)"""

    print("Scanning " + path)

    with tempfile.NamedTemporaryFile("r") as tmp:
        os.system("pdftotext -q -raw %s %s" % (path, tmp.name))
        text = [line.rstrip("\n") for line in tmp.readlines()]
        if verbose:
            print("\n".join(text))

        date = None
        description = None
        value = None

        for line in text:
            words = line.split()
            date_found = False

            try:
                if len(words) > 2:
                    date = datetime.datetime.strptime(words[0], "%d.%m.%Y")
                    if words[1] != "-":
                        datetime.datetime.strptime(words[1], "%d.%m.%Y")
                    description = words[2]
                    date_found = True
            except ValueError:
                pass

            try:
                if len(words) > 1 and (words[-2] == "-" or int(words[-2])):
                    value = float(words[-1].replace(".", "").replace(",", "."))
                if None not in (date, description, value):
                    yield (date, description, value)
                    date = None
                    description = None
                    value = None
                    continue
            except ValueError:
                pass

            if not date_found and description is not None:
                description += " " + line


@scanner.register_conv_update("hanseatic")
def hanseatic_conv_update(path):
    """Yield tuples like (<date>, <description>, <amount>) as found in the given update file (csv)"""

    raise NotImplementedError


if __name__ == "__main__":
    import sys
    sc = scanner("hanseatic")
    for transaction in sc.conv(sys.argv[1], verbose=True):
        print(transaction)
