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
  bin/xshverb.py  # shows these examples and exit
  git show |i  s  u  s -nr  h  c  # shows the most common words in the last Git Commit
  a --help  # shows the Help Doc for the Awk Shell Verb
  p  # chats with Python, and doesn't make you spell out the Imports, or builds & runs a Shell Pipe
  v  # fixes up the Os/Copy Paste Buffer and calls Vim to edit it
"""

# todo: --py to show the Python chosen, --py=... to supply your own Python
# todo: make a place for:  column -t, fmt --ruler, etc


# code reviewed by People, Black, Flake8, MyPy-Strict, & PyLance-Standard


import argparse
import collections.abc
import dataclasses
import difflib
import hashlib
import os
import pathlib
import shlex
import subprocess
import sys
import textwrap


if not __debug__:
    raise NotImplementedError(str((__debug__,)))  # "'python3' is better than 'python3 -O'"


YYYY_MM_DD = "2025-05-25"  # date of last change to this Code, or an earlier date


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

    def exit_help_or_exit_version_if(self) -> None:
        """Show Version or Help and exit zero"""

        argv = self.argv

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

        shpumps = self.parse_shpipe_args_if(argv)

        self.stdout = ShellFile()
        for shpump in shpumps:
            self.stdin = self.stdout
            self.stdout = ShellFile()

            shpipe = self
            argv = shpump.argv
            shpump.func(shpipe, argv)  # two positional args, zero keyword args

        self.stdout.drain_if()

    def parse_shpipe_args_if(self, argv: list[str]) -> list[ShellPump]:
        """Parse Args, else show Version or Help and exit"""

        hints = list(argv)
        hints[0] = os.path.basename(argv[0])  # 'xshverb.py' from 'bin/xshverb.py'

        func_by_name = self.func_by_name

        shpumps = list()
        while hints:
            shpump = ShellPump(hints, func_by_name=func_by_name)  # exits 2 for bad Hints
            shpump.exit_help_or_exit_version_if()
            shpumps.append(shpump)

        return shpumps


def do_little(self: ShellPipe, argv: list[str]) -> None:
    pass


#
# Work like Awk
#


AWK_DOC = r"""

    usage: awk [-F ISEP] [-vOFS OSEP] [NUMBER ...]

    pick one or more columns of words, and drop the rest

    positional arguments:
      NUMBER              the Number of a Column to copy out, or 0 to copy them all (default: -1)

    options:
      -F, --isep ISEP     input word separator (default: Blanks)
      -vOFS, --osep OSEP  output word separator (default: Double Space)

    like to classic Awk:
      rounds down Float Numbers to Ints, even 0.123 to 0
      applies Python Str Split Rules to separate the Words

    unlike classic Awk:
      takes negative Numbers as counting back from the right, not ahead from the left
      takes 0 as meaning all the Words joined by Output Sep, not a copy of the Input Line
      accepts arbitrary Chars as Seps, even $'\n' $'\x00' etc
      rejects misspellings of -vOFS=, after autocorrecting -vO= or -vOF=
      doesn't accept Gnu Awk --field-separator=ISEP nor --assign OFS=OSEP
      doesn't write out trailing Output Seps when trailing Columns missing or empty

    examples:
      alias a= && unalias a && function a() { ls -l |pbcopy && bin/a "$@" && pbpaste; }
      a  # implicitly drops all but the last Column
      a -1  # same deal, but more explicitly
      a 1  # similar deal, but keep only the first Column
      a 1 5 -1  # keep only the 1st, 5th, and last Column
      echo $PATH |a -F:  # show only the last Dir in the Sh Path
      echo $PATH |a -F: -vOFS=$'\n' 0  # show 1 Dir per Line, as if |tr : '\n'
      echo 'a1 a2\tb1 b2\tc1 c2' |a -F$'\t' -vOFS=$'\t' 3 1  # Tabs in and Tabs out

"""


def do_awk(self: ShellPipe, argv: list[str]) -> None:
    """Pick some columns of words, and drop the rest"""

    # Form Shell Args Parser

    assert argparse.ZERO_OR_MORE == "*"

    doc = AWK_DOC
    number_help = "the Number of a Column to copy out, or 0 to copy them all (default: -1)"
    isep_help = "input word separator (default: Blanks)"
    osep_help = "output word separator (default: Double Space)"

    parser = AmpedArgumentParser(doc, add_help=False)
    parser.add_argument(dest="numbers", metavar="NUMBER", nargs="*", help=number_help)
    parser.add_argument("-F", "--isep", metavar="ISEP", help=isep_help)
    parser.add_argument("-vOFS", "--osep", metavar="OSEP", help=osep_help)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    ns = parser.parse_args_if(args)  # often prints help & exits zero

    isep = None if (ns.isep is None) else ns.isep
    osep = "  " if (ns.osep is None) else ns.osep

    numbers = list(int(_) for _ in ns.numbers)  # rounds down Floats, even to 0, as Awk does
    if not numbers:
        numbers = [-1]

    # Pick one or more Columns of Words, and drop the rest

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

        while not owords[-1]:
            owords.pop()

        ojoin = osep.join(owords)
        olines.append(ojoin)

    self.stdout.writelines(olines)


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
# Amp up Import ArgParse
#


class AmpedArgumentParser:
    """Pick out Prog & Description & Epilog well enough to form an Argument Parser"""

    text: str  # something like the __main__.__doc__, but dedented and stripped
    parser: argparse.ArgumentParser  # the inner merely standard Parser
    closing: str  # the last Graf of the Epilog, minus its Top Line

    #
    # Pick apart a Help Doc of Prog & Description & Epilog well enough to form a Parser
    #

    def __init__(self, doc: str, add_help: bool) -> None:
        """Pick out Prog & Description & Epilog well enough to form an Argument Parser"""

        assert doc, (doc,)

        text = textwrap.dedent(doc).strip()
        lines = text.splitlines()

        prog = self.scrape_prog(lines)
        description = self.scrape_description(lines)
        epilog = self.scrape_epilog(lines, description=description)

        closing = self.scrape_closing(epilog=epilog)
        assert closing, (epilog, description, lines)

        parser = argparse.ArgumentParser(  # doesn't distinguish Closing from Epilog
            prog=prog,
            description=description,
            add_help=add_help,
            formatter_class=argparse.RawTextHelpFormatter,  # lets Lines be wide
            epilog=epilog,
        )

        self.text = text
        self.parser = parser
        self.closing = closing

        self.add_argument = parser.add_argument  # helps the Caller say '.parser.parser.' less often

        # 'doc=' is the kind of Help Doc that comes from ArgumentParser.format_help
        # 'add_help=False' for 'cal -h', 'df -h', 'du -h', 'ls -h', etc

        # callers who want Options & Positional Arguments in the Parser have to add them

    def scrape_prog(self, lines: list[str]) -> str:
        """Pick the Prog out of the Usage Graf that starts the Doc"""

        prog = lines[0].split()[1]  # second Word of first Line  # 'prog' from 'usage: prog'

        return prog

    def scrape_description(self, lines: list[str]) -> str:
        """Take the first Line of the Graf after the Usage Graf as the Description"""

        firstlines: list[str] = list(_ for _ in lines if _ and (_ == _.lstrip()))
        alt_description = firstlines[1]  # first Line of second Graf

        description = alt_description
        if self.docline_is_skippable(alt_description):
            description = "just do it"

        return description

    def docline_is_skippable(self, docline: str) -> bool:
        """Guess when a Doc Line can't be the first Line of the Epilog"""

        strip = docline.rstrip()

        skippable = not strip
        skippable = skippable or strip.startswith(" ")  # includes .startswith("  ")
        skippable = skippable or strip.startswith("usage")
        skippable = skippable or strip.startswith("positional arguments")
        skippable = skippable or strip.startswith("options")  # excludes "optional arguments"

        return skippable

    def scrape_epilog(self, lines: list[str], description: str) -> str | None:
        """Take up the Lines past Usage, Positional Arguments, & Options, as the Epilog"""

        epilog = None
        for index, line in enumerate(lines):
            if self.docline_is_skippable(line) or (line == description):
                continue

            epilog = "\n".join(lines[index:])
            break

        return epilog

    def scrape_closing(self, epilog: str | None) -> str:
        """Pick out the last Graf of the Epilog, minus its Top Line"""

        text = "" if (epilog is None) else epilog
        lines = text.splitlines()

        indices = list(_ for _ in range(len(lines)) if lines[_])  # drops empty Lines
        indices = list(_ for _ in indices if not lines[_].startswith(" "))  # finds Ttop Lines

        join = "\n".join(lines[indices[-1] + 1 :])  # last Graf, minus its Top Line
        dedent = textwrap.dedent(join)
        closing = dedent.strip()

        return closing

    #
    # Parse the Shell Args, else print Help and exit zero or nonzero
    #

    def parse_args_if(self, args: list[str]) -> argparse.Namespace:
        """Parse the Shell Args, else print Help and exit zero or nonzero"""

        parser = self.parser
        closing = self.closing

        # Drop the "--" Shell Args Separator, if present,
        # because 'ArgumentParser.parse_args()' without Pos Args wrongly rejects it

        shargs = args
        if args == ["--"]:  # ArgParse chokes if Sep present without Pos Args
            shargs = list()

        # Print Diffs & exit nonzero, when Arg Doc wrong

        diffs = self.diff_doc_vs_format_help()
        if diffs:
            print("\n".join(diffs))

            sys.exit(2)  # exits 2 for wrong Args in Help Doc

        # Print Closing & exit zero, if no Shell Args

        if not args:
            print()
            print(closing)
            print()

            sys.exit(0)  # exits 0 after printing examples

        # Print help lines & exit zero, else return Parsed Args

        ns = parser.parse_args(shargs)

        return ns

        # often prints help & exits zero

    def diff_doc_vs_format_help(self) -> list[str]:
        """Form Diffs from Help Doc to Parser Format_Help"""

        text = self.text
        parser = self.parser

        # Say where the Help Doc came from

        a = text.splitlines()

        basename = os.path.split(__file__)[-1]
        fromfile = "{} --help".format(basename)

        # Fetch the Parser Doc from a fitting virtual Terminal
        # Fetch from a Black Terminal of 89 columns, not from the current Terminal width
        # Fetch from later Python of "options:", not earlier Python of "optional arguments:"

        if "COLUMNS" not in os.environ:

            os.environ["COLUMNS"] = str(89)  # adds
            try:
                b_doc = parser.format_help()
            finally:
                del os.environ["COLUMNS"]  # removes

        else:

            with_columns = os.environ["COLUMNS"]  # backs up
            os.environ["COLUMNS"] = str(89)  # replaces
            try:
                b_doc = parser.format_help()
            finally:
                os.environ["COLUMNS"] = with_columns  # restores

        b_text = b_doc.replace("optional arguments:", "options:")
        b = b_text.splitlines()

        tofile = "ArgumentParser(...)"

        # Form >= 0 Diffs from Help Doc to Parser Format_Help,
        # but ask for lineterm="", for else the '---' '+++' '@@' Diff Control Lines end with '\n'

        diffs = list(difflib.unified_diff(a=a, b=b, fromfile=fromfile, tofile=tofile, lineterm=""))

        # Succeed

        return diffs


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


def eprint(*args: object) -> None:
    print(*args, file=sys.stderr)


#
# Run from the Sh Command Line, if not imported
#


if __name__ == "__main__":
    p = ShellPipe()
    p.shpipe_main(sys.argv)


# posted as:  https://github.com/pelavarre/xshverb/blob/main/bin/xshverb.py
# copied from:  git clone https://github.com/pelavarre/xshverb.git
