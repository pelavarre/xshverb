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
  strips leading and trailing Blanks from each File, and ends with 1 Line-Break, by default
  strips trailing Blanks from each Line, by default
  more doc at https://github.com/pelavarre/xshverb

most common Python words:
  bytes decode dedent encode join list lower str title upper

python examples:
  p lower  # convert the Os/Copy Paste Buffer to lower case
  p lower c  # preview changes without saving changes
  p str lower  # change Chars without first stripping off the Blanks
  p bytes lower  # change Bytes without first stripping off the Blanks
  p join --sep=.  # join Lines into a single Line, with a Dot between each Line

most common Shell words:
  awk b cat diff emacs find grep head str.split jq less ls make
  nl for.str.strip python git reversed sorted tail unique vi w xargs yes z

examples:
  git show |i  s  u  s -nr  h  c  # show the most common words in the last Git Commit
  p  # chat with Python, and don't make you spell out the Imports, or Build & run a Shell Pipe
  v  # fix up the Os/Copy Paste Buffer and call Vim to edit it
"""
# todo: --py to show the Python chosen, --py=... to supply your own Python

# code reviewed by People, Black, Flake8, MyPy-Strict, & PyLance-Standard


import dataclasses
import hashlib
import os
import pathlib
import sys
import textwrap
import typing


YYYY_MM_DD = "2025-05-18"  # date of last change to this Code, or an earlier date


class ShellFunc(typing.Protocol):
    def __call__(self, argv: list[str]) -> None: ...


assert __doc__, (__doc__,)
DOCS: dict[str, str] = dict()
DOCS["python"] = __doc__


@dataclasses.dataclass(order=True)  # , frozen=True)
class ShellVerb:
    """A Shell Pipe Filter"""

    nm: str  # 'p'
    name: str  # 'python'
    func: ShellFunc  # the .do_python of a ShellPipe
    argv: list[str]  # ['p', '--version']

    name_by_nm = {  # each of our .nm's is the .name itself, or an alias of the .name
        "p": "python",
        "xshverb": "python",
        "xshverb.py": "python",
    }

    def __init__(self, hints: list[str], func_by_name: dict[str, ShellFunc]) -> None:
        """Parse a Hint, else show Help and exit"""

        assert hints, (hints,)

        name_by_nm = self.name_by_nm

        # Pop the Sh Verb, and zero or more Dashed Options

        argv = list()
        while hints:
            arg = hints.pop(0)
            argv.append(arg)  # may be '--', and may be '--' more than once

            if hints and not hints[0].startswith("-"):
                break

        # Require a Well-Known Alias of a Well-Known Verb, or the Well-Known Verb itself

        nm = argv[0]

        name = nm
        if nm in name_by_nm.keys():
            name = name_by_nm[nm]

        if name not in func_by_name.keys():
            text = f"xshverb: command not found: {nm}"
            eprint(text)
            sys.exit(2)  # exits 2 for bad Sh Verb

        func = func_by_name[name]

        # Succeed

        self.nm = nm
        self.name = name
        self.func = func
        self.argv = argv

    def parse_shverb_args_else(self) -> None:
        """Parse Args, else show Version or Help and exit zero"""

        argv = self.argv

        assert __doc__, (__doc__, __file__)
        doc = __doc__.strip()
        usage = doc.splitlines()[0]

        shverb = argv[0]
        double_dashed = False
        for arg in argv[1:]:

            if not double_dashed:

                if arg == "--":
                    double_dashed = True
                    continue

                if (arg == "-h") or ("--help".startswith(arg) and arg.startswith("--h")):
                    self.do_show_help()
                    sys.exit(0)

                if (arg == "-V") or ("--version".startswith(arg) and arg.startswith("--v")):
                    self.do_show_version()
                    sys.exit(0)

            text = f"{shverb}: error: unrecognized arguments: {arg}"
            eprint(usage)
            eprint(text)
            sys.exit(2)  # exits 2 for bad Sh Arg

    def do_show_help(self) -> None:
        """Show help and exit zero"""

        nm = self.nm
        name = self.name

        full_doc = DOCS[name]

        key = "usage: xshverb.py "
        doc = textwrap.dedent(full_doc).strip()
        if doc.startswith(key) and (nm != "xshverb.py"):
            count_eq_1 = 1
            doc = doc.replace(key, f"usage: {nm} ", count_eq_1)

        print(doc)

    def do_show_version(self) -> None:
        """Show version and exit zero"""

        version = pathname_read_version(__file__)

        print(YYYY_MM_DD, version)


class ShellPipe:
    """Pump Bytes in, and on through Pipe Filters, and then out again"""

    func_by_name: dict[str, ShellFunc]

    def __init__(self) -> None:
        self.func_by_name = dict(
            python=self.do_python,
        )

    def shpipe_main(self, argv: list[str]) -> None:
        """Run from the Sh Command Line"""

        shverbs = self.parse_shpipe_args_else(argv)

        for shverb in shverbs:
            eprint(shverb)

        for shverb in shverbs:
            shverb.func(shverb.argv)

        sys.exit(1)

    def parse_shpipe_args_else(self, argv: list[str]) -> list[ShellVerb]:
        """Parse Args, else show Version or Help and exit"""

        hints = list(argv)
        hints[0] = os.path.split(argv[0])[-1]  # 'xshverb.py' from 'bin/xshverb.py'

        func_by_name = self.func_by_name

        shverbs = list()
        while hints:
            shverb = ShellVerb(hints, func_by_name=func_by_name)  # exits 2 for bad Hints
            shverb.parse_shverb_args_else()
            shverbs.append(shverb)

        return shverbs

    def do_python(self, argv: list[str]) -> None:
        """Run Python"""

        print(argv)
        sys.exit(1)


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
    p.shpipe_main(sys.argv)


# posted as:  https://github.com/pelavarre/xshverb/blob/main/bin/xshverb.py
# copied from:  git clone https://github.com/pelavarre/xshverb.git
