#!/usr/bin/env python3

r"""
usage: plus.py --

do what's popular now

examples:
  bin/+
  bin/plus.py --yolo
"""

# code reviewed by People, Black, Flake8, MyPy-Strict, & PyLance-Standard


from __future__ import annotations  # backports new datatype syntaxes into old Pythons

import collections.abc
import datetime as dt
import os
import pathlib
import pdb
import select
import signal
import sys
import termios
import textwrap
import tty
import types
import typing

if not __debug__:
    raise NotImplementedError([__debug__])  # refuses to run without live Asserts


#
# Exit nonzero into the Pdb-Pm Post-Mortem Debugger, when not KeyboardInterrupt nor SystemExit
#


with_exc_hook = sys.excepthook  # aliases old hook, and fails fast to chain hooks
assert with_exc_hook.__module__ == "sys", (with_exc_hook.__module__,)
assert with_exc_hook.__name__ == "excepthook", (with_exc_hook.__name__,)

assert sys.__stderr__ is not None  # refuses to run headless
with_stderr = sys.stderr
with_tcgetattr = termios.tcgetattr(sys.__stderr__.fileno())


assert int(0x80 + signal.SIGINT) == 130  # discloses the Nonzero Exit Code for after ⌃C SigInt


def excepthook(
    exc_type: type[BaseException],
    exc_value: BaseException,
    exc_traceback: types.TracebackType | None,
) -> None:

    # Clean up after Terminal Writes, if need be

    with_stderr.write("\x1b[m")  # clears Select Graphic Rendition (SGR)

    when = termios.TCSADRAIN
    attributes = with_tcgetattr  # undoes tty.setraw
    termios.tcsetattr(with_stderr.fileno(), when, attributes)

    # Quit now for visible cause, if KeyboardInterrupt

    if exc_type is KeyboardInterrupt:
        with_stderr.write("KeyboardInterrupt\n")
        sys.exit(130)  # 0x80 + signal.SIGINT

    # Print the Traceback, etc

    with_exc_hook(exc_type, exc_value, exc_traceback)

    # Launch the Post-Mortem Debugger

    print(">>> pdb.pm()", file=with_stderr)
    pdb.pm()


sys.excepthook = excepthook


#
# Run from the Shell Command Line
#


def main() -> None:
    """Run from the Shell Command Line, and exit into the Py Repl"""

    if os.path.basename(sys.argv[0]) != "+":
        assert sys.argv[1:], sys.argv
        assert "--plus".startswith(sys.argv[1]) and sys.argv[1].startswith("--"), sys.argv

    # Emulate having imported the enclosing Module as ./plus.py

    assert "plus" not in sys.modules.keys()
    plus = sys.modules["__main__"]
    sys.modules["plus"] = plus

    # Land the Repl into a small new Module of its own

    module = types.ModuleType("plus.repl")
    sys.modules["__main__"] = module

    d = vars(module)

    d["__file__"] = __file__  # almost correct
    d["__main__"] = module
    d["plus"] = plus

    d["tryme"] = tryme

    # Launch the Py Repl at Process Exit, as if:  python3 -i -c ''

    os.environ["PYTHONINSPECT"] = str(True)

    print("To get started, press Return after typing:  tryme()", file=sys.stderr)
    print(">>> ", file=sys.stderr)
    print(">>> tryme()", file=sys.stderr)
    tryme()
    print(">>> ", file=sys.stderr)


def tryme() -> None:
    """Run when called"""

    func = try_tbp_self_test
    func = try_take_one_if
    func = try_read_byte_packet
    func = try_buffered_loopback
    func = try_screen_editor

    func = try_screen_editor  # last choice wins

    func()


def try_screen_editor() -> None:
    """Loop Keyboard back to Screen, but as whole Packets, & with some emulations"""

    with ScreenEditor() as se:
        se.loopback_awhile()


def try_buffered_loopback() -> None:
    """Loop Keyboard back to Screen, but as whole Packets"""

    with BytesTerminal() as bt:
        fileno = bt.fileno
        while True:
            tbp = bt.read_byte_packet(timeout=None)
            kdata = tbp.to_bytes()
            os.write(fileno, kdata)
            if kdata == b"\r":
                break


def try_read_byte_packet() -> None:
    """Loop over BytesTerminal Read_Byte_Packet"""

    with BytesTerminal() as bt:
        stdio = bt.stdio
        while True:
            tbp = bt.read_byte_packet(timeout=None)
            data = tbp.to_bytes()

            print(tbp, end="\r\n", file=stdio)

            if data == b"\r":
                break


def try_take_one_if() -> None:
    """Loop over TerminalBytePacket Take_One_If"""

    with BytesTerminal() as bt:
        stdio = bt.stdio
        fileno = bt.fileno

        data = b""
        extras = b""
        while True:
            tbp = TerminalBytePacket(extras)

            while True:
                byte = os.read(fileno, 1)
                print(1, byte, file=stdio, end="\r\n")

                extras = tbp.take_one_if(byte)
                data = tbp.to_bytes()
                print(2, tbp, file=stdio, end="\r\n")

                if extras:
                    print(3, f"{extras=}", file=stdio, end="\r\n")
                    tbp.close()
                elif not bt.kbhit(timeout=0.000):
                    tbp.close()

                if tbp.closed:
                    break

            print(file=stdio, end="\r\n")

            if data == b"\r":
                break


def try_tbp_self_test() -> None:
    """Try Tests of Class TerminalBytePacket"""

    tbp = TerminalBytePacket()

    t0 = dt.datetime.now()
    tbp._try_()
    t1 = dt.datetime.now()

    print(t0)
    print(t1 - t0)


#
# Loop Keyboard back to Screen, but as whole Packets, & with some emulations
#


CR = "\r"  # 00/13 Carriage Return  # akin to CSI CHA "\x1B" "[" "G"
LF = "\n"  # 00/10 Line Feed ⌃J  # akin to CSI CUD "\x1B" "[" "B"

CUU_Y = "\x1b" "[" "{}A"  # CSI 04/01 Cursor Up
CUP_Y_X = "\x1b" "[" "{};{}H"  # CSI 04/08 Cursor Position

MAX_PN_32100 = 32100  # an Int beyond the Counts of Rows & Columns at any Terminal


class ScreenEditor:
    """Loop Keyboard back to Screen, but as whole Packets, & with some emulations"""

    keyboard_bytes_log: typing.BinaryIO
    screen_bytes_log: typing.BinaryIO
    bytes_terminal: BytesTerminal
    func_by_kdata: dict[bytes, collections.abc.Callable[[TerminalBytePacket], None]] = dict()

    def __init__(self) -> None:

        klog_path = pathlib.Path("__pycache__/k.keyboard")
        slog_path = pathlib.Path("__pycache__/s.screen")

        klog_path.parent.mkdir(exist_ok=True)
        slog_path.parent.mkdir(exist_ok=True)

        klog = klog_path.open("ab")
        slog = slog_path.open("ab")
        bt = BytesTerminal()

        func_by_kdata = {
            b"\x1bOP": self.do_kdata_fn_f1,
        }

        self.keyboard_bytes_log = klog
        self.screen_bytes_log = slog
        self.bytes_terminal = bt
        self.func_by_kdata = dict(func_by_kdata)  # MyPy needs Dict

    def __enter__(self) -> ScreenEditor:  # -> typing.Self:
        r"""Stop line-buffering Input, stop replacing \n Output with \r\n, etc"""

        bt = self.bytes_terminal
        klog = self.keyboard_bytes_log
        slog = self.screen_bytes_log

        # Enter each

        bt.__enter__()
        klog.__enter__()
        slog.__enter__()

        # Succeed

        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        r"""Start line-buffering Input, start replacing \n Output with \r\n, etc"""

        bt = self.bytes_terminal
        klog = self.keyboard_bytes_log
        slog = self.screen_bytes_log

        fileno = bt.fileno

        assert CUU_Y == "\x1b" "[" "{}A"
        assert CUP_Y_X == "\x1b" "[" "{};{}H"
        assert MAX_PN_32100 == 32100

        # Exit via 1st Column of 1 Row above the Last Row

        sdata = b"\x1b[32100H" + b"\x1b[A"
        os.write(fileno, sdata)

        # Exit each, in reverse order of Enter's

        slog.__exit__(exc_type, exc_val, exc_tb)
        klog.__exit__(exc_type, exc_val, exc_tb)
        bt.__exit__(exc_type, exc_val, exc_tb)

        # Succeed

        return None

    def print(self, *args: object, end: str = "\r\n") -> None:

        bt = self.bytes_terminal
        stdio = bt.stdio

        print(*args, end=end, file=stdio)

    def loopback_awhile(self) -> None:
        """Loop Keyboard back to Screen, but as whole Packets, & with some emulations"""

        bt = self.bytes_terminal
        func_by_kdata = self.func_by_kdata
        klog = self.keyboard_bytes_log
        slog = self.screen_bytes_log

        fileno = bt.fileno

        self.print("Press ⌃D to quit, else Fn F1 for help, else see what happens")

        kba = bytearray()
        while True:
            tbp = bt.read_byte_packet(timeout=None)  # todo: log & echo the Bytes as they arrive
            kdata = tbp.to_bytes()

            kba.extend(kdata)  # todo: .kba grows without end
            klog.write(kdata)

            if kdata not in func_by_kdata.keys():

                sdata = kdata
                os.write(fileno, sdata)  # todo: make unwanted Control Characters visible
                slog.write(sdata)

            else:

                func = func_by_kdata[kdata]

                try:
                    func(tbp)
                except SystemExit:
                    break

            if kba.endswith(b"\x04"):  # ⌃D
                raise SystemExit()

            # todo: quit in many of the Emacs & Vim ways, including Vim ⌃C :vi ⇧Z ⇧Q

    def do_kdata_fn_f1(self, tbp: TerminalBytePacket) -> None:

        help = textwrap.dedent(SCREEN_EDITOR_HELP).strip()

        self.print()
        self.print()

        for line in help.splitlines():
            self.print(line)

        self.print()
        self.print()


SCREEN_EDITOR_HELP = r"""

    Keycap's here are ⎋ Esc, ⌃ Control, ⌥ Option/ Alt, ⇧ Shift, ⌘ Command/ Os

    The best-known forms of Csi are ⎋[ ⇧ @ABCDEGHIJKLMPSTZ & dhlmqt

        ⎋[⇧A ↑  ⎋[⇧B ↓  ⎋[⇧C →  ⎋[⇧D ←
        ⎋[I Tab  ⎋[⇧Z ⇧Tab
        ⎋[d row-go  ⎋[⇧G column-go  ⎋[⇧H row-column-go

        ⎋[⇧M rows-delete  ⎋[⇧L rows-insert  ⎋[⇧P chars-delete  ⎋[⇧@ chars-insert
        ⎋[⇧J after-erase  ⎋[1⇧J before-erase  ⎋[2⇧J screen-erase  ⎋[3⇧J scrollback-erase
        ⎋[⇧K row-tail-erase  ⎋[1⇧K row-head-erase  ⎋[2⇧K row-erase
        ⎋[⇧T scrolls-down  ⎋[⇧S scrolls-up

        ⎋[4h insert  ⎋[4l replace  ⎋[6 q bar  ⎋[4 q skid  ⎋[ q unstyled

        ⎋[1m bold, ⎋[3m italic, ⎋[4m underline, ⎋[7m reverse/inverse
        ⎋[31m red  ⎋[32m green  ⎋[34m blue  ⎋[38;5;130m orange
        ⎋[m plain

        ⎋[5n call for reply ⎋[0n
        ⎋[6n call for reply ⎋[{y};{x}⇧R  ⎋[18t call for reply ⎋[{rows};{columns}t
        ⎋[⇧E \r\n but never implies ⎋[⇧S

        ⎋['⇧} cols-insert  ⎋['⇧~ cols-delete

    Press ⌃D to quit, else Fn F1 for help, else see what happens

"""

# FIXME: ⎋[H⎋[J to clear screen


#
# Amp up Import Tty
#


BS = "\b"  # 00/08 ⌃H Backspace
HT = "\t"  # 00/09 ⌃I Character Tabulation
LF = "\n"  # 00/10 ⌃J Line Feed  # akin to ⌃K and CUD "\x1B" "[" "B"
CR = "\r"  # 00/13 ⌃M Carriage Return  # akin to CHA "\x1B" "[" "G"

ESC = "\x1b"  # 01/11  ⌃[ Escape  # often known as Shell printf '\e', but Python doesn't define \e

DECSC = "\x1b" "7"  # ESC 03/07 Save Cursor [Checkpoint] (DECSC)
DECRC = "\x1b" "8"  # ESC 03/08 Restore Cursor [Rollback] (DECRC)
SS3 = "\x1b" "O"  # ESC 04/15 Single Shift Three  # in macOS F1 F2 F3 F4

CSI = "\x1b" "["  # ESC 05/11 Control Sequence Introducer


class BytesTerminal:
    """Write/ Read Bytes at Screen/ Keyboard of the Terminal"""

    stdio: typing.TextIO
    fileno: int

    before: int  # for writing at Enter
    tcgetattr: list[int | list[bytes | int]]  # replaced by Enter
    after: int  # for writing at Exit  # todo: .TCSAFLUSH vs large Paste

    extras: bytearray  # Bytes from 'os.read' not yet returned inside some TerminalBytePacket

    #
    # Init, enter, exit, flush, and stop
    #

    def __init__(self) -> None:

        assert sys.__stderr__ is not None
        stdio = sys.__stderr__

        self.stdio = stdio
        self.fileno = stdio.fileno()

        self.before = termios.TCSADRAIN  # for writing at Enter
        self.tcgetattr = list()  # replaced by Enter
        self.after = termios.TCSADRAIN  # for writing at Exit  # todo: .TCSAFLUSH vs large Paste

        self.extras = bytearray()

    def __enter__(self) -> BytesTerminal:  # -> typing.Self:
        r"""Stop line-buffering Input, stop replacing \n Output with \r\n, etc"""

        fileno = self.fileno
        before = self.before
        tcgetattr = self.tcgetattr

        if tcgetattr:
            return self

        tcgetattr = termios.tcgetattr(fileno)  # replaces
        assert tcgetattr, (tcgetattr,)

        self.tcgetattr = tcgetattr  # replaces

        assert before in (termios.TCSADRAIN, termios.TCSAFLUSH), (before,)
        tty.setraw(fileno, when=before)  # Tty SetRaw defaults to TcsaFlush
        # tty.setcbreak(fileno, when=termios.TCSAFLUSH)  # for ⌃C prints Py Traceback

        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        r"""Start line-buffering Input, start replacing \n Output with \r\n, etc"""

        stdio = self.stdio
        fileno = self.fileno
        tcgetattr = self.tcgetattr
        after = self.after

        if not tcgetattr:
            return

        self.tcgetattr = list()  # replaces

        stdio.flush()  # for '__exit__' of BytesTerminal

        assert after in (termios.TCSADRAIN, termios.TCSAFLUSH), (after,)

        fd = fileno
        when = after
        attributes = tcgetattr
        termios.tcsetattr(fd, when, attributes)

        return None

    def kbhit(self, timeout: float | None) -> bool:
        """Block till next Input Byte, else till Timeout, else till forever"""

        fileno = self.fileno
        stdio = self.stdio
        assert self.tcgetattr, self.tcgetattr  # todo: kbhit can say readline won't block

        stdio.flush()  # for .kbhit of BytesTerminal

        (r, w, x) = select.select([fileno], [], [], timeout)
        hit = fileno in r

        return hit

        # 'timeout' is 0.000 for Now, None for Never, else count of Seconds

    def read_byte_packet(self, timeout: float | None) -> TerminalBytePacket:
        """Read 1 TerminalBytePacket"""

        stdio = self.stdio
        fileno = self.fileno
        extras = self.extras

        # Flush last of Output, before looking for Input

        stdio.flush()

        # Fetch 1 whole Packet of Input, else an empty Packet when no Bytes here already

        tbp = TerminalBytePacket()

        if self.kbhit(timeout=timeout):
            while self.kbhit(timeout=0.000):
                if not extras:
                    byte = os.read(fileno, 1)
                else:
                    pop = extras.pop(0)
                    byte = bytes([pop])

                more = tbp.take_one_if(byte)
                if more:
                    extras.extend(more)
                    break

                if tbp.closed:
                    break

        tbp.close()

        return tbp  # maybe empty


class TerminalBytePacket:
    """Hold 1 Control Character, else 1 or more Text Characters, else some Bytes"""

    text: str  # 0 or more Chars of Printable Text

    head: bytearray  # 1 Control Byte, else ⎋[, or ⎋O, or 3..6 Bytes starting with ⎋[M
    neck: bytearray  # CSI Parameter Bytes, in 0x30..0x3F (16 Codes)
    back: bytearray  # CSI Intermediate Bytes, in 0x20..0x2F (16 Codes)

    stash: bytearray  # 1..3 Bytes taken for now, in hope of decoding 2..4 Later
    tail: bytearray  # CSI Final Byte, in 0x40..0x7E (63 Codes)

    closed: bool = False  # closed because completed, or because continuation undefined

    #
    # Init, Bool, Repr, Str, and .require_simple to check invariants
    #

    def __init__(self, data: bytes = b"") -> None:

        # Init

        self.text = ""

        self.head = bytearray()
        self.neck = bytearray()
        self.back = bytearray()

        self.stash = bytearray()
        self.tail = bytearray()

        self._require_simple_()

        # Take in the Bytes, but require that they all fit

        extras = self.take_some_if(data)
        if extras:
            raise ValueError(extras)  # for example, raises the b'\x80' of b'\xC0\x80'

        self._require_simple_()

        # doesn't take bytes([0x80 | 0x0B]) as meaning b"\x1B\x5B" CSI ⎋[
        # doesn't take bytes([0x80 | 0x0F]) as meaning b"\x1B\x4F" SS3 ⎋O

    def __bool__(self) -> bool:
        truthy = bool(
            self.text or (self.head or self.neck or self.back) or (self.stash or self.tail)
        )
        return truthy  # no matter if .closed

    def __repr__(self) -> str:

        cname = self.__class__.__name__

        text = self.text

        head_ = bytes(self.head)  # reps bytearray(b'') loosely, as b''
        neck_ = bytes(self.neck)
        back_ = bytes(self.back)

        stash_ = bytes(self.stash)
        tail_ = bytes(self.tail)

        closed = self.closed

        s = f"text={text!r}, "
        s += f"head={head_!r}, neck={neck_!r}, back={back_!r}, stash={stash_!r}, tail={tail_!r}"
        s = f"{cname}({s}, {closed=})"

        return s

        # 'TerminalBytePacket(head=b'', back=b'', neck=b'', stash=b'', tail=b'', closed=False)'

    def __str__(self) -> str:

        text = self.text

        head_ = bytes(self.head)  # reps bytearray(b'') loosely, as b''
        neck_ = bytes(self.neck)
        back_ = bytes(self.back)

        stash_ = bytes(self.stash)
        tail_ = bytes(self.tail)

        if text:
            if stash_:
                return text + " " + str(stash_)
            return text

            # "abc b'\xc0'"

        if not head_:
            if stash_:
                return str(stash_)

                # "b'\xc0'"

        s = str(head_)
        if neck_:  # 'Parameter' Bytes
            s += " " + str(neck_)
        if back_ or stash_ or tail_:  # 'Intermediate' Bytes or Final Byte
            assert (not stash_) or (not tail_), (stash_, tail_)
            s += " " + str(back_ + stash_ + tail_)

        return s  # no matter if .closed

        # "b'\x1b[' b'6' b' q'"

    def to_bytes(self) -> bytes:
        """List the Bytes taken, as yet"""

        text = self.text
        head_ = bytes(self.head)
        neck_ = bytes(self.neck)
        back_ = bytes(self.back)
        stash_ = bytes(self.stash)
        tail_ = bytes(self.tail)

        b = text.encode()
        b += head_ + neck_ + back_ + stash_ + tail_

        return b  # no matter if .closed

    def _require_simple_(self) -> None:
        """Raise Exception if a mutation gone wrong has damaged Self"""

        text = self.text

        head = self.head
        neck = self.neck
        back = self.back

        stash = self.stash
        tail = self.tail

        closed = self.closed  # only via 'def close' if text or stash or not head

        if (not text) and (not head):
            assert (not tail) and (not closed), (tail, closed, stash, self)

        if text:
            assert not head, (head, text, self)
            assert (not neck) and (not back) and (not tail), (neck, back, tail, text, self)

        if head:
            assert not text, (text, head, self)
        if neck or back or tail:
            assert head, (head, neck, back, tail, self)
        if stash:
            assert not tail, (tail, closed, stash, self)
        if tail:
            assert closed, (closed, tail, self)

    #
    # Tests, to run slowly and thoroughly across like 211ms
    #

    def _try_(self) -> None:  # todo: add Code to call this slow thorough Self-Test
        """Try some Packets open to, or closed against, taking more Bytes"""

        # Try some Packets left open to taking more Bytes

        tbp = TerminalBytePacket(b"Superb")
        assert str(tbp) == "Superb" and not tbp.closed, (tbp,)

        self._try_open_(b"")  # empty
        self._try_open_(b"\x1b")  # first Byte of Esc Sequence
        self._try_open_(b"\x1b\x1b")  # first Two Bytes of Esc-Esc Sequence
        self._try_open_(b"\x1bO")  # first Two Bytes of Three-Byte SS3 Sequence
        self._try_open_(b"\x1b[", b"6", b" ")  # CSI Head with Neck and Back but no Tail
        self._try_open_(b"\xed\x80")  # Head of >= 3 Byte UTF-8 Encoding
        self._try_open_(b"\xf4\x80\x80")  # Head of >= 4 Byte UTF-8 Encoding
        self._try_open_(b"\x1b[M#\xff")  # Undecodable Head, incomplete CSI Mouse Report
        self._try_open_(b"\x1b[M \xc4\x8a")  # Head only, 6 Byte incomplete CSI Mouse Report

        # Try some Packets closed against taking more Bytes

        self._try_closed_(b"\n")  # Head only, of 7-bit Control Byte
        self._try_closed_(b"\x1b\x1b[", b"3;5", b"~")  # CSI Head with Neck and Tail, no Back
        self._try_closed_(b"\xc0")  # Head only, of 8-bit Control Byte
        self._try_closed_(b"\xff")  # Head only, of 8-bit Control Byte
        self._try_closed_(b"\xc2\xad")  # Head only, of 2 Byte UTF-8 of U+00AD Soft-Hyphen Control
        self._try_closed_(b"\x1b", b"A")  # Head & Text Tail of a Two-Byte Esc Sequence
        self._try_closed_(b"\x1b", b"\t")  # Head & Control Tail of a Two-Byte Esc Sequence
        self._try_closed_(b"\x1bO", b"P")  # Head & Text Tail of a Three-Byte SS3 Sequence
        self._try_closed_(b"\x1b[", b"3;5", b"H")  # CSI Head with Next and Tail
        self._try_closed_(b"\x1b[", b"6", b" q")  # CSI Head with Neck and Back & Tail

        # todo: test each Control Flow Return? test each Control Flow Branch?

    def _try_open_(self, *args: bytes) -> None:
        """Require the Eval of the Str of the Packet equals its Bytes"""

        tbp = self._try_bytes_(*args)
        assert not tbp.closed, (tbp,)

    def _try_closed_(self, *args: bytes) -> None:
        """Require the Eval of the Str of the Packet equals its Bytes"""

        tbp = self._try_bytes_(*args)
        assert tbp.closed, (tbp,)

    def _try_bytes_(self, *args: bytes) -> "TerminalBytePacket":
        """Require the Eval of the Str of the Packet equals its Bytes"""

        data = b"".join(args)
        join = " ".join(str(_) for _ in args)

        tbp = TerminalBytePacket(data)
        tbp_to_bytes = tbp.to_bytes()
        tbp_to_str = str(tbp)

        assert tbp_to_bytes == data, (tbp_to_bytes, data)
        assert tbp_to_str == join, (data, tbp_to_str, join)

        return tbp

    #
    # Close
    #

    def close(self) -> None:
        """Close, if not closed already"""

        head = self.head
        stash = self.stash
        closed = self.closed

        if closed:
            return

        self.closed = True

        head_plus = head + stash  # if closing a 6-Byte Mouse-Report that decodes to < 6 Chars
        if head_plus.startswith(b"\x1b[M"):
            try:
                decode = head_plus.decode()
                if len(decode) < 6:
                    if len(head_plus) == 6:

                        head.extend(stash)
                        stash.clear()

            except UnicodeDecodeError:
                pass

        self._require_simple_()

    #
    # Take in the Bytes and return 0 Bytes, else return the trailing Bytes that don't fit
    #

    def take_some_if(self, data: bytes) -> bytes:
        """Take in the Bytes and return 0 Bytes, else return the trailing Bytes that don't fit"""

        for index in range(len(data)):
            byte = data[index:][:1]
            after_bytes = data[index:][1:]

            extras = self.take_one_if(byte)
            if extras:
                return extras + after_bytes

        return b""  # maybe .closed, maybe not

    def take_one_if(self, byte: bytes) -> bytes:
        """Take in next 1 Byte and return 0 Bytes, else return 1..4 Bytes that don't fit"""

        extras = self._take_one_if_(byte)
        self._require_simple_()

        return extras

    def _take_one_if_(self, byte: bytes) -> bytes:
        """Take in next 1 Byte and return 0 Bytes, else return 1..4 Bytes that don't fit"""

        text = self.text
        head = self.head
        closed = self.closed

        # Decline Bytes after Closed

        if closed:
            return byte  # declines Byte after Closed

        # Take 1 Byte into Stash, if next Bytes could make it Decodable

        (stash_plus_decodes, stash_extras) = self._take_one_stashable_if(byte)
        assert len(stash_plus_decodes) <= 1, (stash_plus_decodes, stash_extras, byte)
        if not stash_extras:
            return b""  # holds 1..3 possibly Decodable Bytes in Stash

        # Take 1 Byte into Mouse Report, if next Bytes could close as Mouse Report

        mouse_extras = self._take_some_mouse_if_(stash_extras)
        if not mouse_extras:
            return b""  # holds 1..5 Undecodable Bytes, or 1..11 Bytes as 1..5 Chars as Mouse Report

        assert mouse_extras == stash_extras, (mouse_extras, stash_extras)

        # Take 1 Char into Text

        if stash_plus_decodes:
            printable = stash_plus_decodes.isprintable()
            if printable and not head:
                self.text += stash_plus_decodes
                return b""  # takes 1 Printable Char into Text, or as starts Text

        if text:
            return mouse_extras  # declines 1..4 Unprintable Bytes after Text

        # Take 1 Char into 1 Control Sequence

        control_extras = self._take_some_control_if_(stash_plus_decodes, data=mouse_extras)
        return control_extras

    def _take_one_stashable_if(self, byte: bytes) -> tuple[str, bytes]:
        """Take 1 Byte into Stash, if next Bytes could make it Decodable"""

        stash = self.stash
        stash_plus = bytes(stash + byte)

        try:
            decode = stash_plus.decode()
        except UnicodeDecodeError:
            decodes = self.any_decodes_startswith(stash_plus)
            if decodes:
                stash.extend(byte)
                return ("", b"")  # holds 1..3 possibly Decodable Bytes in Stash

            stash.clear()
            return ("", stash_plus)  # declines 1..4 Undecodable Bytes

        stash.clear()
        assert len(decode) == 1, (decode, stash, byte)

        return (decode, stash_plus)  # forwards 1..4 Decodable Bytes

    def any_decodes_startswith(self, data: bytes) -> str:
        """Return Say if these Bytes start 1 or more UTF-8 Encodings of Chars"""

        suffixes = (b"\x80", b"\xbf", b"\x80\x80", b"\xbf\xbf", b"\x80\x80\x80", b"\xbf\xbf\xbf")

        for suffix in suffixes:
            suffixed = data + suffix
            try:
                decode = suffixed.decode()
                assert len(decode) >= 1, (decode,)
                return decode
            except UnicodeDecodeError:
                continue

        return ""

        # b"\xC2\x80", b"\xE0\xA0\x80", b"\xF0\x90\x80\x80" .. b"\xF4\x8F\xBF\xBF"
        # todo: invent UTF-8'ish Encoding beyond 1..4 Bytes for Unicode Codes < 0x110000

    def _take_some_mouse_if_(self, data: bytes) -> bytes:
        """Take 1 Byte into Mouse Report, if next Bytes could close as Mouse Report"""

        assert data, (data,)

        head = self.head
        neck = self.neck
        back = self.back

        # Do take the 3rd Byte of this kind of CSI here, and don't take the first 2 Bytes here

        if (head == b"\x1b[") and (not neck) and (not back):
            if data == b"M":
                head.extend(data)
                return b""  # takes 3rd Byte of CSI Mouse Report here

        if not head.startswith(b"\x1b[M"):  # ⎋[M Mouse Report
            return data  # doesn't take the first 2 Bytes of Mouse Report here

        # Take 3..15 Bytes into a 3..6 Char Mouse Report

        head_plus = head + data
        try:
            head_plus_decode_if = head_plus.decode()
        except UnicodeDecodeError:
            head_plus_decode_if = ""

        if head_plus_decode_if:
            assert len(head_plus_decode_if) <= 6, (head_plus_decode_if, data)
            head.extend(data)
            if len(head_plus_decode_if) == 6:
                self.closed = True
            return b""  # takes 3..15 Bytes into a 6 Char Mouse Report

        # Take 4..15 Bytes into a 6 Byte Mouse Report

        if len(head_plus) > 6:  # 6..15 Bytes
            return data  # declines 2..4 Bytes into 5 of 6 Chars or into 5 of 6 Bytes

        head.extend(data)
        if len(head_plus) == 6:
            self.closed = True

        return b""  # takes 4..14 Bytes into a 6 Byte Mouse Report

    def _take_some_control_if_(self, decodes: str, data: bytes) -> bytes:
        """Take 1 Char into Control Sequence, else return 1..4 Bytes that don't fit"""

        assert data, (data,)

        head = self.head
        tail = self.tail
        closed = self.closed

        assert not tail, (tail,)
        assert not closed, (closed,)

        assert ESC == "\x1b"  # ⎋
        assert CSI == "\x1b" "["  # ⎋[
        assert SS3 == "\x1b" "O"  # ⎋O

        # Look only outside of Mouse Reports

        assert not head.startswith(b"\x1b[M"), (head,)  # Mouse Report

        # Look only at Undecodable, Unprintable, or Escaped Bytes

        printable = False
        assert len(decodes) <= 1, (decodes, data)
        if decodes:
            assert len(decodes) == 1, (decodes, data)
            printable = decodes.isprintable()
            assert head or not printable, (decodes, data, head, printable)

        # Take first 1 or 2 or 3 Bytes into Esc Sequences
        #
        #   ⎋ Esc  # ⎋⎋ Esc Esc
        #   ⎋O SS3  # ⎋⎋O Esc SS3
        #   ⎋[ CSI  # ⎋⎋[ Esc CSI
        #

        head_plus = bytes(head + data)
        if head_plus in (b"\x1b", b"\x1b\x1b", b"\x1b\x1bO", b"\x1b\x1b[", b"\x1bO", b"\x1b["):
            head.extend(data)
            return b""  # takes first 1 or 2 Bytes into Esc Sequences

        # Take & close 1 Unprintable Char or 1..4 Undecodable Bytes, as Head

        if not head:
            if not printable:
                head.extend(data)
                self.closed = True
                return b""  # takes & closes Unprintable Chars or 1..4 Undecodable Bytes

            # takes \b \t \n \r \x7F etc

        # Take & close 1 Escaped Printable Decoded Char, as Tail
        #
        #   ⎋ Esc  # ⎋⎋ Esc Esc
        #   ⎋O SS3  # ⎋⎋O Esc SS3
        #

        if bytes(head) in (b"\x1b", b"\x1b\x1b", b"\x1b\x1bO", b"\x1bO"):
            if printable:
                tail.extend(data)
                self.closed = True
                return b""  # takes & closes 1 Escaped Printable Decoded Char

            # Take & close Unprintable Chars or 1..4 Undecodable Bytes, as Escaped Tail

            tail.extend(data)  # todo: test of Unprintable/ Undecodable after ⎋O SS3
            self.closed = True
            return b""  # takes & closes Unprintable Chars or 1..4 Undecodable Bytes

            # does take ⎋\x10 ⎋\b ⎋\t ⎋\n ⎋\r ⎋\x7F etc

            # doesn't take bytes([0x80 | 0x0B]) as meaning b"\x1B\x5B" CSI ⎋[
            # doesn't take bytes([0x80 | 0x0F]) as meaning b"\x1B\x4F" SS3 ⎋O

        # Decline 1..4 Undecodable Bytes, when escaped by CSI or Esc CSI

        if not decodes:
            return data  # declines 1..4 Undecodable Bytes

        decode = decodes
        assert len(decodes) == 1, (decodes, data)
        assert data == decode.encode(), (data, decodes)

        # Take or don't take 1 Printable Char into CSI or Esc CSI Sequence

        esc_csi_extras = self._esc_csi_take_one_if_(decode)
        return esc_csi_extras  # maybe empty

    def _esc_csi_take_one_if_(self, decode: str) -> bytes:
        """Take 1 Char into CSI or Esc CSI Sequence, else return 1..4 Bytes that don't fit"""

        assert len(decode) == 1, decode
        ord_ = ord(decode)
        encode = decode.encode()

        head = self.head
        back = self.back
        neck = self.neck
        tail = self.tail
        closed = self.closed

        # Look only at unclosed CSI or Esc CSI Sequence

        assert CSI == "\x1b" "[", (CSI,)  # ⎋[
        if not head.startswith(b"\x1b\x1b["):  # ⎋⎋[ Esc CSI
            assert head.startswith(b"\x1b["), (head,)  # ⎋[ CSI

        assert not tail, (tail,)
        assert not closed, (closed,)

        # Decline 1..4 Bytes of Unprintable or Multi-Byte Char

        if ord_ > 0x7F:
            return encode  # declines 2..4 Bytes of 1 Unprintable or Multi-Byte Char

        # Accept 1 Byte into Back, into Neck, or as Tail

        byte = chr(ord_).encode()
        assert byte == encode, (byte, encode)

        if not back:
            if 0x30 <= ord_ < 0x40:  # 16 Codes
                neck.extend(byte)
                return b""  # takes 1 of 16 Parameter Byte Codes

        if 0x20 <= ord_ < 0x30:  # 16 Codes
            back.extend(byte)
            return b""  # takes 1 of 16 Intermediate Byte Codes

        if 0x40 <= ord_ < 0x7F:  # 63 Codes
            tail.extend(byte)
            self.closed = True
            return b""  # takes 1 of 63 Final Byte Codes

        # Decline 1 Byte of Unprintable Char

        return byte  # declines 1 Byte <= b"\x7F" of Unprintable Char

        # splits '⎋[200~' and '⎋[201~' away from enclosed Bracketed Paste

        # todo: limit the length of a CSI Escape Sequence

    # todo: limit rate of input so livelocks go less wild, like in Keyboard/ Screen loopback


#
# Run from the Shell Command Line, if not imported
#


if __name__ == "__main__":
    main()


# 3456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789


# posted as:  https://github.com/pelavarre/xshverb/blob/main/bin/plus.py
# copied from:  git clone https://github.com/pelavarre/xshverb.git
