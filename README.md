# :shipit: clerk

Converts your folder full of bank statements into a simple sqlite database for postprocessing with SQL

## Usage

Considering a file structure like shown below, you can use `clerk abstract_account ingdiba ./diba` to recursively search for bank statements and collect all transactions into a single sqlite database.

```sh
.
├── diba
│   ├── ...
│   ├── 2022
│   │   ├── Girokonto_xxxxxxxxxx_Kontoauszug_20220202.pdf
│   │   └── Girokonto_xxxxxxxxxx_Kontoauszug_20220302.pdf
│   ├── Makefile
│   ├── transactions.sqlite3 # will be created by clerk
│   └── umsatz.csv
```

If your folder structure does not contain the full history of your bank account, you can use the option `--initial` to add an initial transaction with any offset you need.

Most bank accounts allow to download csv files with all recent transactions since the last official statement. You can import those as well by using the option `--update`.

It is convenient to use a `Makefile` for generating and opening the database with [sqlitebrowser](https://sqlitebrowser.org/) by simply running `make`.

```Makefile
all:
  clerk abstract_account ingdiba . --initial "2000-01-01 00:00:00;Uebertrag;123.45" --update umsatz.csv
  sqlitebrowser transactions.sqlite3 &
```

## Installation

- Use the following commands to install `clerk` for the current user

  ```sh
  pip3 install -r requirements.txt --user
  python3 setup.py install --user
  ```

- For updating `clerk`, just repeat these steps after executing `git pull` in your cloned repo

- `clerk` uses [pdftotext](https://www.xpdfreader.com/pdftotext-man.html), [ps2pdf](https://linux.die.net/man/1/ps2pdf), [pdf2ps](https://linux.die.net/man/1/pdf2ps) for parsing bank statements, these tools need to be installed on your system

  ```sh
  # to install pdftotext, ps2pdf and pdf2ps and other useful tools on openSUSE
  zypper install poppler-tools ghostscript sqlite3 sqlitebrowser
  ```

## License

This project is licensed under the GPL - see the [LICENSE](LICENSE) file for details
