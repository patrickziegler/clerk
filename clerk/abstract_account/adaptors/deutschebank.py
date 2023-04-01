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

from clerk.abstract_account.abstract_account import AbstractAccount as scanner

import csv
import datetime
import os
import re
import tempfile


@scanner.register_filt("deutschebank")
def deutschebank_filt(path):
    """Return true if file with given path should be parsed with *_conv function"""

    pattern = "Kontoauszug.*pdf$"
    return re.match(pattern, path)


@scanner.register_conv("deutschebank")
def deutschebank_conv(path, verbose=False):
    """Yield tuples like (<date>, <description>, <amount>) as found in the given bank statement (pdf)"""

    print("Scanning " + path)

    with tempfile.NamedTemporaryFile("r") as tmp:
        os.system("pdf2ps %s - | ps2pdf - - | pdftotext -raw -q - %s" % (path, tmp.name))
        text = [line.rstrip("\n") for line in tmp.readlines()]
        if verbose:
            print("\n".join(text))

    year = None
    for i in range(len(text)):
        if re.match("Kontoauszug vom .* bis .*", text[i]):
            try:
                year = int(text[i][-4:]) # via int to trigger ValueError for invalid input
                break
            except ValueError:
                pass

    if year is None:
        return

    # since Dec 2022 the detection of date would fail without the following filter
    text = [line for line in text if line not in (str(year), str(year-1))]

    i = 0
    date, description, value = (None, "", None)
    while i < len(text):
        if text[i][:2] in ("- ", "+ ") and "," in text[i]:
            try:
                buf = float(text[i].replace(".", "").replace(",", ".").replace(" ", ""))
                if date != None:
                    yield (
                        date,
                        description.replace("Verwendungszweck/ Kundenreferenz", "").replace("\n", " ").strip(),
                        value
                    )
                date, description, value = (None, "", buf)
            except ValueError:
                pass
        elif i < len(text) - 1:
            try:
                assert datetime.datetime.strptime(text[i] + str(year), "%d.%m.%Y")
                date = datetime.datetime.strptime(text[i+1] + str(year), "%d.%m.%Y")
                i += 1
            except ValueError:
                description += " " + text[i]
        i += 1


@scanner.register_conv_update("deutschebank")
def deutschebank_conv_update(path):
    """Yield tuples like (<date>, <description>, <amount>) as found in the given update file (csv)"""

    print("Scanning " + path)

    with open(path, "r", encoding="ISO-8859-1") as fp:
        reader = csv.reader(fp, delimiter=";", quotechar="\"")
        for line in reader:
            if len(line) < 13 or line[1] == "":
                continue
            try:
                yield (
                    datetime.datetime.strptime(line[0], "%d.%m.%Y"),
                    line[4].replace("\n", " "),
                    float((line[-2] if line[-3] == "" else line[-3]).replace(".", "").replace(",", "."))
                )
            except (ValueError, IndexError):
                continue


if __name__ == "__main__":
    import sys
    sc = scanner("deutschebank")
    for transaction in sc.conv(sys.argv[1], verbose=True):
        print(transaction)
