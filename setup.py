from setuptools import setup, find_packages


if __name__ == "__main__":
    from clerk import __version__ as VERSION

    setup(
        version=VERSION,
        packages=find_packages(),
        entry_points = {
            "console_scripts": ["clerk=clerk.main:main"],
        }
    )
