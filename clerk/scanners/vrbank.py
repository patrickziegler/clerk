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

import csv
import datetime
import logging
import os
import re
import tempfile
import time


@scanner.register_filt("vrbank")
def vrbank_filt(path):
    pattern = ".*Kontoauszug.*pdf$"
    return re.match(pattern, path) is not None


@scanner.register_conv("vrbank")
def vrbank_conv(path):
    """Yield tuples like (<date>, <description>, <amount>) as found in the given bank statement (pdf)"""

    logging.info("Reading %s" % path)

    with tempfile.NamedTemporaryFile("r") as tmp:
        os.system("pdftotext -layout -q " + path + " " + tmp.name)
        text = [line for line in tmp.readlines() if line != ""]

    year = None

    for i in range(len(text)):
        pos = text[i].lower().find("erstellt am ")
        if pos > -1:
            try:
                year = str(time.strptime(text[i][pos:pos + 22], "erstellt am %d.%m.%Y").tm_year)
                break
            except ValueError:
                pass

    if year is None:
        return

    skip = 0

    for i in range(len(text)):
        if skip:
            skip -= 1
            continue

        scope = text[i].split()

        if len(scope) == 0:
            continue
        try:
            date = datetime.datetime.strptime(scope[0] + year, "%d.%m.%Y")
            description = None
            value = None

            if len(scope) > 1:
                time.strptime(scope[1] + year, "%d.%m.%Y")
                description = " ".join(scope[2:-2])
                value = scope[-2].replace(".", "").replace(",", ".")
                value = float("{value:.{digits}f}".format(value=float(value), digits=2))

                if scope[-1].lower() == "s":
                    value = -1 * value

                j = 1
                while i + j < len(text):
                    scope = text[i + j].split()
                    if len(scope) == 0:
                        break
                    if len(scope) > 1 and re.match(".*XX.*XX.*XX.*XX", "".join(scope[0:2]).replace(".", "XX")) is not None:
                        break
                    description += " ".join(scope)
                    skip = j
                    j += 1

            yield (date, description, value)

        except ValueError:
            pass


@scanner.register_conv_update("vrbank")
def vrbank_conv_update(path):
    """Yield tuples like (<date>, <description>, <amount>) as found in the given bank statement (csv)"""

    with open(filename, "r", encoding="ISO-8859-1") as fp:
        reader = csv.reader(fp, delimiter=";", quotechar="\"")
        for line in reader:
            try:
                if line[1] == "":
                    continue
                date = datetime.strptime(line[0], "%d.%m.%Y")
                description = " ".join(line[2:10])
                value = float(line[-2].replace(".", "").replace(",", ".")) * (-1 if line[-1].lower() == "s" else 1)

                yield (date, description, value)

            except (ValueError, IndexError):
                continue
