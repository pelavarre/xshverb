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
  p  # chats with Python, and doesn't make you spell out the Imports, or builds & runs a Shell Pipe
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
import difflib
import hashlib
import json
import math
import os
import pathlib
import re
import shlex
import subprocess
import sys
import textwrap
import unicodedata
import zoneinfo  # new since Oct/2020 Python 3.9


_: dict[str, int] | None  # new since Oct/2021 Python 3.10

if not __debug__:
    raise NotImplementedError(str((__debug__,)))  # "'python3' is better than 'python3 -O'"


YYYY_MM_DD = "2025-05-31"  # date of last change to this Code, or an earlier date

_3_10_ARGPARSE = (3, 10)  # Oct/2021 Python 3.10  # oldest trusted to run ArgParse Static Analyses

Pacific = zoneinfo.ZoneInfo("America/Los_Angeles")  # todo: also welcome logins from the periphery
UTC = zoneinfo.ZoneInfo("UTC")


GATEWAY_VERBS = ("dt", "e", "k", "v")  # these override how we parse the ArgV of each ShPump


def main() -> None:
    """Run from the Sh Command Line"""

    argv = sys.argv

    # Form Shell Args Parser

    assert argparse.ZERO_OR_MORE == "*"
    assert __main__.__doc__, __main__.__doc__

    doc = __main__.__doc__
    hint_help = "hint of which Shell Pipe Filter you mean"
    version_help = "show version and exit"

    parser = AmpedArgumentParser(doc, add_help=True)
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

    alt.stdout = ShellFile()  # adds or replaces
    for index, shpump in enumerate(shpumps):
        alt.index = index
        alt.rindex = index - len(shpumps)

        alt.stdin = alt.stdout
        alt.stdout = ShellFile()  # adds or replaces

        argv = shpump.argv
        shpump.func(argv)  # two positional args, zero keyword args

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
            eprint(f"xshverb: command not found: |{vb}")  # a la Bash & Zsh vs New Verbs
            sys.exit(2)  # exits 2 for bad Shell Verb Hint

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
                if hint.isidentifier():
                    assert len(words) == 1, (len(words), words, hint)

                # Accept a Shell-Quote'd Verb with its baggage of Options and Args

                elif len(words) > 1:
                    splits = shlex.split(hint)
                    assert splits, (splits, hint)
                    if splits[0].isidentifier():
                        argv = splits
                        break

                # Fall back to have Pq make sense of anything else, and maybe more that follows

                else:
                    argv.append("pq")

            arg = hint
            argv.append(arg)  # may be '--', and may be '--' more than once

            # Take all the remaining Hints as Args, after a Gateway Verb into a Namespacre

            assert GATEWAY_VERBS == ("dt", "e", "k", "v")

            if index == 0:
                if argv[0] in GATEWAY_VERBS:  # todo: which verbs consume indefinitely many hints?
                    continue

            # Insert a Break between Shell Pipe Filters,
            # rather than accepting a first Positional Argument,
            # when not Shell-Quote'd in with the Verb

            if hints:
                next_hint = hints[0]

                if next_hint.isidentifier():  # not any '-' or '--' option, nor '(.)' etc etc
                    break

        return argv

    def exit_doc_if(self) -> None:
        """Show Help or Closing or Version and exit zero, else return"""

        doc = self.doc
        argv = self.argv

        parser = AmpedArgumentParser(doc, add_help=False)  # enough to print Closing
        if argv[1:] == ["--"]:
            self.closing_show(closing=parser.closing)
            sys.exit(0)

        double_dashed = False
        for arg in argv[1:]:

            if not double_dashed:

                if arg == "--":
                    double_dashed = True
                    continue

                if (arg == "-h") or ("--help".startswith(arg) and arg.startswith("--h")):
                    self.doc_show()
                    sys.exit(0)

                if (arg == "-V") or ("--version".startswith(arg) and arg.startswith("--v")):
                    self.version_show()
                    sys.exit(0)

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


@dataclasses.dataclass  # (order=False, frozen=False)
class ShellFile:
    """Pump Bytes in and out"""  # 'Store and forward'

    iobytes: bytes = b""

    filled: bool = False
    drained: bool = False

    #
    # Pump Bytes in
    #

    def readlines(self, hint: int = -1) -> list[str]:
        """Read Lines from Bytes, but first fill from the Os Copy/Paste Buffer if need be"""

        if hint != -1:  # .hint limits the count of Lines read in
            raise NotImplementedError(str((hint,)))

        self.fill_if()

        iobytes = self.iobytes
        decode = iobytes.decode(errors="surrogateescape")
        splitlines = decode.splitlines()

        return splitlines

    def read_text(self) -> str:
        """Read Chars from Stdin, else from Os Copy/Paste Buffer, at most once"""

        self.fill_if()
        iobytes = self.iobytes
        decode = iobytes.decode(errors="surrogateescape")

        return decode

    def read_bytes(self) -> bytes:
        """Read Bytes from Stdin, else from Os Copy/Paste Buffer, at most once"""

        self.fill_if()
        iobytes = self.iobytes

        return iobytes

    def fill_if(self) -> None:
        """Read Bytes from Stdin, else from Os Copy/Paste Buffer, at most once"""

        filled = self.filled
        if filled:
            return

        if not sys.stdin.isatty():
            self.fill_from_stdin()
        else:

            # eprint("fill_from_pbpaste")

            self.filled = True

            shline = "pbpaste"  # macOS convention, often not distributed at Linuxes
            argv = shlex.split(shline)
            run = subprocess.run(
                argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=None, check=True
            )

            self.iobytes = run.stdout  # replaces

        # .errors .returncode .shell .stdin unlike:  iobytes = os.popen(shline).read().encode()

    def fill_from_stdin(self) -> None:
        """Read Bytes from Stdin"""

        # eprint("fill_from_stdin")

        self.filled = True

        path = pathlib.Path("/dev/stdin")  # todo: solve for Windows too
        read_bytes = path.read_bytes()  # maybe not UTF-8 Encoded
        self.iobytes = read_bytes  # replaces

    #
    # Pump Bytes out
    #

    def write_text(self, text: str) -> int:
        """Write Chars into Bytes, but don't drain yet"""

        self.filled = True

        count = len(text)  # counts Decoded Chars, not Encoded Bytes
        encode = text.encode(errors="surrogateescape")
        self.iobytes = encode  # replaces

        return count

        # standard .writelines forces the Caller to choose each Line-Break

    def drain_if(self) -> None:
        """Write Bytes to Stdout, else to the Os Copy/Paste Buffer, at most once"""

        iobytes = self.iobytes

        drained = self.drained
        if drained:
            return

        if not sys.stdout.isatty():
            self.drain_to_stdout()
        else:

            # eprint("drain_to_pbcopy")

            self.drained = True

            shline = "pbcopy"  # macOS convention, often not distributed at Linuxes
            argv = shlex.split(shline)
            subprocess.run(argv, input=iobytes, stdout=subprocess.PIPE, stderr=None, check=True)

    def drain_to_stdout(self) -> None:
        """Write Bytes to Sydout"""

        # eprint("drain_to_stdout")

        iobytes = self.iobytes
        self.drained = True

        fd = sys.stdout.fileno()
        data = iobytes  # maybe not UTF-8 Encoded
        os.write(fd, data)


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
      echo $PATH |a -F:  # show only the last Dir in the Sh Path
      echo $PATH |a -F: -vOFS=$'\n' 0  # show 1 Dir per Line, as if |tr : '\n'
      echo 'a1 a2\tb1 b2\tc1 c2' |a -F$'\t' -vOFS=$'\t' 3 1  # Tabs in and Tabs out

"""

# todo: |awk --tsv to abbreviate |awk -F$'\t' -vOFS=$'\t'


def do_awk(argv: list[str]) -> None:
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

    numbers = list(int(_, base=0) for _ in ns.numbers)  # rejects Floats
    if not numbers:
        numbers = [-1]

    # Pick one or more Columns of Words, and drop the rest

    olines = list()
    ilines = alt.stdin.readlines()

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

    otext = line_break_join_rstrips_plus_if(olines)
    alt.stdout.write_text(otext)


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

    # Form Shell Args Parser

    assert argparse.OPTIONAL == "?"

    doc = CAT_DOC
    ifile_help = "explicitly mention the Terminal, in place of a Pathname"

    parser = AmpedArgumentParser(doc, add_help=False)
    parser.add_argument("ifile", metavar="-", nargs="?", help=ifile_help)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    ns = parser.parse_args_if(args)  # often prints help & exits zero

    if ns.ifile is not None:
        if ns.ifile != "-":
            parser.parser.print_usage()
            sys.exit(2)  # exits 2 for bad Arg

    # Read from Stdin Tty at start of Pipe

    sys_stdin_isatty = sys.stdin.isatty()

    filled_from_tty = False
    if alt.index == 0:
        if not sys_stdin_isatty:
            alt.stdin.fill_from_stdin()
        else:
            filled_from_tty = True

            eprint(
                "Start typing"
                + ". Press Return after each Line"
                + ". Press ⌃D to continue, or ⌃C to quit"
            )
            alt.stdin.fill_from_stdin()
            eprint("")

    # Strip trailing Blanks off each Line

    ilines = alt.stdin.readlines()
    otext = line_break_join_rstrips_plus_if(ilines)
    alt.stdout.write_text(otext)

    # Write to Stdout Tty at end of Pipe

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

    parser = AmpedArgumentParser(doc, add_help=False)
    parser.add_argument("-k", "--keys", action="count", help=keys_help)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    ns = parser.parse_args_if(args)  # often prints help & exits zero

    # Count or drop duplicate Lines, no sort required

    ilines = alt.stdin.readlines()
    counter = collections.Counter(ilines)

    if ns.keys:
        olines = list(counter.keys())
    else:
        olines = list(f"{v:6}  {k}" for k, v in counter.items())

        # f"{v:6}\t{k}" with its sometimes troublesome \t is classic '|cat -n' format

    otext = line_break_join_rstrips_plus_if(olines)
    alt.stdout.write_text(otext)


#
# Drop the Style out of Json Data
#


DT_DOC = r"""

    usage: dt [WORD ...]

    do the thing, but show its date/time and pass/fail details

    positional arguments:
      WORD  the words of command: the Shell verb and its options and args to run

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

    # Form Shell Args Parser

    doc = DT_DOC
    word_help = "the words of command: the Shell verb and its options and args to run"
    parser = AmpedArgumentParser(doc, add_help=False)
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
    eprint(f"{s0a}  ({s0b})")

    if not argv[1:]:
        assert ns.words == ["true"], (ns.words,)
        sys.exit(0)

    shargv = ns.words
    shline = " ".join(shlex.quote(_) for _ in shargv)
    eprint("+", shline)

    run = subprocess.run(shargv, stdin=None)
    returncode = run.returncode
    eprint(f"+ exit {returncode}")  # printed even when zero

    t1 = dt.datetime.now(UTC)
    t1t0 = t1 - t0
    eprint(dt_timedelta_strftime(t1t0))  # such as '346ms' to mean 0.346 <= t <= 0.347

    sys.exit(returncode)


#
# Replace troublesome character encodings
#


EXPAND_DOC = r"""

    usage: expand

    replace troublesome character encodings

    comparable to:
      |expand |tr '' ''

    quirks:
      not pushed by us as '|expand' because many macOS & Linux Shells define '|expand' narrowly

    examples:
      echo $'\xC2\xA0 « » “ ’ ” – — ′ ″ ‴ ' |pq expand c

"""


def do_expand(argv: list[str]) -> None:  # do_expandtabs
    """# Replace troublesome character encodings"""

    # Form Shell Args Parser

    doc = SET_DOC
    parser = AmpedArgumentParser(doc, add_help=False)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    parser.parse_args_if(args)  # often prints help & exits zero

    # Replace troublesome character encodings

    itext = alt.stdin.read_text()
    iotext = str_expand_plus(itext)
    olines = iotext.splitlines()

    otext = line_break_join_rstrips_plus_if(olines)
    alt.stdout.write_text(otext)

    # todo: Control Chars other than the 5 "\t\n\f\r " kinds of Blanks


def str_expand_plus(text: str) -> str:
    """# Replace troublesome character encodings"""

    d = {
        "\f": "<hr>",  # U+000C \f
        unicodedata.lookup("No-Break Space"): "&nbsp;",  # U+00A0 \xA0  # vs Apple ⌥Space
        unicodedata.lookup("Zero Width Space"): "-",  # U+200B
        unicodedata.lookup("En Dash"): "--",  # U+2013  # vs Microsoft
        unicodedata.lookup("Em Dash"): " -- ",  # U+2014  # vs Microsoft
        unicodedata.lookup("Left Single Quotation Mark"): "'",  # U+2018 ‘  # vs Microsoft
        unicodedata.lookup("Right Single Quotation Mark"): "'",  # U+2019 ’  # vs Microsoft
        unicodedata.lookup("Left Double Quotation Mark"): '"',  # U+201C “  # vs Microsoft
        unicodedata.lookup("Right Double Quotation Mark"): '"',  # U+201D ”  # vs Microsoft
        unicodedata.lookup("Horizontal Ellipsis"): "...",  # U+2026  # vs Microsoft
        unicodedata.lookup("Prime"): "'",  # U+2032
        unicodedata.lookup("Double Prime"): "''",  # U+2033
        unicodedata.lookup("Triple Prime"): "'''",  # U+2034
    }

    iotext = text
    iotext = iotext.expandtabs(tabsize=8)
    for k, v in d.items():
        iotext = iotext.replace(k, v)

    return iotext

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
      echo .1 .2 .3 a1 b2 c3 |tr ' ' '\n' |pbcopy
      g .1 .2 '(.3)'  c  # .1 .2 .3 c3
      pq 'g a. b2 c.'  c  # b2

"""


def do_grep(argv: list[str]) -> None:  # Generalized Regular Expression Print
    """Take Lines that match a Pattern, drop the rest"""

    # Form Shell Args Parser

    doc = GREP_DOC

    pattern_help = (
        "the text to find, or a Mixed Case Text to find in any Case, or a RegEx of () [] {}"
    )

    parser = AmpedArgumentParser(doc, add_help=False)
    parser.add_argument(dest="patterns", metavar="PATTERN", nargs="*", help=pattern_help)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    ns = parser.parse_args_if(args)  # often prints help & exits zero
    patterns = ns.patterns

    eprint(patterns)

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

    ilines = alt.stdin.readlines()

    olines = list()
    for iline in ilines:
        for pattern in patterns:

            if pattern.islower() or pattern.isupper():
                if pattern.casefold() not in iline.casefold():
                    continue

            elif str_is_re_pattern_ish(pattern):
                if not re.search(pattern, iline):
                    continue

            elif pattern not in iline:
                continue

            olines.append(iline)
            break

            # todo: factor out pattern classification for speed

        # todo: multiline patterns

    otext = line_break_join_rstrips_plus_if(olines)
    alt.stdout.write_text(otext)

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

    parser = AmpedArgumentParser(doc, add_help=False)
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

    ilines = alt.stdin.readlines()
    olines = ilines[:-n]

    otext = line_break_join_rstrips_plus_if(olines)
    alt.stdout.write_text(otext)


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
      seq 99 |ht  c  # show not much of 99 Lines
      find . |ht  c  # show not much of many Pathnames that begin with "." Dot or not

"""


def do_ht(argv: list[str]) -> None:
    """Chop output to fit on screen"""

    # Form Shell Args Parser

    doc = HT_DOC
    parser = AmpedArgumentParser(doc, add_help=False)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    parser.parse_args_if(args)  # often prints help & exits zero

    # Chop output to fit on screen

    ilines = alt.stdin.readlines()
    n = len(ilines)

    if n < (3 + 3 + 2):
        otext = line_break_join_rstrips_plus_if(ilines)
        alt.stdout.write_text(otext)
        return

    olines = ilines[:3] + ["...", f"... 3+2 of {n} Lines shown ...", "..."] + ilines[-2:]
    otext = line_break_join_rstrips_plus_if(olines)
    alt.stdout.write_text(otext)

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


def do_jq(argv: list[str]) -> None:
    """Drop the Style out of Json Data"""

    # Form Shell Args Parser

    doc = JQ_DOC
    parser = AmpedArgumentParser(doc, add_help=False)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    parser.parse_args_if(args)  # often prints help & exits zero

    # Drop the Style out of Json Data

    itext = alt.stdin.read_text()
    j = json.loads(itext)
    otext = json.dumps(j, indent=2, ensure_ascii=False) + "\n"

    olines = otext.splitlines()
    otext_ = line_break_join_rstrips_plus_if(olines)
    assert otext == otext_, (otext, otext_)

    alt.stdout.write_text(otext)


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

    parser = AmpedArgumentParser(doc, add_help=False)
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

    # Number the Lines

    ilines = alt.stdin.readlines()

    olines = list()
    for n_plus_index, iline in enumerate(ilines, start=n):
        oline = f"{n_plus_index:6}  {iline}"
        olines.append(oline)

    otext = line_break_join_rstrips_plus_if(olines)
    alt.stdout.write_text(otext)


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
    parser = AmpedArgumentParser(doc, add_help=False)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    parser.parse_args_if(args)  # often prints help & exits zero

    # Change the order of Lines

    ilines = alt.stdin.readlines()

    olines = list(ilines)  # todo: aka:  olines = list(reversed(ilines))
    olines.reverse()

    otext = line_break_join_rstrips_plus_if(olines)
    alt.stdout.write_text(otext)


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
      ls -l |pbcopy && pq set c
      cat bin/xshverb.py|pq set c
      cat $(git ls-files) |pq set c

"""


def do_set(argv: list[str]) -> None:
    """List distinct Chars in sorted order"""

    # Form Shell Args Parser

    doc = SET_DOC
    parser = AmpedArgumentParser(doc, add_help=False)

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

    otext = line_break_join_rstrips_plus_if(olines)
    alt.stdout.write_text(otext)

    # todo: Control Chars other than the 5 "\t\n\f\r " kinds of Blanks


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

    parser = AmpedArgumentParser(doc, add_help=False)
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

    ilines = alt.stdin.readlines()

    if not numeric:
        olines = sorted(ilines)
    else:
        olines = sorted(ilines, key=keyfunc)

    if descending:
        olines.reverse()

    otext = line_break_join_rstrips_plus_if(olines)
    alt.stdout.write_text(otext)


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

    parser = AmpedArgumentParser(doc, add_help=False)
    parser.add_argument("--sep", metavar="SEP", help=sep_help)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    ns = parser.parse_args_if(args)  # often prints help & exits zero

    sep = None if (ns.sep is None) else ns.sep  # maybe empty

    # Break Lines apart into Words

    itext = alt.stdin.read_text()
    olines = itext.split(sep)  # raises ValueError("empty separator") when Sep is empty

    otext = line_break_join_rstrips_plus_if(olines)
    alt.stdout.write_text(otext)


#
# Drop leading and trailing Blanks, or the Chars of some other Set
#


STRIP_DOC = r"""

    usage: strip [--charset CHARSET]

    drop leading and trailing Blanks, or the Chars of some other Set

    options:
      --charset CHARSET  list the Chars to drop if found, preferably in sorted order

    comparable to:
      |sed 's,^  *,,g' |sed 's,  *$,,g'

    examples:
      echo '  a  b  ' |o |cat -etv
      echo '++a++b++' |o --chars='+' |cat -etv

"""


def do_strip(argv: list[str]) -> None:
    """Drop leading and trailing Blanks, or the Chars of some other Set"""

    # Form Shell Args Parser

    doc = STRIP_DOC
    charset_help = "list the Chars to drop if found, preferably in sorted order"

    parser = AmpedArgumentParser(doc, add_help=False)
    parser.add_argument("--charset", metavar="CHARSET", help=charset_help)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    ns = parser.parse_args_if(args)  # often prints help & exits zero

    charset = None if (ns.charset is None) else ns.charset  # maybe empty

    # Break Lines apart into Words

    ilines = alt.stdin.readlines()
    olines = list(_.strip(charset) for _ in ilines)  # drops enclosing Blanks when Sep is empty

    otext = line_break_join_rstrips_plus_if(olines)
    alt.stdout.write_text(otext)


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

    parser = AmpedArgumentParser(doc, add_help=False)
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

    assert n != 0, (n,)

    ilines = alt.stdin.readlines()
    olines = ilines[n:] if (n < 0) else ilines[(n - 1) :]

    otext = line_break_join_rstrips_plus_if(olines)
    alt.stdout.write_text(otext)


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
      ls -l |pq  w  c
      ls -l |pq  wcl  c

"""


def do_wcl(argv: list[str]) -> None:
    """Count the Lines"""

    # Form Shell Args Parser

    doc = WCL_DOC
    parser = AmpedArgumentParser(doc, add_help=False)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    parser.parse_args_if(args)  # often prints help & exits zero

    # Count the Lines

    ilines = alt.stdin.readlines()
    oint = len(ilines)
    otext = str(oint)

    alt.stdout.write_text(otext)


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

    parser = AmpedArgumentParser(doc, add_help=False)
    parser.add_argument("--sep", metavar="SEP", help=sep_help)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    ns = parser.parse_args_if(args)  # often prints help & exits zero

    sep = " " if (ns.sep is None) else ns.sep  # maybe empty

    # Join the Lines into a single Line

    ilines = alt.stdin.readlines()
    otext = sep.join(ilines) + "\n"  # deletes Line-Break's when Sep is empty

    alt.stdout.write_text(otext)

    # can end Lines with Blanks when given Blanks in Sep


#
# Mess about inside the Os/Copy Paste Buffer
#


PQ_DOC = r"""
usage: pq [HINT ...]

mess about inside the Os/Copy Paste Buffer

positional arguments:
  HINT  hint of which Shell Pipe Filter you mean

quirks:
  defaults to decode the Bytes as UTF-8, replacing decoding errors with U+003F '?' Question-Mark's
  defaults to dedent the Lines, strip trailing Blanks from each Line, and end with 1 Line-Break
  more help at:  xshverb.py --help

examples:
  pq  # dedents and strips the Os/Copy Paste Buffer, first to Tty Out, and then to replace itself
  pq .  # guesses what edit you want in the Os/Copy Paste Buffer and runs ahead to do it
  pq v  # dedents and strips the Os/Copy Paste Buffer, and then calls Vim to edit it
  echo $'\xC0\x80' |pq |sort  # doesn't deny service to shout up "illegal byte sequence"
"""

XSHVERB_DOC = PQ_DOC

# "There is nothing -- absolutely nothing -- half so much worth doing as simply messing about in ..." ~ Kenneth Grahame


def do_xshverb(argv: list[str]) -> None:  # def do_pq  # def do_p
    """Mess about inside the Os/Copy Paste Buffer"""

    # Form Shell Args Parser

    doc = XSHVERB_DOC
    hint_help = "hint of which Shell Pipe Filter you mean"

    parser = AmpedArgumentParser(doc, add_help=False)
    parser.add_argument(dest="hints", metavar="HINT", nargs="*", help=hint_help)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    ns = parser.parse_args_if(args)  # often prints help & exits zero

    if ns.hints:
        parser.parser.print_usage()
        eprint(f"|pq: {ns.hints!r}: no such Shell Pipe Filters yet")
        sys.exit(2)  # exits 2 for bad Args

    # Dedents and strip the Os/Copy Paste Buffer, first to Tty Out, and then to replace itself

    assert unicodedata.lookup("Replacement Character") == "\ufffd"

    ibytes = alt.stdin.read_bytes()
    decode = ibytes.decode(errors="replace")  # not errors="surrogateescape"
    itext = decode.replace("\ufffd", "?")

    dedent = textwrap.dedent(itext)
    strip = dedent.strip()
    olines = strip.splitlines()

    otext = line_break_join_rstrips_plus_if(olines)
    alt.stdout.write_text(otext)

    # Say what the most plain Undirected Pq without Args means

    if (alt.index == 0) and (alt.rindex == -1):
        if alt.sys_stdin_isatty and alt.sys_stdout_isatty:

            # Dedent & strip & replace, first to Tty, and then to Pipe

            sys.stdout.write(otext)


#
# Amp up Import ArgParse
#


class AmpedArgumentParser:
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


def argv_parse_if(parser: AmpedArgumentParser, argv: list[str]) -> argparse.Namespace:
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
# Amp up Import BuiltsIns Str
#


def line_break_join_rstrips_plus_if(lines: list[str]) -> str:
    """Convert Lines to Chars but strip trailing Blanks off each Line"""

    rstrips = list(_.rstrip() for _ in lines)
    join = "\n".join(rstrips)
    plus_if = (join + "\n") if join else ""

    return plus_if  # maybe empty  # maybe starts with or ends with Empty Lines


#
# Amp up Import DateTime as DT
#


def dt_timedelta_strftime(td: dt.timedelta, depth: int = 1, str_zero: str = "0s") -> str:
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

    return chars  # such as '346ms' to mean 0.346 <= t <= 0.347


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
# Index the Doc and Func of each main Shell Verb
#


assert __doc__, (__doc__,)

DOC_BY_VERB = dict(
    awk=AWK_DOC,
    cat=CAT_DOC,
    counter=COUNTER_DOC,
    dt=DT_DOC,
    expand=EXPAND_DOC,
    grep=GREP_DOC,
    head=HEAD_DOC,
    ht=HT_DOC,
    jq=JQ_DOC,
    nl=NL_DOC,
    reverse=REVERSE_DOC,
    set=SET_DOC,
    sort=SORT_DOC,
    split=SPLIT_DOC,
    strip=STRIP_DOC,
    tail=TAIL_DOC,
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
    dt=do_dt,
    expand=do_expand,
    grep=do_grep,
    head=do_head,
    ht=do_ht,
    jq=do_jq,
    nl=do_nl,
    reverse=do_reverse,
    set=do_set,
    sort=do_sort,
    split=do_split,
    strip=do_strip,
    tail=do_tail,
    wcl=do_wcl,
    xargs=do_xargs,
    xshverb=do_xshverb,
)


VERB_BY_VB = {  # lists the abbreviated or unabbreviated Aliases of each Shell Verb
    "a": "awk",
    "c": "cat",
    "dict": "counter",
    "g": "grep",
    "h": "head",
    "i": "split",
    "j": "jq",
    "len": "wcl",
    "n": "nl",
    "o": "strip",
    "p": "xshverb",
    "pq": "xshverb",  # |pq in homage of |jq, not |py and not |python
    "r": "reverse",
    "s": "sort",
    "t": "tail",
    "u": "counter",
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


alt = ShellPipe()


#
# Run from the Sh Command Line, if not imported
#


if __name__ == "__main__":
    main()


# todo: pq .  # guesses what edit you want in the Os/Copy Paste Buffer and runs ahead to do it


# todo: + |y is to show what's up and halt till you say move on

# todo: + |e is for **Emacs**, but inside the Terminal with no Menu Bar and no Splash
# todo: + |k is for **Less** of the '|tee >(less -FIRX)' kind because |l and |m were taken
# todo: + |v is for **Vi** but default to edit the Os Copy/Paste Buffer, same as at |e

# todo: + m is for **Make**, but timestamp the work and never print the same Line twice

# todo: + q is for **Git**, because G was taken

# todo: + d is for **Diff**, but default to '|diff -brpu a b'
# todo: + f is for **Find**, but default to search $PWD spelled as ""
# todo: + l is for **Ls** of the '|ls -dhlAF -rt' kind, not more popular less detailed '|ls -CF'


# todo: |p ascii and |p repr without so many quotes in the output


# 3456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789


# posted as:  https://github.com/pelavarre/xshverb/blob/main/bin/xshverb.py
# copied from:  git clone https://github.com/pelavarre/xshverb.git
