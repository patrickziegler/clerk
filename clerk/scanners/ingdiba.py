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

import datetime
import os
import re
import tempfile


@scanner.register_filt("ingdiba")
def ingdiba_filt(path):
    pattern = "^Girokonto.*Kontoauszug.*pdf$"
    return re.match(pattern, path) is not None


@scanner.register_conv("ingdiba")
def ingdiba_conv(path):
    """Yield tuples like (<date>, <description>, <amount>) as found in the given bank statement (pdf)"""

    blacklist = [
        "TILG", # kfw lastschrift bafoeg beschreibung missdeutig
    ]

    assets = []

    with tempfile.NamedTemporaryFile("r") as tmp:
        os.system("pdftotext -raw -q " + path + " " + tmp.name)

        for line in tmp.readlines():
            words = line.split()
            if len(words) < 2:
                continue

            try:
                date = datetime.datetime.strptime(words[0], "%d.%m.%Y")
            except ValueError:
                continue

            try:
                if [w for w in blacklist if w in words]:
                    continue

                if "," in words[-1] and "TILG" not in words:
                    value = float(words[-1].replace(".", "").replace(",", "."))
                else:
                    raise ValueError

                assets.append((date, " ".join(words[1:-1]), value))

            except ValueError:

                if len(assets) > 0 and date == assets[-1][0]:
                    value = assets[-1][2]
                    description = assets[-1][1] + " " + " ".join(words[1::])
                    del assets[-1]
                    assets.append((date, description, value))

    for asset in assets:
        yield asset


@scanner.register_conv_update("ingdiba")
def ingdiba_conv_update(path):
    """Yield tuples like (<date>, <description>, <amount>) as found in the given bank statement (csv)"""

    assets = []

    for line in DocumentCrawler._get_text(filename):
        words = line.split(";")
        if len(words) < 9 or "," not in words[-2]:
            continue
        try:
            assets.append((
                datetime.datetime.strptime(words[0], "%d.%m.%Y"),
                " ".join(words[2:5]),
                float(words[-2].replace(".", "").replace(",", "."))
            ))
        except ValueError:
            continue

    for asset in assets:
        yield asset
