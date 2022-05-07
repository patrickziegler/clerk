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

from clerk.scanner import StatementScanner as scanner

import datetime
import os
import re
import tempfile


@scanner.register_filt("ingdiba")
def ingdiba_filt(path):
    """Return true if file with given path should be parsed with *_conv function"""

    pattern = "^Girokonto.*Kontoauszug.*pdf$"
    return re.match(pattern, path) is not None


@scanner.register_conv("ingdiba")
def ingdiba_conv(path):
    """Yield tuples like (<date>, <description>, <amount>) as found in the given bank statement (pdf)"""

    print("Scanning " + path)

    blacklist = [
        "TILG", # kfw lastschrift bafoeg beschreibung missdeutig
    ]

    with tempfile.NamedTemporaryFile("r") as tmp:
        os.system("pdftotext -raw -q %s %s" % (path, tmp.name))

        for line in tmp.readlines():
            words = line.split()
            if len(words) < 2:
                continue
            try:
                if [forbidden for forbidden in blacklist if forbidden in words]:
                    continue
                if "," not in words[-1]:
                    continue
                yield (
                    datetime.datetime.strptime(words[0], "%d.%m.%Y"),
                    " ".join(words[1:-1]).replace("\n", " "),
                    float(words[-1].replace(".", "").replace(",", "."))
                )
            except ValueError:
                continue


@scanner.register_conv_update("ingdiba")
def ingdiba_conv_update(path):
    """Yield tuples like (<date>, <description>, <amount>) as found in the given update file (csv)"""

    print("Scanning " + path)

    with open(path, "r", encoding="ISO-8859-1") as fp:
        for line in fp.readlines():
            words = line.split(";")
            if len(words) < 9 or "," not in words[-2]:
                continue
            try:
                yield (
                    datetime.datetime.strptime(words[0], "%d.%m.%Y"),
                    " ".join(words[2:5]).replace("\n", " "),
                    float(words[-2].replace(".", "").replace(",", "."))
                )
            except ValueError:
                continue
