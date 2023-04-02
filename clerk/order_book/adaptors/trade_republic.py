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

from clerk.order_book.order_book import OrderBook as scanner

import csv
import datetime
import os
import re
import tempfile
import datetime


@scanner.register_filt("trade_republic")
def trade_republic_filt(path):
    """Return true if file with given path should be parsed with *_conv function"""

    pattern = "pb.*pdf$"
    return re.match(pattern, path)


@scanner.register_conv("trade_republic")
def trade_republic_conv(path):
    """Yield tuples like (date, description, isin, quantity, price, value, fee, capital_returns_tax, soli, church_tax) as found in the given settlement (pdf)"""

    print("Scanning " + path)

    date = None
    description = None
    isin = None
    quantity = None
    price = None
    value = None
    fee = None
    capital_returns_tax = None
    soli = None
    church_tax = None
    sign = None

    with tempfile.NamedTemporaryFile("r") as tmp:
        os.system("pdftotext -raw -q %s %s" % (path, tmp.name))
        text = tmp.read()

        result = re.search(r"POSITION ANZAHL KURS BETRAG\n(.*)\nISIN:", text, re.DOTALL)
        if result != None and len(result.groups()):
            description = " ".join(result.group(1).split("\n"))

        for line in text.split("\n"):
            result = re.search(r"Verkauf am (\d+.\d+.\d+), um (\d+:\d+) Uhr", line)
            if result != None and len(result.groups()) > 1:
                datestr = "%s %s" % (result.group(1), result.group(2))
                date = datetime.datetime.strptime(datestr, "%d.%m.%Y %H:%M")
                sign = -1.0
                continue

            result = re.search(r"Kauf am (\d+.\d+.\d+), um (\d+:\d+) Uhr", line)
            if result != None and len(result.groups()) > 1:
                datestr = "%s %s" % (result.group(1), result.group(2))
                date = datetime.datetime.strptime(datestr, "%d.%m.%Y %H:%M")
                sign = 1.0
                continue

            result = re.search(r"ISIN: (.*)", line)
            if result != None and len(result.groups()):
                isin = result.group(1)
                continue

            line = line.replace(".", "").replace(",", ".")

            result = re.search(r"Fremdkostenzuschlag (-?\d+\.\d+) EUR", line)
            if result != None and len(result.groups()):
                fee = float(result.group(1).replace(",", "."))
                continue

            result = re.search(r"Kapitalertragsteuer.* (-?\d+\.\d+) EUR", line)
            if result != None and len(result.groups()):
                capital_returns_tax = float(result.group(1).replace(",", "."))
                continue

            result = re.search(r"Solidaritätszuschlag.* (-?\d+\.\d+) EUR", line)
            if result != None and len(result.groups()):
                soli = float(result.group(1).replace(",", "."))
                continue

            result = re.search(r"Kirchensteuer.* (-?\d+\.\d+) EUR", line)
            if result != None and len(result.groups()):
                church_tax = float(result.group(1).replace(",", "."))
                continue

            result = re.search(r"(\d+) Stk (-?\d+\.\d+) EUR (-?\d+\.\d+) EUR", line)
            if result != None and len(result.groups()) > 2:
                quantity = float(result.group(1).replace(",", ".")) * sign
                price = float(result.group(2).replace(",", "."))
                value = float(result.group(3).replace(",", ".")) * sign * -1.0
                continue

    yield date, description, isin, quantity, price, value, fee, capital_returns_tax, soli, church_tax, path


if __name__ == "__main__":
    import sys
    sc = scanner("trade_republic")
    for transaction in sc.conv(sys.argv[1]):
        print(transaction)
