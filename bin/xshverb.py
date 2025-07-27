#!/usr/bin/env python3

r"""
usage: xshverb.py [-h] [-V] [HINT ...]

make it quick and easy to build and run a good Shell Pipe

positional arguments:
  HINT           hint of which Shell Pipe Filter you mean

options:
  -h, --help     show this help message and exit
  -V, --version  show version and exit

quirks:
  defaults to dedent the Lines, strip trailing Blanks from each Line, and end with 1 Line-Break
  docs the [-h] and [-V] options only here, not again and again for every different Hint
  often replaces or creates a ./xshverb.pbpaste File, and also __pycache__/$pid-xshverb.pbpaste
  more doc at https://github.com/pelavarre/xshverb

most common Python words:
  bytes decode dedent encode join list lower replace str title upper

python examples:
  pq lower  # convert the Os/Copy Paste Buffer to lower case
  pq lower c  # preview changes without saving changes
  pq str strip  # drop leading/ trailing Blank Lines but leave all Blanks inside unchanged
  pq bytes lower  # change Bytes without first stripping off the Blanks
  pq join --sep=.  # join Lines into a single Line, with a Dot between each Line

most common Shell words:
  awk b cat diff emacs find grep head str.split jq less ls make
  nl for.str.strip python git reverse sort tail unique vi w xargs yes z

examples:
  bin/xshverb.py  # shows these examples and exit
  git show |i  u  s -nr  h  c  # shows the most common words in the last Git Commit
  a --  # shows the Closing Paragraph of the Help Doc for the Awk Shell Verb
  a --help  # shows the whole Help Doc for the Awk Shell Verb
  a --version  # shows the Version of the Code here
  p  # chats with Python, and doesn't make you spell out the Imports
  pq  # dedents and strips the Os/Copy Paste Buffer, first to Tty Out, and then to replace itself
  pq .  # guesses what edit you want in the Os/Copy Paste Buffer and runs ahead to do it
  v  # dedents and strips the Os/Copy Paste Buffer, and then calls Vi to edit it
"""

# todo: --py to show the Python chosen, --py=... to supply your own Python
# todo: make a place for:  column -t, fmt --ruler, tee, tee -a, etc


# code reviewed by People, Black, Flake8, MyPy-Strict, & PyLance-Standard


from __future__ import annotations

import __main__
import argparse
import collections.abc
import dataclasses
import datetime as dt
import decimal
import difflib
import hashlib
import importlib
import json
import math
import os
import pathlib
import pdb
import re
import shlex
import shutil
import signal
import socket
import string
import subprocess
import sys
import textwrap
import types
import unicodedata
import urllib.parse
import zoneinfo  # new since Oct/2020 Python 3.9


_: dict[str, int] | None  # new since Oct/2021 Python 3.10

if not __debug__:
    raise NotImplementedError(str((__debug__,)))  # "'python3' is better than 'python3 -O'"


#
# Name a few things
#


YYYY_MM_DD = "2025-06-24"  # date of last change to this Code, or an earlier date

_3_10_ARGPARSE = (3, 10)  # Oct/2021 Python 3.10  # oldest trusted to run ArgParse Static Analyses


GatewayVerbs = ("dt", "d", "g", "e", "k", "v")  # todo: these eat args despite str_is_identifier_ish


Pacific = zoneinfo.ZoneInfo("America/Los_Angeles")
PacificLaunch = dt.datetime.now(Pacific)
UTC = zoneinfo.ZoneInfo("UTC")  # todo: extend welcome into the periphery beyond San Francisco


AppPathname = "__pycache__/p.pbpaste"  # traces the last Pipe

OsGetPid = os.getpid()  # traces each Pipe separately, till Os recycles Pid's
PidPathname = f"__pycache__/{OsGetPid}.pbpaste"

GotOsCopyPasteClipboardBuffer = bool(shutil.which("pbpaste") and shutil.which("pbcopy"))
# GotOsCopyPasteClipboardBuffer = False  # runs as if Clipboard not found


#
# Do exit into a Post-Mortem Debugger, when not exiting via SystemExit
#


with_hook = sys.excepthook
assert (with_hook.__module__, with_hook.__name__) == ("sys", "excepthook"), (with_hook,)


assert int(0x80 + signal.SIGINT) == 130  # 'mypy --strict' needs the int() here


def excepthook(
    exc_type: type[BaseException],
    exc_value: BaseException,
    exc_traceback: types.TracebackType | None,
) -> None:

    if exc_type is KeyboardInterrupt:
        sys.stderr.write("\n")
        sys.exit(130)  # 0x80 + signal.SIGINT

    with_hook(exc_type, exc_value, exc_traceback)

    print(">>> pdb.pm()", file=sys.stderr)
    pdb.pm()


sys.excepthook = excepthook


#
# Run from the Shell Command Line
#


def main() -> None:
    """Run from the Shell Command Line, but never raise SystemExit"""

    try:
        try_main()
    except SystemExit as exc:
        if exc.code:
            raise

    # falling out, rather than raising SystemExit, makes os.environ["PYTHONINSPECT"] work


def try_main() -> None:
    """Run from the Shell Command Line"""

    argv = sys.argv

    # Form Shell Args Parser

    assert argparse.ZERO_OR_MORE == "*"
    assert __main__.__doc__, __main__.__doc__

    doc = __main__.__doc__
    hint_help = "hint of which Shell Pipe Filter you mean"
    version_help = "show version and exit"

    parser = ArgDocParser(doc, add_help=True)
    parser.add_argument(dest="hints", metavar="HINT", nargs="*", help=hint_help)
    parser.add_argument("-V", "--version", action="store_true", help=version_help)

    # Take up Shell Args

    basename = os.path.basename(argv[0])

    args = ["--"] + [basename] + argv[1:]
    if basename == "xshverb.py":
        if not argv[1:]:
            args = list()  # asks to print Closing

    ns = parser.parse_args_if(args)  # often prints help & exits zero

    shpumps = argv_to_shell_pumps(argv=ns.hints)  # often prints help & exits zero
    assert shpumps, (shpumps, ns.hints)

    alt.stdout = ShellFile()  # adds or replaces
    for index, shpump in enumerate(shpumps):
        alt.index = index
        alt.rindex = index - len(shpumps)

        alt.stdin = alt.stdout
        alt.stdout = ShellFile()  # adds or replaces

        assert not alt.stdout.filled, (alt.stdout.filled, index)

        argv = shpump.argv
        shpump.func(argv)  # two positional args, zero keyword args

        assert alt.stdout.filled, (alt.stdout.filled, index, argv)

    alt.stdout.drain_if()

    # todo: add code to make how truthy ns.version works more simple


@dataclasses.dataclass  # (order=False, frozen=False)
class ShellPipe:
    """Pump Bytes through a pipe of Shell Pumps"""

    def __init__(self) -> None:

        self.stdin = ShellFile()  # what we're reading
        self.stdout = ShellFile()  # what we're writing

        self.index = -1  # how far from the left the present ShellPump is:  0, 1, 2, etc
        self.rindex = 0  # how far from the right the present ShellPump is:  -1, -2, -3, etc

        self.sys_stdin_isatty = sys.stdin.isatty()  # was Stdin left undirected
        self.sys_stdout_isatty = sys.stdout.isatty()  # was Stdout left undirected


def argv_to_shell_pumps(argv: list[str]) -> list[ShellPump]:
    """Parse Args, else show Version or Help and exit"""

    verb_by_vb = VERB_BY_VB

    # Take the Name of this Process as the first Hint,
    # except not when it is an XShVerb Alias serving as a Gateway Verb into this Name Space

    basename = os.path.basename(argv[0])  # 'xshverb.py' from 'bin/xshverb.py'

    hints = list(argv)
    hints[0] = basename

    if basename in verb_by_vb.keys():
        verb = verb_by_vb[basename]
        if verb == "xshverb":
            hints.pop(0)

    # Take >= 1 Hints to build each Shell Pump

    shpumps: list[ShellPump]
    shpumps = list()

    while hints:
        index = len(shpumps)
        with_hints = list(hints)

        shpump = ShellPump()
        shpump.pop_some_hints(hints, index=index)  # exits 2 at first bad Hint
        assert len(hints) < len(with_hints), (hints, with_hints)

        shpump.exit_doc_if()  # exits 0 for Doc or Closing or Version

        shpumps.append(shpump)

    # Give meaning to the absence of Hints

    if not shpumps:

        shpump = ShellPump()
        shpump.pop_some_hints(["xshverb"], index=0)
        shpumps.append(shpump)

    return shpumps

    # often prints help & exits zero


@dataclasses.dataclass  # (order=False, frozen=False)
class ShellPump:  # much like a Shell Pipe Filter when coded as a Linux Process
    """Work to drain 1 ShellFile and fill the next ShellFile"""

    vb: str  # 'a'  # 'p'
    verb: str  # 'awk'  # 'python'

    doc: str  # AWK_DOC  # PYTHON_DOC
    func: collections.abc.Callable[[list[str]], None]  # do_awk  # do_xshverb
    argv: list[str]  # ['a']  # ['awk']

    def __init__(self) -> None:

        self.vb = ""
        self.verb = ""

        self.doc = ""
        self.func = do_pass  # explicit 'def __init__' lets us mention .do_pass before defining it
        self.argv = list()  # technically mutable, but replaced soon

    def pop_some_hints(self, hints: list[str], index: int) -> None:
        """Pop some Hints, else show Help and exit"""

        assert hints, (hints,)

        doc_by_verb = DOC_BY_VERB
        func_by_verb = FUNC_BY_VERB
        verb_by_vb = VERB_BY_VB

        # Require an Alias of a Shell Verb, or the Shell Verb itself

        argv = self.pop_argv_from_hints(hints, index=index)

        vb = argv[0]

        verb = vb  # goes with the Shell Verb itself
        if vb in verb_by_vb.keys():
            verb = verb_by_vb[vb]  # replaces an Alias with its Shell Verb

            if argv == ["dict"]:  # todo: declare more Aliases which imply Shell Args
                argv.append("--keys")

        if verb not in func_by_verb.keys():
            eprint(f"xshverb: command not found: |pq {vb}")  # a la Bash & Zsh vs New Verbs
            sys.exit(2)  # exits 2 for bad Shell Verb Hint

            # todo: report more than first meaningless undefined Verb

        # Find the Doc

        assert __main__.__doc__, (__main__.__doc__,)

        doc = doc_by_verb[verb]
        if vb == "xshverb.py":
            doc = __main__.__doc__

        # Find the Func

        func = func_by_verb[verb]

        # Succeed

        assert vb and verb and doc and argv, (vb, verb, doc, argv)  # doesn't constrain .func

        self.vb = vb
        self.verb = verb

        self.doc = doc
        self.func = func
        self.argv = argv  # replaces a mutable

        # exits 2 for bad Shell Verb

    def pop_argv_from_hints(self, hints: list[str], index: int) -> list[str]:
        """Pop the Shell Verb, its Options, and its Positional Arguments"""

        argv: list[str]
        argv = list()

        while hints:
            hint = hints.pop(0)
            words = hint.split()

            # Accept an Identifier as the Shell Verb

            if not argv:
                if str_is_identifier_ish(hint):
                    assert len(words) == 1, (len(words), words, hint)

                # Accept a Shell-Quote'd Verb with its baggage of Options and Args

                elif len(words) > 1:
                    splits = shlex.split(hint)
                    assert splits, (splits, hint)
                    if str_is_identifier_ish(splits[0]):
                        argv = splits
                        break

                # Fall back to have Pq make sense of anything else, and maybe more that follows

                else:
                    argv.append("pq")

            arg = hint
            argv.append(arg)  # may be '--', and may be '--' more than once

            # Take all the remaining Hints as Args, after a Gateway Verb into a Namespacre

            assert GatewayVerbs == ("dt", "d", "g", "e", "k", "v")

            if argv[0] in GatewayVerbs:
                continue

            # Insert a Break between Shell Pipe Filters,
            # rather than accepting a first Positional Argument,
            # when not Shell-Quote'd in with the Verb

            if hints:
                next_hint = hints[0]

                if str_is_identifier_ish(next_hint):  # not any '-' or '--' option, nor '(.)' etc etc
                    break

        return argv

    def exit_doc_if(self) -> None:
        """Show Help or Closing or Version and exit zero, else return"""

        doc = self.doc
        argv = self.argv

        parser = ArgDocParser(doc, add_help=False)  # enough to print Closing
        if argv[1:] == ["--"]:
            self.closing_show(closing=parser.closing)
            sys.exit(0)  # exits 0 after printing Closing

        double_dashed = False
        for arg in argv[1:]:

            if not double_dashed:

                if arg == "--":
                    double_dashed = True
                    continue

                if (arg == "-h") or ("--help".startswith(arg) and arg.startswith("--h")):
                    self.doc_show()
                    sys.exit(0)  # exits 0 after printing Help

                if (arg == "-V") or ("--version".startswith(arg) and arg.startswith("--v")):
                    self.version_show()
                    sys.exit(0)  # exits 0 after printing Version

        # often prints help & exits zero

    def doc_show(self) -> None:
        """Show the Help and exit zero"""

        doc = self.doc
        print(doc)

    def closing_show(self, closing: str) -> None:
        """Show the Closing and exit zero"""

        print()
        print(closing)
        print()

    def version_show(self) -> None:
        """Show version and exit zero"""

        version = pathlib_path_read_version(__file__)
        print(YYYY_MM_DD, version)


def str_is_identifier_ish(text: str) -> bool:
    """Guess when a Str is an Identifier, or close enough"""

    if text == ".":
        return True

    splits = text.split(".")
    if all(_.isidentifier() for _ in splits):
        return True

    return False


@dataclasses.dataclass  # (order=False, frozen=False)
class ShellFile:
    """Pump Bytes in and out"""  # 'Store and forward'

    iobytes: bytes = b""

    filled: bool = False
    drained: bool = False

    #
    # Pump Bytes in from Nowhere and out to Nowhere
    #

    def fill_and_drain(self) -> None:
        """Fill from Nowhere, and drain to Nowhere"""

        assert (not self.filled) and (not self.drained), (self.filled, self.drained)
        self.filled = True

        self.drained = True

    #
    # Pump Bytes in
    #

    def read_splitlines(self) -> list[str]:
        """Read Lines from Bytes, but first fill from the Os Copy/Paste Buffer if need be"""

        self.fill_if()

        iobytes = self.iobytes
        decode = iobytes.decode(errors="surrogateescape")
        splitlines = decode.splitlines()

        return splitlines

        # standard .read_splitlines sends back a Line-Break as the end of most Lines
        # standard .read_splitlines stops reading after Hint

    def read_text(self) -> str:
        """Read Chars from Stdin, else from Os Copy/Paste Buffer, at most once"""

        self.fill_if()

        iobytes = self.iobytes
        decode = iobytes.decode(errors="surrogateescape")

        return decode

        # maybe empty  # maybe enclosed in Blanks

    def read_bytes(self) -> bytes:
        """Read Bytes from Stdin, else from Os Copy/Paste Buffer, at most once"""

        self.fill_if()

        iobytes = self.iobytes

        return iobytes

        # maybe empty  # maybe enclosed in Blanks

    def fill_if(self) -> None:
        """Read Bytes from Stdin, else from Os Copy/Paste Buffer, at most once"""

        assert AppPathname == "__pycache__/p.pbpaste"
        app_path = pathlib.Path(AppPathname)

        assert not self.drained, (self.drained,)
        if self.filled:
            return

        # Fill from somewhere, always

        if not sys.stdin.isatty():
            self.tprint("fill_from_stdin")
            self.fill_from_stdin()
        elif GotOsCopyPasteClipboardBuffer:
            self.tprint("fill_from_clipboard")
            self.fill_from_clipboard()
        elif app_path.exists():
            self.tprint("fill from", app_path)
            self.filled = True
            self.iobytes = app_path.read_bytes()
        else:
            self.tprint("fill from Jabberwocky")
            self.filled = True
            self.iobytes = Jabberwocky.encode()  # fills from Source, if need be

        # .errors .returncode .shell .stdin unlike:  iobytes = os.popen(shline).read().encode()

    def fill_from_stdin(self) -> None:
        """Read Bytes from Stdin"""

        assert (not self.filled) and (not self.drained), (self.filled, self.drained)
        self.filled = True

        path = pathlib.Path("/dev/stdin")  # todo: solve for Windows too
        read_bytes = path.read_bytes()  # maybe not UTF-8 Encoded

        self.iobytes = read_bytes  # replaces

    def fill_from_clipboard(self) -> None:
        """Read Bytes from Clipboard"""

        assert (not self.filled) and (not self.drained), (self.filled, self.drained)
        self.filled = True

        shline = "pbpaste"  # macOS convention, often not distributed at Linuxes
        argv = shlex.split(shline)

        run = subprocess.run(
            argv,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=None,
            check=True,
        )

        stdout_bytes = run.stdout

        self.iobytes = stdout_bytes  # replaces

    #
    # Pump Bytes out
    #

    def write_splitlines(self, texts: list[str]) -> None:
        """Write Lines into Bytes, and do close the last Line, but don't drain the Bytes yet"""

        assert (not self.filled) and (not self.drained), (self.filled, self.drained)
        self.filled = True

        join = "\n".join(texts)
        join_plus = (join + "\n") if join else ""

        encode = join_plus.encode(errors="surrogateescape")
        self.iobytes = encode  # replaces

    def write_text(self, text: str) -> None:
        """Write Chars into Bytes, and don't drain them yet"""

        assert (not self.filled) and (not self.drained), (self.filled, self.drained)
        self.filled = True

        encode = text.encode(errors="surrogateescape")
        self.iobytes = encode  # replaces

        # may write zero Chars  # may write Chars enclosed in Blanks

        # standard .write sends back a count of Chars written
        # standard .writelines adds no Line-Break's to end the Lines

    def write_bytes(self, data: bytes) -> None:
        """Write Chars into Bytes, and don't drain them yet"""

        assert (not self.filled) and (not self.drained), (self.filled, self.drained)
        self.filled = True

        self.iobytes = data  # replaces

        # may write zero Bytes  # may write enclosed in Blanks  # might not end with Line-Break

        # standard .write forces the Def to count the Chars
        # standard .writelines forces the Caller to choose each Line-Break

    def drain_if(self) -> None:
        """Write Bytes to Stdout, else to the Os Copy/Paste Buffer, else nowhere, at most once"""

        assert self.filled, (self.filled,)
        if self.drained:
            return

        self.drain()

    def drain(self) -> pathlib.Path:
        """Write Bytes to Stdout, else to the Os Copy/Paste Buffer, else nowhere"""

        iobytes = self.iobytes

        # Write Bytes to Pid Path and App Path

        app_path = self.write_to_path_etc(iobytes)

        # Drain if possible

        if not sys.stdout.isatty():
            self.tprint("drain_to_stdout")
            self.drain_to_stdout()
        elif GotOsCopyPasteClipboardBuffer:
            self.tprint("drain_to_clipboard")  # , iobytes)
            self.drain_to_clipboard()
        else:
            self.tprint("drain to nowhere")
            self.drained = True

        return app_path

    def write_to_path_etc(self, iobytes: bytes) -> pathlib.Path:
        """Write Bytes to Pid Path and then App Path and then return App Path"""

        assert AppPathname == "__pycache__/p.pbpaste"
        app_path = pathlib.Path(AppPathname)
        pid_path = pathlib.Path(PidPathname)  # adds next revision of Paste Buffer

        # Retain one File of Output per XShVerb Process Id

        self.tprint("write shadow copy to", pid_path)
        pid_path.parent.mkdir(exist_ok=True)  # implicit .parents=False
        pid_path.write_bytes(iobytes)

        # Push a File into the next XShVerb Process  # todo: same Date/Time Stamp as Pid Path

        self.tprint("write shadow copy to", app_path)
        app_path.parent.mkdir(exist_ok=True)  # implicit .parents=False
        app_path.write_bytes(iobytes)  # traces Date/ Time/ Bytes of PbCopy

        return app_path

    def drain_to_stdout(self) -> None:
        """Write Bytes to Stdout"""

        iobytes = self.iobytes

        assert self.filled and (not self.drained), (self.filled, self.drained)
        self.drained = True

        fd = sys.stdout.fileno()
        data = iobytes  # maybe not UTF-8 Encoded

        assert int(0x80 + signal.SIGPIPE) == 141  # 'mypy --strict' needs the int() here
        try:
            os.write(fd, data)
        except BrokenPipeError:
            sys.exit(141)  # 0x80 + signal.SIGPIPE

            # tested by:  set -o pipefail && seq 123456 |pq |head -1; echo + exit $?
            # else:  BrokenPipeError: [Errno 32] Broken pipe

    def drain_to_clipboard(self) -> None:
        """Write Bytes to Clipboard"""

        iobytes = self.iobytes

        assert self.filled and (not self.drained), (self.filled, self.drained)
        self.drained = True

        shline = "pbcopy"  # macOS convention, often not distributed at Linuxes
        argv = shlex.split(shline)
        subprocess.run(argv, input=iobytes, stdout=subprocess.PIPE, stderr=None, check=True)

    #
    # Print to Stderr, or don't
    #

    def tprint(self, *args: object) -> None:
        """Print to Stderr, or don't"""

        text = " ".join(str(_) for _ in args)  # always does test if printable enough

        if False:  # prints, or doesn't print
            print(text, file=sys.stderr)


#
# Do nothing much,
# like to hold the place of the main Func of a Shell Pump
#


def do_pass(argv: list[str]) -> None:
    """Do nothing much"""

    pass


#
# Do work like much of Awk's work, but with more flair
#


AWK_DOC = r"""

    usage: awk [-F ISEP] [-vOFS OSEP] [NUMBER ...]

    pick one or more columns of words, and drop the rest

    positional arguments:
      NUMBER              the Number of a Column to copy out, or 0 to copy them all (default: -1)

    options:
      -F, --isep ISEP     input word separator (default: Blanks)
      -vOFS, --osep OSEP  output word separator (default: Double Space)

    comparable to:
      |awk -vOFS='  ' '{ print $1, $5, $(NF+1-1) }'  # |a 1 5 -1

    like to classic Awk:
      applies Python Str Split Rules to separate the Words

    unlike classic Awk:
      default to Double Space, not Single Space, as its Output Sep
      takes negative Numbers as counting back from the end, not ahead from the start
      takes 0 as meaning all the Words joined by Output Sep, not a copy of the Input Line
      accepts arbitrary Chars as Seps, even $'\n' $'\x00' etc
      rejects Float Literals, doesn't round to Int, not even 0.123 to 0
      rejects misspellings of -vOFS=, after autocorrecting -vO= or -vOF=
      doesn't accept Gnu Awk --field-separator=ISEP nor --assign OFS=OSEP
      doesn't write out trailing Output Seps when trailing Columns missing or empty

    examples:
      alias a= && unalias a && function a() { ls -l |pbcopy && bin/a "$@" && pbpaste; }
      a  # implicitly drops all but the last Column
      a -1  # same deal, but more explicitly
      a 1  # similar deal, but keep only the first Column
      a 1 5 -1  # keep only the 1st, 5th, and last Column
      echo $PATH |a -F:  # show only the last Dir in the Shell Path
      echo $PATH |a -F: -vOFS=$'\n' 0  # show 1 Dir per Line, as if |tr : '\n'
      echo 'a1 a2\tb1 b2\tc1 c2' |a -F$'\t' -vOFS=$'\t' 3 1  # Tabs in and Tabs out

"""

_STALE_AWK_DOC = """

    positional arguments:
      NUMBER                the Number of a Column to copy out, or 0 to copy them all (default: -1)

    options:
      -F ISEP, --isep ISEP  input word separator (default: Blanks)
      -vOFS OSEP, --osep OSEP
                            output word separator (default: Double Space)

    comparable to:

"""


# todo: |awk --tsv to abbreviate |awk -F$'\t' -vOFS=$'\t'


def do_awk(argv: list[str]) -> None:
    """Pick some columns of words, and drop the rest"""

    # Form Shell Args Parser

    assert argparse.ZERO_OR_MORE == "*"

    stale_awk_doc = _STALE_AWK_DOC
    stale_start = stale_awk_doc.index("positional arguments")
    stale_end = stale_awk_doc.index("comparable to")
    stale = stale_awk_doc[stale_start:stale_end]

    doc = AWK_DOC
    fresh_start = doc.index("positional arguments")
    fresh_end = doc.index("comparable to")
    if sys.version_info < (3, 13):
        doc = doc[:fresh_start] + stale + doc[fresh_end:]

    number_help = "the Number of a Column to copy out, or 0 to copy them all (default: -1)"
    isep_help = "input word separator (default: Blanks)"
    osep_help = "output word separator (default: Double Space)"

    parser = ArgDocParser(doc, add_help=False)
    parser.add_argument(dest="numbers", metavar="NUMBER", nargs="*", help=number_help)
    parser.add_argument("-F", "--isep", metavar="ISEP", help=isep_help)
    parser.add_argument("-vOFS", "--osep", metavar="OSEP", help=osep_help)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    ns = parser.parse_args_if(args)  # often prints help & exits zero

    isep = None if (ns.isep is None) else ns.isep
    osep = "  " if (ns.osep is None) else ns.osep

    numbers = list(int(_, base=0) for _ in ns.numbers)  # rejects Floats
    if not numbers:
        numbers = [-1]

    # Pick one or more Columns of Words, and drop the rest

    olines = list()
    ilines = alt.stdin.read_splitlines()

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

        while owords and not owords[-1]:
            owords.pop()

        ojoin = osep.join(owords)
        olines.append(ojoin)

    alt.stdout.write_splitlines(olines)


#
# To cat is to explicitly substitute the Terminal for the Os Copy/Paste Buffer
#


CAT_DOC = """

    usage: cat [-]

    read with prompt from the Terminal, or write to the Terminal

    positional arguments:
      -  explicitly mention the Terminal, in place of a Pathname

    comparable to:
      echo Press ⌃D or ⌃C; cat - |...
      ...|cat -

    unlike classic Cat and Tee:
      doesn't take Pathnames as Positional Arguments, doesn't define many Options

    examples:
      c  # fill your Os Copy/Paste Buffer
      c  a  c  # type your own Lines to chop down to their last Word
      ls -l |a  c  # see what |a would shove into the Os Copy/Paste Buffer, without shoving it

"""


def do_cat(argv: list[str]) -> None:
    """Read with prompt from the Terminal, or write to the Terminal"""

    assert argparse.OPTIONAL == "?"

    # Form Shell Args Parser

    doc = CAT_DOC
    ifile_help = "explicitly mention the Terminal, in place of a Pathname"

    parser = ArgDocParser(doc, add_help=False)
    parser.add_argument("ifile", metavar="-", nargs="?", help=ifile_help)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    ns = parser.parse_args_if(args)  # often prints help & exits zero

    if ns.ifile is not None:
        if ns.ifile != "-":
            parser.parser.print_usage()
            sys.exit(2)  # exits 2 for bad Arg

    # Read from Stdin Tty into start of Pipe

    sys_stdin_isatty = sys.stdin.isatty()

    filled_from_tty = False
    if alt.index == 0:
        assert not alt.stdin.filled, (alt.stdin.filled,)

        if not sys_stdin_isatty:
            alt.stdin.fill_from_stdin()
        else:
            filled_from_tty = True

            eprint(
                "Start typing"
                + ". Press Return after each Line"
                + ". Press ⌃D to continue, or ⌃C to quit"
            )
            alt.stdin.fill_from_stdin()  # todo: test TTY EOF after Chars without Line-Break
            eprint("")

    # Write the Lines, maybe with enclosing Blanks, but closed

    splitlines = alt.stdin.read_splitlines()
    alt.stdout.write_splitlines(splitlines)

    # Drain end of Pipe to Stdout Tty (don't default that to Stdout Pipe or Os Copy/Paste Buffer)

    if not filled_from_tty:
        if alt.rindex == -1:
            alt.stdout.drain_to_stdout()


#
# Count or drop duplicate Lines, no sort required
#


COUNTER_DOC = """

    usage: counter [-k]

    count or drop duplicate Lines, no sort required

    options:
      -k, --keys  print each distinct Line when it first arrives, without a count (default: False)

    comparable to:
      |awk '!d[$0]++'  # drop duplicates
      |awk '{d[$_]++}END{for(k in d){print d[k],k}}'  # count duplicates

    examples:
      ls -l |i  u  # counts each Word, prints Lines of Count Tab Text
      ls -l |i  counter --keys  c  # prints each Word once
      ls -l |i  dict  c  # same as '|counter --keys', but by way of the Python Datatypes Namespace

"""

# todo: |counter --tsv to write Tab as O Sep
# todo: abbreviate as |i co -k, as |i cou -k, etc


def do_counter(argv: list[str]) -> None:
    """Count or drop duplicate Lines, no sort required"""

    # Form Shell Args Parser

    doc = COUNTER_DOC
    keys_help = "print each distinct Line when it first arrives, without a count (default: False)"

    parser = ArgDocParser(doc, add_help=False)
    parser.add_argument("-k", "--keys", action="count", help=keys_help)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    ns = parser.parse_args_if(args)  # often prints help & exits zero

    # Count or drop duplicate Lines, no sort required

    ilines = alt.stdin.read_splitlines()
    counter = collections.Counter(ilines)

    if ns.keys:
        olines = list(counter.keys())
    else:
        olines = list(f"{v:6}  {k}" for k, v in counter.items())

        # f"{v:6}\t{k}" with \t sometimes troublesome was the classic '|cat -n' format

    alt.stdout.write_splitlines(olines)


#
# Drop blank Columns on the left
#


DEDENT_DOC = r"""

    usage: dedent

    drop blank Columns on the left

    comparable to:
      |pq expand
      |pq strip

    quirks:
      doesn't drop trailing Blanks in each Line
      doesn't drop leading and trailing Blank Lines

    examples:
      ls -l |pq dent |pq dedent |cat -
      printf '\n\n      a3 a4 a5 \n   b2 b3       \n\n\n' |pq dedent  |cat -etv  # lots stripped

"""


def do_dedent(argv: list[str]) -> None:
    """Drop blank Columns on the left"""

    # Form Shell Args Parser

    doc = DEDENT_DOC
    parser = ArgDocParser(doc, add_help=False)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    parser.parse_args_if(args)  # often prints help & exits zero

    # Drop the enclosing Blanks, and replace other troublesome character encodings

    itext = alt.stdin.read_text()
    otext = textwrap.dedent(itext)
    alt.stdout.write_text(otext)


#
# Insert 4 leading Blanks in each Line
#


DENT_DOC = r"""

    usage: dent

    insert 4 leading Blanks in each Line

    comparable to:
      |sed 's,,^    ,'

    quirks:
      doesn't drop leading Blank Lines

    examples:
      ls -l |pq dent dent |cat -
      ls -l |pq dent dent |pq dedent  |cat -
      printf '\n\n      a3 a4 a5 \n   b2 b3       \n\n\n' |pq dent  |cat -etv  # dented

"""


def do_dent(argv: list[str]) -> None:
    """Insert 4 leading Blanks in each Line"""

    # Form Shell Args Parser

    doc = DENT_DOC
    parser = ArgDocParser(doc, add_help=False)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    parser.parse_args_if(args)  # often prints help & exits zero

    # Insert 4 leading Blanks in each Line

    dent = 4 * " "

    ilines = alt.stdin.read_splitlines()
    olines = list((dent + _) for _ in ilines)
    alt.stdout.write_splitlines(olines)


#
# Diff two texts
#


DIFF_DOC = r"""

    usage: diff [A] [B]

    compare and contrast two texts

    positional arguments:
      A  the earlier file (default: a)
      B  the later file (default: b)

    comparable to:
      diff -brpu A B

    examples:
      d  # diff -brpu a b
      d y  # diff -brpu a y
      d x y  # diff -brpu x y

"""


def do_diff(argv: list[str]) -> None:
    """Compare and contrast two texts"""

    assert argparse.OPTIONAL == "?"

    # Form Shell Args Parser

    doc = DIFF_DOC
    a_help = "the earlier file (default: a)"
    b_help = "the later file (default: b)"
    parser = ArgDocParser(doc, add_help=False)
    parser.add_argument(dest="a", metavar="A", nargs="?", help=a_help)
    parser.add_argument(dest="b", metavar="B", nargs="?", help=b_help)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    ns = parser.parse_args_if(args)  # often prints help & exits zero

    if ns.a is None:
        assert ns.b is None, (ns.b,)
        (a, b) = ("a", "b")
    elif ns.b is None:
        (a, b) = ("a", ns.a)
    else:
        (a, b) = (ns.a, ns.b)

    # Do the Diff & exit

    shargv = ["diff", "-brpu", a, b]
    shline = " ".join(shlex.quote(_) for _ in shargv)
    eprint("+", shline)

    run = subprocess.run(shargv, stdin=None)
    returncode = run.returncode

    alt.stdout.fill_and_drain()  # leaves Pipe and Os Copy/Paste Buffer alone
    if returncode:
        sys.exit(returncode)  # silently exits nonzero after Diff exits nonzero


#
# Search out Code to match the Text and run the Code to tweak the Text
#


DOT_DOC = r"""

    usage: pq [HINT]

    search out Code to match the Text and run the Code to tweak the Text

    positional arguments:
      HINT  one of codereviews|google|jenkins|jira|wiki, else toggle address|title, else fail

    quirks:
      takes '.' as Hint to mean whatever one Hint works

    conversions:
      as |pq . codereviews
        to http://codereviews/r/123456/diff of ReviewBoard
          from https://codereviews.example.com/r/123456/diff/8/#index_header
      as |pq . google
        to https://docs.google.com/document/d/$HASH
          from https://docs.google.com/document/d/$HASH/edit?usp=sharing
          from https://docs.google.com/document/d/$HASH/edit#gid=0'
      as |pq . wiki
        to https://wiki.example.com/pages/viewpage.action?pageId=12345
          from https://wiki.example.com/pages/viewpreviousversions.action?pageId=12345

    toggles:
      as pq . jenkins
        between http://AbcJenkins
          and https://abcjenkins.dev.example.com
      as pq . jira
        between PROJ-12345
          and https://jira.example.com/browse/PROJ-12345
      as pq . address and pq . title
        between https :// twitter . com /intent/tweet?text=/@PELaVarre+XShVerb
          and https://twitter.com/intent/tweet?text=/@PELaVarre+XShVerb

    quirks:
      '|pq . title' is unrelated to '|pq title'

    examples:
      pq .
      pq dot chill

"""


def do_dot(argv: list[str]) -> None:
    """Search out Code to match the Text and run the Code to tweak the Text"""

    assert argparse.OPTIONAL == "?"

    # Form Shell Args Parser

    doc = DOT_DOC
    hint_help = "one of codereviews|google|jenkins|jira|wiki, else toggle address|title, else fail"

    parser = ArgDocParser(doc, add_help=False)
    # parser.add_argument(arg="HINT", nargs="?", help=hint_help)  # FIXME
    parser.add_argument("hint", metavar="HINT", nargs="?", help=hint_help)

    # Name the bits of Code near here

    func_by_hint = dict(
        address=dot_address,
        codereviews=dot_codereviews,
        google=dot_google,
        jenkins=dot_jenkins,
        jira=dot_jira,
        title=dot_title,
        wiki=dot_wiki,
    )

    func_hints = list(func_by_hint.keys())

    wave1 = ["codereviews", "google", "jenkins", "jira", "wiki"]
    wave2 = ["address", "title"]
    waves = [wave1, wave2]

    waves_hints = sorted(set(_ for wave in waves for _ in wave))
    assert func_hints == waves_hints, (func_hints, waves_hints)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    ns = parser.parse_args_if(args)  # often prints help & exits zero

    if ns.hint is not None:
        if ns.hint not in func_hints:
            parser.parser.print_usage()
            eprint(f"|pq dot {ns.hint!r}: no such Shell Pipe Dot Filter yet")
            sys.exit(2)  # exits 2 for bad Args

    # Search for Code to match the Text

    splitlines = alt.stdin.read_splitlines()

    n = len(splitlines)
    if n != 1:
        eprint(f"|pq dot: our Codes need 1 Line of Text, got {n}")
        sys.exit(1)  # exits 1 for bad Data

    iline = splitlines[0]

    oline = ""
    ohints = list()
    for wave in waves:
        for hint in wave:
            if (ns.hint is None) or (ns.hint == hint):
                func = func_by_hint[hint]

                try:
                    hint_oline = func(iline)
                except Exception:
                    hint_oline = ""

                if hint_oline:
                    ohints.append(hint)
                    oline = hint_oline  # replaces

        if ohints:
            break

    ohints.sort()

    # Require exactly one Code found

    if not ohints:
        if ns.hint is not None:
            eprint(f"|pq dot {ns.hint!r}: doesn't fit {iline!r}")
            sys.exit(1)  # exits 1 for no Code found by bad Data
        else:
            eprint(f"|pq dot: none of our Codes fits {iline!r}")
            sys.exit(1)  # exits 1 for no Code found by bad Data

    if len(ohints) > 1:
        eprint(f"|pq dot: data fits multiple Codes {ohints!r}")
        sys.exit(1)  # exits 1 for multiple Codes found by bad Data

    # Succeed

    alt.stdout.write_splitlines([oline])


def dot_address(text: str) -> str:
    """Drop Spaces to heat up a chilled Web Address Title"""

    assert " " in text, (text,)

    replace = text.replace(" ", "")
    return replace

    # to https://twitter.com/intent/tweet?text=/@PELaVarre+XShVerb
    # from https :// twitter . com /intent/tweet?text=/@PELaVarre+XShVerb


def dot_codereviews(text: str) -> str:
    """Mention the Diff enclosing a more detailed Web Address"""

    assert re.match(r"http.*codereviews[./]", string=text)

    urlsplits = urllib.parse.urlsplit(text)
    m = re.match(r"^/r/([0-9]+)", string=urlsplits.path)  # discards end of path
    assert m, (m, urlsplits.path)

    r = int(m.group(1))

    osplits = urllib.parse.SplitResult(
        scheme="http",  # not "https"
        netloc=urlsplits.netloc.split(".")[0],  # "codereviews"
        path=f"/r/{r}/diff",
        query="",
        fragment="",
    )

    geturl = osplits.geturl()
    return geturl

    # to http://codereviews/r/123456/diff
    # from https://codereviews.example.com/r/123456/diff/8/#index_header


def dot_google(text: str) -> str:
    """More simply mention the Google Drive File involved in a detailed Web Address"""

    assert re.match(r"http.*[.]google.com/", string=text)
    assert ("/edit" in text) or ("/view" in text)

    urlsplits = urllib.parse.urlsplit(text)

    opath = urlsplits.path
    opath = opath.removesuffix("/edit")
    opath = opath.removesuffix("/view")

    osplits = urllib.parse.SplitResult(
        scheme=urlsplits.scheme,
        netloc=urlsplits.netloc,
        path=opath,
        query="",
        fragment="",
    )

    geturl = osplits.geturl()
    return geturl

    # to https://docs.google.com/document/d/$HASH
    # from https://docs.google.com/document/d/$HASH/edit?usp=sharing
    # from https://docs.google.com/document/d/$HASH/edit#gid=0'


def dot_jenkins(text: str) -> str:
    """Toggle between the Jenkins Title and the Jenkins Web Address"""

    m1 = re.match(r"^http.*jenkins[0-9]*[.]", string=text)
    m2 = re.search(r"[jJ]enkins[0-9]*/", string=text)
    assert m1 or m2, (m1, m2)

    if m1:
        return dot_jenkins_thin(text)

    return dot_jenkins_wide(text)


def dot_jenkins_thin(text: str) -> str:
    """Convert to the more brief Http Jenkins Web Address from the detailed HttpS"""

    urlsplits = urllib.parse.urlsplit(text)
    urlsplits = urlsplits._replace(scheme="http")
    urlsplits = urlsplits._replace(path=urlsplits.path.rstrip("/") + "/")

    netloc = urlsplits.netloc.split(".")[0]
    netloc = string.capwords(netloc).replace("jenkins", "Jenkins")
    urlsplits = urlsplits._replace(netloc=netloc)

    geturl = urlsplits.geturl()
    return geturl

    # to http://AbcJenkins
    # from https://abcjenkins.dev.example.com

    # todo: prefer str.title over string.capwords, maybe


def dot_jenkins_wide(text: str) -> str:
    """Convert to the more precise HttpS Jenkins Web Address from the Http"""

    fqdn = socket.getfqdn()
    dn = fqdn.partition(".")[-1]  # 'Domain Name of HostName'
    dn = dn or "example.com"

    urlsplits = urllib.parse.urlsplit(text)
    urlsplits = urlsplits._replace(scheme="https")
    urlsplits = urlsplits._replace(path=urlsplits.path.rstrip("/"))

    urlsplits = urlsplits._replace(netloc=f"{urlsplits.netloc.casefold()}.dev.{dn}")

    geturl = urlsplits.geturl()
    return geturl


def dot_jira(text: str) -> str:
    """Toggle between the Jira Title and the Jira Web Address"""

    m1 = re.match(r"^http.*jira.*/browse/.*$", string=text)
    m2 = re.match(r"^[A-Z]+[-][0-9]+$", string=text)
    assert m1 or m2, (m1, m2)

    if m1:
        return dot_jira_title(text)

    return dot_jira_address(text)


def dot_jira_address(text: str) -> str:
    """Convert to the Jira Web Address from the Jira Key"""

    fqdn = socket.getfqdn()
    dn = fqdn.partition(".")[-1]  # 'Domain Name of HostName'
    dn = dn or "example.com"

    _ = urllib.parse.urlsplit(text)

    osplits = urllib.parse.SplitResult(
        scheme="https",
        netloc=f"jira.{dn}",
        path=f"/browse/{text}",
        query="",
        fragment="",
    )

    geturl = osplits.geturl()
    return geturl

    # to https://jira.example.com/browse/PROJ-12345
    # from PROJ-12345


def dot_jira_title(text: str) -> str:
    """Convert to the Jira Key from the Jira Web Address"""

    urlsplits = urllib.parse.urlsplit(text)
    path = urlsplits.path

    assert path.startswith("/browse/"), (path,)
    jira_key = path.removeprefix("/browse/")

    return jira_key

    # to PROJ-12345
    # from https://jira.example.com/browse/PROJ-12345


def dot_title(text: str) -> str:
    """Insert Spaces to chill a hot-link'able Web Address HRef"""

    assert " " not in text, (text,)

    assert text.startswith("http"), (text,)  # 'https', 'http', etc

    address = text
    address = address.replace("/x.com/", "/twitter.com/")

    splits = address.split("/")
    assert splits[1] == "", (splits[1], splits, address)
    chilled = (
        splits[0].removesuffix(":")
        + " :// "
        + splits[2].replace(".", " . ")
        + " /"
        + "/".join(splits[3:])
    )

    return chilled

    # to https :// twitter . com /intent/tweet?text=/@PELaVarre+XShVerb
    # from https://twitter.com/intent/tweet?text=/@PELaVarre+XShVerb


def dot_wiki(text: str) -> str:
    """Mention the Page by Id of a Page-History Web-Address"""

    urlsplits = urllib.parse.urlsplit(text)
    assert urlsplits.path == "/pages/viewpreviousversions.action"
    osplits = urlsplits._replace(path="/pages/viewpage.action")

    geturl = osplits.geturl()
    return geturl


#
# Do the thing, but show its date/time and pass/fail details
#


DT_DOC = r"""

    usage: dt [WORD ...]

    do the thing, but show its date/time and pass/fail details

    positional arguments:
      WORD  a word of command: first the shell verb, and then its options and args

    comparable to:
      date && time ...; echo + exit $?

    quirks:
      shows absolute date/time, elapsed date/time, and process exit status returncode
      shows the whole second in the California Pacific Time Zone, and the microsecond in UTC
      exits nonzero when the Shell Command exits nonzero

    examples:
      dt  # shows when now is, and says nothing more
      dt sleep 0.123  # show how much slower observed time can be
      dt make requirements.txt  # show how fast a particular thing runs

"""


def do_dt(argv: list[str]) -> None:
    """Do the thing, but show its date/time and pass/fail details"""

    assert argparse.ZERO_OR_MORE == "*"

    # Form Shell Args Parser

    doc = DT_DOC
    word_help = "a word of command: first the shell verb, and then its options and args"
    parser = ArgDocParser(doc, add_help=False)
    parser.add_argument(dest="words", metavar="WORD", nargs="*", help=word_help)

    # Take up Shell Args

    args = argv[1:]
    if not argv[1:]:
        args = ["--", "true"]  # not as precise as '/usr/bin/true'
    else:
        if not argv[1].startswith("-"):
            args = ["--"] + argv[1:]

    ns = parser.parse_args_if(args)  # often prints help & exits zero

    # Do the thing, but show its date/time and pass/fail details

    t0 = dt.datetime.now(UTC)  # 2025-06-01 10:26:51 -0700  (2025-06-01 17:26:51.743258)
    s0a = t0.astimezone(Pacific).strftime("%Y-%m-%d %H:%M:%S %z")
    s0b = t0.strftime("%Y-%m-%d %H:%M:%S.%f")

    if not argv[1:]:
        assert ns.words == ["true"], (ns.words,)

        eprint(f"{s0a}  ({s0b})")

        sys.exit(0)  # exits 0 after printing Date/Time

    eprint(f"{s0a}  ({s0b})  enter")

    shargv = ns.words
    shline = " ".join(shlex.quote(_) for _ in shargv)
    eprint("+", shline)

    run = subprocess.run(shargv, stdin=None)
    returncode = run.returncode
    eprint(f"+ exit {returncode}")  # printed even when zero

    t1 = dt.datetime.now(UTC)
    s1a = t1.astimezone(Pacific).strftime("%Y-%m-%d %H:%M:%S %z")
    s1b = t1.strftime("%Y-%m-%d %H:%M:%S.%f")
    eprint(f"{s1a}  ({s1b})  exit")

    t1t0 = t1 - t0
    eprint(dt_timedelta_strftime(t1t0))  # '9ms331us' to mean 9ms 331us <= t < 9ms 333us

    sys.exit(returncode)  # exits after Dating & Timing 1 Shell Command Line


#
# Call up Emacs inside the Terminal with no Menu Bar and no Splash
#


EMACS_DOC = r"""

    usage: e [WORD ...]

    call up Emacs inside the Terminal with no Menu Bar and no Splash

    positional arguments:
      WORD  a word of command: options and args of Emacs

    comparable to:
      emacs -nw --no-splash --eval '(menu-bar-mode -1)' ...

    quirks:
      tells Emacs to edit the Shell Pipe or Os Copy/Paste Buffer only when you give no Pos Args

    examples:
      e  # edits the Os Copy/Paste Buffer
      echo |e |sh  # edit a Shell Command and then run it

"""


def do_emacs(argv: list[str]) -> None:
    """Call up Emacs inside the Terminal with no Menu Bar and no Splash"""

    assert argparse.ZERO_OR_MORE == "*"

    # Form Shell Args Parser

    doc = EMACS_DOC
    word_help = "a word of command: options and args of Emacs"
    parser = ArgDocParser(doc, add_help=False)
    parser.add_argument(dest="words", metavar="WORD", nargs="*", help=word_help)

    # Take up Shell Args

    args = ["--"] + argv[1:]  # quotes them all, to forward onto Emacs unchanged
    parser.parse_args_if(args)  # often prints help & exits zero

    # Call up Emacs inside the Terminal with no Menu Bar and no Splash

    shverb = "emacs" if shutil.which("emacs") else "/opt/homebrew/bin/emacs"
    starts = shlex.split("-nw --no-splash --eval '(menu-bar-mode -1)'")

    _do_edit(argv, shverb=shverb, starts=starts)


def _do_edit(argv: list[str], shverb: str, starts: list[str]) -> None:
    """Call up a Text Editor for Pos Args, else to edit the Shell Pipe or Os Copy/Paste Buffer"""

    argv_tails = argv[1:]

    # Drain early into a LocalHost GetCwd File, if need be

    drain_path = pathlib.Path()
    drain_pathname = ""

    if (not argv_tails) or all(_.startswith("-") for _ in argv_tails):
        alt.stdin.fill_if()
        if not sys.stdout.isatty():
            drain_path = alt.stdin.write_to_path_etc(iobytes=alt.stdin.iobytes)
        else:
            drain_path = alt.stdin.drain()

            # todo: do touch but don't rewrite the PbPaste Buffer before an Edit of its Bytes

        drain_pathname = drain_path.name
        assert drain_pathname, (drain_pathname, drain_path)

    # Trace and do work

    shargv = [shverb] + starts + argv_tails
    if drain_pathname:
        shargv.append(drain_pathname)

    shline = " ".join(shlex.quote(_) for _ in shargv)
    eprint("+", shline)

    with open("/dev/tty", "rb") as notapipe_in:
        with open("/dev/tty", "wb") as notapipe_out:
            run = subprocess.run(shargv, stdin=notapipe_in, stdout=notapipe_out)

            # todo: what works better with stdin=None when sys.stdin.isatty() ?
            # todo: what works better with stdout=None when sys.stdout.isatty() ?

    returncode = run.returncode
    if returncode:
        eprint(f"+ exit {returncode}")
        sys.exit(returncode)  # doesn't drain, when exiting sad after Editing

    # Don't drain at exist, unless already drained early

    if not drain_pathname:
        alt.stdout.fill_and_drain()  # leaves Pipe and Os Copy/Paste Buffer alone
    else:
        obytes = drain_path.read_bytes()  # don't implicitly textify after edit
        alt.stdout.write_bytes(obytes)

        # todo: do touch but don't rewrite the AppPathname after an Edit of its Bytes


#
# Drop the enclosing Blanks, and replace other troublesome character encodings
#


EXPAND_DOC = r"""

    usage: expand

    drop the enclosing Blanks, and replace other troublesome character encodings

    comparable to:
      |expand |sed $'s,\xC2\xA0,\&nsbp;,g'

    quirks:
      not pushed by us as '|expand' because many macOS & Linux Shells define '|expand' narrowly

    examples:
      echo $'\xC2\xA0 « » “ ’ ” – — ′ ″ ‴ ' |pq expand |cat -
      echo $'\xC2\xA0 \xC2\xA0' |sed 's,\xC2\xA0,\&nsbp;,g'
      printf '\n\n      a3 a4 a5 \n   b2 b3       \n\n\n' |pq expand  |cat -etv  # most stripped

"""

# todo: better example for contrast with 'most stripped' here


def do_expand(argv: list[str]) -> None:  # do_expandtabs
    """Drop the enclosing Blanks, and replace other troublesome character encodings"""

    # Form Shell Args Parser

    doc = EXPAND_DOC
    parser = ArgDocParser(doc, add_help=False)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    parser.parse_args_if(args)  # often prints help & exits zero

    # Drop the enclosing Blanks, and replace other troublesome character encodings

    itext = alt.stdin.read_text()
    otext = str_expand_plus(itext)
    alt.stdout.write_text(otext)


def str_expand_plus(text: str) -> str:
    """Drop the enclosing Blanks, and replace other troublesome character encodings"""

    ud = unicodedata

    d = {
        "\f": "<hr>",  # U+000C \f
        ud.lookup("No-Break Space"): "&nbsp;",  # U+00A0 \xA0  # vs Apple ⌥Space
        ud.lookup("Left-Pointing Double Angle Quotation Mark"): "<<",  # U+00AB «  # vs Microsoft
        ud.lookup("Right-Pointing Double Angle Quotation Mark"): "<<",  # U+00BB »  # vs Microsoft
        ud.lookup("Zero Width Space"): "'",  # U+200B &ZeroWidthSpace;
        ud.lookup("En Dash"): "--",  # U+2013 –  # vs Microsoft
        ud.lookup("Em Dash"): "---",  # U+2014 —  # vs Microsoft
        ud.lookup("Left Single Quotation Mark"): "'",  # U+2018 ‘  # vs Microsoft
        ud.lookup("Right Single Quotation Mark"): "'",  # U+2019 ’  # vs Microsoft
        ud.lookup("Left Double Quotation Mark"): '"',  # U+201C “  # vs Microsoft
        ud.lookup("Right Double Quotation Mark"): '"',  # U+201D ”  # vs Microsoft
        ud.lookup("Horizontal Ellipsis"): "...",  # U+2026 …  # vs Microsoft
        ud.lookup("Prime"): "'",  # U+2032 ′
        ud.lookup("Double Prime"): "''",  # U+2032 ″
        ud.lookup("Triple Prime"): "'''",  # U+2034 ‴
    }

    otext = text
    otext = otext.expandtabs(tabsize=8)
    otext = str_textify(otext)
    for k, v in d.items():
        otext = otext.replace(k, v)

    return otext

    # todo: |expand of Control Chars

    # todo: are we happy leaving « » Angle Quotation Marks in place as U+00AB U+00BB

    # todo: more conformity to PyPi·Org Black SHOUTED UPPER CASE Unicode Names
    # todo: more conformity to PyPi·Org Black fuzz-the-eyes lowercase Hex


#
# Take Lines that match a Pattern
#


GREP_DOC = r"""

    usage: grep [PATTERN ...]

    take Lines that match a Pattern, drop the rest

    positional arguments:
      PATTERN  the text to find, or a Mixed Case Text to find in any Case, or a RegEx of () [] {}

    comparable to:
      |grep -F -i -e .1 -e .2

    quirks:
      takes one or more Patterns, not just one Pattern, without forcing you to spell out '-e '
      takes the Pattern as requiring matching Case only when it contains Mixed Case
      takes the Pattern as a RegEx only when it contains >=1 balanced pairs of () [] {}

    examples:
      ls -l |g FUTU Make '(n$)' |c

"""


def do_grep(argv: list[str]) -> None:  # Generalized Regular Expression Print
    """Take Lines that match a Pattern, drop the rest"""

    assert argparse.ZERO_OR_MORE == "*"

    # Form Shell Args Parser

    doc = GREP_DOC

    pattern_help = (
        "the text to find, or a Mixed Case Text to find in any Case, or a RegEx of () [] {}"
    )

    parser = ArgDocParser(doc, add_help=False)
    parser.add_argument(dest="patterns", metavar="PATTERN", nargs="*", help=pattern_help)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    ns = parser.parse_args_if(args)  # often prints help & exits zero
    patterns = ns.patterns

    # eprint(patterns)

    # Say which Patterns we don't run as Regular Expressions

    def str_is_re_pattern_ish(pattern: str) -> bool:

        try:
            re.compile(pattern)
        except re.PatternError:
            return False

        if "(" not in pattern:
            if "[" not in pattern:
                if "{" not in pattern:
                    return False

        return True

    # Take Lines that match a Pattern, drop the rest

    ilines = alt.stdin.read_splitlines()

    olines = list()
    for iline in ilines:
        for pattern in patterns:

            if str_is_re_pattern_ish(pattern):
                if not re.search(pattern, iline):
                    # eprint(f"re.search {pattern!r} skips:", iline)
                    continue
                # eprint(f"re.search {pattern!r} takes:", iline)

            elif pattern.islower() or pattern.isupper():
                if pattern.casefold() not in iline.casefold():
                    # eprint(f"casefold.in {pattern!r} skips:", iline)
                    continue
                # eprint(f"casefold.in {pattern!r} takes:", iline)

            else:
                if pattern not in iline:
                    # eprint("str.in skips:", iline)
                    continue
                # eprint(f"str.in {pattern!r} takes:", iline)

            olines.append(iline)
            break

            # todo: factor out pattern classification for speed

        # todo: multiline patterns

    alt.stdout.write_splitlines(olines)

    # todo: |grep -n


#
# Take only the first few Lines
#


HEAD_DOC = """

    usage: head [-N]

    take only the first few Lines

    positional arguments:
      -N  how many leading Lines to take (default: 10)

    comparable to:
      |head -N

    future work:
      we could make meaning out of |head - - |tail +++
      we could take the $LINES of the Terminal Window Tab Pane into account

    examples:
      ls -l |i  u  s -nr  h  c  # prints some most common Words
      ls -hlAF -rt |h -3  c  # prints the first 3 Lines

"""


def do_head(argv: list[str]) -> None:
    """Take only the first few Lines"""

    assert argparse.OPTIONAL == "?"

    # Form Shell Args Parser

    doc = HEAD_DOC
    n_help = "how many leading Lines to take (default: 10)"

    parser = ArgDocParser(doc, add_help=False)
    parser.add_argument(dest="n", metavar="-N", nargs="?", help=n_help)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    ns = parser.parse_args_if(args)  # often prints help & exits zero

    n = -10
    if ns.n is not None:
        try:
            n = int(ns.n, base=0)
            if n >= 0:
                raise ValueError(ns.n)
        except ValueError:
            parser.parser.print_usage()
            eprint(f"|head: {ns.n!r}: could be -10 or -3 or -12345, but isn't")
            sys.exit(2)  # exits 2 for bad Arg

    # Take only the first few Lines
    # Write out the taken Lines, maybe with enclosing Blanks, but closed

    ilines = alt.stdin.read_splitlines()
    olines = ilines[:-n]

    alt.stdout.write_splitlines(olines)


#
# Chop output to fit on screen
#


HT_DOC = r"""

    usage: ht

    chop output to fit on screen

    comparable to:
      |awk '{a[NR]=$0} END{print a[1]; print a[2]; print "..."; print a[NR - 1]; print a[NR]}'
      |sed -n -e '1,3p;3,3s/.*/.../p;$p'  # prints only 1 of Tail

    quirks:
      shows 3 Lines of Head, 2 Lines of Tail, and '...' in the middle

    examples:
      seq 99 |pq ht |cat -  # show not much of 99 Lines
      find . |pq ht |cat -  # show not much of many Pathnames that begin with "." Dot or not
      printf '\n\n      a3 a4 a5 \n   b2 b3       \n\n\n' |pq ht  |cat -etv  # no change

"""


def do_ht(argv: list[str]) -> None:
    """Chop output to fit on screen"""

    # Form Shell Args Parser

    doc = HT_DOC
    parser = ArgDocParser(doc, add_help=False)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    parser.parse_args_if(args)  # often prints help & exits zero

    # Write the Lines, maybe with enclosing Blanks, but closed and chopped to fit on screen

    ilines = alt.stdin.read_splitlines()
    n = len(ilines)

    if n < (3 + 3 + 2):
        olines = list(ilines)  # 'copied is better than aliased'
    else:
        olines = ilines[:3] + ["...", f"... 3+2 of {n} Lines shown ...", "..."] + ilines[-2:]

    alt.stdout.write_splitlines(olines)

    # todo: |ht [-B=BEFORE] [-A=AFTER] [-C=BOTH] for more/less above/below
    # todo: |ht when the Output is too wide


#
# Drop the Style out of Json Data
#


JQ_DOC = r"""

    usage: jq

    drop the Style out of Json Data

    comparable to:
      |jq .  # available by default in macOS nowadays
      |python3 -m json.tool --indent=2 --no-ensure-ascii

    quirks:
      promotes the --indent=2 of Json, not the --indent=4 of Python

    examples:
      python3 -c 'import json; print(json.dumps(dict(e=101, é=233)))' >j.json
      cat j.json |j  c

"""

# todo: usage: |j .


def do_jq(argv: list[str]) -> None:
    """Drop the Style out of Json Data"""

    # Form Shell Args Parser

    doc = JQ_DOC
    parser = ArgDocParser(doc, add_help=False)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    parser.parse_args_if(args)  # often prints help & exits zero

    # Drop the Style out of Json Data

    itext = alt.stdin.read_text()
    j = json.loads(itext)
    otext = json.dumps(j, indent=2, ensure_ascii=False) + "\n"

    otext_ = str_textify(otext)  # never need textify to |jq
    assert otext == otext_, (otext, otext_)

    alt.stdout.write_text(otext)  # |jq textified by .json.dumps, we trust and verify


#
# Call up Less inside the Terminal, only if larger than Screen, and don't clear the Screen
#


LESS_DOC = r"""

    usage: k [WORD ...]

    call up Less inside the Terminal, only if larger than Screen, and don't clear the Screen

    positional arguments:
      WORD  a word of command: options and args of Less

    comparable to:
      less -FIRX

    quirks:
      tells Less to show the Shell Pipe or Os Copy/Paste Buffer only when you give no Pos Args
      do make people press ⌃R to search for strings as strings, not as regular expressions
      do make people learn and spell out \< \> to search for whole words

    examples:
      k  # shows the Os Copy/Paste Buffer
      seq 123 |k  # shows a Pipe

"""

# todo: FIXME why doesn't 'seq 123 |k' end by showing as much as:  seq 123 |k >k && cat k


def do_less(argv: list[str]) -> None:
    """Call up Less inside the Terminal, only if larger than Screen, and don't clear the Screen"""

    assert argparse.ZERO_OR_MORE == "*"

    # Form Shell Args Parser

    doc = LESS_DOC
    word_help = "a word of command: options and args of Less"
    parser = ArgDocParser(doc, add_help=False)
    parser.add_argument(dest="words", metavar="WORD", nargs="*", help=word_help)

    # Take up Shell Args

    args = ["--"] + argv[1:]  # quotes them all, to forward onto Emacs unchanged
    parser.parse_args_if(args)  # often prints help & exits zero

    # Call up Less inside the Terminal, only if larger than Screen, and don't clear the Screen

    shverb = "less"
    starts = shlex.split("-FIRX")

    _do_edit(argv, shverb=shverb, starts=starts)


#
# Lower the Case of each Word in each Line
#


LOWER_DOC = r"""

    usage: lower

    lower the Case of each Word in each Line

    examples:
      ls -l |pq lower |cat -

"""


def do_lower(argv: list[str]) -> None:
    """Lower the Case of each Word in each Line"""

    # Form Shell Args Parser

    doc = LOWER_DOC

    parser = ArgDocParser(doc, add_help=False)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    parser.parse_args_if(args)  # often prints help & exits zero

    # Lower the Case of each Word in each Line

    itext = alt.stdin.read_text()
    otext = itext.lower()
    alt.stdout.write_text(otext)


#
# Drop leading Blanks in each Line, or leading Chars of some other Set
#


LSTRIP_DOC = r"""

    usage: lstrip [--charset CHARSET]

    drop leading Blanks in each Line, or leading Chars of some other Set

    options:
      --charset CHARSET  list the Chars to drop if found, preferably in sorted order

    comparable to:
      |sed 's,^  *,,'

    quirks:
      doesn't drop leading Blank Lines

    examples:
      printf '\n\n      a3 a4 a5 \n   b2 b3       \n\n\n' |pq lstrip  |cat -etv  # left stripped

"""


def do_lstrip(argv: list[str]) -> None:
    """Drop leading Blanks in each Line, or leading Chars of some other Set"""

    # Form Shell Args Parser

    doc = LSTRIP_DOC
    charset_help = "list the Chars to drop if found, preferably in sorted order"

    parser = ArgDocParser(doc, add_help=False)
    parser.add_argument("--charset", metavar="CHARSET", help=charset_help)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    ns = parser.parse_args_if(args)  # often prints help & exits zero

    charset = None if (ns.charset is None) else ns.charset  # maybe empty

    # Drop leading Blanks in each Line, or leading Chars of some other Set

    ilines = alt.stdin.read_splitlines()
    olines = list(_.lstrip(charset) for _ in ilines)
    alt.stdout.write_splitlines(olines)


#
# Number the Lines
#


NL_DOC = """

    usage: nl [+N]

    number the Lines, up from one, or up from zero

    positional arguments:
      +N  up from what (default: +1)

    comparable to:
      |nl -v0
      |nl -v1

    examples:
      ls -l |n  c  # number as if by |cat -n |expand
      ls -l |n +0  c  # number as if by |nl -v0 |expand

"""


def do_nl(argv: list[str]) -> None:
    """Number the Lines, up from one, or up from zero"""

    assert argparse.OPTIONAL == "?"

    # Form Shell Args Parser

    doc = NL_DOC
    n_help = "up from what (default: +1)"

    parser = ArgDocParser(doc, add_help=False)
    parser.add_argument(dest="n", metavar="+N", nargs="?", help=n_help)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    ns = parser.parse_args_if(args)  # often prints help & exits zero

    n = 1
    if ns.n is not None:
        try:
            n = int(ns.n, base=0)
            if (n not in [0, 1]) or (ns.n[:1] not in ["-", "+"]):
                raise ValueError(ns.n)
        except ValueError:
            parser.parser.print_usage()
            eprint(f"|nl: {ns.n!r}: could be +0 or +1, but isn't")
            sys.exit(2)  # exits 2 for bad Arg

    # Number the Lines, and drop the trailing Blanks from each Line

    ilines = alt.stdin.read_splitlines()

    olines = list()
    for n_plus_index, iline in enumerate(ilines, start=n):
        oline = f"{n_plus_index:6}  {iline}"
        olines.append(oline)

    alt.stdout.write_splitlines(olines)


#
# Launch a chat with Python
#


PYTHON_DOC = r"""

    usage: python

    launch a chat with Python

    comparable to:
      python3 -i -c '...'

    examples:
      p

"""


def do_python(argv: list[str]) -> None:
    """Launch a chat with Python"""

    # Form Shell Args Parser

    doc = PYTHON_DOC
    parser = ArgDocParser(doc, add_help=False)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    parser.parse_args_if(args)  # often prints help & exits zero

    globals_add_python_import_names()

    # Don't disturb Pipe and Os Copy/Paste Buffer

    alt.stdout.fill_and_drain()

    # Schedule a chat with Python to happen after Return from Def Main

    os.environ["PYTHONINSPECT"] = str(True)


def globals_add_python_import_names() -> None:

    g = globals()
    for name in PYTHON_IMPORTS:
        if name not in g.keys():
            g[name] = LazyImport(name)

    if "D" not in g.keys():
        g["D"] = decimal.Decimal  # todo: lazily do:  from decimal import Decimal as D

    if "dt" not in g.keys():
        dt = LazyImport(import_="datetime", as_="dt")
        g["dt"] = dt

    if "et" not in g.keys():
        et = LazyImport(import_="xml.etree.ElementTree", as_="et")
        g["et"] = et

    if "np" not in g.keys():
        np = LazyImport(import_="numpy", as_="np")
        g["np"] = np

    if "parser" not in g.keys():
        parser = argparse.ArgumentParser()
        g["parser"] = parser

    if "pd" not in g.keys():
        pd = LazyImport(import_="pandas", as_="pd")
        g["pd"] = pd

    if "plt" not in g.keys():
        plt = LazyImport(import_="matplotlib.pyplot", as_="plt")
        g["plt"] = plt

    if "t" not in g.keys():
        g["t"] = PacificLaunch


class LazyImport:
    """Defer the work of "import X as Y" till first Y.Z fetched"""

    def __init__(self, import_: str, as_: str | None = None) -> None:
        self.import_ = import_
        self.as_ = import_ if (as_ is None) else as_

    def __getattribute__(self, name: str) -> object:
        if name in "as_ import_".split():
            return super().__getattribute__(name)
        module = importlib.import_module(self.import_)
        globals()[self.as_] = module
        return module.__getattribute__(name)

    def __repr__(self) -> str:
        module = importlib.import_module(self.import_)
        globals()[self.as_] = module
        return module.__repr__()


_PYTHON_IMPORTS_TEXT = """


    # hard-to-discover basics
    # sorted(_[0] for _  in sys.modules.items() if not hasattr(_[-1], "__file__"))

    __main__

    atexit builtins errno itertools marshal posix pwd sys time


    # from ".so" Shared Object Libraries
    # minus deprecated: audioop nis pyexpat

    array binascii cmath fcntl grp
    math mmap readline resource select syslog termios unicodedata zlib


    # from Py Files
    # minus deprecated: aifc cgi cgitb chunk crypt imghdr
    # minus deprecated: mailcap nntplib pipes sndhdr sunau telnetlib uu uuid xdrlib

    abc antigravity argparse ast asynchat asyncore  base64 bdb bisect bz2
    cProfile calendar cmd code codecs codeop colorsys
        compileall configparser contextlib contextvars copy copyreg csv
    dataclasses datetime decimal difflib dis doctest  enum
    filecmp fileinput fnmatch fractions ftplib functools
    genericpath getopt getpass gettext glob graphlib gzip
    hashlib heapq hmac  imaplib imp inspect io ipaddress  keyword
    linecache locale lzma

    mailbox mimetypes modulefinder
    netrc ntpath nturl2path numbers  opcode operator optparse os
    pathlib pdb pickle pickletools pkgutil platform plistlib poplib posixpath
        pprint profile pstats pty py_compile pyclbr pydoc
    queue quopri  random reprlib rlcompleter runpy
    sched secrets selectors shelve shlex shutil signal site smtpd smtplib socket
        socketserver sre_compile sre_constants sre_parse ssl stat statistics string
        stringprep struct subprocess symtable sysconfig
    tabnanny tarfile tempfile textwrap this threading timeit token tokenize
        trace traceback tracemalloc tty turtle types typing
    warnings  wave weakref webbrowser  zipapp zipfile zipimport


    # from Dirs containing an "_init__.py" File

    asyncio  collections concurrent ctypes curses  dbm distutils
    email encodings ensurepip  html http  idlelib importlib  json  lib2to3 logging

    multiprocessing  pydoc_data  re  sqlite3  test tkinter tomllib turtledemo
    unittest urllib urllib.parse  venv  wsgiref  xml xmlrpc  zoneinfo


    # from VEnv Pip Install

    jira matplotlib numpy pandas psutil psycopg2 redis requests


"""

PYTHON_IMPORTS = _PYTHON_IMPORTS_TEXT.splitlines()
PYTHON_IMPORTS = list(_.partition("#")[0] for _ in PYTHON_IMPORTS)
PYTHON_IMPORTS = list(_.strip() for _ in PYTHON_IMPORTS)
PYTHON_IMPORTS = " ".join(PYTHON_IMPORTS).split()

assert len(PYTHON_IMPORTS) == 201, (len(PYTHON_IMPORTS), 201)


#
# Count or drop duplicate Lines, no sort required
#


REVERSE_DOC = """

    usage: reverse

    reverse the order of Lines

    comparable to:
      |tac  # at Linux
      |tail -r  # at macOS

    examples:
      ls -1 |r  c  # reverses the Sort-by-Name chosen by Ls

"""


def do_reverse(argv: list[str]) -> None:
    """Reverse the order of Lines"""

    # Form Shell Args Parser

    doc = REVERSE_DOC
    parser = ArgDocParser(doc, add_help=False)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    parser.parse_args_if(args)  # often prints help & exits zero

    # Reverse the order of Lines

    ilines = alt.stdin.read_splitlines()

    olines = list(ilines)  # todo: aka:  olines = list(reversed(ilines))
    olines.reverse()

    alt.stdout.write_splitlines(olines)


#
# Drop trailing Blanks in each Line, or trailing Chars of some other Set
#


RSTRIP_DOC = r"""

    usage: rstrip [--charset CHARSET]

    drop trailing Blanks in each Line, or trailing Chars of some other Set

    options:
      --charset CHARSET  list the Chars to drop if found, preferably in sorted order

    comparable to:
      |sed 's,  *$,,'

    quirks:
      doesn't drop trailing Blank Lines

    examples:
      printf '\n\n      a3 a4 a5 \n   b2 b3       \n\n\n' |pq rstrip  |cat -etv  # right stripped

"""


def do_rstrip(argv: list[str]) -> None:
    """Drop trailing Blanks in each Line, or trailing Chars of some other Set"""

    # Form Shell Args Parser

    doc = RSTRIP_DOC
    charset_help = "list the Chars to drop if found, preferably in sorted order"

    parser = ArgDocParser(doc, add_help=False)
    parser.add_argument("--charset", metavar="CHARSET", help=charset_help)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    ns = parser.parse_args_if(args)  # often prints help & exits zero

    charset = None if (ns.charset is None) else ns.charset  # maybe empty

    # Drop trailing Blanks in each Line, or trailing Chars of some other Set

    ilines = alt.stdin.read_splitlines()
    olines = list(_.rstrip(charset) for _ in ilines)
    alt.stdout.write_splitlines(olines)


#
# List distinct Chars in sorted order
#


SET_DOC = r"""

    usage: set

    list distinct Chars in sorted order

    comparable to:
      |sed 's,.,&\n,g' |sort |uniq |xargs |sed 's, ,,g'

    quirks:
      doesn't count Blanks of the " \t\n\f\r" kind
      not pushed by us as '|set' because many macOS & Linux Shells define 'set NAME=VALUE'

    examples:
      ls -l |pbcopy && pq set |cat -
      cat bin/xshverb.py|pq set |cat -
      cat $(git ls-files) |pq set |cat -

"""


def do_set(argv: list[str]) -> None:
    """List distinct Chars in sorted order"""

    # Form Shell Args Parser

    doc = SET_DOC
    parser = ArgDocParser(doc, add_help=False)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    parser.parse_args_if(args)  # often prints help & exits zero

    # List distinct Chars in sorted order

    itext = alt.stdin.read_text()

    iotext = itext
    blanks = "\t\n\f\r "
    for blank in blanks:
        iotext = iotext.replace(blank, "")

    otail = "".join(sorted(collections.Counter(iotext).keys()))

    ohead = ""
    for blank in blanks:
        if blank in itext:
            ohead += repr(blank)[1:-1]

    oline = ohead + otail
    olines = [oline]

    alt.stdout.write_splitlines(olines)

    # todo: |set of Control Chars other than the 5 "\t\n\f\r " kinds of Blanks


#
# Count or drop duplicate Lines, no sort required
#


SORT_DOC = """

    usage: sort [-n] [-r]

    change the order of Lines

    options:
      -n  sort as numbers, from least to most positive, but nulls last (default: sort as text)
      -r  reverse the sort (default: ascending)

    comparable to:
      |sort
      |sort -nr

    unlike classic Sort:
      defaults to sort by Unicode Codepoint, much as if LC_ALL=C, not by Locale's Collation Order
      sorts numerically on request without ignoring the exponents of Float Literals
      sorts not-a-number as last, no matter if reversed, and not as zero
      requires an odd count of -n to do -n work, requires an odd count of -r to do -r work
      doesn't offer --sort= general-numeric, human-numeric, random-when-unequal, version, etc
      doesn't offer --check, --merge, --dictionary-order, --ignore-case, --key, etc

    examples:
      ls -l |i  u  # counts each Word, prints Lines of Count Tab Text
      ls -l |i  counter --keys  c  # prints each Word once

"""

# todo: --nulls=last, --nulls=first
# todo: -V, --version-sort, --sort=version  # classic 'man sort' doesn't meantion '--sort=version'
# todo: random.shuffle


def do_sort(argv: list[str]) -> None:
    """Change the order of Lines"""

    # Form Shell Args Parser

    doc = SORT_DOC
    n_help = "sort as numbers, from least to most positive, but nulls last (default: sort as text)"
    r_help = "reverse the sort (default: ascending)"

    parser = ArgDocParser(doc, add_help=False)
    parser.add_argument("-n", action="count", help=n_help)
    parser.add_argument("-r", action="count", help=r_help)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    ns = parser.parse_args_if(args)  # often prints help & exits zero

    numeric = bool(ns.n % 2) if ns.n else False
    descending = bool(ns.r % 2) if ns.r else False

    # Define what ordered by Numeric means to us

    def keyfunc(line: str) -> tuple[float, str]:

        words = line.split()

        float_ = -math.inf if descending else math.inf  # not-a-number comes last

        if words:
            try:
                float_ = float(words[0])
            except ValueError:
                pass

        return (float_, line)

        # todo: stop losing '|sort -n' precision by converting large Int's to Float

    # Change the order of Lines

    ilines = alt.stdin.read_splitlines()

    if not numeric:
        olines = sorted(ilines)
    else:
        olines = sorted(ilines, key=keyfunc)

    if descending:
        olines.reverse()

    alt.stdout.write_splitlines(olines)


#
# Break Lines apart into Words
#


SPLIT_DOC = r"""

    usage: split [--sep SEP]

    break Lines apart into Words

    options:
      --sep SEP  split at each SEP, no matter if empty (default: split by Blanks & drop empty Words)

    comparable to:
      |tr ' \t' '\n' |grep .
      |tr + '\n'

    examples:
      ls -l |i  c
      ls -l |i --sep=' '  c
      echo a+b++d |i --sep=+  c

"""


def do_split(argv: list[str]) -> None:
    """Break Lines apart into Words"""

    # Form Shell Args Parser

    doc = SPLIT_DOC
    sep_help = "split at each SEP, no matter if empty (default: split by Blanks & drop empty Words)"

    parser = ArgDocParser(doc, add_help=False)
    parser.add_argument("--sep", metavar="SEP", help=sep_help)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    ns = parser.parse_args_if(args)  # often prints help & exits zero

    sep = None if (ns.sep is None) else ns.sep  # maybe empty

    # Break Lines apart into Words

    itext = alt.stdin.read_text()
    olines = itext.split(sep)  # raises ValueError("empty separator") when Sep is empty
    alt.stdout.write_splitlines(olines)  # may write enclosing Blanks when not split by Blanks


#
# Drop leading and trailing Blank Lines, and the leading Blanks in the first Line
#


STR_STRIP_DOC = r"""

    usage: str.strip

    drop leading and trailing Blank Lines, and the leading Blanks in the first Line

    comparable to:
      |pq expand
      |pq strip

    quirks:
      doesn't drop leading nor trailing Blanks in each Line

    examples:
      printf '\n\n      a3 a4 a5 \n   b2 b3       \n\n\n' |pq str.strip  |cat -etv  # some stripped

"""


def do_str_strip(argv: list[str]) -> None:
    """Drop leading and trailing Blank Lines, and the leading Blanks in the first Line"""

    # Form Shell Args Parser

    doc = STR_STRIP_DOC
    parser = ArgDocParser(doc, add_help=False)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    parser.parse_args_if(args)  # often prints help & exits zero

    # Drop leading and trailing Blank Lines, and the leading Blanks in the first Line

    itext = alt.stdin.read_text()
    otext = itext.strip()
    alt.stdout.write_text(otext)


#
# Drop leading and trailing Blanks in each Line, or leading/ trailing Chars of some other Set
#


STRIP_DOC = r"""

    usage: strip [--charset CHARSET]

    drop leading and trailing Blanks in each Line, or leading/ trailing Chars of some other Set

    options:
      --charset CHARSET  list the Chars to drop if found, preferably in sorted order

    comparable to:
      |sed 's,^  *,,' |sed 's,  *$,,'
      |pq dedent

    quirks:
      doesn't drop leading and trailing Blank Lines

    examples:
      echo '  a  b  ' |o |cat -etv
      echo '++a++b++' |o --chars='+' |cat -etv
      printf '\n\n      a3 a4 a5 \n   b2 b3       \n\n\n' |pq strip  |cat -etv  # some stripped

"""


def do_strip(argv: list[str]) -> None:
    """Drop leading and trailing Blanks in each Line, or leading/ trailing Chars of some other Set"""

    # Form Shell Args Parser

    doc = STRIP_DOC
    charset_help = "list the Chars to drop if found, preferably in sorted order"

    parser = ArgDocParser(doc, add_help=False)
    parser.add_argument("--charset", metavar="CHARSET", help=charset_help)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    ns = parser.parse_args_if(args)  # often prints help & exits zero

    charset = None if (ns.charset is None) else ns.charset  # maybe empty

    # Drop leading and trailing Blanks in each Line, or leading/ trailing Chars of some other Set

    ilines = alt.stdin.read_splitlines()
    olines = list(_.strip(charset) for _ in ilines)
    alt.stdout.write_splitlines(olines)


#
# Take only the last few Lines, or take only a chosen Line and what follows
#


TAIL_DOC = """

    usage: tail [-N|+N]

    take only the last few Lines, or take only a chosen Line and what follows

    positional arguments:
      -N|+N  how many trailing Lines to take, or which Line to take before the rest (default: -10)

    comparable to:
      |tail -N
      |tail +N

    future work:
      we could co-evolve with |head

    examples:
      ls -l |i  u  s -nr  t  c  # prints some least common Words
      ls -hlAF -rt bin/ |cat -n |expand |t -3  c  # prints the last 3 Lines
      ls -hlAF -rt bin/ |cat -n |expand |t +7  c  # prints the 7th Line and following

"""


def do_tail(argv: list[str]) -> None:
    """Take only the last few Lines, or take only a chosen Line and what follows"""

    assert argparse.OPTIONAL == "?"

    # Form Shell Args Parser

    doc = TAIL_DOC
    n_help = "how many trailing Lines to take, or which Line to take before the rest (default: -10)"

    parser = ArgDocParser(doc, add_help=False)
    parser.add_argument(dest="n", metavar="-N|+N", nargs="?", help=n_help)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    ns = parser.parse_args_if(args)  # often prints help & exits zero

    n = -10
    if ns.n is not None:
        try:
            n = int(ns.n, base=0)
            if (not n) or (ns.n[:1] not in ["-", "+"]):
                raise ValueError(ns.n)
        except ValueError:
            parser.parser.print_usage()
            eprint(f"|tail: {ns.n!r}: could be -10 or +3 or -12345, but isn't")
            sys.exit(2)  # exits 2 for bad Arg

    # Take only the last few Lines, or take only a chosen Line and what follows
    # Write out the taken Lines, maybe with enclosing Blanks, but closed

    assert n != 0, (n,)

    ilines = alt.stdin.read_splitlines()
    olines = ilines[n:] if (n < 0) else ilines[(n - 1) :]

    alt.stdout.write_splitlines(olines)


#
# Title the Case of each Word in each Line
#


TITLE_DOC = r"""

    usage: title

    title the Case of each Word in each Line

    quirks:
      '|pq title' is unrelated to '|pq . title'

    examples:
      ls -l |pq title |cat -

"""


def do_title(argv: list[str]) -> None:
    """Title the Case of each Word in each Line"""

    # Form Shell Args Parser

    doc = TITLE_DOC

    parser = ArgDocParser(doc, add_help=False)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    parser.parse_args_if(args)  # often prints help & exits zero

    # Title the Case of each Word in each Line

    itext = alt.stdin.read_text()
    otext = itext.title()
    alt.stdout.write_text(otext)


#
# Upper the Case of each Word in each Line
#


UPPER_DOC = r"""

    usage: upper

    upper the Case of each Word in each Line

    examples:
      ls -l |pq upper |cat -

"""


def do_upper(argv: list[str]) -> None:
    """Upper the Case of each Word in each Line"""

    # Form Shell Args Parser

    doc = UPPER_DOC

    parser = ArgDocParser(doc, add_help=False)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    parser.parse_args_if(args)  # often prints help & exits zero

    # Upper the Case of each Word in each Line

    itext = alt.stdin.read_text()
    otext = itext.upper()
    alt.stdout.write_text(otext)


#
# Split and unsplit a Web Address
#


URLLIB_DOC = r"""

    usage: urrlib

    split and unsplit a Web Address

    quirks:
      splits a single line, unsplits multiple lines

    examples:
      echo 'https://www.google.com/search?tbm=isch&q=carelman' |pq urllib |cat -
      echo 'https://www.google.com/search?tbm=isch&q=carelman' |pq urllib |pq urllib |cat -

"""


def do_urllib(argv: list[str]) -> None:
    """Split and unsplit a Web Address"""

    # Form Shell Args Parser

    doc = URLLIB_DOC
    parser = ArgDocParser(doc, add_help=False)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    parser.parse_args_if(args)  # often prints help & exits zero

    # Split and unsplit a Web Address

    ilines = alt.stdin.read_splitlines()

    if len(ilines) != 1:
        oline = " ".join(ilines)
        oline = oline.replace(" ", "")
        alt.stdout.write_splitlines([oline])
        return

    iline = ilines[-1]

    urlsplits = urllib.parse.urlsplit(iline)

    pairs = urllib.parse.parse_qsl(urlsplits.query)
    join = "\n".join(f"&{k}={v}" for k, v in pairs)
    lstrip = join.lstrip(" &")

    olines = list()
    olines.append(urlsplits.scheme + "://")
    olines.append(urlsplits.netloc)
    olines.append(urlsplits.path + ("?" if lstrip else ""))
    olines.extend(lstrip.splitlines())
    olines.append(urlsplits.fragment)

    olines = list(_ for _ in olines if _)

    alt.stdout.write_splitlines(olines)


#
# Call up Vi
#


VI_DOC = r"""

    usage: v [WORD ...]

    call up Vi

    positional arguments:
      WORD  a word of command: options and args of Vi

    comparable to:
      vi ...

    quirks:
      tells Vi to edit the Shell Pipe or Os Copy/Paste Buffer only when you give no Pos Args

    examples:
      v  # edits the Os Copy/Paste Buffer
      echo |v |sh  # edit a Shell Command and then run it

"""


def do_vi(argv: list[str]) -> None:
    """Call up Emacs inside the Terminal with no Menu Bar and no Splash"""

    assert argparse.ZERO_OR_MORE == "*"

    # Form Shell Args Parser

    doc = VI_DOC
    word_help = "a word of command: options and args of Vi"
    parser = ArgDocParser(doc, add_help=False)
    parser.add_argument(dest="words", metavar="WORD", nargs="*", help=word_help)

    # Take up Shell Args

    args = ["--"] + argv[1:]  # quotes them all, to forward onto Emacs unchanged
    parser.parse_args_if(args)  # often prints help & exits zero

    # Call up Emacs inside the Terminal with no Menu Bar and no Splash

    shverb = "vi"
    starts: list[str] = list()  # aka starts = shlex.split("")

    _do_edit(argv, shverb=shverb, starts=starts)


#
# Count the Lines
#


WCL_DOC = r"""

    usage: wcl

    count the Lines

    comparable to:
      |wc -l  # doesn't count last Line without a closing Line-Break
      |cat -n |expand |tail -3  # does count last Line without a closing Line-Break

    quirks:
      counts the last Line, even without a closing Line-Break, like class Cat N, unlike classic WC L
      not pushed by us as '|w' because many macOS & Linux Shells define 'w' something like 'who'
      not pushed by us as '|wcl' because less is more

    examples:
      ls -l |pq w |cat -
      ls -l |pq wcl |cat -

"""


def do_wcl(argv: list[str]) -> None:
    """Count the Lines"""

    # Form Shell Args Parser

    doc = WCL_DOC
    parser = ArgDocParser(doc, add_help=False)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    parser.parse_args_if(args)  # often prints help & exits zero

    # Count the Lines

    ilines = alt.stdin.read_splitlines()
    oint = len(ilines)
    otext = str(oint) + "\n"

    alt.stdout.write_text(otext)  # |wcl textified by construction


#
# Join the Lines into a single Line
#


XARGS_DOC = r"""

    usage: xargs [--sep SEP]

    join the Lines into a single Line

    options:
      --sep SEP  the Char or Chars to place between each two Lines

    comparable to:
      |xargs

    examples:
      ls -l |i  x  c

"""


def do_xargs(argv: list[str]) -> None:
    """Join the Lines into a single Line"""

    # Form Shell Args Parser

    doc = XARGS_DOC
    sep_help = "the Char or Chars to place between each two Lines"

    parser = ArgDocParser(doc, add_help=False)
    parser.add_argument("--sep", metavar="SEP", help=sep_help)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    ns = parser.parse_args_if(args)  # often prints help & exits zero

    sep = " " if (ns.sep is None) else ns.sep  # maybe empty

    # Join the Lines into a single Line

    ilines = alt.stdin.read_splitlines()
    oline = sep.join(ilines)  # deletes Line-Break's when Sep is empty
    olines = [oline]

    alt.stdout.write_splitlines(olines)

    # |xargs can start or end its 1 Output Line with Blanks when Sep is Blank


#
# Mess about inside the Os/Copy Paste Buffer
#


XSHVERB_DOC = r"""

    usage: pq [HINT ...]

    mess about inside the Os/Copy Paste Buffer

    positional arguments:
      HINT  hint of which Shell Pipe Filter you mean

    quirks:
      defaults to decode the Bytes as UTF-8, replacing decoding Errors with U+003F '?' Question-Mark's
      defaults to dedent the Lines, strip trailing Blanks from each Line, and end with 1 Line-Break
      defaults to drop leading and trailing Blank Lines, but not the Dent of the first Line
      more help at:  xshverb.py --help

    examples:
      pq  # dedents and strips the Os/Copy Paste Buffer, first to Tty Out, and then to replace itself
      pq .  # guesses what edit you want in the Os/Copy Paste Buffer and runs ahead to do it
      pq v  # dedents and strips the Os/Copy Paste Buffer, and then calls Vi to edit it
      printf '\n\n      a3 a4 a5 \n   b2 b3       \n\n\n' |pq  |cat -etv  # much stripped
      echo $'\xC0\x80' |pq |sort  # doesn't deny service to shout up "illegal byte sequence"

"""

PQ_DOC = XSHVERB_DOC

# "There is nothing -- absolutely nothing -- half so much worth doing as simply messing about in ..." ~ Kenneth Grahame


def do_xshverb(argv: list[str]) -> None:  # def do_pq  # def do_p
    """Mess about inside the Os/Copy Paste Buffer"""

    assert argparse.ZERO_OR_MORE == "*"

    # Form Shell Args Parser

    doc = XSHVERB_DOC
    hint_help = "hint of which Shell Pipe Filter you mean"

    parser = ArgDocParser(doc, add_help=False)
    parser.add_argument(dest="hints", metavar="HINT", nargs="*", help=hint_help)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    ns = parser.parse_args_if(args)  # often prints help & exits zero

    if ns.hints:
        hint = ns.hints[0]  # todo: report more than first meaningless undefined Verb
        # parser.parser.print_usage()
        eprint(f"xshverb: command not found: |pq {hint}")
        sys.exit(2)  # exits 2 for bad Args

    # Dedent and strip

    ibytes = alt.stdin.read_bytes()
    obytes = bytes_textify(ibytes)  # textified by |pq here
    alt.stdout.write_bytes(obytes)

    # Say what the most plain Undirected Pq without Args means

    otext = obytes.decode()
    if (alt.index == 0) and (alt.rindex == -1):
        if alt.sys_stdin_isatty and alt.sys_stdout_isatty:

            # Write a copy to Tty without draining .alt.stdout

            sys.stdout.write(otext)


#
# Amp up Import ArgParse
#


class ArgDocParser:
    """Pick out Prog & Description & Epilog well enough to form an Argument Parser"""

    text: str  # something like the __main__.__doc__, but dedented and stripped
    parser: argparse.ArgumentParser  # the inner standard ArgumentParser
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

        text = epilog if epilog else ""
        lines = text.splitlines()

        indices = list(_ for _ in range(len(lines)) if lines[_])  # drops empty Lines
        indices = list(_ for _ in indices if not lines[_].startswith(" "))  # finds Ttop Lines

        closing = ""
        if indices:
            index = indices[-1] + 1
            join = "\n".join(lines[index:])  # last Graf, minus its Top Line
            dedent = textwrap.dedent(join)
            closing = dedent.strip()

        return closing  # maybe empty

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
            if sys.version_info >= _3_10_ARGPARSE:  # Oct/2021 Python 3.10 of Ubuntu 2022
                print("\n".join(diffs))

                sys.exit(2)  # exits 2 for wrong Args in Help Doc

            # takes 'usage: ... [HINT ...]', rejects 'usage: ... HINT [HINT ...]'
            # takes 'options:', rejects 'optional arguments:'
            # takes '-F, --isep ISEP', rejects '-F ISEP, --isep ISEP'

        # Print Closing & exit zero, if no Shell Args

        if not args:
            print()
            print(closing)
            print()

            sys.exit(0)  # exits 0 after printing Closing

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
                b_text = parser.format_help()
            finally:
                del os.environ["COLUMNS"]  # removes

        else:

            with_columns = os.environ["COLUMNS"]  # backs up
            os.environ["COLUMNS"] = str(89)  # replaces
            try:
                b_text = parser.format_help()
            finally:
                os.environ["COLUMNS"] = with_columns  # restores

        b = b_text.splitlines()

        tofile = "ArgumentParser(...)"

        # Form >= 0 Diffs from Help Doc to Parser Format_Help,
        # but ask for lineterm="", for else the '---' '+++' '@@' Diff Control Lines end with '\n'

        diffs = list(difflib.unified_diff(a=a, b=b, fromfile=fromfile, tofile=tofile, lineterm=""))

        # Succeed

        return diffs


def argv_parse_if(parser: ArgDocParser, argv: list[str]) -> argparse.Namespace:
    """Parse the Shell Args, else print Help and exit zero or nonzero"""

    args = ["--"]  # for when I'm feeling lucky
    if argv[1:]:
        args = list()  # for when I need examples
        if argv[1:] != ["--"]:
            args = argv[1:]  # for when I've got specifics

    ns = parser.parse_args_if(args)  # often prints help & exits zero

    return ns

    # often prints help & exits zero


#
# Amp up Import BuiltsIns Bytes
#


def bytes_textify(bytes_: bytes) -> bytes:
    """Keep the Text, but replace the Errors with '?' and drop the enclosing Blanks"""

    assert unicodedata.lookup("Replacement Character") == "\ufffd"
    decode = bytes_.decode(errors="replace")  # not errors="surrogateescape"
    text = decode.replace("\ufffd", "?")  # U+003F Question-Mark

    textify = str_textify(text)
    encode = textify.encode()  # doesn't raise UnicodeEncodeError

    return encode


#
# Amp up Import BuiltsIns Str
#


def str_textify(text: str) -> str:
    """Keep the Text, but drop the enclosing Blanks"""

    dedent = textwrap.dedent(text)
    splitlines = dedent.splitlines()
    rstrips = list(_.rstrip() for _ in splitlines)

    while rstrips and not rstrips[0]:
        rstrips.pop(0)
    while rstrips and not rstrips[-1]:
        rstrips.pop()

    join = "\n".join(rstrips)
    join_plus = (join + "\n") if join else ""

    return join_plus

    # doesn't start with Blank Columns, doesn't end any Lines with Blank Chars
    # doesn't start with Empty Lines, doesn't end with Empty Lines
    # does end with "\n" when not empty

    # doesn't raise UnicodeDecodeError, doesn't substitute \ufffd, does substitute '?'

    # todo: .func vs Control Chars, and when to deal with just Ascii

    # todo: Who doesn't pipe text? Dt
    # todo: Who calls to textify? Pq, Expand, and the editors: Emacs, Less, Vi
    # todo: Who never needs to textify? Jq, Wcl
    # todo: Who doesn't guarantee a closing Line-Break? The editors after the edit (Emacs, Vi)

    # todo: Who haven't we put into a group here yet?
    #
    #   Awk, Cat, Counter, Grep, Head, Ht, Nl, Reverse, Set Sort, Strip, Tail, XArgs
    #


#
# Amp up Import DateTime as DT
#


def dt_timedelta_strftime(td: dt.timedelta, depth: int = 2, str_zero: str = "0s") -> str:
    """Give 'w d h m s ms us ms' to mean 'weeks=', 'days=', etc"""

    # Pick Weeks out of Days, Minutes out of Seconds, and Millis out of Micros

    w = td.days // 7
    d = td.days % 7

    h = td.seconds // 3600
    h_s = td.seconds % 3600
    m = h_s // 60
    s = h_s % 60

    ms = td.microseconds // 1000
    us = td.microseconds % 1000

    # Catenate Value-Key Pairs in order, but strip leading and trailing Zeroes,
    # and choose one unit arbitrarily when speaking of any zeroed TimeDelta

    keys = "w d h m s ms us".split()
    values = (w, d, h, m, s, ms, us)
    pairs = list(zip(keys, values))

    chars = ""
    count = 0
    for index, (k, v) in enumerate(pairs):
        if (chars or v) and any(values[index:]):
            chars += "{}{}".format(v, k)
            count += 1

            if count >= depth:  # truncates, does Not round up
                break

    str_zeroes = list((str(0) + _) for _ in keys)
    if not chars:
        assert str_zero in str_zeroes, (str_zero, str_zeroes)
        chars = str_zero

    # Succeed

    return chars  # '9ms331us' to mean 9ms 331us <= t < 9ms 333us


#
# Amp up Import PathLib
#


def pathlib_path_read_version(pathname: str) -> str:
    """Hash the Bytes of a File down to a purely Decimal $Major.$Minor.$Micro Version Str"""

    path = pathlib.Path(pathname)
    path_bytes = path.read_bytes()

    hasher = hashlib.md5()
    hasher.update(path_bytes)
    hash_bytes = hasher.digest()

    str_hash = hash_bytes.hex()
    str_hash = str_hash.upper()  # such as 32 nybbles 'C24931F77721476EF76D85F3451118DB'

    major = 0
    minor = int(str_hash[0], base=0x10)  # 0..15
    micro = int(str_hash[1:][:2], base=0x10)  # 0..255

    version = f"{major}.{minor}.{micro}"
    return version

    # 0.15.255


#
# Amp up Import Sys
#


def eprint(*args: object) -> None:
    print(*args, file=sys.stderr)


#
# Fabricate Bytes to begin with, for the case of we got no Input
#


Jabberwocky = """

    ’Twas brillig, and the slithy toves
        Did gyre and gimble in the wabe:
    All mimsy were the borogoves,
        And the mome raths outgrabe.

    “Beware the Jabberwock, my son!
        The jaws that bite, the claws that catch!
    Beware the Jubjub bird, and shun
        The frumious Bandersnatch!”

    He took his vorpal sword in hand;
        Long time the manxome foe he sought—
    So rested he by the Tumtum tree
        And stood awhile in thought.

    And, as in uffish thought he stood,
        The Jabberwock, with eyes of flame,
    Came whiffling through the tulgey wood,
        And burbled as it came!

    One, two! One, two! And through and through
        The vorpal blade went snicker-snack!
    He left it dead, and with its head
        He went galumphing back.

    “And hast thou slain the Jabberwock?
        Come to my arms, my beamish boy!
    O frabjous day! Callooh! Callay!”
        He chortled in his joy.

    ’Twas brillig, and the slithy toves
        Did gyre and gimble in the wabe:
    All mimsy were the borogoves,
        And the mome raths outgrabe.

"""

# for as to defeat "the tyranny of the blank page"


#
# Index the Doc and Func of each main Shell Verb
#


assert __doc__, (__doc__,)

DOC_BY_VERB = dict(
    awk=AWK_DOC,
    cat=CAT_DOC,
    counter=COUNTER_DOC,
    dedent=DEDENT_DOC,
    dent=DENT_DOC,
    diff=DIFF_DOC,
    dot=DOT_DOC,
    dt=DT_DOC,
    emacs=EMACS_DOC,
    expand=EXPAND_DOC,
    grep=GREP_DOC,
    head=HEAD_DOC,
    ht=HT_DOC,
    jq=JQ_DOC,
    less=LESS_DOC,
    lower=LOWER_DOC,
    lstrip=LSTRIP_DOC,
    nl=NL_DOC,
    python=PYTHON_DOC,
    reverse=REVERSE_DOC,
    rstrip=RSTRIP_DOC,
    set=SET_DOC,
    sort=SORT_DOC,
    split=SPLIT_DOC,
    strip=STRIP_DOC,
    tail=TAIL_DOC,
    title=TITLE_DOC,
    upper=UPPER_DOC,
    urllib=URLLIB_DOC,
    vi=VI_DOC,
    wcl=WCL_DOC,
    xargs=XARGS_DOC,
    xshverb=XSHVERB_DOC,
)

for _K_ in DOC_BY_VERB.keys():
    _V_ = textwrap.dedent(DOC_BY_VERB[_K_])
    assert not _V_.lstrip("\n").startswith(" "), (_V_, _K_)  # needs r""" ?
    DOC_BY_VERB[_K_] = _V_.strip()


FUNC_BY_VERB = dict(
    awk=do_awk,
    cat=do_cat,
    counter=do_counter,
    dedent=do_dedent,
    dent=do_dent,
    diff=do_diff,
    dot=do_dot,
    dt=do_dt,
    emacs=do_emacs,
    expand=do_expand,
    grep=do_grep,
    head=do_head,
    ht=do_ht,
    jq=do_jq,
    less=do_less,
    lower=do_lower,
    lstrip=do_lstrip,
    nl=do_nl,
    python=do_python,
    reverse=do_reverse,
    rstrip=do_rstrip,
    set=do_set,
    sort=do_sort,
    split=do_split,
    strip=do_strip,
    tail=do_tail,
    title=do_title,
    upper=do_upper,
    urllib=do_urllib,
    vi=do_vi,
    wcl=do_wcl,
    xargs=do_xargs,
    xshverb=do_xshverb,
)


VERB_BY_VB = {  # lists the abbreviated or unabbreviated Aliases of each Shell Verb
    ".": "dot",
    "a": "awk",
    "c": "cat",
    "d": "diff",
    "dict": "counter",
    "e": "emacs",
    "g": "grep",
    "h": "head",
    "i": "split",
    "j": "jq",
    "k": "less",
    "len": "wcl",
    "n": "nl",
    "o": "strip",
    "p": "python",
    "pq": "xshverb",  # |pq in homage of |jq, not |py and not |python
    "r": "reverse",
    "s": "sort",
    "t": "tail",
    "u": "counter",
    "v": "vi",
    "vim": "vi",
    "w": "wcl",
    "x": "xargs",
    "xshverb.py": "xshverb",
    "|": "xshverb",
}

# todo: find Verbs by today's distinct partial Verbs, such as '|pq exp' for '|pq expand'


_DOC_VERBS_ = list(DOC_BY_VERB.keys())
_FUNC_VERBS_ = list(FUNC_BY_VERB.keys())

_DIFF_VERBS_ = list(difflib.unified_diff(a=_DOC_VERBS_, b=_FUNC_VERBS_, lineterm=""))
assert not _DIFF_VERBS_, (_DIFF_VERBS_,)

_SORTED_VERBS_ = sorted(_DOC_VERBS_)
_DIFF_SORTED_VERBS_ = list(difflib.unified_diff(a=_DOC_VERBS_, b=_SORTED_VERBS_, lineterm=""))
assert not _DIFF_SORTED_VERBS_, (_DIFF_SORTED_VERBS_,)

for _VB_, _VERB_ in VERB_BY_VB.items():
    assert _VB_ not in _FUNC_VERBS_, (_VB_,)
    assert _VERB_ in _FUNC_VERBS_, (_VERB_,)

_VBS_ = list(VERB_BY_VB.keys())
_SORTED_VBS_ = sorted(VERB_BY_VB.keys())
_DIFF_VBS_ = list(difflib.unified_diff(a=_VBS_, b=_SORTED_VBS_, lineterm=""))
assert not _DIFF_VBS_, (_DIFF_VBS_,)

# todo: move these paragraphs of Code into a better place
# todo: do complain, but without blocking Test


DOC_BY_VERB["str.strip"] = STR_STRIP_DOC
DOC_BY_VERB["textwrap.dedent"] = DEDENT_DOC

FUNC_BY_VERB["str.strip"] = do_str_strip
FUNC_BY_VERB["textwrap.dedent"] = do_dedent

# todo: merge these in above, like as .do_textwrap_dedent, .do_str_strip


alt = ShellPipe()


#
# Run from the Shell Command Line, if not imported
#


if __name__ == "__main__":
    main()


# todo: bug: no regex choosing @ cat bin/xshverb.py |g '(def.do_)'  a 2  c

# todo: |grep -n

# todo: define b f l m q w y z  # especially: b z
#
# todo: + f is for **Find**, but default to search $PWD spelled as ""
# todo: + q is for **Git**, because G was taken
# todo: + l is for **Ls** of the '|ls -dhlAF -rt' kind, not more popular less detailed '|ls -CF'
# todo: + m is for **Make**, but timestamp the work and never print the same Line twice
# todo: + |y is to show what's up and halt till you say move on
#

# more test with 1 2 3 etc defined of some particular nonsense such as:  seq 123 |sh

# todo: |p ascii and |p repr without so many quotes in the output


# 3456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789


# posted as:  https://github.com/pelavarre/xshverb/blob/main/bin/xshverb.py
# copied from:  git clone https://github.com/pelavarre/xshverb.git
