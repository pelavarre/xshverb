#!/usr/bin/env python3

r"""
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
  docs the [-h] and [-V] options here, not again and again for every different Hint
  more doc at https://github.com/pelavarre/xshverb

most common Python words:
  bytes decode dedent encode join list lower replace str title upper

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
  git show |i  s  u  s -nr  h  c  # shows the most common words in the last Git Commit
  p  # chats with Python, and doesn't make you spell out the Imports, or builds & runs a Shell Pipe
  v  # fixes up the Os/Copy Paste Buffer and calls Vim to edit it
"""

# todo: --py to show the Python chosen, --py=... to supply your own Python
# todo: make a place for:  column -t, fmt --ruler, etc


# code reviewed by People, Black, Flake8, MyPy-Strict, & PyLance-Standard


import collections.abc
import dataclasses
import hashlib
import os
import pathlib
import re
import shlex
import subprocess
import sys
import textwrap
import typing


YYYY_MM_DD = "2025-05-23"  # date of last change to this Code, or an earlier date


ShellFunc = collections.abc.Callable[["ShellPipe", list[str]], None]


class ShellFile:
    """Pump Bytes in and out"""  # 'Store and forward'

    iobytes: bytes = b""

    fillable: bool = True
    drainable: bool = True

    def fill_if(self) -> None:
        """Read Bytes, if not filled already"""

        fillable = self.fillable
        if fillable:
            self.fillable = False
            self.drainable = False

            self.fill()

    def fill(self) -> None:
        """Read Bytes from Stdin else from Os Copy/Paste Buffer"""

        if not sys.stdin.isatty():

            path = pathlib.Path("/dev/stdin")  # todo: solve for Windows too
            read_bytes = path.read_bytes()
            self.iobytes = read_bytes

        else:

            shline = "pbpaste"  # macOS convention, often not distributed at Linuxes
            argv = shlex.split(shline)
            run = subprocess.run(
                argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=None, check=True
            )

            self.iobytes = run.stdout  # replaces

        # .returncode .shell .stdin differs from:  iobytes = os.popen(shline).read().encode()

    def readlines(self) -> list[str]:
        """Read Lines from Bytes, but first fill from the Os Copy/Paste Buffer if need be"""

        self.fill_if()

        iobytes = self.iobytes
        decode = iobytes.decode()
        splitlines = decode.splitlines()

        return splitlines

    def writelines(self, olines: list[str]) -> None:
        """Write Lines to Bytes"""

        rstrips = list(_.rstrip() for _ in olines)
        join = "\n".join(rstrips)
        strip = join.strip("\n")
        iochars = strip + "\n"
        encode = iochars.encode()

        self.iobytes = encode  # replaces

    def drain_if(self) -> None:
        """Write Bytes, if not drained already"""

        drainable = self.drainable
        if drainable:
            self.fillable = False
            self.drainable = False

            self.drain()

    def drain(self) -> None:
        """Write Bytes to Stdout, else to the Os Copy/Paste Buffer"""

        iobytes = self.iobytes

        if not sys.stdout.isatty():

            fd = sys.stdout.fileno()
            data = iobytes
            os.write(fd, data)

        else:

            shline = "pbcopy"  # macOS convention, often not distributed at Linuxes
            argv = shlex.split(shline)
            subprocess.run(argv, input=iobytes, stdout=subprocess.PIPE, stderr=None, check=True)


@dataclasses.dataclass(order=True)  # , frozen=True)
class ShellPump:
    """Work to drain 1 ShellFile and fill the next ShellFile"""

    nm: str  # 'p'
    name: str  # 'python'
    func: ShellFunc  # the .do_python of a ShellPipe
    argv: list[str]  # ['p', '--version']

    name_by_nm = {  # lists the abbreviated or unabbreviated Aliases of each Shell Verb
        "a": "awk",
        "p": "python",
        "xshverb": "python",
        "xshverb.py": "python",
    }

    def __init__(self, hints: list[str], func_by_name: dict[str, ShellFunc]) -> None:
        """Parse a Hint, else show Help and exit"""

        assert hints, (hints,)

        name_by_nm = self.name_by_nm

        # Pop the Shell Verb, and zero or more Dashed Options

        argv = list()
        while hints:
            arg = hints.pop(0)
            argv.append(arg)  # may be '--', and may be '--' more than once

            if hints:
                peek = hints[0]
                if peek.isidentifier():  # any '-' or '--' option, also 'a|b' etc etc
                    break

        # Require an Alias of a Shell Verb, or the Shell Verb itself

        nm = argv[0]

        name = nm
        if nm in name_by_nm.keys():
            name = name_by_nm[nm]  # Aliases are often shorter than their Shell Verbs

        if name not in func_by_name.keys():
            text = f"xshverb: command not found: {nm}"  # a la Bash & Zsh vs New Verbs
            eprint(text)
            sys.exit(2)  # exits 2 for bad Shell Verb

        func = func_by_name[name]

        # Succeed

        self.nm = nm
        self.name = name
        self.func = func
        self.argv = argv

    def parse_shpump_args_else(self) -> None:
        """Parse Args, else show Version or Help and exit zero"""

        argv = self.argv

        assert __doc__, (__doc__, __file__)
        doc = __doc__.strip()
        usage = doc.splitlines()[0]

        nm = argv[0]
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

            if re.fullmatch(r"[-+]?[0-9]+", arg):  # FIXME: more thought!
                continue

            text = f"{nm}: error: unrecognized arguments: {arg}"
            eprint(usage)
            eprint(text)
            sys.exit(2)  # exits 2 for bad Shell Arg

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
    """Pump Bytes through a pipe of Shell Pumps"""

    stdin: ShellFile
    stdout: ShellFile

    func_by_name: dict[str, ShellFunc]

    def __init__(self) -> None:
        self.func_by_name = dict(
            awk=do_awk,
            python=do_little,
        )

    def shpipe_main(self, argv: list[str]) -> None:
        """Run from the Sh Command Line"""

        shpumps = self.parse_shpipe_args_else(argv)

        self.stdout = ShellFile()
        for shpump in shpumps:
            self.stdin = self.stdout
            self.stdout = ShellFile()

            shpipe = self
            argv = shpump.argv
            shpump.func(shpipe, argv)  # two positional args, zero keyword args

        self.stdout.drain_if()

    def parse_shpipe_args_else(self, argv: list[str]) -> list[ShellPump]:
        """Parse Args, else show Version or Help and exit"""

        hints = list(argv)
        hints[0] = os.path.split(argv[0])[-1]  # 'xshverb.py' from 'bin/xshverb.py'

        func_by_name = self.func_by_name

        shpumps = list()
        while hints:
            shpump = ShellPump(hints, func_by_name=func_by_name)  # exits 2 for bad Hints
            shpump.parse_shpump_args_else()
            shpumps.append(shpump)

        return shpumps


def do_little(self: ShellPipe, argv: list[str]) -> None:
    pass


#
# Work like Awk
#


AWK_DOC = r"""

    usage: awk [-h] [-V] [-F=ISEP] [-vOFS=OSEP] [NUMBER ...]

    pick one or more columns of words, and drop the rest

    positional args:
      NUMBER  the 1-based index of a column to keep, while dropping the rest

    options:
      -F=ISEP, --isep=ISEP     input word separator, default is Blanks
      -vOFS=OSEP, --osep=OSEP  output word separator, default is Single Space

    quirks:
      rounds down Float Numbers to Ints, same as classic Awk does
      applies Python Str Split Rules to separate the Words
      accepts arbitrary chars as Seps, unlike classic Awk quirks at $'\n' $'\x00' etc
      accepts 0 as meaning 1..N, unlike Awk ignoring the Output Sep at $0
      doesn't accept Gnu Awk --field-separator=ISEP nor --assign OFS=OSEP
      doesn't write out trailing Blanks when trailing Columns missing, unlike classic Awk

    examples:
      awk  # implicitly drops all but the last Column
      awk -1  # same deal, but more explicitly
      awk 1  # similar deal, but keep only the first Column
      awk 1 3 5  # keep only the 1st, 3rd, and 5th Columns
      echo $PATH |awk -F:  # show the last Dir in the Sh Path
      echo $PATH |awk -F: -vOFS=$'\n' 0  # show 1 Dir per Line

"""

# FIXME: add -F= and -vOFS= options
# FIXME: -F should mean -F='\t'
# FIXME: -vOFS= should mean -vOFS='\t'


def do_awk(self: ShellPipe, argv: list[str]) -> None:
    """Pick some columns of words, and drop the rest"""

    isep = None
    osep = " "

    numbers = list(int(_) for _ in argv[1:])  # traditional Awk accepts Float indices
    if not numbers:
        numbers = [-1]

    olines = list()
    ilines = self.stdin.readlines()

    for iline in ilines:
        iwords = iline.split() if (isep is None) else iline.split(isep)

        max_number = len(iwords)
        min_number = -max_number

        owords = list()
        for number in numbers:
            if not number:
                owords.extend(iwords)
            elif number >= 1:
                oword = iwords[number - 1] if (number <= max_number) else ""
                owords.append(oword)
            else:
                oword = iwords[number] if (number >= min_number) else ""
                owords.append(oword)

        ojoin = osep.join(owords).rstrip()  # our .writelines does .rstrip too
        olines.append(ojoin)

    self.stdout.writelines(olines)

    # todo: Input/Output Separators other than Blanks and Single Spaces


#
# Index the Main Doc's of each Shell Verb
#


assert __doc__, (__doc__,)
DOCS: dict[str, str] = dict()

DOCS["awk"] = AWK_DOC
DOCS["python"] = __doc__

for _K_ in DOCS.keys():
    DOCS[_K_] = textwrap.dedent(DOCS[_K_]).strip()


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
