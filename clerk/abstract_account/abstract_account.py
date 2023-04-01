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

import operator
import os
import pathlib
import sqlite3

SQL_ABSTRACT_ACCOUNT = """
create view if not exists Kontoauszug(Datum, Beschreibung, Betrag, Saldo) as
select strftime('%Y-%m-%d', date) as Datum, description as Beschreibung, value as Betrag, (
    select round(sum(t2.value), 2)
    from __transactions__ t2
    where t2.id <= t1.id
) as Saldo
from __transactions__ t1;
"""


class AbstractAccount:

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

    @classmethod
    def register_conv_update(cls, key):
        def wrap(fn):
            cls._conv_update[key] = fn
        return wrap

    def __init__(self, key):
        self.key = key
        self.transactions = []

    def filt(self, *args, **kwargs):
        return self._filt[self.key](*args, **kwargs)

    def conv(self, *args, **kwargs):
        return self._conv[self.key](*args, **kwargs)

    def conv_update(self, *args, **kwargs):
        return self._conv_update[self.key](*args, **kwargs)

    def scan(self, input_dir):
        self.transactions = [transaction for root, _, files in os.walk(input_dir)
                for statement in files if self.filt(statement)
                for transaction in self.conv(os.path.join(root, statement))]

    def add(self, transaction):
        self.transactions.append(transaction)

    def update(self, update_file):
        date_max = max(self.transactions, key=operator.itemgetter(0))[0]
        self.transactions.extend(item for item in self.conv_update(update_file) if item[0] > date_max)

    def export(self, output_file):
        pathlib.Path(output_file).unlink(missing_ok=True)
        conn = sqlite3.connect(output_file)
        curs = conn.cursor()
        curs.execute("create table __transactions__ (id integer primary key, date integer, description text, value real)")
        curs.executemany("insert or ignore into __transactions__ (Date, Description, Value) values(?,?,?)", sorted(self.transactions))
        curs.executescript(SQL_ABSTRACT_ACCOUNT)
        conn.commit()
        conn.close()
