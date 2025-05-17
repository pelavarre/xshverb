#!/usr/bin/env python3

"""
usage: xshverb.py [-h] [-V] [HINT ...]

make it quick and easy to build and run a good Shell Pipe

options:
  -h, --help     show this message and exit
  -V, --version  show version and exit

positional args:
  HINT  enough of a hint to search out the correct Shell Pipe Filter

quirks:
  strips leading and trailing blank space from each File
  strips trailing blank space from each Line
  more doc at https://github.com/pelavarre/xshverb

most common words:
  awk b cat diff emacs find grep head str.split jq less ls make
  nl for.str.strip python git reversed sorted tail unique vi w xargs yes z

examples:
  git show |i  s  u  s -nr  h  c  # show the most common words in the last Git Commit
  e  # fix up the Os/Copy Paste Buffer and call Emacs to edit it
  p  # chat with Python, but don't make you spell out the Imports
  v  # fix up the Os/Copy Paste Buffer and call Vim to edit it
"""

# code reviewed by People, Black, Flake8, MyPy Strict, & PyLance-Standard


import hashlib
import os
import pathlib
import sys


class ShellPipe:
    """Pump Bytes in, on through Pipe Filters, and out again"""

    def main(self, argv: list[str]) -> None:
        """Run from the Sh Command Line"""

        hints = self.parse_args_else(argv)

        print(hints)
        sys.exit(1)

    def parse_args_else(self, argv: list[str]) -> list[str]:

        # Show help and exit zero, when asked

        for arg in argv[1:]:
            if arg == "--":
                break

            if (arg == "-h") or ("--help".startswith(arg) and arg.startswith("--h")):
                self.do_show_help()
                sys.exit(0)

            if (arg == "-V") or ("--version".startswith(arg) and arg.startswith("--v")):
                self.do_show_version()
                sys.exit(0)

        # Compile Hints in order

        hints = list(argv)
        hints[0] = os.path.split(argv[0])[-1]  # 'xshverb.py' from 'bin/xshverb.py'

        # Succeed

        return hints

    def do_show_help(self) -> None:
        """Show help and exit zero"""

        assert __doc__, (__doc__, __file__)
        doc = __doc__.strip()

        print(doc)

    def do_show_version(self) -> None:
        """Show version and exit zero"""

        version = pathname_read_version(__file__)

        print("2025-05-17", version)


#
# Amp up Import PathLib
#


def pathname_read_version(pathname: str) -> str:
    """Hash the Bytes of a File down to a purely Decimal $Major.$Minor.$Micro Version Str"""

    path = pathlib.Path(pathname)
    path_bytes = path.read_bytes()

    hasher = hashlib.md5()
    hasher.update(path_bytes)
    hash_bytes = hasher.digest()

    str_hash = hash_bytes.hex()
    str_hash = str_hash.upper()  # such as 32 nybbles 'C24931F77721476EF76D85F3451118DB'
    print(str_hash)

    major = 0
    minor = int(str_hash[0], 0x10)  # 0..15
    micro = int(str_hash[1:][:2], 0x10)  # 0..255

    version = f"{major}.{minor}.{micro}"
    return version

    # 0.15.255


#
# Run from the Sh Command Line, if not imported
#


if __name__ == "__main__":
    p = ShellPipe()
    p.main(sys.argv)


# posted as:  https://github.com/pelavarre/xshverb/blob/main/bin/xshverb.py
# copied from:  git clone https://github.com/pelavarre/xshverb.git
