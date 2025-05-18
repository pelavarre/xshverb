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
  strips leading and trailing blank space from each File, but does end with 1 Line-Break
  strips trailing blank space from each Line
  more doc at https://github.com/pelavarre/xshverb

most common words:
  awk b cat diff emacs find grep head str.split jq less ls make
  nl for.str.strip python git reversed sorted tail unique vi w xargs yes z

examples:
  git show |i  s  u  s -nr  h  c  # show the most common words in the last Git Commit
  p  # chat with Python, and don't make you spell out the Imports, or Build & run a Shell Pipe
  v  # fix up the Os/Copy Paste Buffer and call Vim to edit it
"""

# code reviewed by People, Black, Flake8, MyPy Strict, & PyLance-Standard


import dataclasses
import hashlib
import os
import pathlib
import sys
import typing


@dataclasses.dataclass(order=True)  # , frozen=True)
class ShellVerb:
    """A Shell Pipe Filter"""

    hint: str

    def __init__(self, hints: list[str]) -> None:
        """Parse a Hint, else show Help and exit"""

        hint = hints.pop(0)
        self.hint = hint

        if hint == "xshverb":
            return

        if hint == "p":
            return

        text = f"xshverb: command not found: {hint}"
        eprint(text)
        sys.exit(2)  # exits 2 for undefined Hint


class ShellPipe:
    """Pump Bytes in, and on through Pipe Filters, and then out again"""

    def main(self, argv: list[str]) -> None:
        """Run from the Sh Command Line"""

        shverbs = self.parse_args_else(argv)

        print(shverbs)
        sys.exit(1)

    def parse_args_else(self, argv: list[str]) -> list[ShellVerb]:
        """Parse Args, else show Verson or Help and exit"""

        assert __doc__, (__doc__, __file__)
        doc = __doc__.strip()
        usage = doc.splitlines()[0]

        # Compile Hints in order

        hints = list(argv)
        hints[0] = os.path.split(argv[0])[-1]  # 'xshverb.py' from 'bin/xshverb.py'

        # Show help and exit zero, when asked

        shverbs = list()

        shverb: ShellVerb | None = None
        double_dashed = False

        while hints:
            hint = hints[0]

            if hint == "--":
                hints.pop(0)
                double_dashed = True
                continue

            if not double_dashed:

                if (hint == "-h") or ("--help".startswith(hint) and hint.startswith("--h")):
                    hints.pop(0)
                    self.do_show_help()
                    sys.exit(0)

                if (hint == "-V") or ("--version".startswith(hint) and hint.startswith("--v")):
                    hints.pop(0)
                    self.do_show_version()
                    sys.exit(0)

                text = f"{shverb}: error: unrecognized arguments: {hint}"
                if hint.startswith("-"):
                    hints.pop(0)
                    eprint(usage)
                    eprint(text)
                    sys.exit(2)  # exits 2 for bad Sh Args

            shverb = ShellVerb(hints)  # exits 2 for undefined Hint
            shverbs.append(shverb)

        # Succeed

        return shverbs

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
# Amp up Import Sys
#


def eprint(*args: typing.Any, **kwargs: typing.Any) -> None:
    print(*args, **kwargs, file=sys.stderr)


#
# Run from the Sh Command Line, if not imported
#


if __name__ == "__main__":
    p = ShellPipe()
    p.main(sys.argv)


# posted as:  https://github.com/pelavarre/xshverb/blob/main/bin/xshverb.py
# copied from:  git clone https://github.com/pelavarre/xshverb.git
