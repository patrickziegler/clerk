from setuptools import setup, find_packages


if __name__ == "__main__":
    from statement_scanner.config import __version__ as VERSION

    setup(
        version=VERSION,
        packages=find_packages(),
        entry_points = {
            "console_scripts": ["statement-scanner=statement_scanner.main:main"],
        }
    )
