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

from .adaptors import *
from .scanner import StatementScanner
from clerk import __version__

import argparse
import datetime
import operator
import os
import pathlib
import sqlite3


sql_auszug = """
CREATE VIEW IF NOT EXISTS Kontoauszug(Datum, Beschreibung, Betrag, Saldo) AS
SELECT strftime('%Y-%m-%d', date) AS Datum, description AS Beschreibung, value AS Betrag, (
    SELECT round(sum(t2.value), 2)
    FROM __transactions__ t2
    WHERE t2.id <= t1.id
) AS Saldo
FROM __transactions__ t1;
"""


def parse_args():
    parser = argparse.ArgumentParser(
        description="Converts your folder full of bank statements into a simple sqlite database for postprocessing with SQL")

    parser.add_argument("scanner",
                        type=str,
                        help="Keyword of the the statement scanner to be used")

    parser.add_argument("input_dir",
                        type=str,
                        help="Input folder containing the bank statements")

    parser.add_argument("output_file",
                        type=str,
                        nargs="?",
                        default="transactions.sqlite3",
                        help="Output file name (optional)")

    parser.add_argument("-i", "--initial",
                        type=str,
                        dest="initial_transaction",
                        default=None,
                        help="Initial transfer in the form of <YYYY-mm-dd HH:MM:SS>;<description>;<amount>")

    parser.add_argument("-u", "--update",
                        type=str,
                        dest="update_file",
                        default=None,
                        help="Update file with recent transfers younger than the last bank statement")

    parser.add_argument("-s", "--sql",
                        type=str,
                        dest="sql_dir",
                        default=None,
                        help="Directory containing sql files for postprocessing")

    parser.add_argument("--version",
                        action='version',
                        version="clerk v" + __version__ +
                        ", Copyright (C) 2022 Patrick Ziegler")

    return parser.parse_args()


def main():
    args = parse_args()

    scanner = StatementScanner(args.scanner)

    transactions = [transaction for root, _, files in os.walk(args.input_dir)
           for statement in files if scanner.filt(statement)
           for transaction in scanner.conv(os.path.join(root, statement))]

    if args.initial_transaction is not None:
        date, description, amount = args.initial_transaction.split(";")
        transactions.append((datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S"), description, float(amount)))

    if args.update_file is not None:
        date_max = max(transactions, key=operator.itemgetter(0))[0]
        transactions.extend(item for item in scanner.conv_update(args.update_file) if item[0] > date_max)

    pathlib.Path(args.output_file).unlink(missing_ok=True)

    conn = sqlite3.connect(args.output_file)
    curs = conn.cursor()
    curs.execute("CREATE TABLE __transactions__ (id INTEGER PRIMARY KEY, date INTEGER, description TEXT, value REAL)")
    curs.executemany("INSERT OR IGNORE INTO __transactions__ (Date, Description, Value) VALUES(?,?,?)", sorted(transactions))
    curs.executescript(sql_auszug)

    if args.sql_dir is not None:
        for root, _, files in os.walk(args.sql_dir):
            for filename in files:
                path = os.path.join(root, filename)
                base, ext = os.path.splitext(filename)
                if ext == ".sql":
                    with open(path, "r") as fd:
                        curs.executescript("\n".join(fd.readlines()))
                elif ext == ".csv":
                    curs.execute("CREATE TABLE " + base + " (id INTEGER PRIMARY KEY, description TEXT)")
                    with open(path, "r") as fd:
                        curs.executemany("INSERT INTO " + base + " (Description) VALUES (?)", [(s[:-1],) for s in fd.readlines()])

    conn.commit()
    conn.close()
