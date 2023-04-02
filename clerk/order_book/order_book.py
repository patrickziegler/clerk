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

import os
import pathlib
import sqlite3


class OrderBook:

    _filt = {}
    _conv = {}
    _conv_update = {}

    @classmethod
    def register_filt(cls, key):
        def wrap(fn):
            cls._filt[key] = fn
        return wrap

    @classmethod
    def register_conv(cls, key):
        def wrap(fn):
            cls._conv[key] = fn
        return wrap

    def __init__(self, key):
        self.key = key
        self.transactions = []

    def filt(self, *args, **kwargs):
        return self._filt[self.key](*args, **kwargs)

    def conv(self, *args, **kwargs):
        return self._conv[self.key](*args, **kwargs)

    def scan(self, input_dir):
        self.transactions = [transaction for root, _, files in os.walk(input_dir)
                for settlement in files if self.filt(settlement)
                for transaction in self.conv(os.path.join(root, settlement))]

    def export(self, output_file):
        pathlib.Path(output_file).unlink(missing_ok=True)
        conn = sqlite3.connect(output_file)
        curs = conn.cursor()
        curs.execute("create table __transactions__ (rowid integer primary key, date integer, description text, isin text, quantity integer, price real, value real, fee real, crt real, soli real, ct real, path text)")
        curs.executemany("insert or ignore into __transactions__ (date, description, isin, quantity, price, value, fee, crt, soli, ct, path) values(?,?,?,?,?,?,?,?,?,?,?)", sorted(self.transactions))
        conn.commit()
        conn.close()
