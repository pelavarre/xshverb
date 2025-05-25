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
  defaults to strip trailing Blanks from each Line
  defaults to end with 1 Line-Break
  docs the [-h] and [-V] options only here, not again and again for every different Hint
  more doc at https://github.com/pelavarre/xshverb

most common Python words:
  bytes decode dedent encode join list lower replace str title upper

python examples:
  p lower  # convert the Os/Copy Paste Buffer to lower case
  p lower c  # preview changes without saving changes
  p str strip  # drop leading/ trailing Blank Lines but leave all Blanks inside unchanged
  p bytes lower  # change Bytes without first stripping off the Blanks
  p join --sep=.  # join Lines into a single Line, with a Dot between each Line

most common Shell words:
  awk b cat diff emacs find grep head str.split jq less ls make
  nl for.str.strip python git reversed sorted tail unique vi w xargs yes z

examples:
  bin/xshverb.py  # shows these examples and exit
  git show |i  u  s -nr  h  c  # shows the most common words in the last Git Commit
  a --help  # shows the Help Doc for the Awk Shell Verb
  p  # chats with Python, and doesn't make you spell out the Imports, or builds & runs a Shell Pipe
  v  # fixes up the Os/Copy Paste Buffer and calls Vim to edit it
"""

# todo: --py to show the Python chosen, --py=... to supply your own Python
# todo: make a place for:  column -t, fmt --ruler, tee, tee -a, etc

# FIXME: drop all the 'p' out of the ShPump module_rindex/_index, unless Pipe of only P


# code reviewed by People, Black, Flake8, MyPy-Strict, & PyLance-Standard


import argparse
import collections.abc
import dataclasses
import difflib
import hashlib
import math
import os
import pathlib
import shlex
import subprocess
import sys
import textwrap


YYYY_MM_DD = "2025-05-25"  # date of last change to this Code, or an earlier date


if not __debug__:
    raise NotImplementedError(str((__debug__,)))  # "'python3' is better than 'python3 -O'"


def main() -> None:
    p = ShellPipe()
    p.shpipe_main(sys.argv)


ShellFunc = collections.abc.Callable[[list[str]], None]


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

    def write(self, text: str) -> int:
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


module_index = -1  # ShellPump's place in the Pipe, counting forward from the start
module_rindex = 0  # ShellPump's place in the Pipe, counting back from the end
module_stdin = ShellFile()  # ShellPump's read from .stdin
module_stdout = ShellFile()  # ShellPump's write to .stdout


@dataclasses.dataclass  # (order=False, frozen=False)
class ShellPump:  # much like a Linux Process
    """Work to drain 1 ShellFile and fill the next ShellFile"""

    vb: str  # 'p'
    verb: str  # 'python'
    func: ShellFunc  # do_awk  # do_python
    argv: list[str]  # ['p', '--version']

    verb_by_vb = {  # lists the abbreviated or unabbreviated Aliases of each Shell Verb
        "a": "awk",
        "c": "cat",
        "h": "head",
        "i": "split",
        "p": "python",
        "s": "sort",
        "u": "counter",
        "xshverb": "python",
        "xshverb.py": "python",
    }

    def __init__(self, hints: list[str], func_by_verb: dict[str, ShellFunc]) -> None:
        """Parse a Hint, else show Help and exit"""

        assert hints, (hints,)

        verb_by_vb = self.verb_by_vb

        # Pop the Shell Verb, and zero or more Dashed Options

        argv = list()
        while hints:
            arg = hints.pop(0)
            argv.append(arg)  # may be '--', and may be '--' more than once

            if hints:
                peek = hints[0]
                if peek.isidentifier():  # not any '-' or '--' option, nor 'a|b' etc etc
                    break

        # Require an Alias of a Shell Verb, or the Shell Verb itself

        vb = argv[0]

        verb = vb
        if vb in verb_by_vb.keys():
            verb = verb_by_vb[vb]  # Aliases are often shorter than their Shell Verbs

        if verb not in func_by_verb.keys():
            text = f"xshverb: command not found: {vb}"  # a la Bash & Zsh vs New Verbs
            eprint(text)
            sys.exit(2)  # exits 2 for bad Shell Verb

        func = func_by_verb[verb]

        # Succeed

        self.vb = vb
        self.verb = verb
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

        vb = self.vb
        verb = self.verb

        verb_doc = DOCS_BY_VERB[verb]

        key = "usage: xshverb.py "
        text = textwrap.dedent(verb_doc).strip()
        if text.startswith(key) and (vb != "xshverb.py"):
            count_eq_1 = 1
            text = text.replace(key, f"usage: {vb} ", count_eq_1)

        print(text)

    def do_show_version(self) -> None:
        """Show version and exit zero"""

        version = pathname_read_version(__file__)

        print(YYYY_MM_DD, version)


class ShellPipe:
    """Pump Bytes through a pipe of Shell Pumps"""

    func_by_verb: dict[str, ShellFunc]

    def __init__(self) -> None:

        verbs = list(DOCS_BY_VERB.keys())

        self.func_by_verb = dict(
            awk=do_awk,
            cat=do_cat,
            counter=do_counter,
            head=do_head,
            python=do_little,
            sort=do_sort,
            split=do_split,
        )

        verbs_ = list(self.func_by_verb.keys())

        diffs = list(difflib.unified_diff(a=verbs, b=verbs_, lineterm=""))
        assert not diffs, (diffs,)

    def shpipe_main(self, argv: list[str]) -> None:
        """Run from the Sh Command Line"""

        global module_index, module_rindex, module_stdin, module_stdout

        shpumps = self.parse_shpipe_args_if(argv)

        module_stdout = ShellFile()  # adds or replaces
        for index, shpump in enumerate(shpumps):
            module_index = index
            module_rindex = index - len(shpumps)

            module_stdin = module_stdout
            module_stdout = ShellFile()  # adds or replaces

            argv = shpump.argv
            shpump.func(argv)  # two positional args, zero keyword args

        module_stdout.drain_if()

    def parse_shpipe_args_if(self, argv: list[str]) -> list[ShellPump]:
        """Parse Args, else show Version or Help and exit"""

        hints = list(argv)
        hints[0] = os.path.basename(argv[0])  # 'xshverb.py' from 'bin/xshverb.py'

        func_by_verb = self.func_by_verb

        shpumps = list()
        while hints:
            shpump = ShellPump(hints, func_by_verb=func_by_verb)  # exits 2 for bad Hints
            shpump.exit_help_or_exit_version_if()
            shpumps.append(shpump)

        return shpumps


def do_little(argv: list[str]) -> None:
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
      rounds down Float Numbers to Ints, even 0.123 to 0
      applies Python Str Split Rules to separate the Words

    unlike classic Awk:
      takes negative Numbers as counting back from the end, not ahead from the start
      default to Double Space, not Single Space, as its Output Sep
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

    numbers = list(int(_) for _ in ns.numbers)  # rounds down Floats, even to 0, as Awk does
    if not numbers:
        numbers = [-1]

    # Pick one or more Columns of Words, and drop the rest

    olines = list()
    ilines = module_stdin.readlines()

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

    otext = line_break_join_rstrips_plus(olines)
    module_stdout.write(otext)


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
      bin/c a && pbpaste |cat -etv  # type your own Lines to chop down to their last Word
      ls -l |bin/a c  # see what Awk would push into the Os Copy/Paste Buffer, without pushing it

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

    if module_index == 0:
        if sys.stdin.isatty():
            eprint(
                "Start typing"
                + ". Press Return after each Line"
                + ". Press ⌃D to continue, or ⌃C to quit"
            )
        module_stdin.fill_from_stdin()

    # Strip trailing Blanks off each Line

    ilines = module_stdin.readlines()
    otext = line_break_join_rstrips_plus(ilines)
    module_stdout.write(otext)

    # Write to Stdout Tty at end of Pipe

    if module_rindex == -1:
        module_stdout.drain_to_stdout()


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
      ls -l |bin/i  u  # counts each Word, prints Lines of Count Tab Text
      ls -l |bin/i  counter --keys  c  # prints each Word once

"""

# todo: |counter --tsv to write Tab as O Sep
# todo: abbreviate as |i co -k, as |i cou -k, etc


def do_counter(argv: list[str]) -> None:
    """Count or drop duplicate Lines, no sort required"""

    # Form Shell Args Parser

    doc = COUNTER_DOC
    parser = AmpedArgumentParser(doc, add_help=False)

    keys_help = "print each distinct Line when it first arrives, without a count (default: False)"
    parser.add_argument("-k", "--keys", action="count", help=keys_help)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    ns = parser.parse_args_if(args)  # often prints help & exits zero

    # Break Lines apart into Words

    ilines = module_stdin.readlines()
    counter = collections.Counter(ilines)

    if ns.keys:
        olines = list(counter.keys())
    else:
        olines = list(f"{v:6}  {k}" for k, v in counter.items())

        # f"{v:6}\t{k}" with its sometimes troublesome \t is classic '|cat -n' format

    otext = line_break_join_rstrips_plus(olines)
    module_stdout.write(otext)


#
# Take only the first few Lines
#


HEAD_DOC = """

    usage: head

    take only the first few Lines

    comparable to:
      |head -$((LINES / 3))

    examples:
      ls -l |bin/i  u |sort -nr  |h  # prints some most common Words

"""

# todo: |h -123
# todo: default to $((LINES / 3)) not down to 10


def do_head(argv: list[str]) -> None:
    """Take only the first few Lines"""

    # Form Shell Args Parser

    doc = HEAD_DOC
    parser = AmpedArgumentParser(doc, add_help=False)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    parser.parse_args_if(args)  # often prints help & exits zero

    # Break Lines apart into Words

    ilines = module_stdin.readlines()
    olines = ilines[:10]

    otext = line_break_join_rstrips_plus(olines)
    module_stdout.write(otext)


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
      ls -l |bin/i  u  # counts each Word, prints Lines of Count Tab Text
      ls -l |bin/i  counter --keys  c  # prints each Word once

"""

# todo: --nulls=last, --nulls=first
# todo: -V, --version-sort, --sort=version  # classic 'man sort' doesn't meantion '--sort=version'
# todo: random.shuffle


def do_sort(argv: list[str]) -> None:
    """Change the order of Lines"""

    # Form Shell Args Parser

    doc = SORT_DOC
    parser = AmpedArgumentParser(doc, add_help=False)

    n_help = "sort as numbers, from least to most positive, but nulls last (default: sort as text)"
    r_help = "reverse the sort (default: ascending)"

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

    ilines = module_stdin.readlines()

    if not numeric:
        olines = sorted(ilines)
    else:
        olines = sorted(ilines, key=keyfunc)

    if descending:
        olines.reverse()

    otext = line_break_join_rstrips_plus(olines)
    module_stdout.write(otext)


#
# Break Lines apart into Words
#


SPLIT_DOC = r"""

    usage: split

    break Lines apart into Words

    comparable to:
      |tr ' \t' '\n' |grep .

    examples:
      ls -l |bin/i c

"""

# todo: split --sep=


def do_split(argv: list[str]) -> None:
    """Break Lines apart into Words"""

    # Form Shell Args Parser

    doc = SPLIT_DOC
    parser = AmpedArgumentParser(doc, add_help=False)

    # Take up Shell Args

    args = argv[1:] if argv[1:] else ["--"]  # ducks sending [] to ask to print Closing
    parser.parse_args_if(args)  # often prints help & exits zero

    # Break Lines apart into Words

    itext = module_stdin.read_text()
    olines = itext.split()

    otext = line_break_join_rstrips_plus(olines)
    module_stdout.write(otext)


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
# Amp up Import BuiltsIns Str
#


def line_break_join_rstrips_plus(lines: list[str]) -> str:
    """Convert Lines to Chars but strip trailing Blanks off each Line"""

    rstrips = list(_.rstrip() for _ in lines)
    join = "\n".join(rstrips)
    plus = join + "\n"

    return plus  # maybe starts with or ends with Empty Lines


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
# Index the Main Doc's of each Shell Verb
#


assert __doc__, (__doc__,)
DOCS_BY_VERB: dict[str, str] = dict()

DOCS_BY_VERB["awk"] = AWK_DOC
DOCS_BY_VERB["cat"] = CAT_DOC
DOCS_BY_VERB["counter"] = COUNTER_DOC
DOCS_BY_VERB["head"] = HEAD_DOC
DOCS_BY_VERB["python"] = __doc__
DOCS_BY_VERB["sort"] = SORT_DOC
DOCS_BY_VERB["split"] = SPLIT_DOC

for _K_ in DOCS_BY_VERB.keys():
    DOCS_BY_VERB[_K_] = textwrap.dedent(DOCS_BY_VERB[_K_]).strip()


#
# Run from the Sh Command Line, if not imported
#


if __name__ == "__main__":
    main()


# todo: |p should default to errors="replace" and .replace("\ufffd", "?")


# 3456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789


# posted as:  https://github.com/pelavarre/xshverb/blob/main/bin/xshverb.py
# copied from:  git clone https://github.com/pelavarre/xshverb.git
