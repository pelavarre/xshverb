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

import collections
import collections.abc as abc
import datetime as dt
import os
import pathlib
import pdb
import random  # todo6: choose Seeds for Repeatability
import re
import select
import signal
import sys
import termios
import textwrap
import time
import tty
import types
import typing
import unicodedata

if not __debug__:
    raise NotImplementedError([__debug__])  # refuses to run without live Asserts

env_cloud_shell = os.environ.get("CLOUD_SHELL") == "true"  # Google
sys_platform_darwin = sys.platform == "darwin"  # Apple

_: object


#
# Exit nonzero into the Pdb-Pm Post-Mortem Debugger, when not KeyboardInterrupt nor SystemExit
#


with_excepthook = sys.excepthook  # aliases old hook, and fails fast to chain hooks
assert with_excepthook.__module__ == "sys", (with_excepthook.__module__,)
assert with_excepthook.__name__ == "excepthook", (with_excepthook.__name__,)

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

    with_excepthook(exc_type, exc_value, exc_traceback)

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

    sys.excepthook = with_excepthook


def tryme() -> None:
    """Run when called"""

    func = try_tbp_self_test
    func = try_read_byte_packet
    func = try_screen_editor

    func = try_screen_editor  # last choice wins

    # print(f"tryme: {func.__qualname__}", file=sys.stderr)
    # print(file=sys.stderr)

    func()


def try_screen_editor() -> None:
    """Loop Keyboard back to Screen, but as whole Packets, & with some emulations"""

    with ScreenEditor() as se:
        se.play_screen_editor()


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
# Loop Keyboard back to Screen, but as whole Packets or Emulations thereof  # todo4: name the helped
#


IND = "\x1b" "D"  # ESC 04/04 Index (IND) = C1 Control U+0084 IND (formerly known as INDEX)
NEL = "\x1b" "E"  # ESC 04/05 Next Line (NEL) = C1 Control U+0085 NEXT LINE (NEL)
RI = "\x1b" "M"  # ESC 04/06 Reverse Index (RI) = C1 Control U+0086 REVERSE LINE FEED (RI)

_ICF_RIS_ = "\x1b" "c"  # ESC 06/03 Reset To Initial State (RIS) [an Independent Control Function]
_ICF_CUP_ = "\x1b" "l"  # ESC 06/12 Cursor Position (CUP) [an Independent Control Function]


CUU_Y = "\x1b[" "{}" "A"  # CSI 04/01 Cursor Up
CUD_Y = "\x1b[" "{}" "B"  # CSI 04/02 Cursor Down  # \n is Pn 1 except from last Row
CUF_X = "\x1b[" "{}" "C"  # CSI 04/03 Cursor [Forward] Right
CUB_X = "\x1b[" "{}" "D"  # CSI 04/04 Cursor [Back] Left  # \b is Pn 1

CUP_Y1_X1 = "\x1b[" "H"  # CSI 04/08 Cursor Position
CUP_Y_X1 = "\x1b[" "{}" "H"  # CSI 04/08 Cursor Position
CUP_Y_X = "\x1b[" "{};{}" "H"  # CSI 04/08 Cursor Position

CHT_X = "\x1b" "[" "{}I"  # CSI 04/09 Cursor Forward [Horizontal] Tabulation  # \t is Pn 1

ED_P = "\x1b" "[" "{}" "J"  # CSI 04/10 Erase in Display  # 0 Tail # 1 Head # 2 Rows # 3 Scrollback
EL_P = "\x1b[" "{}" "K"  # CSI 04/11 Erase in Line  # 0 Tail # 1 Head # 2 Row

ICH_X = "\x1b[" "{}" "@"  # CSI 04/00 Insert Character
IL_Y = "\x1b[" "{}" "L"  # CSI 04/12 Insert Line [Row]
DCH_X = "\x1b[" "{}" "P"  # CSI 05/00 Delete Character

SU_Y = "\x1b[" "{}" "S"  # CSI 05/03 Scroll Up [Insert South Lines]
SD_Y = "\x1b[" "{}" "T"  # CSI 05/04 Scroll Down [Insert North Lines]

VPA_Y = "\x1b" "[" "{}" "d"  # CSI 06/04 Line Position Absolute

DECIC_X = "\x1b[" "{}" "'}}"  # CSI 02/07 07/13 VT420 DECIC_X  # "}}" to mean "}"
DECDC_X = "\x1b[" "{}" "'~"  # CSI 02/07 07/14 VT420 DECDC_X

SM_IRM = "\x1b[" "4h"  # CSI 06/08 4 Set Mode Insert, not Replace
RM_IRM = "\x1b[" "4l"  # CSI 06/12 4 Reset Mode Replace, not Insert

SGR = "\x1b[" "{}" "m"  # CSI 06/13 Select Graphic Rendition [Text Style]

DSR_6 = "\x1b[" "6n"  # CSI 06/14 [Request] Device Status Report  # Ps 6 for CPR In
CPR_Y_X_REGEX = r"\x1b\[([0-9]+);([0-9]+)R"  # CSI 05/02 Active [Cursor] Pos Rep (CPR)

_SM_XTERM_ALT_ = "\x1b[" "?1049h"  # show Alt Screen
_RM_XTERM_MAIN_ = "\x1b[" "?1049l"  # show Main Screen


DEL = "\x7f"  # 00/7F Delete [Control Character]  # aka ⌃?


_PN_MAX_32100_ = 32100  # an Int beyond the Counts of Rows & Columns at any Terminal


# todo2: Pull ⎋[{y};{x}⇧R always into Side Channel, when requested or not


screen_editors: list[ScreenEditor] = list()


class ScreenEditor:
    """Loop Keyboard back to Screen, but as whole Packets, & with some emulations"""

    keyboard_bytes_log: typing.BinaryIO  # .klog  # logs Keyboard Delays & Bytes
    screen_bytes_log: typing.BinaryIO  # .slog  # logs Screen Delays & Bytes
    bytes_terminal: BytesTerminal  # .bt  # no Line Buffer on Input  # no implicit CR's in Output

    arrows: int  # counts Keyboard Arrow Chords sent faster than people can type them
    settings: list[str]  # Replacing/ Inserting/ etc
    row_y: int  # Y places encoded as Southbound across 1 .. Height
    column_x: int  # X places encoded as Eastbound across 1 .. Width
    list_str_by_y_x: dict[int, dict[int, list[str]]] = dict()  # shadows the last Write at each Place

    func_by_str: dict[str, abc.Callable[[], None]] = dict()
    loopable_kdata_tuple: tuple[bytes, ...] = tuple()

    #
    # Init, Enter, Exit, Print
    #

    def __init__(self) -> None:

        screen_editors.append(self)

        # Init our Keyboard & Screen Drivers

        klog_path = pathlib.Path("__pycache__/k.keyboard")
        slog_path = pathlib.Path("__pycache__/s.screen")

        klog_path.parent.mkdir(exist_ok=True)
        slog_path.parent.mkdir(exist_ok=True)

        klog = klog_path.open("ab")
        slog = slog_path.open("ab")

        self.keyboard_bytes_log = klog
        self.screen_bytes_log = slog
        self.bytes_terminal = BytesTerminal()

        self.arrows = 0
        self.settings = list()  # todo: or default to ⎋[⇧H ⎋[2⇧J ⎋[m etc but not ⎋[3⇧J
        self.row_y = -1
        self.column_x = -1
        self.list_str_by_y_x = dict()

        # Init our Keyboard Chord Bindings

        func_by_str = self.form_none_func_by_str()
        self.func_by_str = func_by_str

        loopable_kdata_tuple = self.form_loopable_kdata_tuple()
        self.loopable_kdata_tuple = loopable_kdata_tuple

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
        assert CUP_Y_X1 == "\x1b[" "{}" "H"
        assert SGR == "\x1b[" "{}" "m"
        assert RM_IRM == "\x1b[" "4l"
        assert _PN_MAX_32100_ == 32100

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

        schars = " ".join(str(_) for _ in args)
        self.write(schars)
        self.write(end)

    def write(self, text: str) -> None:
        """Write the Bytes, and log them as written"""

        bt = self.bytes_terminal
        fileno = bt.fileno
        slog = self.screen_bytes_log

        schars = text

        sdata = schars.encode()
        os.write(fileno, sdata)

        slog.write(sdata)

        self.write_shadows(sdata)

    #
    # Remember much of what we wrote
    #

    def do_screen_redraw(self) -> None:
        """Redraw the Screen as shadowed, be that wrong or correct"""

        bt = self.bytes_terminal
        column_x = self.column_x
        fileno = bt.fileno
        list_str_by_y_x = self.list_str_by_y_x
        row_y = self.row_y
        slog = self.screen_bytes_log

        (y0, x0) = (self.row_y, self.column_x)

        stext = "\x1b[2J"
        sdata = stext.encode()
        os.write(fileno, sdata)
        slog.write(sdata)

        stext = "\x1b[m"
        sdata = stext.encode()
        os.write(fileno, sdata)
        slog.write(sdata)

        for y in list_str_by_y_x.keys():
            list_str_by_x = list_str_by_y_x[y]
            for x in list_str_by_x.keys():
                x_list_str = list_str_by_x[x]

                self.write(f"\x1b[{y};{x}H")
                for stext in x_list_str:

                    sdata = stext.encode()
                    os.write(fileno, sdata)
                    slog.write(sdata)

        self.write(f"\x1b[{y0};{x0}H")

        # todo4: .do_screen_redraw of Csi ⇧J ⇧H etc bypasses our shadowed writes

    def write_shadows(self, sdata: bytes) -> None:
        """Shadow the Screen Panel"""

        stext = sdata.decode()  # todo: may raise UnicodeDecodeError

        if self.write_text_shadows(stext):
            return

        if self.write_leap_shadows(stext):
            return

        if self.write_toggle_shadows(stext):
            return

        tprint(f"Bytes written but not shadowed {stext=}")  # such as Empty

    def write_text_shadows(self, stext: str) -> bool:
        """Shadow the Text"""

        list_str_by_y_x = self.list_str_by_y_x

        if not stext.isprintable():
            return False

        for ch in stext:
            y = self.row_y
            x = self.column_x

            if (y < 1) or (x < 1):  # todo4: Run .write_text_shadows only in Southwest? How deep?
                continue

            if y not in list_str_by_y_x.keys():
                list_str_by_y_x[y] = dict()

            if x not in list_str_by_y_x[y].keys():
                list_str_by_y_x[y][x] = list()

            writes = list_str_by_y_x[y][x]
            writes.clear()
            writes.append(ch)

            x_width = self._str_guess_x_width(ch)
            self.column_x += x_width

        return False

    def _str_guess_x_width(self, text: str) -> int:
        """Guess the Width on Screen of printing a Text"""

        x_width = 0
        for ch in text:
            eaw = unicodedata.east_asian_width(ch)
            x_width += 1
            if eaw in ("F", "W"):
                x_width += 1

        return x_width

    def write_leap_shadows(self, stext: str) -> bool:
        """Shadow the Control Byte Sequences that move the Terminal Cursor"""

        sdata = stext.encode()  # todo: may raise UnicodeEncodeError

        bt = self.bytes_terminal
        column_x = self.column_x
        row_y = self.row_y

        y_height = bt.read_y_height()
        x_width = bt.read_x_width()

        #

        assert HT == "\t"
        assert LF == "\n"
        assert CR == "\r"

        if sdata == b"\t":
            self.column_x = ((column_x - 1) // 8 + 1) * 8 + 1
            return True

            # todo5: cap \t shadows by screen panel width

        if sdata == b"\n":
            self.row_y = min(y_height, row_y + 1)
            return True

            # todo6: scroll the Shadowed Text at "\n" etc

        if sdata == b"\r":
            self.column_x = 1
            return True

        if sdata == b"\r\n":  # takes CR LF as 1 Control Sequence despite 2 TerminalBytePacket
            self.column_x = 1
            self.row_y = min(y_height, row_y + 1)
            return True

            # todo6: scroll the Shadowed Text at "\n" etc

            # todo: reconsider CR LF is 2 TerminalBytePacket, not 1

        #

        assert CUU_Y == "\x1b[" "{}" "A"
        assert CUD_Y == "\x1b[" "{}" "B"
        assert CUF_X == "\x1b[" "{}" "C"
        assert CUB_X == "\x1b[" "{}" "D"

        assert CUP_Y_X == "\x1b[" "{}" ";" "{}" "H"

        tbp = TerminalBytePacket(sdata)
        csi = tbp.head == b"\x1b["  # takes Csi ⎋[, but not Esc Csi ⎋⎋[

        if csi and tbp.tail in b"ABCD":
            assert not tbp.back, (tbp.back, tbp)
            pn = int(tbp.neck) if tbp.neck else 1

            if tbp.tail == b"A":
                self.row_y = max(1, row_y - pn)
                return True
            if tbp.tail == b"B":
                self.row_y = min(y_height, row_y + pn)
                return True
            if tbp.tail == b"C":
                self.column_x = min(x_width, column_x + pn)
                return True
            if tbp.tail == b"D":
                self.column_x = max(1, column_x - pn)
                return True

        if csi and tbp.tail == b"H":
            assert not tbp.back, (tbp.back, tbp)

            neck_splits = tbp.neck.split(b";")
            assert len(neck_splits) <= 2, (neck_splits, tbp.neck, tbp)

            neck_plus_splits = neck_splits + [b"1", b"1"]

            row_y = int(neck_plus_splits[0])
            column_x = int(neck_plus_splits[1])

            self.row_y = row_y  # for .write_leap_shadows
            self.column_x = column_x  # for .write_leap_shadows

            return True

        #

        return False

    def write_toggle_shadows(self, stext: str) -> bool:
        """Shadow the Replacing/ Inserting choice for before writing each Character"""

        settings = self.settings

        assert SM_IRM == "\x1b[" "4h"
        assert RM_IRM == "\x1b[" "4l"

        toggle_pairs = [
            ("\x1b[" "4h", "\x1b[" "4l"),
        ]

        for toggle_pair in toggle_pairs:
            if stext in toggle_pair:
                index = toggle_pair.index(stext)
                other = toggle_pair[1 - index]

                if other in settings:
                    settings.remove(other)
                settings.append(stext)

                return True

        return False

    def read_shadow_settings(self, stext0: str, stext1: str) -> str:
        """Read the present Shadow Setting of a pair:  the one, the other, else empty Bytes"""

        settings = self.settings

        zero = stext0 in settings
        one = stext1 in settings

        assert not (zero and one), (zero, one, stext0, stext1)
        if zero:
            return stext0
        if one:
            return stext1

        return ""

    #
    # Bind Keyboard Chords to Funcs
    #

    def form_none_func_by_str(self) -> dict[str, abc.Callable[[], None]]:
        """Bind Keycaps to Funcs"""

        func_by_str: dict[str, abc.Callable[[], None]] = {
            #
            # 1-Byte 7-Bit C0 Controls
            #
            "⌃A": self.do_column_leap_leftmost,  # ⌃A for Emacs
            "⌃B": self.do_column_left,  # ⌃B for Emacs
            # "\x03",  # ⌃C
            "⌃D": self.do_char_delete_here,  # ⌃D for Emacs
            "⌃E": self.do_column_leap_rightmost,  # ⌃E for Emacs
            "⌃F": self.do_column_right,  # ⌃F for Emacs
            # b"\x07",  # ⌃G \a bell-ring
            # b"\x08",  # ⌃H \b ←  # todo: where does Windows Backspace land?
            # b"\x09",  # ⌃I \t Tab
            # b"\x0a",  # ⌃J \n ↓, else Scroll Up and then ↓
            "⌃K": self.do_row_tail_erase,  # ⌃K for Emacs when not rightmost
            "⌃L": self.do_screen_redraw,  # ⌃L for Vim  # not ⌃L for Emacs a la Vim ⇧H ⇧M ⇧L
            # # b"\x0d",  # ⌃M \r Return  # only \r Return at gCloud
            "Return": self.do_write_cr_lf,  # ⌃M \r Return  # only \r Return at gCloud
            "⌃N": self.do_row_down,  # ⌃N
            "⌃O": self.do_row_insert,  # ⌃O for Emacs when leftmost  # not Vim I ⌃O
            "⌃P": self.do_row_up,  # ⌃P
            "⌃Q": self.do_quote_one_kdata,  # ⌃Q for Emacs
            # # b"\x12",  # ⌃R
            # # b"\x13",  # ⌃S
            # # b"\x14",  # ⌃T
            # # b"\x15",  # ⌃U
            "⌃V": self.do_quote_one_kdata,  # ⌃V for Vim
            # # b"\x17",  # ⌃W
            # # b"\x18",  # ⌃X
            # # b"\x19",  # ⌃Y
            # # b"\x1a",  # ⌃Z
            # todo2: ⌃X⌃C ⌃X⌃S for Emacs
            #
            # Esc and Esc Byte Pairs
            #
            # # b"\x1b": self.print_kcaps_plus,  # ⎋
            #
            "⎋$": self.do_column_leap_rightmost,  # ⎋⇧$ for Vim  # todo4: ⎋⇧$ vs ⎋$
            "⎋0": self.do_column_leap_leftmost,  # ⎋0 for Vim
            # # b"\x1b" b"7",  # ⎋7 cursor-checkpoint
            # # b"\x1b" b"8",  # ⎋8 cursor-revert
            # todo2: ⎋⇧0 ⎋⇧1 ⎋⇧2 ⎋⇧3 ⎋⇧4 ⎋⇧5 ⎋⇧6 ⎋⇧7 ⎋⇧8 ⎋⇧9 for Vim
            #
            "⎋⇧A": self.do_column_leap_rightmost_inserting_start,  # ⇧A for Vim
            "⎋⇧C": self.do_row_tail_erase_inserting_start,  # ⇧C for Vim
            # # b"\x1b" b"D",  # ⎋⇧D ↓ (IND)
            "⎋⇧D": self.do_row_tail_erase,  # Vim ⇧D
            # # b"\x1b" b"E",  # ⎋⇧E \r\n else \r (NEL)
            # "\x1b" "J": self do_end_delete_right  # ⎋⇧J  # todo2: Delete Row if at 1st Column
            "⎋⇧H": self.do_row_leap_first_column_leftmost,  # ⎋⇧H for Vim
            "⎋⇧L": self.do_row_leap_last_column_leftmost,  # ⎋⇧L for Vim
            # # b"\x1b" b"M",  # ⎋⇧M ↑ (RI)
            "⎋⇧M": self.do_row_leap_middle_column_leftmost,  # ⎋⇧M for Vim
            "⎋⇧O": self.do_row_insert_inserting_start,  # ⎋⇧O for Vim
            "⎋⇧Q": self.do_assert_false,  # ⎋⇧Q for Vim
            "⎋⇧R": self.do_replacing_start,  # ⎋⇧R for Vim
            "⎋⇧S": self.do_row_delete_start_inserting,  # ⎋S for Vim
            "⎋⇧X": self.do_char_delete_left,  # ⎋⇧X for Vim
            # todo2: ⎋⇧Z⇧Q ⎋⇧Z⇧W for Vim
            #
            "⎋A": self.do_column_right_inserting_start,  # ⎋A for Vim
            # # b"\x1b" b"c",  # ⎋C cursor-revert (_ICF_RIS_)
            "⎋H": self.do_column_left,  # ⎋H for Vim
            "⎋I": self.do_inserting_start,  # ⎋I for Vim
            "⎋J": self.do_row_down,  # ⎋J for Vim
            "⎋K": self.do_row_up,  # ⎋K for Vim
            # # b"\x1b" b"l",  # ⎋L row-column-leap  # not at gCloud (_ICF_CUP_)
            "⎋L": self.do_column_right,  # ⎋L for Vim
            "⎋O": self.do_row_down_insert_inserting_start,  # ⎋O for Vim
            "⎋R": self.do_replacing_one_kdata,  # ⎋R for Vim
            "⎋S": self.do_char_delete_here_start_inserting,  # ⎋S for Vim
            "⎋X": self.do_char_delete_here,  # ⎋X for Vim
            #
            # Csi Esc Byte Sequences without Parameters and without Intermediate Bytes,
            #
            # # b"\x1b[": self.print_kcaps_plus,  # ⎋ [
            #
            # b"\x1b[" b"A",  # ⎋[⇧A ↑
            # b"\x1b[" b"B",  # ⎋[⇧B ↓
            # b"\x1b[" b"C",  # ⎋[⇧C →
            # b"\x1b[" b"D",  # ⎋[⇧D ←
            # # b"\x1b[" b"I",  # ⎋[⇧I ⌃I  # not at gCloud
            # b"\x1b[" b"Z",  # ⎋[⇧Z ⇧Tab
            #
            "F9": self.do_kdata_fn_f9,  # Fn F9
            #
            # Ss3 Esc Byte Sequences
            #
            # # b"\x1bO": self.print_kcaps_plus,  # ⎋⇧O
            #
            "F1": self.do_kdata_fn_f1,  # Fn F1  # todo4: Fn F1 vs F1
            "F2": self.do_kdata_fn_f2,  # Fn F2
            #
            # Printable but named Characters
            #
            "Spacebar": self.do_write_spacebar,  # Spacebar
            #
            # The Last 1-Byte 7-Bit Control, which looks lots like a C0 Control
            #
            "Delete": self.do_char_delete_left,  # ⌃? Delete  # todo2: Delete Row if at 1st Column
        }

        return func_by_str

        # # Take Vim ⌃O Str-Str Pairs same as Vim ⎋ Esc-Byte Pairs  # todo4:
        #
        # items = list(func_by_str.items())
        #
        # for (kstr, func) in items:
        #     if len(kstr) == 2:
        #         if kstr.startswith("\x1b"):
        #             alt_kstr = b"\x15" + kdata[1:]  # ⌃O
        #
        #             assert alt_kstr not in func_by_str.keys()
        #             func_by_str[alt_kstr] = func  # todo4: need Chord Sequences to do Vim I ⌃O

    def form_loopable_kdata_tuple(self) -> tuple[bytes, ...]:
        """List Keyboard Encodings that run well when looped back to Screen"""

        d = (
            b"\x07",  # ⌃G \a bell-ring
            b"\x08",  # ⌃H \b ←  # todo: where does Windows Backspace land?
            b"\x09",  # ⌃I \t Tab
            b"\x0a",  # ⌃J \n ↓, else Scroll Up and then ↓
            # b"\x0d",  # ⌃M \r Return  # only \r Return at gCloud
            #
            # b"\x1b": self.print_kcaps_plus,  # ⎋
            #
            # b"\x1b" b"7",  # ⎋7 cursor-checkpoint
            # b"\x1b" b"8",  # ⎋8 cursor-revert
            # b"\x1b" b"D",  # ⎋⇧D ↓ (IND)
            # b"\x1b" b"E",  # ⎋⇧E \r\n else \r (NEL)
            # b"\x1b" b"M",  # ⎋⇧M ↑ (RI)
            # b"\x1b" b"c",  # ⎋C cursor-revert (_ICF_RIS_)
            # b"\x1b" b"l",  # ⎋L row-column-leap  # not at gCloud (_ICF_CUP_)
            #
            # b"\x1bO": self.print_kcaps_plus,  # ⎋⇧O
            #
            # b"\x1b[": self.print_kcaps_plus,  # ⎋ [
            b"\x1b[" b"A",  # ⎋[⇧A ↑
            b"\x1b[" b"B",  # ⎋[⇧B ↓
            b"\x1b[" b"C",  # ⎋[⇧C →
            b"\x1b[" b"D",  # ⎋[⇧D ←
            # b"\x1b[" b"I",  # ⎋[⇧I ⌃I  # not at gCloud
            b"\x1b[" b"Z",  # ⎋[⇧Z ⇧Tab
        )

        loopable_kdata_tuple = tuple(bytes(_) for _ in d)  # to please PyLance

        return loopable_kdata_tuple

        # todo3: bind ⎋ and ⌃U to Vim/Emacs Repeat Counts

        # todo2: bind Keyboard Chord Sequences, no longer just Keyboard Chords
        # todo2: bind ⌃C ⇧O for Emacs overwrite-mode, or something
        # todo2: bind bin/é bin/e-aigu bin/latin-small-letter-e-with-acute to this kind of editing
        # todo2: history binds only while present, or falls back like ⎋⇧$ and ⌃E to max right

    #
    # Loop Keyboard back to Screen, but as whole Packets, & with some emulations
    #

    def play_screen_editor(self) -> None:
        """Loop Keyboard back to Screen, but as whole Packets, & with some emulations"""

        bt = self.bytes_terminal

        # Tell our Shadow where our next Write will land

        (row_y, column_x) = bt.read_row_y_column_x()
        self.row_y = row_y  # for .play_screen_editor
        self.column_x = column_x  # for .play_screen_editor

        #

        self.write("\x1b[J")
        self.print("Want some Buttons?")
        self.print()
        self.print("<Bold> <Underline> <Plain>  <Blue> <Green> <Orange> <Red>  <Jabberwocky>")
        self.print()
        self.print("Press ⌃D to quit, else Fn F1 for help, else see what happens")

        # Walk one step after another

        while True:
            try:
                self.read_eval_print_once()
            except SystemExit:
                break

    def read_eval_print_once(self) -> None:
        """Loop Keyboard back to Screen, but as whole Packets, & with some emulations"""

        # Reply to each Keyboard Chord Input, till quit

        # todo2: Quit in many of the Emacs & Vim ways, including Vim ⌃C :vi ⇧Z ⇧Q
        # todo2: Maybe or maybe-not quit after ⌃D, vs quitting now only at ⌃D

        t0 = time.time()
        (tbp, n) = self.read_some_byte_packets()
        t1 = time.time()
        t1t0 = t1 - t0

        arrows = self.arrows
        tprint(f"{arrows=} {n=} t1t0={t1t0:.6f} {tbp=}  # read_eval_print_once")
        assert tbp, (tbp, n)  # because .timeout=None

        kdata = tbp.to_bytes()
        assert kdata, (kdata,)  # because .timeout=None

        self.reply_to_kdata(tbp, n=n)  # may raise SystemExit

        if kdata == b"\x04":  # ⌃D
            raise SystemExit()

        # todo2: Read Str not Bytes from Keyboard, and then List[Str]
        # todo2: Stop taking slow b'\x1b[' b'L' as 1 Whole Packet from gCloud

    def reply_to_kdata(self, tbp: TerminalBytePacket, n: int) -> None:
        """Reply to 1 Keyboard Chord Input, maybe differently if n == 1 quick, or slow"""

        func_by_str = self.func_by_str
        loopable_kdata_tuple = self.loopable_kdata_tuple
        klog = self.keyboard_bytes_log

        # Append to our __pycache__/k.keyboard Keylogger Keylogging File

        kdata = tbp.to_bytes()
        assert kdata, (kdata,)  # because .timeout=None

        klog.write(kdata)

        # Call 1 Func Def by Keycaps

        kcaps = kdata_to_kcaps(kdata)

        if kcaps in func_by_str.keys():
            none_func = func_by_str[kcaps]
            tprint(f"{none_func.__name__=}  # func_by_str reply_to_kdata")  # not .__qualname__

            none_func()  # may raise SystemExit

            return

        if kdata in loopable_kdata_tuple:
            tprint(f"{kdata=} # do_write_kdata_as_sdata reply_to_kdata")  # not .__qualname__

            self.do_write_kdata_as_sdata(kdata)  # for .loopable_kdata_tuple

            return

        # Write the KData, but as Keycaps, when it is a Keycap but not a Func Def

        kchars = kdata.decode()  # may raise UnicodeDecodeError
        if kchars in KCAP_BY_KCHARS.keys():  # already handled above
            tprint(f"Keycap {kchars=} {str(tbp)=}   # reply_to_kdata")

            if (n == 1) or (tbp.tail != b"H"):  # falls-through to pass-through slow ⎋[⇧H CUP_Y_X

                self.print_kcaps_plus(tbp)

                return

        # Pass through 1 Unicode Character

        if tbp.text:
            tprint(f"tbp.text {kdata=}  # reply_to_kdata")

            self.write(tbp.text)

            return

            # todo2: stop wrongly passing through multibyte Control Characters

        # Pass-Through, or emulate, the famous Control Byte Sequences

        if self.take_tbp_n_kdata_if(tbp, n=n, kdata=kdata):

            return

        # Fallback to show the Keycaps that send this Terminal Byte Packet slowly from Keyboard

        tprint(f"else {kdata=} {str(tbp)=}   # reply_to_kdata")
        self.print_kcaps_plus(tbp)

    def take_tbp_n_kdata_if(self, tbp: TerminalBytePacket, n: int, kdata: bytes) -> bool:
        """Emulate the KData Control Sequence and return it, else return False"""

        # Emulate famous Esc Byte Pairs

        if self._take_csi_row_1_column_1_leap_if_(kdata):  # ⎋L
            return True

        # Emulate famous Csi Control Byte Sequences,
        # beyond Screen_Writer_Help of ⎋[ ⇧@⇧A⇧B⇧C⇧D⇧E⇧G⇧H⇧I⇧J⇧K⇧L⇧M⇧P⇧S⇧T⇧Z ⇧}⇧~ and ⎋[ DHLMNQT,
        # so as to also emulate timeless Csi ⇧F ⇧X ` F and slow Csi X

        csi = tbp.head == b"\x1b["  # takes Csi ⎋[, but not Esc Csi ⎋⎋[

        csi_timeless_tails = b"@ABCDEFGHIJKLPSTXZ" + b"`dfhlqr" + b"}~"
        csi_slow_tails = b"M" b"cmntx"  # still not b"NOQRUVWY" and not "abegijkopsuvwyz"

        csi_famous = csi and tbp.tail and (tbp.tail in csi_timeless_tails)
        if (n > 1) and csi and tbp.tail and (tbp.tail in csi_slow_tails):
            csi_famous = True

        # Shrug off a Mouse Press if quick
        # Reply to a Mouse Release, no matter if slow or quick
        # And kick back on anything else that's not Csi Famous

        if not csi_famous:
            if self._take_csi_mouse_press_if_(tbp, n=n):
                return True
            if self._take_csi_mouse_release_if_(tbp):
                return True

            return False

        # Emulate the Csi Famous that don't work so well when passed through

        if self._take_csi_tab_right_leap_if_(tbp):  # ⎋[{}⇧I
            return True

        if self._take_csi_rows_up_if_(tbp):  # ⎋[{}⇧S
            return True

        if self._take_csi_rows_down_if_(tbp):  # ⎋[{}⇧T
            return True

        if self._take_csi_row_default_leap_if_(kdata):  # ⎋[d
            return True

        if tbp.tail == b"}":  # ⎋ [ ... ⇧} especially ' ⇧}
            self._take_csi_cols_insert_if_(tbp)
            return True

        if tbp.tail == b"~":  # ⎋ [ ... ⇧~ especially ' ⇧~
            self._take_csi_cols_delete_if_(tbp)
            return True

        # Pass-through the .csi_slow_tails when slow.
        # Also pass-through the .csi_timeless_tails not taken above, no matter if slow or quick

        tprint(f"Pass-through {kdata=} {str(tbp)=}   # take_tbp_n_kdata_if")
        self.do_write_kdata_as_sdata(kdata)  # for .csi_slow_tails and untaken .csi_timeless_tails

        return True

    #
    # Define some emulations
    #

    def print_kcaps_plus(self, tbp: TerminalBytePacket) -> None:
        """Show the Keycaps that send this Terminal Byte Packet slowly from Keyboard"""

        kdata = tbp.to_bytes()
        assert kdata, (kdata,)

        kcaps = kdata_to_kcaps(kdata)
        self.print(kcaps, end=" ")

    def _take_csi_cols_delete_if_(self, tbp: TerminalBytePacket) -> bool:
        """Emulate ⎋['⇧~ cols-delete"""

        bt = self.bytes_terminal

        assert DCH_X == "\x1b[" "{}" "P"
        assert VPA_Y == "\x1b[" "{}" "d"
        assert DECDC_X == "\x1b[" "{}" "'~"

        csi = tbp.head == b"\x1b["  # takes Csi ⎋[, but not Esc Csi ⎋⎋[
        if not (csi and ((tbp.back + tbp.tail) == b"'~")):
            return False

        tprint("⎋['⇧~ cols-delete" f" {tbp=}   # _take_csi_cols_delete_if_")

        n = int(tbp.neck) if tbp.neck else 1
        y_height = bt.read_y_height()

        (row_y, column_x) = bt.read_row_y_column_x()
        self.row_y = row_y  # for ._take_csi_cols_delete_if_
        self.column_x = column_x  # for ._take_csi_cols_delete_if_

        for y in range(1, y_height + 1):
            self.write(f"\x1b[{y}d")  # for .columns_delete_n
            self.write(f"\x1b[{n}P")  # for .columns_delete_n
        self.write(f"\x1b[{row_y}d")  # for .columns_delete_n

        return True

        # macOS Terminal & gCloud Shell lack ⎋['⇧~ cols-delete

    def _take_csi_cols_insert_if_(self, tbp: TerminalBytePacket) -> bool:
        """Emulate ⎋['⇧} cols-insert"""

        bt = self.bytes_terminal

        assert ICH_X == "\x1b[" "{}" "@"
        assert VPA_Y == "\x1b[" "{}" "d"
        assert DECDC_X == "\x1b[" "{}" "'~"
        assert DECIC_X == "\x1b[" "{}" "'}}"

        csi = tbp.head == b"\x1b["  # takes Csi ⎋[, but not Esc Csi ⎋⎋[
        if not (csi and ((tbp.back + tbp.tail) == b"'}")):
            return False

        tprint("⎋['⇧~ cols-delete" f" {tbp=}   # _take_csi_cols_delete_if_")

        n = int(tbp.neck) if tbp.neck else 1
        y_height = bt.read_y_height()

        (row_y, column_x) = bt.read_row_y_column_x()
        self.row_y = row_y  # for ._take_csi_cols_insert_if_
        self.column_x = column_x  # for ._take_csi_cols_insert_if_

        for y in range(1, y_height + 1):
            self.write(f"\x1b[{y}d")  # for .columns_delete_n
            self.write(f"\x1b[{n}@")  # for .columns_delete_n
        self.write(f"\x1b[{row_y}d")  # for .columns_delete_n

        return True

        # macOS Terminal & gCloud Shell lack ⎋['⇧} cols-insert

    def _take_csi_row_1_column_1_leap_if_(self, kdata: bytes) -> bool:
        """Emulate Famous Esc Byte Pairs, no matter if quick or slow"""

        assert CUP_Y1_X1 == "\x1b[" "H"

        if kdata != b"\x1b" b"l":
            return False

        tprint(f"{kdata=}  # _take_csi_row_1_column_1_leap_if_")

        self.write("\x1b[H")  # for ⎋L

        return True

        # gCloud Shell lacks macOS ⎋L

    def _take_csi_mouse_press_if_(self, tbp: TerminalBytePacket, n: int) -> bool:
        """Shrug off a Mouse Press if quick"""

        csi = tbp.head == b"\x1b["  # takes Csi ⎋[, but not Esc Csi ⎋⎋[
        if (n == 1) and csi and tbp.tail and (tbp.tail == b"M"):
            return True  # drops first 1/2 or 2/3 of Sgr Mouse

        return False

    def _take_csi_mouse_release_if_(self, tbp: TerminalBytePacket) -> bool:
        """Reply to a Mouse Release, no matter if slow or quick"""

        # Eval the Sgr Mouse Report

        csi = tbp.head == b"\x1b["  # takes Csi ⎋[, but not Esc Csi ⎋⎋[
        if not (csi and tbp.tail and (tbp.tail == b"m")):
            return False

        splits = tbp.neck.removeprefix(b"<").split(b";")
        assert len(splits) == 3, (splits, tbp.neck, tbp)
        (f, x, y) = list(int(_) for _ in splits)  # ⎋[<{f};{x};{y}m

        # Decode f = 0b⌃⌥⇧00

        Basic_0 = 0b00000

        Shift_4 = 0b00100
        Option_8 = 0b01000
        Control_16 = 0b10000

        assert (f & ~(Shift_4 | Option_8 | Control_16)) == 0, (hex(f),)

        # Dispatch ⌥ Mouse Release

        if f in (Basic_0, Option_8):

            self.take_verb_at_yxf_mouse_release(y, x=x, f=f)

            return True

        # Reply to Shifting or no Shifting at Mouse Release

        if f == 0:
            self.write("*")  # unreached when f == 0 because Code far above

        if f & Control_16:
            self.write("⌃")
        if f & Option_8:
            self.write("⌥")  # unreached when f == 8 because Code far above
        if f & Shift_4:
            self.write("⇧")

        return True

        # todo: support 1005 1015 Mice, not just 1006 and Arrows Burst

    def _take_csi_row_default_leap_if_(self, kdata: bytes) -> bool:
        """Emulate Line Position Absolute (VPA_Y) but only for an implicit ΔY = 1"""

        assert VPA_Y == "\x1b[" "{}" "d"

        if kdata != b"\x1b[d":
            return False

        tprint(f"⎋[d {kdata=}   # _take_csi_row_default_leap_if_")

        self.write("\x1b[1d")  # carefully not empty Parameters via "\x1b[d"

        return True

        # gCloud Shell needs ⎋[1D for ⎋[D

    def _take_csi_rows_down_if_(self, tbp: TerminalBytePacket) -> bool:
        """Emulate Scroll Down [Insert North Lines]"""

        assert DECSC == "\x1b" "7"
        assert DECRC == "\x1b" "8"

        assert CUU_Y == "\x1b[" "{}" "A"
        assert IL_Y == "\x1b[" "{}" "L"
        assert SD_Y == "\x1b[" "{}" "T"

        csi = tbp.head == b"\x1b["  # takes Csi ⎋[, but not Esc Csi ⎋⎋[
        if not (csi and (tbp.tail == b"T")):
            return False

        n = int(tbp.neck) if tbp.neck else 1

        self.write("\x1b7")
        self.write("\x1b[32100A")
        self.write(f"\x1b[{n}L")
        self.write("\x1b8")

        return True

        # gCloud Shell lacks macOS ⎋[{}⇧T

    def _take_csi_rows_up_if_(self, tbp: TerminalBytePacket) -> bool:
        """Emulate Scroll Up [Insert South Lines]"""

        assert LF == "\n"

        assert DECSC == "\x1b" "7"
        assert DECRC == "\x1b" "8"

        assert CUD_Y == "\x1b[" "{}" "B"
        assert SU_Y == "\x1b[" "{}" "S"
        assert _PN_MAX_32100_ == 32100

        csi = tbp.head == b"\x1b["  # takes Csi ⎋[, but not Esc Csi ⎋⎋[
        if not (csi and (tbp.tail == b"S")):
            return False

        n = int(tbp.neck) if tbp.neck else 1

        self.write("\x1b7")
        self.write("\x1b[32100B")
        self.write(n * "\n")
        self.write("\x1b8")

        return True

        # gCloud Shell lacks macOS ⎋[{}⇧S

    def _take_csi_tab_right_leap_if_(self, tbp: TerminalBytePacket) -> bool:
        """Emulate Cursor Forward [Horizontal] Tabulation (CHT) for Pn >= 1"""

        assert HT == "\t"
        assert CHT_X == "\x1b[" "{}" "I"

        csi = tbp.head == b"\x1b["  # takes Csi ⎋[, but not Esc Csi ⎋⎋[
        if not (csi and (tbp.tail == b"I")):
            return False

        tprint(f"⎋[...I {tbp=}  # _take_csi_tab_right_leap_if_")

        pn = int(tbp.neck) if tbp.neck else 1
        assert pn >= 1, (pn,)
        self.write(pn * "\t")

        return True

        # gCloud Shell lacks ⎋[ {}I

    def do_write_cr_lf(self) -> None:
        """Write CR LF"""

        assert CR == "\r"
        assert LF == "\n"

        self.write("\r\n")

        # todo3: Emacs ⌃M and ⌃K need the Rows shadowed, as does Vim I ⌃M
        # todo3: classic Vim ⇧R does define ⇧R ⌃M same as I ⌃M

    #
    #
    #

    def read_some_byte_packets(self) -> tuple[TerminalBytePacket, int]:
        """Read 1 TerminalBytePacket, all in one piece, else in split pieces"""

        arrows = self.arrows
        bt = self.bytes_terminal

        # Count out a rapid burst of >= 2 Arrows

        arrows_timeout = 0.010

        n = 1

        t0 = time.time()

        if not arrows:
            tbp = bt.read_byte_packet(timeout=None)
        else:
            tbp = bt.read_byte_packet(timeout=arrows_timeout)
            if not tbp:
                self.arrows = 0  # written only by Init & this Def

                tbp = self.read_arrows_as_byte_packet()
                assert tbp, (tbp,)

                return (tbp, n)

        t1 = time.time()

        kdata = tbp.to_bytes()
        t1t0 = t1 - t0

        if kdata not in (b"\x1b[A", b"\x1b[B", b"\x1b[C", b"\x1b[D"):
            self.arrows = 0  # written only by Init & this Def
        elif t1t0 >= arrows_timeout:
            self.arrows = 0  # written only by Init & this Def
        else:
            self.arrows += 1

        while (not tbp.text) and (not tbp.closed) and (not bt.extras):

            kdata = tbp.to_bytes()
            # if kdata in (b"\x1b", b"\x1bO", b"\x1b[", b"\x1b\x1b", b"\x1b\x1bO", b"\x1b\x1b["):
            if kdata == b"\x1bO":  # ⎋⇧O for Vim
                break

            n += 1
            bt.close_byte_packet_if(tbp, timeout=None)

        # Succeed

        return (tbp, n)

        # todo: log & echo the Keyboard Bytes as they arrive, stop waiting for whole Packet

    def read_arrows_as_byte_packet(self) -> TerminalBytePacket:
        """Take Slow-after-Arrow-Burst as a ⌥ Mouse Release, with never a Press"""

        bt = self.bytes_terminal

        (row_y, column_x) = bt.read_row_y_column_x()
        self.row_y = row_y  # for .read_arrows_as_byte_packet
        self.column_x = column_x  # for .read_arrows_as_byte_packet

        option_f = int("0b01000", base=0)  # f = 0b⌃⌥⇧00
        ktext = f"\x1b[<{option_f};{column_x};{row_y}m"
        kdata = ktext.encode()

        tbp = TerminalBytePacket(kdata)

        return tbp

        # todo6: Undo the Arrow Burst after making it a ⌥ Mouse Release of the ⎋[m kind

    def do_write_spacebar(self) -> None:
        """Write 1 Space"""

        self.write(" ")

    def do_write_kdata_as_sdata(self, kdata: bytes) -> None:
        """Write the Keyboard Bytes looped back to the Screen"""

        sdata = kdata
        stext = sdata.decode()  # may raise UnicodeDecodeError

        self.write(stext)

    def do_replacing_one_kdata(self) -> None:
        """Start replacing, quote 1 Keyboard Chord, then start inserting"""

        self.do_replacing_start()  # Vim ⇧R
        self.do_quote_one_kdata()  # Emacs ⌃Q  # Vim ⌃V
        self.do_inserting_start()  # Vim I

        # Vim R

    def do_quote_one_kdata(self) -> None:
        """Loopback the Bytes of the next 1 Keyboard Chord onto the screen"""

        (tbp, n) = self.read_some_byte_packets()

        kdata = tbp.to_bytes()
        self.do_write_kdata_as_sdata(kdata)  # for .do_quote_one_kdata

        # Emacs ⌃Q  # Vim ⌃V

    def do_assert_false(self) -> None:
        """Assert False"""

        assert False

        # Vim ⇧Q  # (traditionally swaps Ex Key Bindings in place of Vim Key Bindings)

    def do_raise_system_exit(self) -> None:
        """Raise SystemExit"""

        raise SystemExit()

        # Emacs ⎋ X revert-buffer Return ⌃X ⌃C
        # Vim ⌃C ⌃L ⇧: Q ⇧! Return  # after:  vim -y
        # Vim ⇧Z⇧Q

    #
    # Reply to Emacs & Vim Keyboard Chords
    #

    def do_column_left(self) -> None:
        """Go left by 1 Column"""

        assert BS == "\b"
        self.write("\b")

        # Emacs Delete

    def do_column_right(self) -> None:
        """Go right by 1 Column"""

        assert CUF_X == "\x1b[" "{}" "C"
        self.write("\x1b[C")

        # Emacs ⌃F

    def do_column_right_inserting_start(self) -> None:
        """Insert 1 Space at the Cursor, then go right by 1 Column"""

        self.do_column_right()  # Vim L
        self.do_inserting_start()  # Vim I

        # Vim A = Vim L I

        # todo3: Vim <Digits> ⇧H and Vim <Digits> ⇧L and Vim <Digits> ⇧|T

    def do_char_delete_here(self) -> None:
        """Delete the Character beneath the Cursor"""

        assert DCH_X == "\x1b[" "{}" "P"
        self.write("\x1b[P")

        # Emacs ⌃D  # Vim X

    def do_char_delete_here_start_inserting(self) -> None:
        """Delete the Character beneath the Cursor, and Start Inserting"""

        self.do_char_delete_here()  # Emacs ⌃D  # Vim X
        self.do_inserting_start()  # Vim I

        # Vim S = Vim X I

    def do_char_delete_left(self) -> None:
        """Delete the Character at left of the Cursor"""

        assert BS == "\b"
        assert DCH_X == "\x1b[" "{}" "P"

        x = self.bytes_terminal.read_column_x()
        self.column_x = x

        if x > 1:
            self.write("\b")
            self.write("\x1b[P")

        # Emacs Delete  # Vim ⇧X

        # todo2: Show .do_char_delete_left bouncing off the Left Edge

    def do_column_leap_leftmost(self) -> None:
        """Leap to the Leftmost Column"""

        assert CR == "\r"
        self.write("\r")

        # Emacs ⌃A  # Vim 0

    def do_column_leap_rightmost(self) -> None:
        """Leap to the Rightmost Column"""

        assert CUF_X == "\x1b[" "{}" "C"
        assert _PN_MAX_32100_ == 32100
        self.write("\x1b[32100C")  # for .do_column_leap_rightmost  # Emacs ⌃E  # Vim ⇧$

        # todo3: Leap to Rightmost Shadow, if Row Shadowed

        # Emacs ⌃E  # Vim ⇧$

    def do_column_leap_rightmost_inserting_start(self) -> None:
        """Leap to the Rightmost Column, and Start Inserting"""

        self.do_column_leap_rightmost()  # Emacs ⌃E  # Vim ⇧$
        self.do_inserting_start()  # Vim I

        # Vim ⇧A = Vim ⇧$ I

    def do_inserting_start(self) -> None:
        """Start Inserting Characters at the Cursor"""

        assert SM_IRM == "\x1b[" "4h"
        self.write("\x1b[4h")

        # Vim I

        # todo2: Show Inserting while Inserting

    def do_replacing_start(self) -> None:
        """Start Replacing Characters at the Cursor"""

        assert RM_IRM == "\x1b[" "4l"
        self.write("\x1b[4l")

        # Vim ⇧R

        # todo2: Show Replacing while Replacing

    def do_row_delete_start_inserting(self) -> None:
        """Empty the Row beneath the Cursor, and Start Inserting"""

        self.do_column_leap_leftmost()  # Emacs ⌃A  # Vim 0
        self.do_row_tail_erase()  # Vim ⇧D
        self.do_inserting_start()  # Vim I

        # could be coded as ⎋[2K like a .do_row_tail_erase but without moving the Cursor

        # Vim ⇧S = Vim 0 D I

    def do_row_down(self) -> None:
        """Go down by 1 Row, but stop in last Row"""

        assert CUD_Y == "\x1b[" "{}" "B"
        self.write("\x1b[B")

        # Emacs ⌃N

    def do_row_down_insert_inserting_start(self) -> None:
        """Insert 1 Row below the Cursor"""

        self.do_row_down()  # Vim J
        self.do_row_insert_inserting_start()  # Vim ⇧O

        # Vim O = J ⇧O  # despite ⎋O collides with SS3

    def do_row_insert_inserting_start(self) -> None:

        self.do_row_insert()  # Emacs ⌃O when leftmost
        self.do_column_leap_leftmost()  # Emacs ⌃A  # Vim 0
        self.do_inserting_start()  # Vim I

        # Vim ⇧O = Emacs ⌃A ⌃O + Vim I

    def do_row_insert(self) -> None:
        """Insert 1 Row above the Cursor"""

        assert IL_Y == "\x1b[" "{}" "L"
        self.write("\x1b[L")

        # Emacs ⌃O when leftmost

    def do_row_leap_first_column_leftmost(self) -> None:
        """Leap to the Leftmost Column of the First Row"""

        assert CUP_Y1_X1 == "\x1b[" "H"
        self.write("\x1b[H")  # for .do_row_leap_first_column_leftmost  # Vim ⇧H

        # Vim ⇧H

        # todo3: Leap to First Shadow Row, if Column Shadowed

    def do_row_leap_last_column_leftmost(self) -> None:
        """Leap to the Leftmost Column of the Last Row"""

        assert _PN_MAX_32100_ == 32100
        assert CUP_Y_X1 == "\x1b[" "{}" "H"
        self.write("\x1b[32100H")  # for .do_row_leap_last_column_leftmost  # Vim ⇧L

        # todo3: Leap to Last Shadow Row, if Column Shadowed

        # Vim ⇧L

    def do_row_leap_middle_column_leftmost(self) -> None:
        """Leap to the Leftmost Column of the Middle Row"""

        bt = self.bytes_terminal

        y_height = bt.read_y_height()
        mid_height = (y_height // 2) + (y_height % 2)

        assert CUP_Y_X1 == "\x1b[" "{}" "H"
        self.write(f"\x1b[{mid_height}H")  # for .do_row_leap_middle_column_leftmost  # Vim ⇧M

        # Vim ⇧M

    def do_row_tail_erase(self) -> None:
        """Erase from the Cursor to the Tail of the Row"""

        assert EL_P == "\x1b[" "{}" "K"
        self.write("\x1b[K")

        # Vim ⇧D  # Emacs ⌃K when not rightmost

    def do_row_tail_erase_inserting_start(self) -> None:
        """Erase from the Cursor to the Tail of the Row, and Start Inserting"""

        self.do_row_tail_erase()  # Vim ⇧D  # Emacs ⌃K when not rightmost
        self.do_inserting_start()  # Vim I

        # Vim ⇧C = # Vim ⇧D I

    def do_row_up(self) -> None:
        """Go up by 1 Row, but stop in Top Row"""

        assert CUU_Y == "\x1b[" "{}" "A"
        self.write("\x1b[A")

        # Emacs ⌃P

    #
    # Reply to F1 F2 F9 ...
    #

    def do_kdata_fn_f1(self) -> None:
        """Print Lines of main top Help for F1"""

        f1_text = """
            Shall we play a game?

            F2 - Conway's Game-of-Life
            F9 - Screen Editor

            ⌃D - Quit
        """

        f1_text = textwrap.dedent(f1_text).strip()

        self.print()
        self.print()

        self.print(f1_text.replace("\n", "\r\n"))

        self.print()
        self.print()

    def do_kdata_fn_f2(self) -> None:
        """Play Conway's Game-of-Life for F2"""

        with_none_func_by_str = self.func_by_str

        # Default to Replacing, not Inserting

        assert SM_IRM == "\x1b[" "4h"
        assert RM_IRM == "\x1b[" "4l"

        irm_stext = self.read_shadow_settings("\x1b[4h", stext1="\x1b[4l")
        restore_inserting_replacing = irm_stext  # maybe empty

        self.do_replacing_start()  # for F2

        # Run like the basic ScreenEditor, but with Keyboard Chords bound to ConwayLife

        cl = ConwayLife(se=self)

        func_by_str = dict(with_none_func_by_str)
        conway_none_func_by_str = cl.form_conway_none_func_by_str()
        func_by_str.update(conway_none_func_by_str)

        self.func_by_str = func_by_str

        try:
            cl.play_conway_life()
        finally:
            self.func_by_str = with_none_func_by_str  # replaces
            self.write(restore_inserting_replacing)  # doesn't raise UnicodeEncodeError

    def do_kdata_fn_f9(self) -> None:
        """Print the many Lines of Screen Writer Help for F9"""

        help_ = textwrap.dedent(SCREEN_WRITER_HELP).strip()

        self.print()
        self.print()

        for line in help_.splitlines():
            self.print(line)

        if env_cloud_shell:
            self.print()
            self.print("gCloud Shell ignores ⌃M (you must press Return)")
            self.print("gCloud Shell ignores ⎋[3⇧J Scrollback-Erase (you must close Tab)")
            self.print("gCloud Shell ⌃L between Commands clears Screen (not Scrollback)")
            self.print()

            # gCloud Shell has distinct ← ↑ → ↓ and ⌥ ← ↑ → ↓ and ⌃⌥ ← ↑ → ↓
            # gCloud Shell has ⌥ Esc Delete Return, but ⌥ Esc comes as slow Esc Esc

            # todo2: gCloud AltIsMeta has ...

        if sys_platform_darwin:
            self.print()

            # self.print("macOS Shell ignores ⎋['⇧} and ⎋['⇧~ Cols Insert/Delete")

            self.print("macOS Shell ⌘K clears Screen & Scrollback (but not Top Row)")
            self.print()

            # macOS Shell has distinct ← ↑ → ↓ and ⌥ ← → and ⇧ ← → and ⇧ Fn ← ↑ → ↓
            # macOS Option-as-Meta has ⌥⎋ ⌥Delete ⌥Tab ⌥⇧Tab ⌥Return

        self.print("Press ⌃D to quit, else Fn F1 for help, else see what happens")
        self.print()
        self.print()

        # XShVerb F1

        # todo6: ⌃L goes wrong after _f9 scrolls up my default 101x42 MacBook Terminal

        # todo2: Adopt "Keyboard Shortcuts" over "Bindings"

        # todo2: toggle emulations on/off
        # todo2: toggle tracing input on/off
        # todo2: show loss of \e7 memory because of emulations

        # todo2: accept lots of quits and movements as per Vim ⌃O & Emacs

    #
    # Take ⌥ Mouse Release as a call for Read-Eval-Print
    #

    def take_verb_at_yxf_mouse_release(self, y: int, x: int, f: int) -> None:
        """Take ⌥ Mouse Release as a call for Read-Eval-Print"""

        # Read the Widget at the Mouse

        wx = x
        widget = ""

        y_text = self.read_shadowed_row_y_text(y, default=" ")

        syx = y_text[x]
        if syx != " ":

            suffix_text = y_text[:x]
            suffix_splits = suffix_text.split()
            assert suffix_splits, (suffix_splits, syx, y, x)

            suffix = suffix_splits[-1]
            left_text = suffix_text.removesuffix(suffix)
            wx = 1 + len(left_text)

            index = len(suffix_splits) - 1
            y_splits = y_text.split()

            assert index < len(y_splits), (index, len(y_splits), y_splits, suffix_splits)
            widget = y_splits[index]

            # todo8: pick up phrases, not just words, till like a double-Space separator
            # todo8: debug why Arrow Burst buttons after the first frequently don't work

        # Run the Verb at the Mouse

        self.take_widget_at_yxf(widget, y=y, x=wx, f=f)

    def take_widget_at_yxf(self, widget: str, y: int, x: int, f: int) -> None:
        """Run the Verb at the Mouse"""

        assert BEL == "\a"
        assert BS == "\b"
        assert CUP_Y_X == "\x1b[" "{};{}" "H"
        assert DCH_X == "\x1b[" "{}" "P"

        # Require Widget found

        if not widget:
            self.write("\a")  # for .take_widget_at_yxf
            return

        # Decide to vanish and run once, or to persist

        verb = widget
        if (widget[0] == "<") and (widget[-1] == ">"):
            verb = widget[1:-1]
            if not verb:
                self.write("\a")  # for .take_widget_at_yxf
                return

        # Take the Cursor to the Verb (near to the Mouse), no matter if meaningless

        if verb == widget:  # todo8: doc/ comment  # todo8: some visual feedback of the pushed button

            self.write(f"\x1b[{y};{x}H")  # for .take_verb_at_yxf per Mouse Csi ⎋[M
            assert self.row_y == y, (self.row_y, y)
            assert self.column_x == x, (self.column_x, x)

            # Vanish if the Widget is no more than the Verb, unmarked

            irm_stext = self.read_shadow_settings("\x1b[4h", stext1="\x1b[4l")
            if irm_stext == "\x1b[4h":

                self.write(f"\x1b[{len(widget)}P")  # deletes a Verb, while inserting texts

            else:
                assert (not irm_stext) or (irm_stext == "\x1b[4l"), (irm_stext,)

                self.write(len(widget) * " ")  # erases a Verb, while replacing texts
                # self.write(len(widget) * "\b")
                self.write(f"\x1b[{y};{x}H")

        #

        casefold = verb.casefold()

        #

        if casefold == "bold":  # ⎋[1M bold
            self.write("\x1b[1m")
            # if verb == widget:
            #     self.write("bold")
            return

        if casefold == "underline":  # ⎋[4M underline
            self.write("\x1b[4m")
            # if verb == widget:
            #     self.write("underline")
            return

        if casefold in ("reverse", "inverse"):  # ⎋[7M reverse/inverse
            self.write("\x1b[7m")
            # if verb == widget:
            #     self.write("reverse")
            return

        if casefold == "plain":
            self.write("\x1b[m")
            # if verb == widget:
            #     self.write("plain")
            return

        #

        if casefold == "blue":
            self.write("\x1b[34m")
            return

        if casefold == "green":
            self.write("\x1b[32m")
            return

        if casefold == "orange":
            self.write("\x1b[38;5;130m")  # Color '#310'
            return

        if casefold == "red":
            self.write("\x1b[31m")
            return

        #

        if casefold == "jabberwocky":
            splits = Jabberwocky.split()
            split = random.choice(splits)
            self.write(split + " ")
            return

        #

        self.write("\a")  # for .take_widget_at_yxf

        # todo7: accept ⎋[M notation
        # todo4: find an Italic that works at ⎋[3M or somewhere

    def read_shadowed_row_y_text(self, y: int, default: str) -> str:
        """Read back just the Text Shadowed in the Row"""

        assert len(default.encode()) == 1, (default, len(default.encode()))  # todo: other defaults

        bt = self.bytes_terminal
        list_str_by_y_x = self.list_str_by_y_x

        x_width = bt.read_x_width()

        if y not in list_str_by_y_x.keys():
            return x_width * default

        y_text = ""
        list_str_by_x = list_str_by_y_x[y]
        for x in range(1, x_width + 1):

            syx = default
            if x in list_str_by_x.keys():
                list_str = list_str_by_x[x]
                if list_str:
                    syx = list_str[-1]

            y_text += syx

        return y_text


#
# Play Conway's Game-of-Life
#


# todo7: plain bold italic
# todo7: <mark> flip spin
# todo7: glider, sw glider, ne nw se gliders
# todo7: circle triangle square rectangle polygon

# todo3: Each Y X gets a List Str. Last Item of List Str is the Text written after the Controls
# todo3: Hide the Conway Cursor?
# todo3: Discover the same drawing but translated to new Y X or new Rotation


class ConwayLife:
    """Play Conway's Game-of-Life"""

    screen_editor: ScreenEditor

    yx_board: tuple[int, int]  # places the Gameboard on the Screen Panel
    yx_puck: tuple[int, int]  # places the Puck on the Screen Panel
    steps: int  # counts steps, after -1

    def __init__(self, se: ScreenEditor) -> None:

        self.screen_editor = se

        self.yx_board = (-1, -1)
        self.yx_puck = (-1, -1)
        self.steps = -1

    def play_conway_life(self) -> None:
        """Play Conway's Game-of-Life"""

        se = self.screen_editor

        # Say Hello

        se.print()
        se.print("Hello from Conway's Game-of-Life")
        se.print()
        se.print("← ↑ → ↓ Arrows or ⌥ Mouse to move around")
        se.print("+ - to make a Cell older or younger")
        se.print("Spacebar to step, ⌃Spacebar to make a half step, ⌥← to undo")
        se.print("Tab to step 8x Faster, ⇧Tab undo 8x Faster")
        se.print()

        self.restart_conway_life()

        # Walk one step after another

        while True:
            try:
                se.read_eval_print_once()
            except SystemExit:
                break

        # Say Goodbye

        se.print()
        se.print("Goodbye from Conway's Game-of-Life")

        # todo6: ⌃L goes wrong after Conway Goodbye in one row of White Dots

    def restart_conway_life(self) -> None:
        """Start again, with the most famous Conway Life Glider"""

        se = self.screen_editor
        list_str_by_y_x = se.list_str_by_y_x

        choice = 3

        if choice == 1:
            (y0, x0) = self.yx_board_place(dy=-1, dx=-4)  # todo5: derive dy dx
            self.yx_board = (y0, x0)
            self.yx_puck = (y0, x0)
            self.conway_print_some("⚪🔴⚪🔴⚪")  # todo5: Conway Gameboard at Cursor
            self.conway_print_some("⚪⚪🔴🔴⚪")
            self.conway_print_some("🔵⚪🔴⚪⚪")

            # Southeast Glider

        if choice == 2:
            (y0, x0) = self.yx_board_place(dy=-2, dx=-4)  # todo5: derive dy dx
            self.yx_board = (y0, x0)
            self.yx_puck = (y0, x0)
            self.conway_print_some("🔴⚪⚪⚪🔴")
            self.conway_print_some("🔴🔴⚪🔴🔴")
            self.conway_print_some("🔴⚪🔴⚪🔴")
            self.conway_print_some("⚪🔴⚪🔴⚪")
            self.conway_print_some("⚪⚪🔴⚪⚪")

            # https://imgur.com/a/interesting-face-pattern-conways-game-of-life-epMFxEb

            # todo6: compare/contrast web life at Wolf Face

        if choice == 3:
            (y0, x0) = self.yx_board_place(dy=-1, dx=-4)  # todo5: derive dy dx
            self.yx_board = (y0, x0)
            self.yx_puck = (y0, x0)
            self.conway_print_some("⚪🔴⚪🔴⚪🔵🔵🔵🔵⚪🔴⚪🔴⚪")
            self.conway_print_some("⚪🔴🔴⚪⚪🔵🔵🔵🔵⚪⚪🔴🔴⚪")
            self.conway_print_some("⚪⚪🔴⚪🔵🔵🔵🔵🔵🔵⚪🔴⚪⚪")

            # Southwest Glider & Southeast Glider

        yx_list = list()
        for y in list_str_by_y_x.keys():
            for x in list_str_by_y_x[y].keys():
                yx = (y, x)
                yx_list.append(yx)

        for y, x in yx_list:
            writes = list_str_by_y_x[y][x]
            if writes and writes[-1] == "🔴":
                self.y_x_count_around(y, x)  # adds its Next Spots

        self._leap_conway_between_half_steps_()

    def yx_board_place(self, dy: int, dx: int) -> tuple[int, int]:
        """Leap to our main Center of our Screen Panel"""

        se = self.screen_editor
        bt = se.bytes_terminal

        y_height = bt.read_y_height()
        x_width = bt.read_x_width()

        mid_height = (y_height // 2) + (y_height % 2)
        mid_width = (x_width // 2) + (x_width % 2)

        yx_board = (mid_height + dy, mid_width + dx)

        return yx_board

    def conway_print_some(self, s: str) -> None:
        """Print each Character"""

        se = self.screen_editor

        (y0, x0) = self.yx_puck

        assert CUP_Y_X == "\x1b[" "{};{}" "H"
        se.write(f"\x1b[{y0};{x0}H")  # for .conway_print_some

        (y, x) = (y0, x0)
        for syx in s:
            self.conway_print_y_x_syx(y, x=x, syx=syx)
            x += 2

        y1 = y0 + 1
        x1 = x0
        self.yx_puck = (y1, x1)

    def do_conway_8x_redo(self) -> None:
        """Step the Game of Life forward at 8X Speed"""

        for _ in range(8):
            self._do_conway_half_step_()  # once
            self._do_conway_half_step_()  # twice

        self._leap_conway_between_half_steps_()

        # Tab

    def do_conway_full_step(self) -> None:
        """Step the Game of Life forward by 1 Full Step"""

        steps = self.steps

        if (steps % 2) == 0:  # if halfway
            self._do_conway_half_step_()  # out-of-phase

        self._do_conway_half_step_()  # once
        self._do_conway_half_step_()  # twice

        self._leap_conway_between_half_steps_()

        # ⌃Spacebar

    def do_conway_half_step(self) -> None:
        """Step the Game of Life forward by 1/2 Step"""

        self._do_conway_half_step_()
        self._leap_conway_between_half_steps_()

        # Spacebar

    def _leap_conway_between_half_steps_(self) -> None:
        """Place the Puck between Half-Step's"""

        se = self.screen_editor

        (y0, x0) = self.yx_board_place(dy=0, dx=0)

        assert CUP_Y_X == "\x1b[" "{};{}" "H"
        se.write(f"\x1b[{y0};{x0}H")  # for ._leap_conway_between_half_steps_

    def _do_conway_half_step_(self) -> None:
        """Step the Game of Life forward by 1/2 Step"""

        se = self.screen_editor
        list_str_by_y_x = se.list_str_by_y_x

        steps = self.steps

        steps += 1
        self.steps = steps

        yx_list = list()
        for y in list_str_by_y_x.keys():
            for x in list_str_by_y_x[y].keys():
                yx = (y, x)
                yx_list.append(yx)

        for y, x in yx_list:
            writes = list_str_by_y_x[y][x]
            syx = writes[-1] if writes else ""

            if syx not in ("⚪", "⚫", "🔴", "🟥"):
                continue

            if steps % 2 == 0:
                assert syx in ("⚪", "🔴"), (syx,)
                n = self.y_x_count_around(y, x)

                if (n < 2) and (syx == "🔴"):
                    self.conway_print_y_x_syx(y, x=x, syx="🟥")
                elif (n == 3) and (syx == "⚪"):
                    self.conway_print_y_x_syx(y, x=x, syx="⚫")
                    self.y_x_count_around(y, x)  # adds its Next Spots
                elif (n > 3) and (syx == "🔴"):
                    self.conway_print_y_x_syx(y, x=x, syx="🟥")

            else:
                assert syx in ("⚪", "⚫", "🔴", "🟥"), (syx,)

                if syx == "⚫":
                    self.conway_print_y_x_syx(y, x=x, syx="🔴")
                elif syx == "🟥":
                    self.conway_print_y_x_syx(y, x=x, syx="⚪")

    def y_x_count_around(self, y: int, x: int) -> int:
        """Count the Neighbors of a Cell"""

        se = self.screen_editor
        list_str_by_y_x = se.list_str_by_y_x

        yx_writes = list_str_by_y_x[y][x]
        syx = yx_writes[-1] if yx_writes else ""

        dydx_list = list()
        for dy in range(-1, 1 + 1):
            for dx in range(-2, 2 + 1, 2):
                if dy == 0 and dx == 0:
                    continue

                dydx = (dy, dx)
                dydx_list.append(dydx)

        count = 0
        for dy, dx in dydx_list:
            y1 = y + dy
            x1 = x + dx

            if syx == "⚪":
                if y1 not in list_str_by_y_x.keys():
                    continue
                if x1 not in list_str_by_y_x[y1].keys():
                    continue

            y1x1_write = ""
            if not ((y1 in list_str_by_y_x.keys()) and (x1 in list_str_by_y_x[y1].keys())):
                y1x1_write = "⚪"
                self.conway_print_y_x_syx(y1, x=x1, syx=y1x1_write)

            y1x1_writes = list_str_by_y_x[y1][x1]
            shadow_sy1x1 = y1x1_writes[-1] if y1x1_writes else ""
            if y1x1_write:
                assert y1x1_write == shadow_sy1x1, (y1x1_write, shadow_sy1x1, y1, x1)

            if shadow_sy1x1 in ("🔴", "🟥"):
                count += 1

        return count

    def conway_print_y_x_syx(self, y: int, x: int, syx: str) -> None:
        """Print each Character"""

        se = self.screen_editor
        list_str_by_y_x = se.list_str_by_y_x

        assert CUF_X == "\x1b[" "{}" "C"
        assert CUP_Y_X == "\x1b[" "{};{}" "H"

        se.write(f"\x1b[{y};{x}H")  # for .conway_print_y_x_syx

        if syx != "🔵":
            se.write(syx)

            yx_writes = list_str_by_y_x[y][x]
            yx_shadow_text = yx_writes[-1] if yx_writes else ""
            assert syx == yx_shadow_text, (syx, yx_shadow_text, y, x)

        x += 2

        self.yx_puck = (y, x)

    def form_conway_none_func_by_str(self) -> dict[str, abc.Callable[[], None]]:
        "Bind Keycaps to Funcs"

        se = self.screen_editor

        func_by_str: dict[str, abc.Callable[[], None]] = {
            "⌃D": se.do_raise_system_exit,
            "Tab": self.do_conway_8x_redo,
            # "⇧Tab": self.do_conway_8x_undo,
            "Spacebar": self.do_conway_full_step,
            "⌃Spacebar": self.do_conway_half_step,
            # "⌥Spacebar": self.do_conway_undo,
            # "+": self.do_conway_older,  # todo4:
            # "-": self.do_conway_younger,  # todo4:
            # "MousePress": self.do_conway_pass,  # todo4:
            # "MouseRelease": self.do_conway_leap_here,  # todo4:
            "F2": self.restart_conway_life,
        }

        return func_by_str

        # why does MyPy Strict need .func_by_str declared as maybe not only indexed by Literal Str ?


_ = """  # The 8 Half-Steps of a 5-Pixel Glider


    ⚪⚪⚪⚪⚪⚪  ⚪⚪⚪⚪⚪⚪
    ⚪🔴⚪🔴⚪⚪  ⚪🟥⚪🔴⚪⚪
    ⚪⚪🔴🔴⚪⚪  ⚪⚫🟥🔴⚪⚪
    ⚪⚪🔴⚪⚪⚪  ⚪⚪🔴⚫⚪⚪
    ⚪⚪⚪⚪⚪⚪  ⚪⚪⚪⚪⚪⚪
    ⚪⚪⚪⚪⚪⚪  ⚪⚪⚪⚪⚪⚪

    ⚪⚪⚪⚪⚪⚪  ⚪⚪⚪⚪⚪⚪
    ⚪⚪⚪🔴⚪⚪  ⚪⚪⚫🟥⚪⚪
    ⚪🔴⚪🔴⚪⚪  ⚪🟥⚪🔴⚫⚪
    ⚪⚪🔴🔴⚪⚪  ⚪⚪🔴🔴⚪⚪
    ⚪⚪⚪⚪⚪⚪  ⚪⚪⚪⚪⚪⚪
    ⚪⚪⚪⚪⚪⚪  ⚪⚪⚪⚪⚪⚪

    ⚪⚪⚪⚪⚪⚪  ⚪⚪⚪⚪⚪⚪
    ⚪⚪🔴⚪⚪⚪  ⚪⚪🟥⚫⚪⚪
    ⚪⚪⚪🔴🔴⚪  ⚪⚪⚪🟥🔴⚪
    ⚪⚪🔴🔴⚪⚪  ⚪⚪🔴🔴⚫⚪
    ⚪⚪⚪⚪⚪⚪  ⚪⚪⚪⚪⚪⚪
    ⚪⚪⚪⚪⚪⚪  ⚪⚪⚪⚪⚪⚪

    ⚪⚪⚪⚪⚪⚪  ⚪⚪⚪⚪⚪⚪
    ⚪⚪⚪🔴⚪⚪  ⚪⚪⚪🟥⚪⚪
    ⚪⚪⚪⚪🔴⚪  ⚪⚪⚫⚪🔴⚪
    ⚪⚪🔴🔴🔴⚪  ⚪⚪🟥🔴🔴⚪
    ⚪⚪⚪⚪⚪⚪  ⚪⚪⚪⚫⚪⚪
    ⚪⚪⚪⚪⚪⚪  ⚪⚪⚪⚪⚪⚪

"""


# todo2: F1 F2 F3 F4 for the different pages and pages of Help

# todo2: elapsed time logs into k.keyboard and s.screen for record/replay

# todo2: Vim C0 C⇧$ D0 D⇧$ . . . Yea, sample Y X before/ after and do it


# Help with famous ⎋ 7 8 C L ⇧D ⇧E ⇧M (when not taken by Vim)
# Help with famous Csi ⎋[ ⇧@ ⇧A⇧B⇧C⇧D⇧E⇧G⇧H⇧I⇧J⇧K⇧L⇧M⇧P⇧S⇧T⇧Z ⇧}⇧~ and ⎋[ DHLMNQT

SCREEN_WRITER_HELP = r"""

    Keycap Symbols are ⎋ Esc, ⌃ Control, ⌥ Option/ Alt, ⇧ Shift, ⌘ Command/ Os

        ⌃G ⌃H ⌃I ⌃J ⌃M mean \a \b \t \n \r, and ⌃[ means \e, also known as ⎋ Esc
        Tab means ⌃I \t, and Return means ⌃M \r

        Minimal Emacs is ⌃A ⌃B ⌃D ⌃E ⌃F ⌃G ⌃J ⌃K ⌃M ⌃N ⌃O ⌃P ⌃Q ⌃V
        Minimal Vim is ⌃L and ⎋ I ⌃V  ⎋ 0  ⎋ A I J L O R S X  ⎋ ⇧ $ A C D H L M O Q R S X

    Esc ⎋ Byte Pairs

        ⎋7 cursor-checkpoint  ⎋8 cursor-revert (defaults to Y 1 X 1)
        ⎋C screen-erase  ⎋L row-column-leap
        ⎋⇧D ↓  ⎋⇧E \r\n else \r  ⎋⇧M ↑

    Csi ⎋[ Sequences

        ⎋[⇧A ↑  ⎋[⇧B ↓  ⎋[⇧C →  ⎋[⇧D ←
        ⎋[I ⌃I  ⎋[⇧Z ⇧Tab
        ⎋[D row-leap  ⎋[⇧G column-leap  ⎋[⇧H row-column-leap

        ⎋[⇧M rows-delete  ⎋[⇧L rows-insert  ⎋[⇧P chars-delete  ⎋[⇧@ chars-insert
        ⎋[⇧J after-erase  ⎋[1⇧J before-erase  ⎋[2⇧J screen-erase  ⎋[3⇧J scrollback-erase
        ⎋[⇧K row-tail-erase  ⎋[1⇧K row-head-erase  ⎋[2⇧K row-erase  ⎋[⇧X columns-erase
        ⎋[⇧T rows-down  ⎋[⇧S rows-up  ⎋['⇧} cols-insert  ⎋['⇧~ cols-delete

        ⎋[4H insert  ⎋[4L replace  ⎋[6 Q bar  ⎋[4 Q skid  ⎋[ Q unstyled
        ⎋[?1049H screen-alt  ⎋[?1049L screen-main

        ⎋[1M bold  ⎋[4M underline  ⎋[7M reverse/inverse
        ⎋[31M red  ⎋[32M green  ⎋[34M blue  ⎋[38;5;130M orange
        ⎋[M plain

        ⎋[5N call for reply ⎋[0N
        ⎋[6N call for reply ⎋[{y};{x}⇧R
        ⎋[18T call for reply ⎋[8;{rows};{columns}T

        ⎋[?1000;1006H till ⎋[?1000;1006L for mouse ⎋[<{f};{x};{y} ⇧M to M of f = 0b⌃⌥⇧00
        or ⎋[?1000 H L by itself, or 1005, or 1015

"""

# todo3: Vim Q Q ⇧@ Record/ Replay, and ⌃X ⇧( till ⌃C ⇧) and ⌃X E for Emacs

# todo5: Conway Life goes with Sgr Mouse at Google Cloud Shell (where no Option Mouse Arrows)

# todo3: ⌃V ⌃Q combos with each other and self to strip off layers down to pass-through
# todo3: enough ⌃V ⌃Q to get only Keymaps, even from Mouse Work

# todo2: more gCloud Shell test @ or ⎋[?1000 H L by itself, or 1005, or 1015

# ⎋[` near alias of ⎋[⇧G column-leap  # macOS
# ⎋[F near alias of ⎋[⇧H row-column-leap
# ⎋[R near alias of ⎋L row-column-leap

# ⎋[C call for reply ⎋[?1;2C  # ⎋[=C also works at macOS
# ⎋[>C call for reply ⎋[>1;95;0C macOS or ⎋[>84;0;0C gCloud Shell
# ⎋[X call for reply ⎋[2;1;1;112;112;1;0X  # macOS


#
# Amp up Import Tty
#


BEL = "\a"  # 00/07 Bell (BEL)
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

    y_height: int  # Terminal Screen Pane Rows, else -1
    x_width: int  # Terminal Screen Pane Columns, else -1

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

        self.y_height = -1
        self.x_width = -1

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
        assert self.tcgetattr, self.tcgetattr

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

        t = 0.000_001  # defines "immediately"  # 0.000 works as "instantaneously" at macOS

        # if not extras:
        #     kdata = tbp.to_bytes()
        #     if kdata in (b"\x1b", b"\x1bO", b"\x1b[", b"\x1b\x1b", b"\x1b\x1bO", b"\x1b\x1b["):
        #         tbp.close()
        #         return None

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
                        if not self.kbhit(timeout=0.333):
                            break  # rejects slow SS3 b"\x1bO" "P" of Fn F1..F4

    def read_y_height(self) -> int:
        """Count Terminal Screen Pane Rows"""

        fileno = self.fileno
        size = os.get_terminal_size(fileno)
        assert 5 <= size.lines <= _PN_MAX_32100_, (size,)

        y_height = size.lines

        return y_height

        # macOS Terminal guarantees >= 20 Columns and >= 5 Rows

    def read_x_width(self) -> int:
        """Count Terminal Screen Pane Columns"""

        fileno = self.fileno
        size = os.get_terminal_size(fileno)

        assert 20 <= size.columns <= _PN_MAX_32100_, (size,)

        x_width = size.columns

        return x_width

        # macOS Terminal guarantees >= 20 Columns and >= 5 Rows

    def read_column_x(self) -> int:
        """Find the Terminal Cursor Column"""

        (y, x) = self.read_row_y_column_x()

        return x

    def read_row_y_column_x(self) -> tuple[int, int]:
        """Find the Terminal Cursor"""

        stdio = self.stdio

        assert DSR_6 == "\x1b[" "6n"
        assert CPR_Y_X_REGEX == r"\x1b\[([0-9]+);([0-9]+)R"

        kbhit = self.kbhit(timeout=0.000)  # flushes output, then polls input
        assert not kbhit  # todo: cope when Mouse or Paste or Keyboard work disrupts replies to Csi

        stdio.write("\x1b[6n")  # bypass Screen Logs & Screen Shadows above
        tbp = self.read_byte_packet(timeout=None)
        kdata = tbp.to_bytes()

        m = re.fullmatch(rb"\x1b\[([0-9]+);([0-9]+)R", string=kdata)
        assert m, (m, kdata, tbp)

        y_bytes = m.group(1)
        x_bytes = m.group(2)

        y = int(y_bytes)
        x = int(x_bytes)

        assert 1 <= y <= _PN_MAX_32100_, (y, x, kdata, tbp)
        assert 1 <= x <= _PN_MAX_32100_, (y, x, kdata, tbp)

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

        esc_csi_extras = self.take_one_esc_csi_if_(decode)
        return esc_csi_extras  # maybe empty

    def take_one_esc_csi_if_(self, decode: str) -> bytes:
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
    "\x1b" "\x1bO" "A": "⌃⌥↑",  # ESC 04/15 Single-Shift Three (SS3)  # ESC SS3 ⇧A  # gCloud Shell
    "\x1b" "\x1bO" "B": "⌃⌥↓",  # ESC 04/15 Single-Shift Three (SS3)  # ESC SS3 ⇧B  # gCloud Shell
    "\x1b" "\x1bO" "C": "⌃⌥→",  # ESC 04/15 Single-Shift Three (SS3)  # ESC SS3 ⇧C  # gCloud Shell
    "\x1b" "\x1bO" "D": "⌃⌥←",  # ESC 04/15 Single-Shift Three (SS3)  # ESC SS3 ⇧D  # gCloud Shell
    "\x1b" "\x1b" "[" "3;5~": "⎋⌃FnDelete",  # ⌥⌃FnDelete
    "\x1b" "\x1b" "[" "A": "⌥↑",  # CSI 04/01 Cursor Up (CUU)  # Option-as-Meta  # gCloud Shell
    "\x1b" "\x1b" "[" "B": "⌥↓",  # CSI 04/02 Cursor Down (CUD)  # Option-as-Meta  # gCloud Shell
    "\x1b" "\x1b" "[" "C": "⌥→",  # CSI 04/03 Cursor [Forward] Right (CUF_X)  # gCloud Shell
    "\x1b" "\x1b" "[" "D": "⌥←",  # CSI 04/04 Cursor [Back] Left (CUB_X)  # gCloud Shell
    "\x1b" "\x1b" "[" "Z": "⎋⇧Tab",  # ⇤  # CSI 05/10 CBT  # not ⌥⇧Tab
    "\x1b" "\x28": "⎋FnDelete",  # not ⌥FnDelete
    "\x1bO" "P": "F1",  # ESC 04/15 Single-Shift Three (SS3)  # SS3 ⇧P
    "\x1bO" "Q": "F2",  # SS3 ⇧Q
    "\x1bO" "R": "F3",  # SS3 ⇧R
    "\x1bO" "S": "F4",  # SS3 ⇧S
    "\x1b" "[" "15~": "F5",  # Esc 07/14 is LS1R, but CSI 07/14 is unnamed
    "\x1b" "[" "17~": "F6",  # ⌥F1  # ⎋F1
    "\x1b" "[" "18~": "F7",  # ⌥F2  # ⎋F2
    "\x1b" "[" "19~": "F8",  # ⌥F3  # ⎋F3
    "\x1b" "[" "1;2C": "⇧→",  # CSI 04/03 Cursor [Forward] Right (CUF_YX) Y=1 X=2  # macOS
    "\x1b" "[" "1;2D": "⇧←",  # CSI 04/04 Cursor [Back] Left (CUB_YX) Y=1 X=2  # macOS
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
    "\x1b" "[" "A": "↑",  # CSI 04/01 Cursor Up (CUU)  # also ⌥↑ macOS
    "\x1b" "[" "B": "↓",  # CSI 04/02 Cursor Down (CUD)  # also ⌥↓ macOS
    "\x1b" "[" "C": "→",  # CSI 04/03 Cursor Right [Forward] (CUF)  # also ⌥→ macOS
    "\x1b" "[" "D": "←",  # CSI 04/04 Cursor [Back] Left (CUB)  # also ⌥← macOS
    "\x1b" "[" "F": "⇧Fn→",  # macOS  # CSI 04/06 Cursor Preceding Line (CPL)
    "\x1b" "[" "H": "⇧Fn←",  # macOS  # CSI 04/08 Cursor Position (CUP)
    "\x1b" "[" "Z": "⇧Tab",  # ⇤  # CSI 05/10 Cursor Backward Tabulation (CBT)
    "\x1b" "b": "⌥←",  # ⎋B  # ⎋←  # Emacs M-b Backword-Word  # macOS
    "\x1b" "f": "⌥→",  # ⎋F  # ⎋→  # Emacs M-f Forward-Word  # macOS
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

# ⌥⇧K is Apple Logo Icon  is \uF8FF is in the U+E000..U+F8FF Private Use Area (PUA)

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
        if o == 0x1F:  # macOS ⌃- doesn't come through as  (0x2D ^ 0x40)
            s = "^-"  # macOS ⌃-  and ⌃⇧_ do come through as (0x5F ^ 0x40)
        else:
            s = "⌃" + chr(o ^ 0x40)  # '^ 0x40' mixes ⌃ into one of @ A..Z [\]^_ ?

        # '^ 0x40' speaks of ⌃@ but not ⌃⇧@ and not ⌃⇧2 and not ⌃Spacebar at b"\x00"
        # '^ 0x40' speaks of ⌃M but not Return at b"\x0D"
        # '^ 0x40' speaks of ⌃[ ⌃\ ⌃] ⌃_ but not ⎋ and not ⌃⇧_ and not ⌃⇧{ ⌃⇧| ⌃⇧} ⌃-
        # '^ 0x40' speaks of ⌃? but not Delete at b"\x7F"

        # ^` ^2 ^6 ^⇧~ don't work

    elif "A" <= ch <= "Z":  # printable Upper Case English
        s = "⇧" + chr(o)  # shifted Key Cap '⇧A' from b'A'

    elif "a" <= ch <= "z":  # printable Lower Case English
        s = chr(o ^ 0x20)  # plain Key Cap 'A' from b'a'

    # Test that no Keyboard sends the C1 Control Bytes, nor the Quasi-C1 Bytes

    elif o in range(0x80, 0xA0):  # C1 Control Bytes
        s = repr(bytes([o]))  # b'\x80'
    elif o == 0xA0:  # 'No-Break Space'
        s = "⌥Spacebar"
        assert False, (o, ch)  # unreached because 'kcap_by_kchars'
    elif o == 0xAD:  # 'Soft Hyphen'  # near to a C1 Control Byte
        s = repr(bytes([o]))  # b'\xad'

    # Show the US-Ascii or Unicode Char as if its own Key Cap

    else:
        assert o < 0x11_0000, (o, ch)
        s = chr(o)  # '!', '¡', etc

        # todo: have we fuzzed b"\xA1" .. FF vs "\u00A1" .. 00FF like we want?

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
# Quote some words to choose at random
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
# Mention the unmentioned skidded names defined by this File, to please PyLance
#


_ = _ICF_RIS_, _ICF_CUP_, _SM_XTERM_ALT_, _RM_XTERM_MAIN_


#
# Run from the Shell Command Line, if not imported
#


if __name__ == "__main__":
    main()


# 3456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789


# posted as:  https://github.com/pelavarre/xshverb/blob/main/bin/plus.py
# copied from:  git clone https://github.com/pelavarre/xshverb.git
