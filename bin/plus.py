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
import re
import select
import signal
import sys
import termios
import textwrap
import tty
import types
import typing
import unicodedata

if not __debug__:
    raise NotImplementedError([__debug__])  # refuses to run without live Asserts

env_cloud_shell = os.environ.get("CLOUD_SHELL") == "true"  # Google
sys_platform_darwin = sys.platform == "darwin"  # Apple


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
    """Run at Process Exit, when not bypassed by raisingSystemExit"""

    # Clean up after Terminal Writes, if need be

    with_stderr.write("\x1b[" "m")  # clears Select Graphic Rendition via SGR
    with_stderr.write("\x1b[" "4" "l")  # restores Replace (not Insert) via RM_IRM

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
    func = try_read_byte_packet
    func = try_screen_editor

    func = try_screen_editor  # last choice wins

    print(f"tryme: {func.__qualname__}", file=sys.stderr)
    print(file=sys.stderr)

    func()


def try_screen_editor() -> None:
    """Loop Keyboard back to Screen, but as whole Packets, & with some emulations"""

    with ScreenEditor() as se:
        se.loopback_awhile()


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


def try_tbp_self_test() -> None:
    """Try Tests of Class TerminalBytePacket"""

    tbp = TerminalBytePacket()

    t0 = dt.datetime.now()
    tbp._try_terminal_byte_packet_()
    t1 = dt.datetime.now()

    print(t0)
    print(t1 - t0)


#
# Loop Keyboard back to Screen, but as whole Packets, & with some emulations
#


TAB = "\t"  # 00/09 Horizontal Tab
CR = "\r"  # 00/13 Carriage Return  # akin to CSI CHA "\x1b[" "G"
LF = "\n"  # 00/10 Line Feed ⌃J  # akin to CSI CUD "\x1b[" "B"


IND = "\x1b" "D"  # ESC 04/04 Index (IND) = C1 Control U+0084 IND (formerly known as INDEX)
NEL = "\x1b" "E"  # ESC 04/05 Next Line (NEL) = C1 Control U+0085 NEXT LINE (NEL)
RI = "\x1b" "M"  # ESC 04/06 Reverse Index (RI) = C1 Control U+0086 REVERSE LINE FEED (RI)

ICF_RIS = "\x1b" "c"  # ESC 06/03 Reset To Initial State (RIS) [an Independent Control Function]
ICF_CUP = "\x1b" "l"  # ESC 06/12 Cursor Position (CUP) [an Independent Control Function]


CUU_Y = "\x1b[" "{}" "A"  # CSI 04/01 Cursor Up
CUD_Y = "\x1b[" "{}" "B"  # CSI 04/02 Cursor Down  # \n is Pn 1 except from last Row
CUF_X = "\x1b[" "{}" "C"  # CSI 04/03 Cursor [Forward] Right
CUB_X = "\x1b[" "{}" "D"  # CSI 04/04 Cursor [Back] Left  # \b is Pn 1

CUP_Y_X = "\x1b[" "{};{}" "H"  # CSI 04/08 Cursor Position
CHT_X = "\x1b" "[" "{}I"  # CSI 04/09 Cursor Forward [Horizontal] Tabulation  # \t is Pn 1

EL_P = "\x1b[" "{}" "K"  # CSI 04/11 Erase in Line  # 0 Tail # 1 Head # 2 Row

IL_Y = "\x1b[" "{}" "L"  # CSI 04/12 Insert Line [Row]
DCH_X = "\x1b[" "{}" "P"  # CSI 05/00 Delete Character

VPA_Y = "\x1b" "[" "{}" "d"  # CSI 06/04 Line Position Absolute

SM_IRM = "\x1b" "[" "4h"  # CSI 06/08 4 Set Mode Insert, not Replace
RM_IRM = "\x1b" "[" "4l"  # CSI 06/12 4 Reset Mode Replace, not Insert

SGR = "\x1b" "[" "{}" "m"  # CSI 06/13 Select Graphic Rendition [Text Style]

DSR_6 = "\x1b" "[" "6n"  # CSI 06/14 [Request] Device Status Report  # Ps 6 for CPR In
CPR_Y_X_REGEX = r"\x1b\[([0-9]+);([0-9]+)R"  # CSI 05/02 Active [Cursor] Pos Rep (CPR)


DEL = "\x7f"  # 00/7F Delete [Control Character]  # aka ⌃?


PN_MAX_32100 = 32100  # an Int beyond the Counts of Rows & Columns at any Terminal


# FIXME: Pull ⎋[{y};{x}⇧R always into Side Channel, when requested or not


class ScreenEditor:
    """Loop Keyboard back to Screen, but as whole Packets, & with some emulations"""

    keyboard_bytes_log: typing.BinaryIO  # .klog
    screen_bytes_log: typing.BinaryIO  # .slog
    bytes_terminal: BytesTerminal  # .bt

    func_by_kdata: dict[bytes, collections.abc.Callable[[TerminalBytePacket], None]] = dict()

    #
    # Init, Enter, Exit, Print
    #

    def __init__(self) -> None:

        klog_path = pathlib.Path("__pycache__/k.keyboard")
        slog_path = pathlib.Path("__pycache__/s.screen")

        klog_path.parent.mkdir(exist_ok=True)
        slog_path.parent.mkdir(exist_ok=True)

        klog = klog_path.open("ab")
        slog = slog_path.open("ab")
        bt = BytesTerminal()

        func_by_kdata = self.form_func_by_kdata()

        self.keyboard_bytes_log = klog
        self.screen_bytes_log = slog
        self.bytes_terminal = bt
        self.func_by_kdata = func_by_kdata  # MyPy needs Dict

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

        assert CUU_Y == "\x1b[" "{}" "A"
        assert CUP_Y_X == "\x1b[" "{}" ";{}H"
        assert SGR == "\x1b[" "{}" "m"
        assert RM_IRM == "\x1b[" "4" "l"
        assert PN_MAX_32100 == 32100

        # Exit via 1st Column of 1 Row above the Last Row

        sdata = b"\x1b[32100H" + b"\x1b[A" + b"\x1b[m" + b"\x1b[4l"
        os.write(fileno, sdata)

        # Exit each, in reverse order of Enter's

        slog.__exit__(exc_type, exc_val, exc_tb)
        klog.__exit__(exc_type, exc_val, exc_tb)
        bt.__exit__(exc_type, exc_val, exc_tb)

        # Succeed

        return None

    def print(self, *args: object, end: str = "\r\n") -> None:
        """Join the Args by Space, add the End, and write the Encoded Chars"""

        schars = " ".join(str(_) for _ in args) + end
        self.write(schars)

    def write(self, text: str) -> None:
        """Write the Bytes, and log them as written"""

        bt = self.bytes_terminal
        fileno = bt.fileno
        slog = self.screen_bytes_log

        schars = text

        sdata = schars.encode()
        os.write(fileno, sdata)

        slog.write(sdata)

    #
    # Bind Keyboard Codes to Funcs
    #

    def form_func_by_kdata(
        self,
    ) -> dict[bytes, collections.abc.Callable[[TerminalBytePacket], None]]:

        func_by_literal_kdata = {
            #
            b"\x01": self.do_column_leap_leftmost,  # ⌃A for Emacs
            b"\x02": self.do_column_left,  # ⌃B for Emacs
            b"\x04": self.do_char_delete_here,  # ⌃D for Emacs
            b"\x05": self.do_column_leap_rightmost,  # ⌃E for Emacs
            b"\x06": self.do_column_right,  # ⌃F for Emacs
            b"\x07": self.do_write_kdata,  # ⌃G \a bell-ring
            b"\x08": self.do_write_kdata,  # ⌃H \b ←  # todo: where does Windows Backspace land?
            b"\x09": self.do_write_kdata,  # ⌃I \t Tab
            b"\x0a": self.do_write_kdata,  # ⌃J \n ↓, else Scroll Up and then ↓
            b"\x0b": self.do_row_tail_erase,  # ⌃K for Emacs when not rightmost
            # b"\x0d": self.do_write_kdata,  # ⌃M \r Return  # only \r Return at gCloud
            b"\x0d": self.do_write_cr_lf,  # ⌃M \r Return  # only \r Return at gCloud
            b"\x0e": self.do_row_down,  # ⌃N
            b"\x0f": self.do_row_insert,  # ⌃O for Emacs when leftmost
            b"\x10": self.do_row_up,  # ⌃P
            b"\x11": self.do_quote_one_kdata,  # ⌃Q for Emacs
            b"\x16": self.do_quote_one_kdata,  # ⌃V for Vim
            # FIXME: ⌃X⌃C ⌃X⌃S for Emacs
            b"\x1b" b"$": self.do_column_leap_rightmost,  # ⎋⇧$ for Vim
            #
            b"\x1b" b"0": self.do_column_leap_leftmost,  # ⎋0 for Vim
            b"\x1b" b"7": self.do_write_kdata,  # ⎋7 cursor-checkpoint
            b"\x1b" b"8": self.do_write_kdata,  # ⎋8 cursor-revert
            # FIXME: ⎋⇧0 ⎋⇧1 ⎋⇧2 ⎋⇧3 ⎋⇧4 ⎋⇧5 ⎋⇧6 ⎋⇧7 ⎋⇧8 ⎋⇧9 for Vim
            #
            b"\x1b" b"D": self.do_write_kdata,  # ⎋⇧D ↓ (IND)
            b"\x1b" b"E": self.do_write_kdata,  # ⎋⇧E \r\n else \r (NEL)
            # b"\x1b" b"J": self do_end_delete_right  # ⎋⇧J  # FIXME: Delete Row if at 1st Column
            b"\x1b" b"H": self.do_row_leap_first_column_leftmost,  # ⎋⇧H for Vim
            b"\x1b" b"L": self.do_row_leap_last_column_leftmost,  # ⎋⇧L for Vim
            # b"\x1b" b"M": self.do_write_kdata,  # ⎋⇧M ↑ (RI)
            b"\x1b" b"M": self.do_row_leap_middle_column_leftmost,  # ⎋⇧M for Vim
            b"\x1bO": self.do_row_insert_inserting_start,  # ⎋⇧O for Vim
            b"\x1bQ": self.do_assert_false,  # ⎋⇧Q for Vim
            b"\x1b" b"R": self.do_replacing_start,  # ⎋⇧R for Vim
            b"\x1b" b"S": self.do_row_delete_insert_start_inserting,  # ⎋S for Vim
            b"\x1b" b"X": self.do_char_delete_left,  # ⎋⇧X for Vim
            # FIXME: ⎋⇧Z⇧Q ⎋⇧Z⇧W for Vim
            #
            b"\x1b" b"a": self.do_column_right_inserting_start,  # ⎋A for Vim
            b"\x1b" b"c": self.do_write_kdata,  # ⎋C cursor-revert (ICF_RIS)
            # b"\x1b" b"l": self.do_write_kdata,  # ⎋L row-column-leap  # not at gCloud (ICF_CUP)
            b"\x1b" b"h": self.do_column_left,  # ⎋H for Vim
            b"\x1b" b"i": self.do_inserting_start,  # ⎋I for Vim
            b"\x1b" b"j": self.do_row_down,  # ⎋J for Vim
            b"\x1b" b"k": self.do_row_up,  # ⎋K for Vim
            b"\x1b" b"l": self.do_column_right,  # ⎋L for Vim
            b"\x1b" b"o": self.do_row_down_insert_inserting_start,  # ⎋O for Vim
            b"\x1b" b"r": self.do_replacing_one_kdata,  # ⎋R for Vim
            b"\x1b" b"s": self.do_char_delete_here_start_inserting,  # ⎋S for Vim
            b"\x1b" b"x": self.do_char_delete_here,  # ⎋X for Vim
            #
            b"\x1b[" b"A": self.do_write_kdata,  # ⎋[⇧A ↑
            b"\x1b[" b"B": self.do_write_kdata,  # ⎋[⇧B ↓
            b"\x1b[" b"C": self.do_write_kdata,  # ⎋[⇧C →
            b"\x1b[" b"D": self.do_write_kdata,  # ⎋[⇧D ←
            # b"\x1b[" b"I": self.do_write_kdata,  # ⎋[⇧I ⌃I  # not at gCloud
            b"\x1b[" b"Z": self.do_write_kdata,  # ⎋[⇧Z ⇧Tab
            #
            b"\x1bO" b"P": self.do_kdata_fn_f1,  # Fn F1
            #
            b"\x7f": self.do_char_delete_left,  # ⌃? Delete  # FIXME: Delete Row if at 1st Column
        }

        func_by_kdata = dict(func_by_literal_kdata)

        return func_by_kdata

        # FIXME: ⌃U for Emacs
        # FIXME: bind ⎋ and ⌃U to Vim/Emacs Repeat Counts
        # FIXME: bind ⎋0 etc to Vi Meanings - but don't get stuck inside ⎋-Lock

        # FIXME: bind ⌃C ⇧O for Emacs overwrite-mode, or something
        # FIXME: bind Keyboard Chord Sequences, no longer just Keyboard Chords

        # FIXME: bind bin/é bin/e-aigu bin/latin-small-letter-e-with-acute to this kind of editing

        # FIXME: history binds only while present, or falls back like ⎋⇧$ and ⌃E to max right

    #
    #
    #

    def loopback_awhile(self) -> None:
        """Loop Keyboard back to Screen, but as whole Packets, & with some emulations"""

        self.print("Press ⌃D to quit, else Fn F1 for help, else see what happens")

        # Default to Inserting, not Replacing

        tbp = TerminalBytePacket()
        self.do_inserting_start(tbp)

        # Reply to each Keyboard Chord Input, till quit
        # FIXME: Quit in many of the Emacs & Vim ways, including Vim ⌃C :vi ⇧Z ⇧Q
        # FIXME: Maybe or maybe-not quit after ⌃D, vs quitting now only at ⌃D

        while True:
            (tbp, n) = self.read_some_byte_packets()
            tprint(f"{n=} {tbp=}  # loopback_awhile")
            assert tbp, (tbp, n)  # because .timeout=None

            kdata = tbp.to_bytes()
            assert kdata, (kdata,)  # because .timeout=None

            try:
                self.reply_to_kdata(tbp, n=n)
            except SystemExit:
                break

            if kdata == b"\x04":  # ⌃D
                break

        # FIXME: FIXME: Shadow Terminal with default Replacing
        # FIXME: Read Str not Bytes from Keyboard, and then List[Str]
        # FIXME: Stop taking slow b'\x1b[' b'L' as 1 Whole Packet from gCloud

    def reply_to_kdata(self, tbp: TerminalBytePacket, n: int) -> None:
        """Reply to 1 Keyboard Chord Input, maybe differently if n == 1 quick, or slow"""

        func_by_kdata = self.func_by_kdata
        klog = self.keyboard_bytes_log

        # Append to our __pycache__/k.keyboard Keylogger Keylogging File

        kdata = tbp.to_bytes()
        assert kdata, (kdata,)  # because .timeout=None

        klog.write(kdata)

        # Call 1 Func Def

        if kdata in func_by_kdata.keys():
            func = func_by_kdata[kdata]
            tprint(f"{func=}  # loopback_awhile")

            func(tbp)  # may raise SystemExit

            return

        # Write the KData, but as Keycaps, when it is a Keycap but not a Func Def

        kchars = kdata.decode()  # may raise UnicodeDecodeError
        if kchars in KCAP_BY_KCHARS.keys():  # already handled above
            tprint(f"Keycap {kchars=} {str(tbp)=}   # reply_to_kdata")

            if tbp.tail != b"H":  # falls-through to pass-through ⎋[⇧H CUP_Y_X

                kcaps = kdata_to_kcaps(kdata)
                self.print(kcaps, end=" ")

                return

        # Pass through 1 Unicode Character

        if tbp.text:
            tprint(f"tbp.text {kdata=}  # reply_to_kdata")

            self.do_write_kdata(tbp)

            return

            # FIXME: stop wrongly passing through multibyte Control Characters

        # Emulate some Control Byte Sequences promoted by less than all our Terminals

        famous_kdata = self.reply_to_famous_kdata(tbp, n=n)
        if famous_kdata:
            return

        # Show the Keycaps to send the Terminal Byte Packet slowly from Keyboard

        tprint(f"else {kdata=} {str(tbp)=}   # reply_to_kdata")

        kcaps = kdata_to_kcaps(kdata)
        self.print(kcaps, end=" ")

    def reply_to_famous_kdata(self, tbp: TerminalBytePacket, n: int) -> bytes:
        """Emulate the KData Control Sequence and return it, else return empty bytes()"""

        kdata = tbp.to_bytes()  # already logged by caller, we trust
        assert kdata, (kdata,)  # because .timeout=None

        # Emulate Famous Esc Byte Pairs, no matter if quick or slow

        esc_pair_famous = kdata == b"\x1b" b"l"
        if esc_pair_famous:  # gCloud Shell needs ⎋[1;1⇧H for ⎋L
            tprint(f"{kdata=}  # reply_to_kdata")

            self.write("\x1b[" "1;1" "H")

            return kdata

        # Emulate famous Csi Control Byte Sequences,
        # beyond Screen_Writer_Help of ⎋[ ⇧@⇧A⇧B⇧C⇧D⇧E⇧G⇧H⇧I⇧J⇧K⇧L⇧M⇧P⇧S⇧T⇧Z ⇧}⇧~ and ⎋[ DHLMNQT,
        # so as to also emulate timeless Csi ⇧F ⇧X ` F and slow Csi X

        csi = tbp.head == b"\x1b["  # takes Csi ⎋[, but not Esc Csi ⎋⎋[

        csi_timeless_tails = b"@ABCDEFGHIJKLMPSTXZ" + b"`dfhlmqr" + b"}~"
        csi_slow_tails = b"cntx"  # still not b"NOQRUVWY" and not "abegijkopsuvwyz"

        csi_famous = csi and tbp.tail and (tbp.tail in csi_timeless_tails)
        if (n > 1) and csi and tbp.tail and (tbp.tail in csi_slow_tails):
            csi_famous = True

        if not csi_famous:
            return b""

        # Emulate Cursor Forward [Horizontal] Tabulation (CHT) for Pn >= 1

        assert TAB == "\t"
        assert CHT_X == "\x1b" "[" "{}I"

        if tbp.tail == b"I":
            tprint(f"⎋[...I {tbp=} {kdata=}  # reply_to_kdata")

            pn = int(tbp.neck) if tbp.neck else 1
            assert pn >= 1, (pn,)
            self.write(pn * "\t")

            return kdata

            # gCloud Shell needs \t for ⎋[ {}I

        # Emulate Line Position Absolute (VPA_Y) but only for an implicit ΔY = 1

        assert VPA_Y == "\x1b" "[" "{}" "d"

        if kdata == b"\x1b[" b"d":
            tprint(f"⎋[d {kdata=}   # reply_to_kdata")

            self.write("\x1b[" "1" "d")

            return kdata

            # gCloud Shell needs ⎋[1D for ⎋[D

        # Emulate ⎋['⇧} cols-insert  ⎋['⇧~ cols-delete  # FIXME: FIXME #

        if tbp.tail == b"}":
            if tbp.back != b"'":
                return b""

            tprint("⎋['⇧} cols-insert" f" {tbp=} {kdata=}   # reply_to_kdata")

            self.print(tbp, end="  ")

            return kdata

        if tbp.tail == b"~":
            if tbp.back != b"'":
                return b""

            tprint("⎋['⇧~ cols-delete" f" {tbp=} {kdata=}   # reply_to_kdata")

            self.print(tbp, end="  ")

            return kdata

        # Pass through the .csi_timeless_tails, be they quick or slow,
        # and pass through the .csi_slow_tails but only when slow

        tprint(f"Pass-through {kdata=} {str(tbp)=}   # reply_to_kdata")

        self.do_write_kdata(tbp)

        return kdata

    def read_some_byte_packets(self) -> tuple[TerminalBytePacket, int]:
        """Read 1 TerminalBytePacket, all in one piece, else in split pieces"""

        bt = self.bytes_terminal

        n = 1
        tbp = bt.read_byte_packet(timeout=None)  # todo: log & echo the Bytes as they arrive

        while (not tbp.text) and (not tbp.closed) and (not bt.extras):
            kdata = tbp.to_bytes()
            if kdata == b"\x1bO":  # ⎋⇧O for Vim
                break
            n += 1
            bt.close_byte_packet_if(tbp, timeout=None)

        return (tbp, n)

    def do_write_cr_lf(self, tbp: TerminalBytePacket) -> None:
        """Write CR LF"""

        assert CR == "\r"
        assert LF == "\n"

        self.write("\r\n")

    def do_write_kdata(self, tbp: TerminalBytePacket) -> None:
        """Loop the Keyboard back to the Screen, literally, directly"""

        kdata = tbp.to_bytes()

        bt = self.bytes_terminal
        fileno = bt.fileno
        slog = self.screen_bytes_log

        sdata = kdata
        os.write(fileno, sdata)

        slog.write(sdata)

    def do_quote_one_kdata(self, tbp: TerminalBytePacket) -> None:
        """Loopback the Bytes of the next 1 Keyboard Chord onto the screen"""

        (tbp, n) = self.read_some_byte_packets()
        self.do_write_kdata(tbp)

        # Emacs ⌃Q  # Vim ⌃V

    def do_replacing_one_kdata(self, tbp: TerminalBytePacket) -> None:
        """Start replacing, quote 1 Keyboard Chord, then start inserting"""

        self.do_replacing_start(tbp)  # Vim ⇧R
        self.do_quote_one_kdata(tbp)  # Emacs ⌃Q  # Vim ⌃V
        self.do_inserting_start(tbp)  # Vim I

        # FIXME: FIXME: Shadow Terminal with default Replacing

    #
    #
    #

    def do_column_left(self, tbp: TerminalBytePacket) -> None:
        """Go left by 1 Column"""

        assert BS == "\b"

        tbp = TerminalBytePacket(b"\b")
        self.do_write_kdata(tbp)

        # Emacs Delete

    def do_column_right(self, tbp: TerminalBytePacket) -> None:
        """Go right by 1 Column"""

        assert CUF_X == "\x1b[" "{}" "C"
        self.write("\x1b[" "C")

        # Emacs ⌃F

    def do_column_right_inserting_start(self, tbp: TerminalBytePacket) -> None:
        """Insert 1 Space at the Cursor, then go right by 1 Column"""

        self.do_column_right(tbp)  # Vim L
        self.do_inserting_start(tbp)  # Vim I

        # Vim A

    def do_char_delete_here(self, tbp: TerminalBytePacket) -> None:
        """Delete the Character beneath the Cursor"""

        assert DCH_X == "\x1b[" "{}" "P"
        self.write("\x1b[" "P")

        # Emacs ⌃D  # Vim X

    def do_assert_false(self, tbp: TerminalBytePacket) -> None:
        """Assert False"""

        assert False

    def do_char_delete_here_start_inserting(self, tbp: TerminalBytePacket) -> None:
        """Delete the Character beneath the Cursor, and Start Inserting"""

        self.do_char_delete_here(tbp)  # Emacs ⌃D  # Vim X
        self.do_inserting_start(tbp)  # Vim I

        # Vim S

    def do_char_delete_left(self, tbp: TerminalBytePacket) -> None:
        """Delete the Character at left of the Cursor"""

        assert BS == "\b"
        assert DCH_X == "\x1b[" "{}" "P"

        x = self.bytes_terminal.read_column_x()
        if x > 1:
            self.write("\b" "\x1b[" "P")

        # Emacs Delete  # Vim ⇧X

        # FIXME: Show .do_char_delete_left bouncing off the Left Edge

    def do_column_leap_leftmost(self, tbp: TerminalBytePacket) -> None:
        """Leap to the Leftmost Column"""

        assert CR == "\r"
        self.write("\r")

        # Emacs ⌃A  # Vim 0

    def do_column_leap_rightmost(self, tbp: TerminalBytePacket) -> None:
        """Leap to the Rightmost Column"""

        assert CUF_X == "\x1b[" "{}" "C"
        assert PN_MAX_32100 == 32100
        self.write("\x1b[" "32100" "C")

        # Emacs ⌃E  # Vim ⇧$

    def do_inserting_start(self, tbp: TerminalBytePacket) -> None:
        """Start Inserting Characters at the Cursor"""

        assert SM_IRM == "\x1b[" "4h"
        self.write("\x1b[" "4h")

        # Vim I

        # FIXME: Show Inserting while Inserting

    def do_replacing_start(self, tbp: TerminalBytePacket) -> None:
        """Start Replacing Characters at the Cursor"""

        assert RM_IRM == "\x1b[" "4l"
        self.write("\x1b[" "4l")

        # Vim ⇧R

        # FIXME: Show Replacing while Replacing

    def do_row_delete_insert_start_inserting(self, tbp: TerminalBytePacket) -> None:
        """Empty the Row beneath the Cursor, and Start Inserting"""

        assert EL_P == "\x1b[" "{}" "K"  # 2 Row
        self.write("\x1b[" "2" "K")

        self.do_column_leap_leftmost(tbp)  # Emacs ⌃A  # Vim 0
        self.do_inserting_start(tbp)  # Vim I

        # Vim ⇧S

    def do_row_down(self, tbp: TerminalBytePacket) -> None:
        """Go down by 1 Row, but stop in last Row"""

        assert CUD_Y == "\x1b[" "{}" "B"
        self.write("\x1b[" "B")

        # Emacs ⌃N

    def do_row_down_insert_inserting_start(self, tbp: TerminalBytePacket) -> None:
        """Insert 1 Row below the Cursor"""

        self.do_row_down(tbp)  # Vim J
        self.do_row_insert(tbp)  # Emacs ⌃O when leftmost
        self.do_inserting_start(tbp)  # Vim I

        # Vim O

    def do_row_insert_inserting_start(self, tbp: TerminalBytePacket) -> None:

        self.do_row_insert(tbp)  # Emacs ⌃O when leftmost
        self.do_inserting_start(tbp)  # Vim I

        # Vim ⇧O

    def do_row_insert(self, tbp: TerminalBytePacket) -> None:
        """Insert 1 Row above the Cursor"""

        assert IL_Y == "\x1b[" "{}" "L"
        self.write("\x1b[" "L")

        # Emacs ⌃O when leftmost

    def do_row_leap_first_column_leftmost(self, tbp: TerminalBytePacket) -> None:
        """Leap to the Leftmost Column of the First Row"""

        assert CUP_Y_X == "\x1b[" "{};{}" "H"
        self.write("\x1b[" "1;1" "H")

        # Vim ⇧H

    def do_row_leap_last_column_leftmost(self, tbp: TerminalBytePacket) -> None:
        """Leap to the Leftmost Column of the Last Row"""

        assert PN_MAX_32100 == 32100
        assert CUP_Y_X == "\x1b[" "{};{}" "H"
        self.write("\x1b[" "32100;1" "H")

        # Vim ⇧H

    def do_row_leap_middle_column_leftmost(self, tbp: TerminalBytePacket) -> None:
        """Leap to the Leftmost Column of the Middle Row"""

        bt = self.bytes_terminal

        height = bt.read_height()
        middle = (height // 2) + (height % 2)

        assert CUP_Y_X == "\x1b[" "{};{}" "H"
        self.write(f"\x1b[{middle};1" "H")

        # Vim ⎋⇧M

    def do_row_tail_erase(self, tbp: TerminalBytePacket) -> None:
        """Erase from the Cursor to the Tail of the Row"""

        assert EL_P == "\x1b[" "{}" "K"
        self.write("\x1b[" "K")

        # Emacs ⌃K when not rightmost

    def do_row_up(self, tbp: TerminalBytePacket) -> None:
        """Go up by 1 Row, but stop in Top Row"""

        assert CUU_Y == "\x1b[" "{}" "A"
        self.write("\x1b[" "A")

        # Emacs ⌃P

    #
    #
    #

    def do_kdata_fn_f1(self, tbp: TerminalBytePacket, /) -> None:
        """Print the many Lines of Screen Writer Help"""

        help_ = textwrap.dedent(SCREEN_WRITER_HELP).strip()

        self.print()
        self.print()

        for line in help_.splitlines():
            self.print(line)

        if env_cloud_shell:
            self.print()
            self.print("gCloud Shell ignores ⌃M (you must press Return)")
            self.print("gCloud Shell ignores a quick ⎋[D (you must press ⎋[1D)")
            self.print("gCloud Shell often ignores ⎋[I (you must press Tab)")
            self.print("gCloud Shell ignores ⎋[3⇧J Scrollback-Erase (you must close Tab)")
            self.print("gCloud Shell ⌃L between Commands clears Screen (not Scrollback)")
            self.print()

            # self.print("gCloud Shell ignores ⎋[⇧T Scrolls-Down (but accepts ⎋[⇧L)")
            # self.print("gCloud Shell ignores ⎋[⇧S Scrolls-Up (but accepts ⌃J)")
            # self.print("gCloud Shell ignores ⎋['⇧} and ⎋['⇧~ Cols Insert/Delete")

            # gCloud Shell has ← ↑ → ↓
            # gCloud Shell has ⌥ ← ↑ → ↓
            # gCloud Shell has ⌃⌥ ← ↑ → ↓
            # gCloud Shell has ⌥ Esc Delete Return, but ⌥ Esc comes as Esc Xms Esc

            # gCloud AltIsMeta has FIXME

        if sys_platform_darwin:
            self.print()

            # self.print("macOS Shell ignores ⎋['⇧} and ⎋['⇧~ Cols Insert/Delete")

            self.print("macOS Shell ⌘K clears Screen & Scrollback (but not Top Row)")
            self.print()

            # macOS Shell has ← ↑ → ↓
            # macOS Shell has ⌥ ← → and ⇧ ← →
            # macOS Shell has ⇧ Fn ← ↑ → ↓
            # macOS Option-as-Meta has ⌥⎋ ⌥Delete ⌥Tab ⌥⇧Tab ⌥Return

        self.print("Press ⌃D to quit, else Fn F1 for help, else see what happens")
        self.print()
        self.print()

        # XShVerb F1

        # FIXME: toggle emulations on/off
        # FIXME: toggle tracing input on/off
        # FIXME: show loss of \e7 memory because of emulations

        # FIXME: accept lots of quits and movements as per Vim ⌃O & Emacs


# FIXME: show time gone since last Keyboard Byte

SCREEN_WRITER_HELP = r"""

    Keycap Symbols are ⎋ Esc, ⌃ Control, ⌥ Option/ Alt, ⇧ Shift, ⌘ Command/ Os

        ⌃G ⌃H ⌃I ⌃J ⌃M mean \a \b \t \n \r, and ⌃[ means \e, also known as ⎋ Esc
        Tab means ⌃I \t, and Return means ⌃M \r

    The famous Esc ⎋ Byte Pairs are ⎋ 7 8 C L ⇧D ⇧E ⇧M

        ⎋7 cursor-checkpoint  ⎋8 cursor-revert (defaults to Y 1 X 1)
        ⎋C screen-erase  ⎋L row-column-leap
        ⎋⇧D ↓  ⎋⇧E \r\n else \r  ⎋⇧M ↑

    The famous Csi ⎋[ Sequences are ⎋[ ⇧@ ⇧A⇧B⇧C⇧D⇧E⇧G⇧H⇧I⇧J⇧K⇧L⇧M⇧P⇧S⇧T⇧Z ⇧}⇧~ and ⎋[ DHLMNQT

        ⎋[⇧A ↑  ⎋[⇧B ↓  ⎋[⇧C →  ⎋[⇧D ←
        ⎋[I ⌃I  ⎋[⇧Z ⇧Tab
        ⎋[D row-leap  ⎋[⇧G column-leap  ⎋[⇧H row-column-leap

        ⎋[⇧M rows-delete  ⎋[⇧L rows-insert  ⎋[⇧P chars-delete  ⎋[⇧@ chars-insert
        ⎋[⇧J after-erase  ⎋[1⇧J before-erase  ⎋[2⇧J screen-erase  ⎋[3⇧J scrollback-erase
        ⎋[⇧K row-tail-erase  ⎋[1⇧K row-head-erase  ⎋[2⇧K row-erase  ⎋[⇧X columns-erase
        ⎋[⇧T scrolls-down  ⎋[⇧S scrolls-up

        ⎋[4H insert  ⎋[4L replace  ⎋[6 Q bar  ⎋[4 Q skid  ⎋[ Q unstyled

        ⎋[1M bold  ⎋[4M underline  ⎋[7M reverse/inverse
        ⎋[31M red  ⎋[32M green  ⎋[34M blue  ⎋[38;5;130M orange
        ⎋[M plain

        ⎋[5N call for reply ⎋[0N
        ⎋[6N call for reply ⎋[{y};{x}⇧R
        ⎋[18T call for reply ⎋[8;{rows};{columns}T

        ⎋['⇧} cols-insert  ⎋['⇧~ cols-delete

"""

# ⎋[` near alias of ⎋[⇧G column-leap  # macOS
# ⎋[F near alias of ⎋[⇧H row-column-leap
# ⎋[R near alias of ⎋L row-column-leap

# ⎋[C call for reply ⎋[?1;2C  # ⎋[=C also works at macOS
# ⎋[>C call for reply ⎋[>1;95;0C macOS or ⎋[>84;0;0C gCloud Shell
# ⎋[X call for reply ⎋[2;1;1;112;112;1;0X  # macOS


# FIXME: help for Emacs, help for Vim


#
# Amp up Import Tty
#


BS = "\b"  # 00/08 ⌃H Backspace
HT = "\t"  # 00/09 ⌃I Character Tabulation
LF = "\n"  # 00/10 ⌃J Line Feed  # akin to ⌃K and CUD "\x1b[" "B"
CR = "\r"  # 00/13 ⌃M Carriage Return  # akin to CHA "\x1b[" "G"

ESC = "\x1b"  # 01/11  ⌃[ Escape  # often known as Shell printf '\e', but Python doesn't define \e
SS3 = "\x1bO"  # ESC 04/15 Single Shift Three  # in macOS F1 F2 F3 F4
CSI = "\x1b["  # ESC 05/11 Control Sequence Introducer

DECSC = "\x1b" "7"  # ESC 03/07 Save Cursor [Checkpoint] (DECSC)
DECRC = "\x1b" "8"  # ESC 03/08 Restore Cursor [Rollback] (DECRC)

CSI_PIF_REGEX = r"(\x1b\[)" r"([0-?]*)" r"([ -/]*)" r"(.)"  # Parameter/ Intermediate/ Final Bytes


class BytesTerminal:
    """Write/ Read Bytes at Screen/ Keyboard of the Terminal"""

    stdio: typing.TextIO
    fileno: int

    before: int  # for writing at Enter
    tcgetattr: list[int | list[bytes | int]]  # replaced by Enter
    after: int  # for writing at Exit  # todo: .TCSAFLUSH vs large Paste

    extras: bytearray  # Bytes from 'os.read' not yet returned inside some TerminalBytePacket

    height: int  # Terminal Screen Pane Rows, else -1
    width: int  # Terminal Screen Pane Columns, else -1

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

        self.height = -1
        self.width = -1

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
        """Read 1 TerminalBytePacket, closed immediately, or not"""

        tbp = TerminalBytePacket()
        self.close_byte_packet_if(tbp, timeout=timeout)

        return tbp  # maybe empty

    def close_byte_packet_if(self, tbp: TerminalBytePacket, timeout: float | None) -> None:
        """Read 0 or more Bytes into the Packet, and close it, or not"""

        stdio = self.stdio
        fileno = self.fileno
        extras = self.extras

        # Flush last of Output, before looking for Input

        stdio.flush()

        # Wait for first Byte, add in already available Bytes. and declare victory

        t = 0.000_001  # 0.000 works at macOS

        if extras or self.kbhit(timeout=timeout):
            while extras or self.kbhit(timeout=t):

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

                kdata = tbp.to_bytes()
                if not extras:
                    if kdata == b"\x1bO":  # ⎋⇧O for Vim
                        if not self.kbhit(
                            timeout=0.333
                        ):  # rejects slow SS3 b"\x1bO" "P" of Fn F1..F4
                            break

    def read_height(self) -> int:
        """Count Terminal Screen Pane Rows"""

        fileno = self.fileno
        size = os.get_terminal_size(fileno)
        assert 5 <= size.lines <= PN_MAX_32100, (size,)

        height = size.lines

        return height

        # macOS Terminal guarantees >= 20 Columns and >= 5 Rows

    def read_width(self) -> int:
        """Count Terminal Screen Pane Columns"""

        fileno = self.fileno
        size = os.get_terminal_size(fileno)

        assert 20 <= size.columns <= PN_MAX_32100, (size,)

        width = size.columns

        return width

        # macOS Terminal guarantees >= 20 Columns and >= 5 Rows

    def read_column_x(self) -> int:
        """Find the Terminal Cursor Column"""

        (y, x) = self.read_row_y_column_x()

        return x

    def read_row_y_column_x(self) -> tuple[int, int]:
        """Find the Terminal Cursor"""

        stdio = self.stdio

        assert DSR_6 == "\x1b" "[" "6n"
        assert CPR_Y_X_REGEX == r"\x1b\[([0-9]+);([0-9]+)R"

        kbhit = self.kbhit(timeout=0.000)  # flushes output, then polls input
        assert not kbhit  # todo: cope when Mouse or Paste work disrupts os.read

        stdio.write("\x1b[6n")  # bypass Screen Logs & Screen Shadows above
        tbp = self.read_byte_packet(timeout=None)
        kdata = tbp.to_bytes()

        m = re.fullmatch(rb"\x1b\[([0-9]+);([0-9]+)R", string=kdata)
        assert m, (m, kdata, tbp)

        y_bytes = m.group(1)
        x_bytes = m.group(2)

        y = int(y_bytes)
        x = int(x_bytes)

        assert 1 <= y <= PN_MAX_32100, (y, x, kdata, tbp)
        assert 1 <= x <= PN_MAX_32100, (y, x, kdata, tbp)

        assert y >= 1, (y, y_bytes, kdata, tbp)
        assert x >= 1, (x, x_bytes, kdata, tbp)

        return (y, x)


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
            raise ValueError(extras)  # for example, raises the b'\x80' of b'\xc0\x80'

        self._require_simple_()

        # doesn't take bytes([0x80 | 0x0B]) as meaning b"\x1b\x5b" CSI ⎋[
        # doesn't take bytes([0x80 | 0x0F]) as meaning b"\x1b\x4f" SS3 ⎋O

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
                return repr(text) + " " + str(stash_)
            return repr(text)

            # "'abc' b'\xc0'"

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

    def _try_terminal_byte_packet_(self) -> None:  # todo: call this slow Self-Test more often
        """Try some Packets open to, or closed against, taking more Bytes"""

        # Try some Packets left open to taking more Bytes

        tbp = TerminalBytePacket(b"Superb")
        assert str(tbp) == "'Superb'" and not tbp.closed, (tbp,)
        extras = tbp.take_one_if(b"\xc2")
        assert not extras and not tbp.closed, (extras, tbp.closed, tbp)
        assert str(tbp) == r"'Superb' b'\xc2'", (repr(str(tbp)), tbp)

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

        # b"\xc2\x80", b"\xe0\xa0\x80", b"\xf0\x90\x80\x80" .. b"\xf4\x8f\xbf\xbf"
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
        assert CSI == "\x1b["  # ⎋[
        assert SS3 == "\x1bO"  # ⎋O

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

            # takes \b \t \n \r \x7f etc

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

            # does take ⎋\x10 ⎋\b ⎋\t ⎋\n ⎋\r ⎋\x7f etc

            # doesn't take bytes([0x80 | 0x0B]) as meaning b"\x1b\x5b" CSI ⎋[
            # doesn't take bytes([0x80 | 0x0F]) as meaning b"\x1b\x4f" SS3 ⎋O

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

        assert CSI == "\x1b[", (CSI,)  # ⎋[
        if not head.startswith(b"\x1b\x1b["):  # ⎋⎋[ Esc CSI
            assert head.startswith(b"\x1b["), (head,)  # ⎋[ CSI

        assert not tail, (tail,)
        assert not closed, (closed,)

        byte = chr(ord_).encode()
        assert byte == encode, (byte, encode)

        # Decline 1..4 Bytes of Unprintable or Multi-Byte Char

        if ord_ > 0x7F:
            return byte  # declines 2..4 Bytes of 1 Unprintable or Multi-Byte Char

        # Accept 1 Byte into Back, into Neck, or as Tail

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

        return byte  # declines 1 Byte <= b"\x7f" of Unprintable Char

        # splits '⎋[200~' and '⎋[201~' away from enclosed Bracketed Paste

        # todo: limit the length of a CSI Escape Sequence

    # todo: limit rate of input so livelocks go less wild, like in Keyboard/ Screen loopback


# Name the Shifting Keys

Meta = unicodedata.lookup("Broken Circle With Northwest Arrow")  # ⎋
Control = unicodedata.lookup("Up Arrowhead")  # ⌃
Option = unicodedata.lookup("Option Key")  # ⌥
Shift = unicodedata.lookup("Upwards White Arrow")  # ⇧
Command = unicodedata.lookup("Place of Interest Sign")  # ⌘  # Super  # Windows
# 'Fn'

# note: Meta hides inside macOS Terminal > Settings > Keyboard > Use Option as Meta Key
# note: Meta hides inside gloud Shell > Settings > Keyboard > Alt is Meta


# Encode each Key Chord as a Str without a " " Space in it

KCAP_SEP = " "  # separates '⇧Tab' from '⇧T a b', '⎋⇧FnX' from '⎋⇧Fn X', etc

KCAP_BY_KCHARS = {  # r"←|↑|→|↓" and so on and on
    "\x00": "⌃Spacebar",  # ⌃@  # ⌃⇧2
    "\x09": "Tab",  # '\t' ⇥
    "\x0d": "Return",  # '\r' ⏎
    "\x1b": "⎋",  # Esc  # Meta  # includes ⎋Spacebar ⎋Tab ⎋Return ⎋Delete without ⌥
    "\x1b" "\x01": "⌥⇧Fn←",  # ⎋⇧Fn←   # coded with ⌃A
    "\x1b" "\x03": "⎋FnReturn",  # coded with ⌃C  # not ⌥FnReturn
    "\x1b" "\x04": "⌥⇧Fn→",  # ⎋⇧Fn→   # coded with ⌃D
    "\x1b" "\x08": "⎋⌃Delete",  # ⎋⌃Delete  # coded with ⌃H  # aka \b
    "\x1b" "\x0b": "⌥⇧Fn↑",  # ⎋⇧Fn↑   # coded with ⌃K
    "\x1b" "\x0c": "⌥⇧Fn↓",  # ⎋⇧Fn↓  # coded with ⌃L  # aka \f
    "\x1b" "\x10": "⎋⇧Fn",  # ⎋ Meta ⇧ Shift of Fn F1..F12  # not ⌥⇧Fn  # coded with ⌃P
    "\x1b" "\x1b": "⎋⎋",  # Meta Esc  # not ⌥⎋
    "\x1b" "\x1b" "OA": "⌃⌥↑",  # ESC 04/15 Single-Shift Three (SS3)  # ESC SS3 ⇧A  # gCloud Shell
    "\x1b" "\x1b" "OB": "⌃⌥↓",  # ESC 04/15 Single-Shift Three (SS3)  # ESC SS3 ⇧B  # gCloud Shell
    "\x1b" "\x1b" "OC": "⌃⌥→",  # ESC 04/15 Single-Shift Three (SS3)  # ESC SS3 ⇧C  # gCloud Shell
    "\x1b" "\x1b" "OD": "⌃⌥←",  # ESC 04/15 Single-Shift Three (SS3)  # ESC SS3 ⇧D  # gCloud Shell
    "\x1b" "\x1b" "[" "3;5~": "⎋⌃FnDelete",  # ⌥⌃FnDelete
    "\x1b" "\x1b" "[" "A": "⎋↑",  # CSI 04/01 Cursor Up (CUU)  # not ⌥↑
    "\x1b" "\x1b" "[" "B": "⎋↓",  # CSI 04/02 Cursor Down (CUD)  # not ⌥↓
    "\x1b" "\x1b" "[" "Z": "⎋⇧Tab",  # ⇤  # CSI 05/10 CBT  # not ⌥⇧Tab
    "\x1b" "\x28": "⎋FnDelete",  # not ⌥FnDelete
    "\x1b" "OP": "F1",  # ESC 04/15 Single-Shift Three (SS3)  # SS3 ⇧P
    "\x1b" "OQ": "F2",  # SS3 ⇧Q
    "\x1b" "OR": "F3",  # SS3 ⇧R
    "\x1b" "OS": "F4",  # SS3 ⇧S
    "\x1b" "[" "15~": "F5",  # Esc 07/14 is LS1R, but CSI 07/14 is unnamed
    "\x1b" "[" "17~": "F6",  # ⌥F1  # ⎋F1
    "\x1b" "[" "18~": "F7",  # ⌥F2  # ⎋F2
    "\x1b" "[" "19~": "F8",  # ⌥F3  # ⎋F3
    "\x1b" "[" "1;2C": "⇧→",  # CSI 04/03 Cursor [Forward] Right (CUF_YX) Y=1 X=2
    "\x1b" "[" "1;2D": "⇧←",  # CSI 04/04 Cursor [Back] Left (CUB_YX) Y=1 X=2
    "\x1b" "[" "20~": "F9",  # ⌥F4  # ⎋F4
    "\x1b" "[" "21~": "F10",  # ⌥F5  # ⎋F5
    "\x1b" "[" "23~": "F11",  # ⌥F6  # ⎋F6  # macOS takes F11
    "\x1b" "[" "24~": "F12",  # ⌥F7  # ⎋F7
    "\x1b" "[" "25~": "⇧F5",  # ⌥F8  # ⎋F8
    "\x1b" "[" "26~": "⇧F6",  # ⌥F9  # ⎋F9
    "\x1b" "[" "28~": "⇧F7",  # ⌥F10  # ⎋F10
    "\x1b" "[" "29~": "⇧F8",  # ⌥F11  # ⎋F11
    "\x1b" "[" "31~": "⇧F9",  # ⌥F12  # ⎋F12
    "\x1b" "[" "32~": "⇧F10",
    "\x1b" "[" "33~": "⇧F11",
    "\x1b" "[" "34~": "⇧F12",
    "\x1b" "[" "3;2~": "⇧FnDelete",
    "\x1b" "[" "3;5~": "⌃FnDelete",
    "\x1b" "[" "3~": "FnDelete",
    "\x1b" "[" "5~": "⇧Fn↑",  # macOS
    "\x1b" "[" "6~": "⇧Fn↓",  # macOS
    "\x1b" "[" "A": "↑",  # CSI 04/01 Cursor Up (CUU)
    "\x1b" "[" "B": "↓",  # CSI 04/02 Cursor Down (CUD)
    "\x1b" "[" "C": "→",  # CSI 04/03 Cursor Right [Forward] (CUF)
    "\x1b" "[" "D": "←",  # CSI 04/04 Cursor [Back] Left (CUB)
    "\x1b" "[" "F": "⇧Fn→",  # macOS  # CSI 04/06 Cursor Preceding Line (CPL)
    "\x1b" "[" "H": "⇧Fn←",  # macOS  # CSI 04/08 Cursor Position (CUP)
    "\x1b" "[" "Z": "⇧Tab",  # ⇤  # CSI 05/10 Cursor Backward Tabulation (CBT)
    "\x1b" "b": "⌥←",  # ⎋B  # ⎋←  # Emacs M-b Backword-Word
    "\x1b" "f": "⌥→",  # ⎋F  # ⎋→  # Emacs M-f Forward-Word
    "\x20": "Spacebar",  # ' ' ␠ ␣ ␢
    "\x7f": "Delete",  # ␡ ⌫ ⌦
    "\xa0": "⌥Spacebar",  # '\N{No-Break Space}'
}

assert list(KCAP_BY_KCHARS.keys()) == sorted(KCAP_BY_KCHARS.keys())

assert KCAP_SEP == " "
for _KCAP in KCAP_BY_KCHARS.values():
    assert " " not in _KCAP, (_KCAP,)

# the ⌥⇧Fn Key Cap quotes only the Shifting Keys, dropping the substantive final Key Cap,
# except that four Shifted Arrows exist at ⎋⇧Fn← ⎋⇧Fn→ ⎋⇧Fn↑ ⎋⇧Fn↓


OPTION_KSTR_BY_1_KCHAR = {
    "á": "⌥EA",  # E
    "é": "⌥EE",
    "í": "⌥EI",
    # without the "j́" of ⌥EJ here (because its Combining Accent comes after as a 2nd K Char)
    "ó": "⌥EO",
    "ú": "⌥EU",
    "´": "⌥ESpacebar",
    "é": "⌥EE",
    "â": "⌥IA",  # I
    "ê": "⌥IE",
    "î": "⌥II",
    "ô": "⌥IO",
    "û": "⌥IU",
    "ˆ": "⌥ISpacebar",
    "ã": "⌥NA",  # N
    "ñ": "⌥NN",
    "õ": "⌥NO",
    "˜": "⌥NSpacebar",
    "ä": "⌥UA",  # U
    "ë": "⌥UE",
    "ï": "⌥UI",
    "ö": "⌥UO",
    "ü": "⌥UU",
    "ÿ": "⌥UY",
    "¨": "⌥USpacebar",
    "à": "⌥`A",  # `
    "è": "⌥`E",
    "ì": "⌥`I",
    "ò": "⌥`O",
    "ù": "⌥`U",
    "`": "⌥`Spacebar",  # comes out as ⌥~
}

# hand-sorted by ⌥E ⌥I ⌥N ⌥U ⌥` order


OPTION_KTEXT = """
     ⁄Æ‹›ﬁ‡æ·‚°±≤–≥÷º¡™£¢∞§¶•ªÚ…¯≠˘¿
    €ÅıÇÎ Ï˝Ó Ô\uf8ffÒÂ Ø∏Œ‰Íˇ ◊„˛Á¸“«‘ﬂ—
     å∫ç∂ ƒ©˙ ∆˚¬µ øπœ®ß† √∑≈¥Ω”»’
"""

# ⌥⇧K is Apple Icon  is \uF8FF is in the U+E000..U+F8FF Private Use Area (PUA)

OPTION_KCHARS = " " + textwrap.dedent(OPTION_KTEXT).strip() + " "
OPTION_KCHARS = OPTION_KCHARS.replace("\n", "")

assert len(OPTION_KCHARS) == (0x7E - 0x20) + 1

OPTION_KCHARS_SPACELESS = OPTION_KCHARS.replace(" ", "")


# Give out each Key Cap once, never more than once

_KCHARS_LISTS = [
    list(KCAP_BY_KCHARS.keys()),
    list(OPTION_KSTR_BY_1_KCHAR.keys()),
    list(OPTION_KCHARS_SPACELESS),
]

_KCHARS_LIST = list(_KCHARS for _KL in _KCHARS_LISTS for _KCHARS in _KL)
assert KCAP_SEP == " "
for _KCHARS, _COUNT in collections.Counter(_KCHARS_LIST).items():
    assert _COUNT == 1, (_COUNT, _KCHARS)


def kdata_to_kcaps(kdata: bytes) -> str:
    """Choose Keycaps to speak of the Bytes of 1 Keyboard Chord"""

    kchars = kdata.decode()  # may raise UnicodeDecodeError

    kcap_by_kchars = KCAP_BY_KCHARS  # '\e\e[A' for ⎋↑ etc

    if kchars in kcap_by_kchars.keys():
        kcaps = kcap_by_kchars[kchars]
    else:
        kcaps = ""
        for kch in kchars:  # often 'len(kchars) == 1'
            s = _kch_to_kcap_(kch)
            kcaps += s

            # '⎋[25;80R' Cursor-Position-Report (CPR)
            # '⎋[25;80t' Rows x Column Terminal Size Report
            # '⎋[200~' and '⎋[201~' before/ after Paste to bracket it

        # ⌥Y often comes through as \ U+005C Reverse-Solidus aka Backslash  # not ¥ Yen-Sign

    # Succeed

    assert KCAP_SEP == " "  # solves '⇧Tab' vs '⇧T a b', '⎋⇧FnX' vs '⎋⇧Fn X', etc
    assert " " not in kcaps, (kcaps,)

    return kcaps

    # '⌃L'  # '⇧Z'
    # '⎋A' from ⌥A while macOS Keyboard > Option as Meta Key


def _kch_to_kcap_(ch: str) -> str:  # noqa C901
    """Choose a Key Cap to speak of 1 Char read from the Keyboard"""

    o = ord(ch)

    option_kchars_spaceless = OPTION_KCHARS_SPACELESS  # '∂' for ⌥D
    option_kstr_by_1_kchar = OPTION_KSTR_BY_1_KCHAR  # 'é' for ⌥EE
    kcap_by_kchars = KCAP_BY_KCHARS  # '\x7F' for 'Delete'

    # Show more Key Caps than US-Ascii mentions

    if ch in kcap_by_kchars.keys():  # Mac US Key Caps for Spacebar, F12, etc
        s = kcap_by_kchars[ch]  # '⌃Spacebar', 'Return', 'Delete', etc

    elif ch in option_kstr_by_1_kchar.keys():  # Mac US Option Accents
        s = option_kstr_by_1_kchar[ch]

    elif ch in option_kchars_spaceless:  # Mac US Option Key Caps
        s = _spaceless_ch_to_option_kstr_(ch)

    # Show the Key Caps of US-Ascii, plus the ⌃ ⇧ Control/ Shift Key Caps

    elif (o < 0x20) or (o == 0x7F):  # C0 Control Bytes, or \x7F Delete (DEL)
        s = "⌃" + chr(o ^ 0x40)  # '^ 0x40' speaks of ⌃ with one of @ A..Z [\]^_ ?

        # '^ 0x40' speaks of ⌃@ but not ⌃⇧@ and not ⌃⇧2 and not ⌃Spacebar at b"\x00"
        # '^ 0x40' speaks of ⌃M but not Return at b"\x0D"
        # '^ 0x40' speaks of ⌃[ ⌃\ ⌃] ⌃_ but not ⎋ and not ⌃⇧_ and not ⌃⇧{ ⌃⇧| ⌃⇧} ⌃-
        # '^ 0x40' speaks of ⌃? but not Delete at b"\x7F"

        # ^` ^2 ^6 ^⇧~ don't work

        # todo: can we more quickly decide that ⌃[ is only ⎋ by itself not continued?
        # todo: should we push ⌃- above ⌃⇧_

    elif "A" <= ch <= "Z":  # printable Upper Case English
        s = "⇧" + chr(o)  # shifted Key Cap '⇧A' from b'A'

    elif "a" <= ch <= "z":  # printable Lower Case English
        s = chr(o ^ 0x20)  # plain Key Cap 'A' from b'a'

    # Test that no Keyboard sends the C1 Control Bytes, nor the Quasi-C1 Bytes

    elif o in range(0x80, 0xA0):  # C1 Control Bytes
        assert False, (o, ch)
    elif o == 0xA0:  # 'No-Break Space'
        s = "⌥Spacebar"
        assert False, (o, ch)  # unreached because 'kcap_by_kchars'
    elif o == 0xAD:  # 'Soft Hyphen'
        assert False, (o, ch)

    # Show the US-Ascii or Unicode Char as if its own Key Cap

    else:
        assert o < 0x11_0000, (o, ch)
        s = chr(o)  # '!', '¡', etc

    # Succeed, but insist that Blank Space is never a Key Cap

    assert s.isprintable(), (s, o, ch)  # has no \x00..\x1f, \x7f, \xa0, \xad, etc
    assert " " not in s, (s, o, ch)

    return s

    # '⌃L'  # '⇧Z'


def _spaceless_ch_to_option_kstr_(ch: str) -> str:
    """Convert to Mac US Option Key Caps from any of OPTION_KCHARS_SPACELESS"""

    option_kchars = OPTION_KCHARS  # '∂' for ⌥D

    index = option_kchars.index(ch)
    asc = chr(0x20 + index)
    if "A" <= asc <= "Z":
        asc = "⇧" + asc  # '⇧A'
    if "a" <= asc <= "z":
        asc = chr(ord(asc) ^ 0x20)  # 'A'
    s = "⌥" + asc  # '⌥⇧P'

    return s


#
# Trace what's going on
#


tprinting = False
tprinting = True  # last wins

if tprinting:

    tlog_path = pathlib.Path("__pycache__/t.trace")
    tlog_path.parent.mkdir(exist_ok=True)
    tlog = tlog_path.open("a")


def tprint(*args: object) -> None:
    """Trace what's going on"""

    text = " ".join(str(_) for _ in args)

    if tprinting:
        tlog.write(text + "\n")


#
# Run from the Shell Command Line, if not imported
#


if __name__ == "__main__":
    main()

# 3456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789


# posted as:  https://github.com/pelavarre/xshverb/blob/main/bin/plus.py
# copied from:  git clone https://github.com/pelavarre/xshverb.git
