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

import bdb
import collections
import collections.abc as abc
import datetime as dt
import math
import os
import pathlib
import pdb
import random  # todo6: choose Seeds for Repeatability
import re
import select
import signal
import subprocess
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
# Call Main, and also launch the Repl if Main doesn't raise SystemExit
# todo10: shuffle Quit Details below most of the Code
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

    assert exc_type is not SystemExit, (exc_type,)

    assert EL_PS == "\033[" "{}" "K"

    # Quit now for visible cause, if KeyboardInterrupt

    if exc_type is KeyboardInterrupt:
        with_stderr.write("KeyboardInterrupt\n")
        sys.exit(130)  # 0x80 + signal.SIGINT

    if exc_type is bdb.BdbQuit:
        with_stderr.write("BdbQuit\n")
        sys.exit(130)  # 0x80 + signal.SIGINT  # same as for KeyboardInterrupt

    slam_enough_stty_bits_to_normal()

    # Print the Traceback, etc

    print("\033[K", file=with_stderr)
    print("\033[K", file=with_stderr)
    print("\033[K" "ExceptHook", file=with_stderr)

    with_excepthook(exc_type, exc_value, exc_traceback)

    # Launch the Post-Mortem Debugger

    print(">>> pdb.pm()", file=with_stderr)
    pdb.pm()


def slam_enough_stty_bits_to_normal() -> None:
    """Guess at Normal after some Terminal Writes bypass our Screen Logs, if need be"""

    assert DECSC == "\0337"
    assert DECRC == "\0338"

    assert RM_IRM == "\033[" "4l"
    assert _RM_SGR_MOUSE_ == "\033[" "?1000;1006l"
    assert _RM_XTERM_MAIN_ == "\033[" "?1049l"
    assert SGR_PS == "\033[" "{}" "m"

    write = ""

    write += "\033[m"
    write += "\033[4l"
    write += "\0337"
    write += "\033[?1049l"  # and implies \033[H at macOS Terminal
    write += "\0338"
    write += "\033[?1000;1006l"

    with_stderr.write(write)

    when = termios.TCSADRAIN
    attributes = with_tcgetattr  # undoes tty.setraw
    termios.tcsetattr(with_stderr.fileno(), when, attributes)

    # compare ProxyTerminal.__exit__


sys.excepthook = excepthook


def try_main_else_repl() -> None:
    """Run from the Shell Command Line, and exit into the Py Repl"""

    if os.path.basename(sys.argv[0]) != "+":
        assert sys.argv[1:], sys.argv
        assert "--yolo".startswith(sys.argv[1]) and sys.argv[1].startswith("--"), sys.argv

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

    d["main"] = main

    # Launch the Py Repl at Process Exit, as if:  python3 -i -c ''

    # print("To get started, press Return after typing:  tryme()", file=sys.stderr)
    # print(">>> ", file=sys.stderr)
    # print(">>> tryme()", file=sys.stderr)

    main()

    # print("try_main_else_repl: after main", file=sys.stderr)

    # slam_enough_stty_bits_to_normal()  # nope, depend on ProxyTerminal.__exit__

    # print(">>> ", file=sys.stderr)
    # sys.excepthook = with_excepthook
    # os.environ["PYTHONINSPECT"] = str(True)


#
# Run from the Shell Command Line
#


def main() -> None:
    """Run from the Shell Command Line"""

    tprint()
    tprint()
    tprint()

    func = try_tbp_self_test
    func = try_read_byte_packet
    func = try_screen_editor

    func = try_screen_editor  # last choice wins

    # print(f"main: before {func.__qualname__}", file=sys.stderr)

    func()

    # print(f"main: after {func.__qualname__}", file=sys.stderr)


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
# Loop Keyboard back to Screen, but as whole Packets or Emulations thereof  # todo7: name the helped
#


IND = "\033" "D"  # ESC 04/04 Index (IND) = C1 Control U+0084 IND (formerly known as INDEX)
NEL = "\033" "E"  # ESC 04/05 Next Line (NEL) = C1 Control U+0085 NEXT LINE (NEL)
RI = "\033" "M"  # ESC 04/06 Reverse Index (RI) = C1 Control U+0086 REVERSE LINE FEED (RI)

_ICF_RIS_ = "\033" "c"  # ESC 06/03 Reset To Initial State (RIS) [an Independent Control Function]
_ICF_CUP_ = "\033" "l"  # ESC 06/12 Cursor Position (CUP) [an Independent Control Function]

X1 = 1  # counts Columns West from 1
Y1 = 1  # counting Rows South from 1

CUU_Y = "\033[" "{}" "A"  # CSI 04/01 Cursor Up
CUD_Y = "\033[" "{}" "B"  # CSI 04/02 Cursor Down  # \n is Pn 1 except from last Row
CUF_X = "\033[" "{}" "C"  # CSI 04/03 Cursor [Forward] Right
CUB_X = "\033[" "{}" "D"  # CSI 04/04 Cursor [Back] Left  # \b is Pn 1

CHA_X = "\033[" "{}" "G"  # CSI 04/07 Cursor Character Absolute  # \r is Pn 1

CUP_Y1_X1 = "\033[" "H"  # CSI 04/08 Cursor Position
CUP_Y_X1 = "\033[" "{}" "H"  # CSI 04/08 Cursor Position
CUP_Y_X = "\033[" "{};{}" "H"  # CSI 04/08 Cursor Position

CHT_X = "\033[" "{}" "I"  # CSI 04/09 Cursor Forward [Horizontal] Tabulation  # \t is Pn 1

ED_PS = "\033[" "{}" "J"  # CSI 04/10 Erase in Display  # 0 Tail # 1 Head # 2 Rows # 3 Scrollback
EL_PS = "\033[" "{}" "K"  # CSI 04/11 Erase in Line  # 0 Tail # 1 Head # 2 Row

ICH_X = "\033[" "{}" "@"  # CSI 04/00 Insert Character
IL_Y = "\033[" "{}" "L"  # CSI 04/12 Insert Line [Row]
DCH_X = "\033[" "{}" "P"  # CSI 05/00 Delete Character

SU_Y = "\033[" "{}" "S"  # CSI 05/03 Scroll Up [Insert South Lines]
SD_Y = "\033[" "{}" "T"  # CSI 05/04 Scroll Down [Insert North Lines]

ECH_X = "\033[" "{}" "X"  # CSI 05/08 Erase Character

CBT_X = "\033[" "{}" "Z"  # CSI 05/10 Cursor Backward Tabulation

VPA_Y = "\033[" "{}" "d"  # CSI 06/04 Line Position Absolute

DECIC_X = "\033[" "{}" "'}}"  # CSI 02/07 07/13 VT420 DECIC_X  # "}}" to mean "}"
DECDC_X = "\033[" "{}" "'~"  # CSI 02/07 07/14 VT420 DECDC_X


SM_IRM = "\033[" "4h"  # CSI 06/08 4 Set Mode Insert, not Replace
RM_IRM = "\033[" "4l"  # CSI 06/12 4 Reset Mode Replace, not Insert

SM_DECTCEM = "\033[" "?25h"  # 06/08 Set Mode (SMS) 25 VT220 Show Cursor
RM_DECTCEM = "\033[" "?25l"  # 06/12 Reset Mode (RM) 25 VT220 Hide Cursor


_SM_XTERM_ALT_ = "\033[" "?1049h"  # show Alt Screen
_RM_XTERM_MAIN_ = "\033[" "?1049l"  # show Main Screen

_SM_SGR_MOUSE_ = "\033[" "?1000;1006h"
_RM_SGR_MOUSE_ = "\033[" "?1000;1006l"


SGR_PS = "\033[" "{}" "m"  # CSI 06/13 Select Graphic Rendition [Text Style]

DSR_6 = "\033[" "6n"  # CSI 06/14 [Request] Device Status Report  # Ps 6 for CPR In
CPR_Y_X_REGEX = r"\033\[([0-9]+);([0-9]+)R"  # CSI 05/02 Active [Cursor] Pos Rep (CPR)


DEL = "\x7f"  # 00/7F Delete [Control Character]  # aka ⌃?


PS0 = 0  # often the default Int of a Selective [Enum] Parameter of a Csi Esc Sequence, etc
PN1 = 1  # often the min & default Int of a Numeric [Int] Parameter of a Csi Esc Sequence, etc
_PN_MAX_32100_ = 32100  # a Numeric [Int] beyond the Counts of Rows & Columns at any Terminal


CUP_Y_X_REGEX = r"\033\[((-?[0-9]+)(;(-?[0-9]+))?)?H"  # like CUP_Y_X but accepts Y <= 0 and X <= 0


# todo2: Pull ⎋[{y};{x}⇧R always into Side Channel, when requested or not
# todo: Stop writing "32100", like to cope with Terminals beyond 32100 Rows & Columns


#
# Play Conway's Game-of-Life
#


class ConwayLife:
    """Play Conway's Game-of-Life"""

    screen_editor: ScreenEditor  # writes Screen and reads Keyboard

    conway_half_steps: int  # counts steps, after -1
    conway_yx_list: list[tuple[int, int]]  # where Cells written lately

    def __init__(self, screen_editor: ScreenEditor) -> None:

        self.screen_editor = screen_editor

        self.conway_half_steps = -1
        self.conway_yx_list = list()

    def play_conway_life(self) -> None:
        """Play Conway's Game-of-Life"""

        se = self.screen_editor

        # Say Hello

        se.print()
        se.print("Hello from Conway's Game-of-Life")
        se.print()
        se.print("← ↑ → ↓ Arrows or ⌥ Mouse to move around")
        # se.print("+ - to make a Cell older or younger")  # todo4:
        se.print("Spacebar to step, ⌃Spacebar to make a half step")  # todo9: , ⌥← to undo
        se.print("Tab to step 8x Faster, ⇧Tab undo 8x Faster, ⌃D to quit")
        se.print()
        se.print()
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

        conway_yx_list = self.conway_yx_list
        se = self.screen_editor
        pt = se.proxy_terminal

        bt = pt.bytes_terminal
        writes_by_y_x = pt.writes_by_y_x

        (ya, xa) = pt.proxy_read_row_y_column_x()
        x_width = bt.read_x_width()

        assert CUP_Y_X1 == "\033[" "{}" "H"

        conway_yx_list.clear()

        choice = 1

        if choice == 1:

            x_mid = x_width // 3
            se.write(f"\033[{ya};{x_mid}H")  # for .restart_conway_life

            self.conway_print("🔵🔵⚪⚪⚪🔵🔵🔵🔵🔵🔵🔵🔵🔵")
            self.conway_print("⚪⚪⚪🔴⚪🔵🔵🔵🔵🔵🔵🔵🔵🔵")
            self.conway_print("⚪🔴⚪⚪⚪🔵🔵🔵🔵🔵🔵🔵🔵🔵")
            self.conway_print("⚪🔴🔴🔴⚪🔵🔵🔵🔵🔵🔵🔵🔵🔵")
            self.conway_print("⚪⚪⚪⚪⚪🔵🔵🔵🔵⚪🔴⚪🔴⚪")
            self.conway_print("🔵🔵🔵🔵🔵🔵🔵🔵🔵⚪⚪🔴🔴⚪")
            self.conway_print("🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵⚪🔴⚪⚪")

            # Southwest Glider & Southeast Glider

        if choice == 3:

            self.conway_print("🔴⚪⚪⚪🔴")
            self.conway_print("🔴🔴⚪🔴🔴")
            self.conway_print("🔴⚪🔴⚪🔴")
            self.conway_print("⚪🔴⚪🔴⚪")
            self.conway_print("⚪⚪🔴⚪⚪")

            # https://imgur.com/a/interesting-face-pattern-conways-game-of-life-epMFxEb

            # todo6: compare/contrast web life at Wolf Face

        # Add the Next Spots as a Perimeter around the Spots, if need be

        yx_pairs = pt.proxy_read_yx_pairs()
        for y, x in yx_pairs:
            yx_writes = writes_by_y_x[y][x]
            if yx_writes and yx_writes[-1] == "🔴":
                self.y_x_count_around(y, x)  # adds its Next Spots

        # Choose the first place of the Cursor

        y_list = list(_[0] for _ in conway_yx_list)
        x_list = list(_[-1] for _ in conway_yx_list)

        y_min = min(y_list)
        y_max = max(y_list)
        x_min = min(x_list)
        x_max = max(x_list)

        y_mid = (y_min + y_max) // 2
        x_mid = (x_min + x_max) // 2

        se.write(f"\033[{y_mid};{x_mid}H")  # for .restart_conway_life

    def conway_print(self, text: str) -> None:
        """Write Some Text Characters at one Y X Place"""

        se = self.screen_editor
        pt = se.proxy_terminal

        (ya, xb) = (pt.row_y, pt.column_x)

        (y, x) = (ya, xb)
        for t in text:
            if t == "🔵":
                se.write("\033[2C")  # todo: Conway Spots always 2 Columns wide?
            else:
                self.conway_write_y_x_text(y, x=x, text=t)

            x += 2

        y += 1

        se.write(f"\033[{y};{xb}H")  # for .conway_print

    def conway_write_y_x_text(self, y: int, x: int, text: str) -> None:
        """Write Some Text Characters at one Y X Place"""

        se = self.screen_editor
        conway_yx_list = self.conway_yx_list

        pt = se.proxy_terminal

        assert CUP_Y_X == "\033[" "{}" ";" "{}" "H"

        se.write(f"\033[{y};{x}H")  # for .conway_write_y_x_text
        se.write(text)

        g_width = pt.str_guess_print_width(text)
        for x in range(x, x + g_width):
            yx = (y, x)
            conway_yx_list.append(yx)

    def do_conway_8x_redo(self) -> None:
        """Step the Game of Life forward at 8X Speed"""

        for _ in range(8):
            self.do_conway_half_step()  # once
            self.do_conway_half_step()  # twice

        # Tab

    def do_conway_full_step(self) -> None:
        """Step the Game of Life forward by 1 Full Step"""

        conway_half_steps = self.conway_half_steps

        if (conway_half_steps % 2) == 0:  # if halfway
            self.do_conway_half_step()  # out-of-phase

        self.do_conway_half_step()  # once
        self.do_conway_half_step()  # twice

        # ⌃Spacebar

    def do_conway_half_step(self) -> None:
        """Step the Game of Life forward by 1/2 Step"""

        se = self.screen_editor

        assert DECSC == "\033" "7"  # DECSC 7 Cursor Save
        assert DECRC == "\033" "8"  # DECRC 8 Cursor Restore

        se.write("\0337")
        self._conway_half_step_()
        se.write("\0338")

        # Spacebar

    def _conway_half_step_(self) -> None:
        """Step the Game of Life forward by 1/2 Step"""

        se = self.screen_editor
        pt = se.proxy_terminal
        writes_by_y_x = pt.writes_by_y_x

        self.conway_half_steps += 1
        conway_half_steps = self.conway_half_steps

        yx_list = list()
        for y in writes_by_y_x.keys():
            for x in writes_by_y_x[y].keys():
                yx = (y, x)
                yx_list.append(yx)

        for y, x in yx_list:
            yx_writes = writes_by_y_x[y][x]
            text = yx_writes[-1] if yx_writes else ""

            if text not in ("⚪", "⚫", "🔴", "🟥"):
                continue

            if conway_half_steps % 2 == 0:
                assert text in ("⚪", "🔴"), (text,)
                n = self.y_x_count_around(y, x)

                if (n < 2) and (text == "🔴"):
                    self.conway_write_y_x_text(y, x=x, text="🟥")
                elif (n == 3) and (text == "⚪"):
                    self.conway_write_y_x_text(y, x=x, text="⚫")
                    self.y_x_count_around(y, x)  # adds its Next Spots
                elif (n > 3) and (text == "🔴"):
                    self.conway_write_y_x_text(y, x=x, text="🟥")

            else:
                assert text in ("⚪", "⚫", "🔴", "🟥"), (text,)

                if text == "⚫":
                    self.conway_write_y_x_text(y, x=x, text="🔴")
                elif text == "🟥":
                    self.conway_write_y_x_text(y, x=x, text="⚪")

    def y_x_count_around(self, y: int, x: int) -> int:
        """Count the Neighbors of a Cell"""

        se = self.screen_editor
        pt = se.proxy_terminal
        writes_by_y_x = pt.writes_by_y_x

        # Fetch the Cell

        yx_writes = writes_by_y_x[y][x]
        yx_write = yx_writes[-1] if yx_writes else ""

        # Walk around the Cell

        dydx_list = list()
        for dy in range(-1, 1 + 1):
            for dx in range(-2, 2 + 1, 2):
                if dy == 0 and dx == 0:
                    continue

                dydx = (dy, dx)
                dydx_list.append(dydx)

        # Count a Red Circle or Red Square next door

        count = 0
        for dy, dx in dydx_list:
            yb = y + dy
            xb = x + dx

            # Do nothing more for Blank Cells

            if yx_write == "⚪":
                if yb not in writes_by_y_x.keys():
                    continue
                if xb not in writes_by_y_x[yb].keys():
                    continue

            # Pop up the Blank Cell found missing next door

            ybxb_write = ""
            if not ((yb in writes_by_y_x.keys()) and (xb in writes_by_y_x[yb].keys())):
                ybxb_write = "⚪"
                se.y_x_text_print(yb, x=xb, text=ybxb_write)

                y_after = yb in writes_by_y_x.keys()
                x_after = (xb in writes_by_y_x[yb].keys()) if y_after else False
                assert y_after and x_after, (yb, xb, y_after, x_after)

            # Fetch the Cell next door

            ybxb_writes = writes_by_y_x[yb][xb]
            ybxb_mirror_write = ybxb_writes[-1] if ybxb_writes else ""

            # Require writes mirrored

            if ybxb_write:
                assert ybxb_write == ybxb_mirror_write, (ybxb_write, ybxb_mirror_write, yb, xb)

            # Count a Red Circle or Red Square next door

            if ybxb_mirror_write in ("🔴", "🟥"):
                count += 1

        # Succeed

        return count

    def form_conway_func_by_str(self) -> dict[str, abc.Callable[[], None]]:
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


screen_editors: list[ScreenEditor] = list()


class ScreenEditor:
    """Loop Keyboard back to Screen, but as whole Packets, & with some emulations"""

    proxy_terminal: ProxyTerminal
    terminal_byte_packets: list[TerminalBytePacket]

    arrows: int  # counts Keyboard Arrow Chords sent faster than people can type them
    arrow_row_y: int  # the Y of Y X after the first Keyboard Arrow Chord
    arrow_column_x: int  # the X of Y X after the first Keyboard Arrow Chord

    func_by_str: dict[str, abc.Callable[[], None]] = dict()
    loopable_kdata_tuple: tuple[bytes, ...] = tuple()

    #
    # Init, Enter, Exit, Print
    #

    def __init__(self) -> None:

        screen_editors.append(self)

        pt = ProxyTerminal()

        self.proxy_terminal = pt
        self.terminal_byte_packets = list()

        self.arrows = 0
        self.arrow_row_y = -1
        self.arrow_column_x = -1

        func_by_str = self.form_func_by_str()
        self.func_by_str = func_by_str

        loopable_kdata_tuple = self.form_loopable_kdata_tuple()
        self.loopable_kdata_tuple = loopable_kdata_tuple

    def __enter__(self) -> typing.Self:
        r"""Stop line-buffering Input, stop replacing \n Output with \r\n, etc"""

        pt = self.proxy_terminal
        pt.__enter__()

        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        r"""Start line-buffering Input, start replacing \n Output with \r\n, etc"""

        pt = self.proxy_terminal  # todo7: write up MyPy Strict forbids kwarg [call-arg]
        pt.__exit__(exc_type, exc_val, exc_tb)

        return None

    def y_x_text_print(self, y: int, x: int, text: str) -> None:
        """Write Some Text Characters at one Y X Place"""

        pt = self.proxy_terminal
        pt.proxy_y_x_text_print(y=y, x=x, text=text)

    def print(self, *args: object, end: str = "\r\n") -> None:
        """Join the Args by Space, add the End, and write the Encoded Chars"""

        pt = self.proxy_terminal
        pt.proxy_print(*args, end=end)

    def write(self, text: str) -> None:
        """Write the Bytes, log them as written, and mirror them"""

        pt = self.proxy_terminal
        pt.proxy_write(text)

    #
    # Bind Keyboard Chords to Funcs
    #

    def form_func_by_str(self) -> dict[str, abc.Callable[[], None]]:
        """Bind Keycaps to Funcs"""

        pt = self.proxy_terminal

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
            "⌃L": pt.write_screen,  # ⌃L for Vim  # not ⌃L for Emacs a la Vim ⇧H ⇧M ⇧L
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
            # # b"\033": self.print_kcaps_plus,  # ⎋
            #
            "⎋$": self.do_column_leap_rightmost,  # ⎋⇧$ for Vim  # todo4: ⎋⇧$ vs ⎋$
            "⎋0": self.do_column_leap_leftmost,  # ⎋0 for Vim
            # # b"\033" b"7",  # ⎋7 cursor-checkpoint
            # # b"\033" b"8",  # ⎋8 cursor-revert
            # todo2: ⎋⇧0 ⎋⇧1 ⎋⇧2 ⎋⇧3 ⎋⇧4 ⎋⇧5 ⎋⇧6 ⎋⇧7 ⎋⇧8 ⎋⇧9 for Vim
            #
            "⎋⇧A": self.do_column_leap_rightmost_inserting_start,  # ⇧A for Vim
            "⎋⇧C": self.do_row_tail_erase_inserting_start,  # ⇧C for Vim
            # # b"\033" b"D",  # ⎋⇧D ↓ (IND)
            "⎋⇧D": self.do_row_tail_erase,  # Vim ⇧D
            # # b"\033" b"E",  # ⎋⇧E \r\n else \r (NEL)
            # "\033" "J": self do_end_delete_right  # ⎋⇧J  # todo2: Delete Row if at 1st Column
            "⎋⇧H": self.do_row_leap_first_column_leftmost,  # ⎋⇧H for Vim
            "⎋⇧L": self.do_row_leap_last_column_leftmost,  # ⎋⇧L for Vim
            # # b"\033" b"M",  # ⎋⇧M ↑ (RI)
            "⎋⇧M": self.do_row_leap_middle_column_leftmost,  # ⎋⇧M for Vim
            "⎋⇧O": self.do_row_insert_inserting_start,  # ⎋⇧O for Vim
            "⎋⇧Q": self.do_assert_false,  # ⎋⇧Q for Vim
            "⎋⇧R": self.do_replacing_start,  # ⎋⇧R for Vim
            "⎋⇧S": self.do_row_delete_start_inserting,  # ⎋S for Vim
            "⎋⇧X": self.do_char_delete_left,  # ⎋⇧X for Vim
            # todo2: ⎋⇧Z⇧Q ⎋⇧Z⇧W for Vim
            #
            "⎋A": self.do_column_right_inserting_start,  # ⎋A for Vim
            # # b"\033" b"c",  # ⎋C cursor-revert (_ICF_RIS_)
            "⎋H": self.do_column_left,  # ⎋H for Vim
            "⎋I": self.do_inserting_start,  # ⎋I for Vim
            "⎋J": self.do_row_down,  # ⎋J for Vim
            "⎋K": self.do_row_up,  # ⎋K for Vim
            # # b"\033" b"l",  # ⎋L row-column-leap  # not at gCloud (_ICF_CUP_)
            "⎋L": self.do_column_right,  # ⎋L for Vim
            "⎋O": self.do_row_down_insert_inserting_start,  # ⎋O for Vim
            "⎋R": self.do_replacing_one_kdata,  # ⎋R for Vim
            "⎋S": self.do_char_delete_here_start_inserting,  # ⎋S for Vim
            "⎋X": self.do_char_delete_here,  # ⎋X for Vim
            #
            # Csi Esc Byte Sequences without Parameters and without Intermediate Bytes,
            #
            # # b"\033[": self.print_kcaps_plus,  # ⎋ [
            #
            # b"\033[" b"A",  # ⎋[⇧A ↑
            # b"\033[" b"B",  # ⎋[⇧B ↓
            # b"\033[" b"C",  # ⎋[⇧C →
            # b"\033[" b"D",  # ⎋[⇧D ←
            # # b"\033[" b"I",  # ⎋[⇧I ⌃I  # not at gCloud
            # b"\033[" b"Z",  # ⎋[⇧Z ⇧Tab
            #
            "F5": self.do_kdata_fn_f5,  # FnF5
            "F8": self.do_kdata_fn_f8,  # FnF8
            "F9": self.do_kdata_fn_f9,  # FnF9
            #
            # Ss3 Esc Byte Sequences
            #
            # # b"\033O": self.print_kcaps_plus,  # ⎋⇧O
            #
            "F1": self.do_kdata_fn_f1,  # FnF1  # todo4: FnF1 vs F1
            "F2": self.do_kdata_fn_f2,  # FnF2
            "F3": self.do_kdata_fn_f3,  # FnF3  # todo9: should this be "FnF3" ?
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
        #         if kstr.startswith("\033"):
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
            # b"\033": self.print_kcaps_plus,  # ⎋
            #
            # b"\033" b"7",  # ⎋7 cursor-checkpoint
            # b"\033" b"8",  # ⎋8 cursor-revert
            # b"\033" b"D",  # ⎋⇧D ↓ (IND)
            # b"\033" b"E",  # ⎋⇧E \r\n else \r (NEL)
            # b"\033" b"M",  # ⎋⇧M ↑ (RI)
            # b"\033" b"c",  # ⎋C cursor-revert (_ICF_RIS_)
            # b"\033" b"l",  # ⎋L row-column-leap  # not at gCloud (_ICF_CUP_)
            #
            # b"\033O": self.print_kcaps_plus,  # ⎋⇧O
            #
            # b"\033[": self.print_kcaps_plus,  # ⎋ [
            b"\033[" b"A",  # ⎋[⇧A ↑
            b"\033[" b"B",  # ⎋[⇧B ↓
            b"\033[" b"C",  # ⎋[⇧C →
            b"\033[" b"D",  # ⎋[⇧D ←
            # b"\033[" b"I",  # ⎋[⇧I ⌃I  # not at gCloud
            b"\033[" b"Z",  # ⎋[⇧Z ⇧Tab
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

    def play_screen_editor(self: ScreenEditor) -> None:
        """Loop Keyboard back to Screen, but as whole Packets, & with some emulations"""

        pt = self.proxy_terminal

        assert CUU_Y == "\033[" "{}" "A"
        assert CUP_Y_X == "\033[" "{}" ";" "{}" "H"
        assert ED_PS == "\033[" "{}" "J"
        assert EL_PS == "\033[" "{}" "K"
        assert SGR_PS == "\033[" "{}" "m"
        assert _SM_SGR_MOUSE_ == "\033[" "?1000;1006h"

        # Tell the Mirror where the first Write will land

        assert pt.row_y == -1, (pt.row_y,)  # for .play_screen_editor
        assert pt.column_x == -1, (pt.column_x,)  # for .play_screen_editor
        assert pt.y_height == -1, (pt.y_height,)  # for .play_screen_editor
        assert pt.x_width == -1, (pt.x_width,)  # for .play_screen_editor

        pt.proxy_read_row_y_column_x()
        pt.proxy_read_y_height_x_width()

        # Prompt at Launch  # todo9: next experiments

        autolaunchers = [11, 22]  # todo4: 'with' Context Handlers to undo Autolaunchers

        y_height = -1

        if 11 in autolaunchers:
            self.write("\033[8;32100;101t")  # Chosen Width, Max Height
            (y_height, x_width) = pt.proxy_read_y_height_x_width()

        if 21 in autolaunchers:
            for _ in range(4):
                self.write("\033[A")

        if 22 in autolaunchers:
            self.write(y_height * "\n")  # scrolls the Screen into Scrollback
            self.write("\033[H")

            # no destructive wipe of the Rows above via ⎋[2⇧J Screen Erase

        if 33 in autolaunchers:
            self.write("\033[?1000;1006h")

        if 44 in autolaunchers:
            pt.write_screen()

        self.write("\033[K")
        self.print("<#555 on #005>  <Jabberwocky>")  # todo10: <#24 on #005>
        self.write("\033[K")
        self.print("Try ⌥-Clicks at  F1  F2  F3  F4  F5  F6  F7  F8  F9  F10  F11  F12")
        self.write("\033[K")
        self.print("Press ⌃D to quit, else F1 for help, else see what happens")  # todo: FnF1 vs F1
        self.write("\033[K")
        self.print()

        # Walk one step after another

        while True:
            try:
                self.read_eval_print_once()
            except SystemExit:
                break

        # self.print("Goodbye from Screen Editor")

    def read_eval_print_once(self) -> None:
        """Loop Keyboard back to Screen, but as whole Packets, & with some emulations"""

        terminal_byte_packets = self.terminal_byte_packets

        pt = self.proxy_terminal
        klog = pt.keyboard_bytes_log

        # Reply to each Keyboard Chord Input, till quit

        # todo2: Quit in many of the Emacs & Vim ways, including Vim ⌃C :vi ⇧Z ⇧Q
        # todo2: Maybe or maybe-not quit after ⌃D, vs quitting now only at ⌃D

        t0 = time.time()
        (tbp, n) = self.read_some_byte_packets()
        t1 = time.time()
        t1t0 = t1 - t0

        arrows = self.arrows

        terminal_byte_packets.append(tbp)
        kdata = tbp.to_bytes()

        if len(kdata) == 1:
            tprint(str(kdata)[2:-1], "in")
        elif (not arrows) and (t1t0 > 0.020):
            if kdata in self.loopable_kdata_tuple:
                tprint(str(kdata)[2:-1], "in")
            elif n > 1:
                tprint(str(kdata)[2:-1], "in", n)
            else:
                tprint(f"{arrows=} {n=} t1t0={t1t0:.6f} {tbp=}  # read_eval_print_once 1")
        else:
            tprint(f"{arrows=} {n=} t1t0={t1t0:.6f} {tbp=}  # read_eval_print_once 2")

        assert tbp, (tbp, n)  # because .timeout=None

        kdata = tbp.to_bytes()
        assert kdata, (kdata,)  # because .timeout=None

        klog.write(kdata)

        if kdata == b"\x04":  # ⌃D
            raise SystemExit()  # todo10: make all the classic Vim/ Emacs/ Sh Quits work

        self.reply_to_kdata(tbp, n=n)  # may raise SystemExit

        # todo2: Read Str not Bytes from Keyboard, and then List[Str]
        # todo2: Stop taking slow b'\033[' b'L' IL_Y as 1 Whole Packet from gCloud

    def klog_to_kcount(self) -> int:
        """Count how many times the same Keyboard Chord struck"""

        terminal_byte_packets = self.terminal_byte_packets

        depth = 0
        kdata = terminal_byte_packets[-1].to_bytes()
        for tbp in reversed(terminal_byte_packets):
            if tbp.to_bytes() != kdata:  # todo: equality between TerminalBytePacket's
                break
            depth += 1

        return depth  # fed by 'terminal_byte_packets.append(tbp)' inside .read_eval_print_once

    def reply_to_kdata(self, tbp: TerminalBytePacket, n: int) -> None:
        """Reply to 1 Keyboard Chord Input, maybe differently if n == 1 quick, or slow"""

        func_by_str = self.func_by_str
        loopable_kdata_tuple = self.loopable_kdata_tuple

        # Append to the __pycache__/k.keyboard Keylogger Keylogging File

        kdata = tbp.to_bytes()
        assert kdata, (kdata,)  # because .timeout=None

        # Call 1 Func Def by Keycaps

        kcaps = kdata_to_kcaps(kdata)

        if kcaps in func_by_str.keys():
            func = func_by_str[kcaps]
            tprint(func.__name__)  # not .__qualname__

            func()  # may raise SystemExit

            return

        if kdata in loopable_kdata_tuple:

            self.do_write_kdata_as_sdata(kdata)  # for .loopable_kdata_tuple

            return

        # Write the KData, but as Keycaps, when it is a Keycap but not a Func Def

        kchars = kdata.decode()  # may raise UnicodeDecodeError
        if kchars in KCAP_BY_KCHARS.keys():  # already handled above

            if (n == 1) or (tbp.tail != b"H"):  # falls-through to pass-through slow ⎋[⇧H CUP_Y_X

                self.print_kcaps_plus(tbp)

                return

        # Pass through 1 Unicode Character

        if tbp.text:

            self.write(tbp.text)

            return

            # todo2: stop wrongly passing through multibyte Control Characters

        # Pass-Through, or emulate, the famous Control Byte Sequences

        if self.take_tbp_n_kdata_if(tbp, n=n, kdata=kdata):

            return

        # Fallback to show the Keycaps that send this Terminal Byte Packet slowly from Keyboard

        self.print_kcaps_plus(tbp)

    def take_tbp_n_kdata_if(self, tbp: TerminalBytePacket, n: int, kdata: bytes) -> bool:
        """Emulate the KData Control Sequence and return it, else return False"""

        # Emulate famous Esc Byte Pairs

        if self._take_csi_row_1_column_1_leap_if_(kdata):  # ⎋L
            return True

        # Emulate famous Csi Control Byte Sequences,
        # beyond Screen_Writer_Help of ⎋[ ⇧@⇧A⇧B⇧C⇧D⇧E⇧G⇧H⇧I⇧J⇧K⇧L⇧M⇧P⇧S⇧T⇧Z ⇧}⇧~ and ⎋[ DHLMNQT,
        # so as to also emulate timeless Csi ⇧F ⇧X ` F and slow Csi X

        csi = tbp.head == b"\033["  # takes Csi ⎋[, but not Esc Csi ⎋⎋[

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

        self.do_write_kdata_as_sdata(kdata)  # for .csi_slow_tails and untaken .csi_timeless_tails

        return True

        # todo10: to .pack from .tbp

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

        pt = self.proxy_terminal
        bt = pt.bytes_terminal

        assert DCH_X == "\033[" "{}" "P"
        assert VPA_Y == "\033[" "{}" "d"
        assert DECDC_X == "\033[" "{}" "'~"

        csi = tbp.head == b"\033["  # takes Csi ⎋[, but not Esc Csi ⎋⎋[
        if not (csi and ((tbp.back + tbp.tail) == b"'~")):
            return False

        tprint(f"⎋['⇧~ cols-delete {tbp=}   # _take_csi_cols_delete_if_")

        pn = int(tbp.neck) if tbp.neck else PN1
        y_height = bt.read_y_height()

        (row_y, column_x) = pt.proxy_read_row_y_column_x()

        for y in range(1, y_height + 1):
            self.write(f"\033[{y}d")  # for .columns_delete_n
            self.write(f"\033[{pn}P")  # for .columns_delete_n
        self.write(f"\033[{row_y}d")  # for .columns_delete_n

        return True

        # macOS Terminal & gCloud Shell lack ⎋['⇧~ cols-delete

    def _take_csi_cols_insert_if_(self, tbp: TerminalBytePacket) -> bool:
        """Emulate ⎋['⇧} cols-insert"""

        pt = self.proxy_terminal
        bt = pt.bytes_terminal

        assert ICH_X == "\033[" "{}" "@"
        assert VPA_Y == "\033[" "{}" "d"
        assert DECDC_X == "\033[" "{}" "'~"
        assert DECIC_X == "\033[" "{}" "'}}"

        csi = tbp.head == b"\033["  # takes Csi ⎋[, but not Esc Csi ⎋⎋[
        if not (csi and ((tbp.back + tbp.tail) == b"'}")):
            return False

        tprint(f"⎋['⇧}} cols-insert {tbp=}   # _take_csi_cols_insert_if_")

        pn = int(tbp.neck) if tbp.neck else PN1
        y_height = bt.read_y_height()

        (row_y, column_x) = pt.proxy_read_row_y_column_x()

        for y in range(1, y_height + 1):
            self.write(f"\033[{y}d")  # for .columns_delete_n
            self.write(f"\033[{pn}@")  # for .columns_delete_n
        self.write(f"\033[{row_y}d")  # for .columns_delete_n

        return True

        # macOS Terminal & gCloud Shell lack ⎋['⇧} cols-insert

    def _take_csi_row_1_column_1_leap_if_(self, kdata: bytes) -> bool:
        """Emulate Famous Esc Byte Pairs, no matter if quick or slow"""

        assert CUP_Y1_X1 == "\033[" "H"

        if kdata != b"\033" b"l":
            return False

        tprint(f"{kdata=}  # _take_csi_row_1_column_1_leap_if_")

        self.write("\033[H")  # for ⎋L

        return True

        # gCloud Shell lacks macOS ⎋L

    def _take_csi_mouse_press_if_(self, tbp: TerminalBytePacket, n: int) -> bool:
        """Shrug off a Mouse Press if quick"""

        csi = tbp.head == b"\033["  # takes Csi ⎋[, but not Esc Csi ⎋⎋[
        if (n == 1) and csi and (tbp.tail == b"M"):
            tprint("# _take_csi_mouse_press_if_")
            return True  # drops first 1/2 or 2/3 of Sgr Mouse

        return False

    def _take_csi_mouse_release_if_(self, tbp: TerminalBytePacket) -> bool:
        """Reply to a Mouse Release, no matter if slow or quick"""

        # Eval the Sgr Mouse Report

        csi = tbp.head == b"\033["  # takes Csi ⎋[, but not Esc Csi ⎋⎋[
        if not (csi and (tbp.tail == b"m")):
            return False

        splits = tbp.neck.removeprefix(b"<").split(b";")
        assert len(splits) == 3, (splits, tbp.neck, tbp)
        (f, x, y) = list(int(_) for _ in splits)  # ⎋[<{f};{x};{y}m

        tprint(f"{f=} {x=} {y=}  # _take_csi_mouse_release_if_")

        # Decode f = 0b⌃⌥⇧00

        Basic_0 = 0b00000

        Shift_4 = 0b00100
        Option_8 = 0b01000
        Control_16 = 0b10000

        assert (f & ~(Shift_4 | Option_8 | Control_16)) == 0, (hex(f),)

        # Dispatch ⌥ Mouse Release

        if f in (Basic_0, Option_8):

            self.take_widget_at_yxf_mouse_release(y, x=x, f=f)

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

        assert VPA_Y == "\033[" "{}" "d"

        if kdata != b"\033[d":
            return False

        tprint(f"⎋[d {kdata=}   # _take_csi_row_default_leap_if_")

        self.write("\033[1d")  # carefully not empty Parameters via "\033[d"

        return True

        # gCloud Shell needs ⎋[1D for ⎋[D

    def _take_csi_rows_down_if_(self, tbp: TerminalBytePacket) -> bool:
        """Emulate Scroll Down [Insert North Lines]"""

        assert DECSC == "\033" "7"
        assert DECRC == "\033" "8"

        assert CUU_Y == "\033[" "{}" "A"
        assert IL_Y == "\033[" "{}" "L"
        assert SD_Y == "\033[" "{}" "T"

        csi = tbp.head == b"\033["  # takes Csi ⎋[, but not Esc Csi ⎋⎋[
        if not (csi and (tbp.tail == b"T")):
            return False

        pn = int(tbp.neck) if tbp.neck else PN1

        self.write("\0337")
        self.write("\033[32100A")
        self.write(f"\033[{pn}L")
        self.write("\0338")

        return True

        # gCloud Shell lacks macOS ⎋[{}⇧T

    def _take_csi_rows_up_if_(self, tbp: TerminalBytePacket) -> bool:
        """Emulate Scroll Up [Insert South Lines]"""

        assert LF == "\n"

        assert DECSC == "\033" "7"
        assert DECRC == "\033" "8"

        assert CUD_Y == "\033[" "{}" "B"
        assert SU_Y == "\033[" "{}" "S"
        assert _PN_MAX_32100_ == 32100

        csi = tbp.head == b"\033["  # takes Csi ⎋[, but not Esc Csi ⎋⎋[
        if not (csi and (tbp.tail == b"S")):
            return False

        pn = int(tbp.neck) if tbp.neck else PN1

        self.write("\0337")
        self.write("\033[32100B")
        self.write(pn * "\n")
        self.write("\0338")

        return True

        # gCloud Shell lacks macOS ⎋[{}⇧S

    def _take_csi_tab_right_leap_if_(self, tbp: TerminalBytePacket) -> bool:
        """Emulate Cursor Forward [Horizontal] Tabulation (CHT) for Pn >= 1"""

        pt = self.proxy_terminal
        column_x = pt.column_x

        bt = pt.bytes_terminal
        x_width = bt.read_x_width()

        assert HT == "\t"
        assert CHA_X == "\033[" "{}" "G"
        assert CHT_X == "\033[" "{}" "I"

        csi = tbp.head == b"\033["  # takes Csi ⎋[, but not Esc Csi ⎋⎋[
        if not (csi and (tbp.tail == b"I")):
            return False

        tprint(f"⎋[...I {tbp=}  # _take_csi_tab_right_leap_if_")

        pn = int(tbp.neck) if tbp.neck else PN1
        assert pn >= 1, (pn,)

        tab_stop_n = X1 + ((column_x - X1) // 8 + pn) * 8
        x = min(x_width, tab_stop_n)
        self.write(f"\033[{x}G")  # does Not fill with Background Color

        return True

        # gCloud Shell lacks ⎋[ {}I

    def do_write_cr_lf(self) -> None:
        """Write CR LF"""

        assert CR == "\r"
        assert LF == "\n"

        self.write("\r\n")

        # todo3: Emacs ⌃M and ⌃K need the Rows mirrored, as does Vim I ⌃M
        # todo3: classic Vim ⇧R does define ⇧R ⌃M same as I ⌃M

    #
    #
    #

    def read_some_byte_packets(self) -> tuple[TerminalBytePacket, int]:
        """Read 1 TerminalBytePacket, all in one piece, else in split pieces"""

        terminal_byte_packets = self.terminal_byte_packets
        arrows = self.arrows

        pt = self.proxy_terminal
        row_y = pt.row_y
        column_x = pt.column_x

        bt = pt.bytes_terminal

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

        arrows_kdata_tuple = (b"\033[A", b"\033[B", b"\033[C", b"\033[D")

        if kdata not in arrows_kdata_tuple:
            self.arrows = 0  # written only by Init & this Def
        elif t1t0 >= arrows_timeout:
            self.arrows = 0  # written only by Init & this Def
        elif arrows > 0:
            self.arrows += 1
        else:
            assert arrows == 0, (arrows,)

            self.arrows += 1

            packet = terminal_byte_packets[-1]
            packet_kdata = packet.to_bytes()
            assert packet_kdata in arrows_kdata_tuple, (packet_kdata,)

            (y, x) = (row_y, column_x)
            if packet_kdata == b"\033[A":
                y += 1  # goes up, not down
            elif packet_kdata == b"\033[B":
                y -= 1  # goes up, not down
            elif packet_kdata == b"\033[C":
                x -= 1  # goes left, not right
            elif packet_kdata == b"\033[D":
                x += 1  # goes right, not left

            self.arrow_row_y = y
            self.arrow_column_x = x

        while (not tbp.text) and (not tbp.closed) and (not bt.extras):

            kdata = tbp.to_bytes()
            # if kdata in (b"\033", b"\033O", b"\033[", b"\033\033", b"\033\033O", b"\033\033["):
            if kdata == b"\033O":  # ⎋⇧O for Vim
                break

            n += 1
            bt.close_byte_packet_if(tbp, timeout=None)

        # Succeed

        return (tbp, n)

        # todo: log & echo the Keyboard Bytes as they arrive, stop waiting for whole Packet

    def read_arrows_as_byte_packet(self) -> TerminalBytePacket:
        """Take Slow-after-Arrow-Burst as a ⌥ Mouse Release, with never a Press"""

        arrow_row_y = self.arrow_row_y
        arrow_column_x = self.arrow_column_x
        arrow_yx = (arrow_row_y, arrow_column_x)

        pt = self.proxy_terminal

        assert CUP_Y_X == "\033[" "{};{}" "H"

        yx = pt.proxy_read_row_y_column_x()
        (row_y, column_x) = yx

        cup = f"\033[{arrow_row_y};{arrow_column_x}H"
        self.write(f"\033[{arrow_row_y};{arrow_column_x}H")
        after_write_yx = (pt.row_y, pt.column_x)

        assert after_write_yx == arrow_yx, (after_write_yx, arrow_yx, yx, cup)

        option_f = int("0b01000", base=0)  # f = 0b⌃⌥⇧00
        ktext = f"\033[<{option_f};{column_x};{row_y}m"
        kdata = ktext.encode()

        tbp = TerminalBytePacket(kdata)

        return tbp

        # todo6: Undo the Arrow Burst after making it a ⌥ Mouse Release of the ⎋[m kind
        # todo6: Debug why Arrow Burst buttons after the first frequently don't work, if still so?

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

        # self.print("do_assert_false")

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

        assert CUF_X == "\033[" "{}" "C"
        self.write("\033[C")

        # Emacs ⌃F

    def do_column_right_inserting_start(self) -> None:
        """Insert 1 Space at the Cursor, then go right by 1 Column"""

        self.do_column_right()  # Vim L
        self.do_inserting_start()  # Vim I

        # Vim A = Vim L I

        # todo3: Vim <Digits> ⇧H and Vim <Digits> ⇧L and Vim <Digits> ⇧|T

    def do_char_delete_here(self) -> None:
        """Delete the Character beneath the Cursor"""

        assert DCH_X == "\033[" "{}" "P"
        self.write("\033[P")

        # Emacs ⌃D  # Vim X

    def do_char_delete_here_start_inserting(self) -> None:
        """Delete the Character beneath the Cursor, and Start Inserting"""

        self.do_char_delete_here()  # Emacs ⌃D  # Vim X
        self.do_inserting_start()  # Vim I

        # Vim S = Vim X I

    def do_char_delete_left(self) -> None:
        """Delete the Character at left of the Cursor"""

        pt = self.proxy_terminal

        assert BS == "\b"
        assert DCH_X == "\033[" "{}" "P"

        x = pt.proxy_read_column_x()

        if x > 1:
            self.write("\b")
            self.write("\033[P")

        # Emacs Delete  # Vim ⇧X

        # todo2: Show .do_char_delete_left bouncing off the Left Edge

    def do_column_leap_leftmost(self) -> None:
        """Leap to the Leftmost Column"""

        assert CR == "\r"
        self.write("\r")

        # Emacs ⌃A  # Vim 0

    def do_column_leap_rightmost(self) -> None:
        """Leap to the Rightmost Column"""

        assert CUF_X == "\033[" "{}" "C"
        assert _PN_MAX_32100_ == 32100
        self.write("\033[32100C")  # for .do_column_leap_rightmost  # Emacs ⌃E  # Vim ⇧$

        # todo3: Leap to Rightmost Mirror, if Row Mirrored

        # Emacs ⌃E  # Vim ⇧$

    def do_column_leap_rightmost_inserting_start(self) -> None:
        """Leap to the Rightmost Column, and Start Inserting"""

        self.do_column_leap_rightmost()  # Emacs ⌃E  # Vim ⇧$
        self.do_inserting_start()  # Vim I

        # Vim ⇧A = Vim ⇧$ I

    def do_inserting_start(self) -> None:
        """Start Inserting Characters at the Cursor"""

        assert SM_IRM == "\033[" "4h"
        self.write("\033[4h")

        # Vim I

        # todo2: Show Inserting while Inserting

    def do_replacing_start(self) -> None:
        """Start Replacing Characters at the Cursor"""

        assert RM_IRM == "\033[" "4l"
        self.write("\033[4l")

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

        assert CUD_Y == "\033[" "{}" "B"
        self.write("\033[B")

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

        assert IL_Y == "\033[" "{}" "L"
        self.write("\033[L")

        # Emacs ⌃O when leftmost

    def do_row_leap_first_column_leftmost(self) -> None:
        """Leap to the Leftmost Column of the First Row"""

        depth = self.klog_to_kcount()

        pt = self.proxy_terminal
        bt = pt.bytes_terminal

        x_width = bt.read_x_width()
        mid_width = (x_width // 2) + (x_width % 2)

        assert CUP_Y1_X1 == "\033[" "H"

        if (depth % 3) == 1:
            self.write("\033[H")  # for .do_row_leap_first_column_leftmost  # Vim ⇧H
        elif (depth % 3) == 2:
            x = mid_width
            self.write(f"\033[1;{x}H")  # for .do_row_leap_first_column_leftmost  # Vim ⇧H
        else:
            self.write("\033[1;31200H")  # for .do_row_leap_first_column_leftmost  # Vim ⇧H

        if (depth % 3) == 1:
            (y, x) = (Y1, X1)  # todo: send "H" in place of "1;1H"
        elif (depth % 3) == 2:
            (y, x) = (Y1, mid_width)
        else:
            (y, x) = (Y1, 31200)

        self.write(f"\033[{y};{x}H")  # for .do_row_leap_first_column_leftmost  # Vim ⇧H
        # Vim ⇧H

        # todo3: Leap to First Mirror Row, if Column Mirrored

    def do_row_leap_last_column_leftmost(self) -> None:
        """Leap to the Leftmost Column of the Last Row"""

        depth = self.klog_to_kcount()

        pt = self.proxy_terminal
        bt = pt.bytes_terminal

        x_width = bt.read_x_width()
        mid_width = (x_width // 2) + (x_width % 2)

        assert _PN_MAX_32100_ == 32100
        assert CUP_Y_X1 == "\033[" "{}" "H"

        if (depth % 3) == 1:
            (y, x) = (32100, X1)  # todo: send "H" in place of ";1H"
        elif (depth % 3) == 2:
            (y, x) = (32100, mid_width)
        else:
            (y, x) = (32100, 31200)

        self.write(f"\033[{y};{x}H")  # for .do_row_leap_last_column_leftmost  # Vim ⇧L

        # todo3: Leap to Last Mirror Row, if Column Mirrored

        # Vim ⇧L

    def do_row_leap_middle_column_leftmost(self) -> None:
        """Leap to the Leftmost Column of the Middle Row"""

        depth = self.klog_to_kcount()

        pt = self.proxy_terminal
        y_height = pt.y_height
        x_width = pt.x_width

        mid_height = (y_height // 2) + (y_height % 2)
        mid_width = (x_width // 2) + (x_width % 2)

        assert CUP_Y_X1 == "\033[" "{}" "H"
        assert _PN_MAX_32100_ == 32100

        if (depth % 3) == 1:
            (y, x) = (mid_height, X1)  # todo: send "H" in place of ";1H"
        elif (depth % 3) == 2:
            (y, x) = (mid_height, mid_width)
        else:
            (y, x) = (mid_height, 31200)

        self.write(f"\033[{y};{x}H")  # for .do_row_leap_middle_column_leftmost  # Vim ⇧M

        # Vim ⇧M

    def do_row_tail_erase(self) -> None:
        """Erase from the Cursor to the Tail of the Row"""

        assert EL_PS == "\033[" "{}" "K"
        self.write("\033[K")

        # Vim ⇧D  # Emacs ⌃K when not rightmost

    def do_row_tail_erase_inserting_start(self) -> None:
        """Erase from the Cursor to the Tail of the Row, and Start Inserting"""

        self.do_row_tail_erase()  # Vim ⇧D  # Emacs ⌃K when not rightmost
        self.do_inserting_start()  # Vim I

        # Vim ⇧C = # Vim ⇧D I

    def do_row_up(self) -> None:
        """Go up by 1 Row, but stop in Top Row"""

        assert CUU_Y == "\033[" "{}" "A"
        self.write("\033[A")

        # Emacs ⌃P

    #
    # Reply to F1 F2 F9 ...
    #

    def do_kdata_fn_f1(self) -> None:
        """Print Lines of main top Help for F1"""

        f1_text = """
            Shall we play a game?

            F1 - List Games
            F2 - Conway's Game-of-Life
            F3 - Snuck
            F5 - Puckman
            F8 - Color Picker
            F9 - Screen Editor

            ⌃D - Quit
        """

        # todo: F7 - Color Swatches

        f1_text = textwrap.dedent(f1_text).strip()

        self.print()
        self.print()

        for line in f1_text.splitlines():
            self.print(line)

        self.print()
        self.print()

    def do_kdata_fn_f2(self) -> None:
        """Play Conway's Game-of-Life for F2"""

        pt = self.proxy_terminal
        with_func_by_str = self.func_by_str

        # Default to Replacing, not Inserting

        assert SM_IRM == "\033[" "4h"
        assert RM_IRM == "\033[" "4l"

        irm_stext = pt.proxy_read_toggle_mirrors("\033[4h", stext1="\033[4l")
        restore_inserting_replacing = irm_stext  # maybe empty

        self.do_replacing_start()  # for F2

        # Run like the basic ScreenEditor, but with Keyboard Chords bound to ConwayLife

        cl = ConwayLife(screen_editor=self)

        func_by_str = dict(with_func_by_str)
        conway_func_by_str = cl.form_conway_func_by_str()
        func_by_str.update(conway_func_by_str)

        self.func_by_str = func_by_str

        try:
            cl.play_conway_life()
        finally:
            self.func_by_str = with_func_by_str  # replaces
            self.write(restore_inserting_replacing)  # doesn't raise UnicodeEncodeError

        # todo: refactor the callback out of  ScreenEditor forms ConwayLife to call back?

    def do_kdata_fn_f3(self) -> None:
        """Play Snuck for F3"""

        pt = self.proxy_terminal
        with_func_by_str = self.func_by_str

        # Default to Replacing, not Inserting

        assert SM_IRM == "\033[" "4h"
        assert RM_IRM == "\033[" "4l"

        irm_stext = pt.proxy_read_toggle_mirrors("\033[4h", stext1="\033[4l")
        restore_inserting_replacing = irm_stext  # maybe empty

        self.do_replacing_start()  # for F2

        # Run like the basic ScreenEditor, but with Keyboard Chords bound to ConwayLife

        sl = SnuckLife(screen_editor=self, dy=0, dx=2)

        func_by_str = dict(with_func_by_str)
        snuck_func_by_str = sl.form_snuck_func_by_str()
        func_by_str.update(snuck_func_by_str)

        self.func_by_str = func_by_str

        try:
            sl.play_snuck_life()
        finally:
            self.func_by_str = with_func_by_str  # replaces
            self.write(restore_inserting_replacing)  # doesn't raise UnicodeEncodeError

        # todo: refactor the callback out of  ScreenEditor forms ConwayLife to call back?

    def do_kdata_fn_f5(self) -> None:
        """Play Puckman"""

        path = pathlib.Path(sys.argv[0])
        cwd = path.parent
        xshverb = cwd / "xshverb.py"
        assert xshverb.exists(), (xshverb,)

        argv = [str(xshverb), "turtling"]

        self.__exit__(*sys.exc_info())
        subprocess.run(argv)
        self.__enter__()

        self.print("Goodbye from Puckman")

    def do_kdata_fn_f8(self) -> None:
        """Print a #555 Color Picker"""

        pt = self.proxy_terminal
        y_height = pt.y_height
        x_width = pt.x_width

        # Split a Landscape Terminal vertically

        y_frame = 2
        x_frame = 4

        board_height = y_height - 2 * y_frame
        board_height -= 1 - (board_height % 2)

        board_width = (x_width - 4 * x_frame) // 2
        board_width -= 1 - (board_width % 2)

        color_picker_pns.clear()

        # Plot the Left Panel

        ya = Y1 + y_frame
        yb = ya + board_height - 1

        xa = X1 + x_frame
        xb = xa + board_width - 1

        left_panel = True
        if left_panel:
            color_picker_plot(se=self, ya=ya, xa=xa, yb=yb, xb=xb, dc=1)

        # Plot the Right Panel

        (yc, yd) = (ya, yb)

        xd = x_width - x_frame
        xc = xd - board_width + 1

        right_panel = True
        if right_panel:
            color_picker_plot(se=self, ya=yc, xa=xc, yb=yd, xb=xd, dc=-1)

        #

        self.write("\033[m")

        print_gaps = True
        if print_gaps:

            self.write("\033[32100H")
            self.write("\033[A")
            self.print("(((", end=" ")

            for pn in range(32, 231 + 1):
                if pn not in color_picker_pns:
                    self.print(pn, end=" ")

            self.print(")))", end=" ")

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
            self.print()  # each ⌘L at Shell erases the last Input & Output

            # macOS Shell has distinct ← ↑ → ↓ and ⌥ ← → and ⇧ ← → and ⇧ Fn ← ↑ → ↓
            # macOS Option-as-Meta has ⌥⎋ ⌥Delete ⌥Tab ⌥⇧Tab ⌥Return

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

    def take_widget_at_yxf_mouse_release(self, y: int, x: int, f: int) -> None:
        """Take ⌥ Mouse Release as a call for Read-Eval-Print"""

        pt = self.proxy_terminal

        # List the Widgets of the Row

        y_text = pt.proxy_read_y_row_text(y, default=" ")
        widget_by_i = self.split_widgets(text=y_text)

        # Find a Widget beneath the Mouse Release

        x_widget = ""
        wx = -1

        for i, widget in widget_by_i.items():
            if x in range(1 + i, 1 + i + len(widget) + 1):
                x_widget = widget
                wx = X1 + i
                break

        if not x_widget:
            self.write("\a")  # for .take_widget_at_yxf_mouse_release
            return

        # todo8: Vanish the Command Verb typed out and then pushed

        verb = x_widget
        if x_widget.startswith("<") and x_widget.endswith(">") and (len(x_widget) > len("<>")):
            verb = x_widget[1:-1]

        vanisher = False  # todo8: do vanish each verb run almost at left of cursor
        if vanisher:
            self.vanish_widget_at_yxf(x_widget, y=y, x=wx)

        # Run the Widget at the Mouse Release

        self.take_mouse_verb_at_yxf(verb=verb, y=y, x=wx, f=f)

    def split_widgets(self, text: str) -> dict[int, str]:

        widget_by_i = dict()

        wi = -1
        text_plus = text + "  "
        for i, ich in enumerate(text):

            if wi == -1:
                if ich != " ":
                    wi = i
                    widget_by_i[wi] = ich

            elif widget_by_i[wi][0] == "<":
                widget_by_i[wi] += ich
                if ich == ">":
                    wi = -1

            elif text_plus[i] == "<":
                wi = i
                widget_by_i[wi] = ich

            else:
                if text_plus[i:].startswith("  "):
                    wi = -1
                else:
                    widget_by_i[wi] += ich

        return widget_by_i

    def vanish_widget_at_yxf(self, widget: str, y: int, x: int) -> None:
        """Vanish the Widget at the Mouse"""

        pt = self.proxy_terminal

        assert y >= 1, (y, x, widget)
        assert x >= 1, (y, x, widget)

        assert BEL == "\a"  # todo7: more complete doc/ comment of Screen Encodings
        assert BS == "\b"
        assert DECSC == "\033" "7"
        assert DECRC == "\033" "8"
        assert CUP_Y_X == "\033[" "{};{}" "H"
        assert DCH_X == "\033[" "{}" "P"
        assert RM_IRM == "\033[" "4l"
        assert SM_IRM == "\033[" "4h"

        self.write("\0337")

        self.write(f"\033[{y};{x}H")  # for .vanish_widget_at_yxf per Mouse Csi ⎋[M Release
        assert pt.row_y == y, (pt.row_y, y)
        assert pt.column_x == x, (pt.column_x, x)

        # Vanish if the Widget is no more than the Verb, unmarked

        irm_stext = pt.proxy_read_toggle_mirrors("\033[4h", stext1="\033[4l")
        if irm_stext == "\033[4h":

            self.write(f"\033[{len(widget)}P")  # deletes a Widget while inserting Texts

        else:
            assert (not irm_stext) or (irm_stext == "\033[4l"), (irm_stext,)

            self.write(len(widget) * " ")  # erases a Widget, while replacing Texts
            # self.write(len(widget) * "\b")  # todo4: Burst \b more naturally than ⎋[D or ⎋[H
            self.write(f"\033[{y};{x}H")  # for .vanish_widget_at_yxf

        self.write("\0338")

    def take_mouse_verb_at_yxf(self, verb: str, y: int, x: int, f: int) -> None:
        """Run the Verb at the Mouse Release"""

        pt = self.proxy_terminal
        column_x = pt.column_x
        row_y = pt.row_y
        writes_by_y_x = pt.writes_by_y_x

        # Eval some Keycaps

        if self.mouse_verb_to_write_sdata(verb):
            return

        # Sample Jabberwocky

        casefold = verb.casefold()

        if casefold == "jabberwocky":
            splits = Jabberwocky.split()
            split = random.choice(splits)

            if column_x > X1:
                sep = " "
                if row_y in writes_by_y_x.keys():
                    writes_by_x = writes_by_y_x[row_y]
                    if (column_x - 1) in writes_by_x.keys():
                        writes = writes_by_x[column_x - 1]
                        sep = writes[-1]

                if sep != " ":
                    self.write(" ")

            self.write(split)

            return

        # Shout out no Verb found

        assert BEL == "\a"

        self.write(repr(verb))
        self.write("\a")  # for .take_widget_at_yxf

        # todo4: find an Italic that works at ⎋[3M or somewhere

    def mouse_verb_to_write_sdata(self, verb: str) -> bool:
        """Eval some Keycaps"""

        if self.mouse_verb_to_push_kdata(verb):
            return True

        if self.mouse_verb_to_write_color_sdata(verb):
            return True

        if self.mouse_verb_to_write_keycaps_sdata(verb):
            return True

        return False

    def mouse_verb_to_push_kdata(self, verb: str) -> bool:
        """Eval a Keycap as 1 Packet of KData"""

        pt = self.proxy_terminal
        bt = pt.bytes_terminal

        kcap_list = list(_[0] for _ in KCAP_BY_KCHARS.items() if _[-1] == verb)
        if len(kcap_list) == 1:
            kdata = kcap_list[0].encode()
            tbp = TerminalBytePacket(kdata)
            bt.prefetches.append(tbp)
            return True

        return False

    def mouse_verb_to_write_keycaps_sdata(self, verb: str) -> bool:
        """Eval some Keycaps as Foreground, as Background, or as Foreground on Background Color"""

        splits = verb.split()
        keycaps = splits[0]

        if not keycaps.startswith("⎋"):
            return False

        sdata = b""
        shifting = False

        for t in keycaps:

            if t == "⎋":
                sdata += b"\033"
            elif t == "␣":  # Spacebar as a single-wide Glyph
                sdata += b" "
            elif t == "⇧":
                shifting = True
                continue
            elif shifting:
                sdata += t.encode()
            else:
                sdata += t.lower().encode()

            shifting = False

        # Succeed

        stext = sdata.decode()  # may raise UnicodeDecodeError
        self.write(stext)

        return True

    def mouse_verb_to_write_color_sdata(self, verb: str) -> bool:
        """Eval some Keycaps as Foreground, as Background, or as Foreground on Background Color"""

        splits = verb.split()

        if splits[2:]:
            if splits[1].casefold() == "on":
                fverb = splits[0]
                bverb = splits[2]

                fg = self.verb_to_color_sdata_if(fverb, kind="Foreground")
                bg = self.verb_to_color_sdata_if(bverb, kind="Background")
                if fg and bg:
                    self.write(bg.decode())
                    self.write(fg.decode())
                    return True

        elif splits[1:]:
            if splits[0].casefold() == "on":
                bverb = splits[1]

                bg = self.verb_to_color_sdata_if(bverb, kind="Background")
                if bg:
                    self.write(bg.decode())
                    return True

        else:
            fverb = splits[0]
            fg = self.verb_to_color_sdata_if(fverb, kind="Foreground")
            if fg:
                self.write(fg.decode())
                return True

        return False

    def verb_to_color_sdata_if(self, verb: str, kind: str) -> bytes:
        """Eval a Keycap as a Foreground or a Background Color"""

        splits = verb.split()
        assert kind in ("Foreground", "Background"), (kind,)

        keycaps = splits[0]

        # Eval a 6**3 Color

        if re.fullmatch(r"#[0-5][0-5][0-5]", string=keycaps):
            pn = self.six_cubed_color_verb_to_pn(keycaps)
            if kind == "Foreground":
                sdata = f"\033[38;5;{pn}m".encode()
                return sdata
            else:
                sdata = f"\033[48;5;{pn}m".encode()
                return sdata

        # Eval a 24-Bit Color

        if re.fullmatch(r"#[0-9A-Fa-f]{6}", string=keycaps):
            (r, g, b) = self.twenty_four_bit_color_verb_to_r_g_b(keycaps)

            if not sys_platform_darwin:
                if kind == "Foreground":
                    sdata = f"\033[38;2;{r};{b};{b}m".encode()
                    return sdata
                else:
                    sdata = f"\033[48;2;{r};{g};{b}m".encode()
                    return sdata

            # Else emulate the 24-Bit Color with a 6**3 Color

            r6 = int((r / 0xFF) * 5)
            g6 = int((g / 0xFF) * 5)
            b6 = int((b / 0xFF) * 5)

            pn = 0x10 + (r6 * 36 + g6 * 6 + b6)

            if kind == "Foreground":
                sdata = f"\033[38;5;{pn}m".encode()
                return sdata
            else:
                sdata = f"\033[48;5;{pn}m".encode()
                return sdata

        # Else don't succeed

        return b""

    def six_cubed_color_verb_to_pn(self, verb: str) -> int:
        """Eval a #RGB color"""

        assert verb[0] == "#", (verb,)

        r6 = int(verb[1])
        g6 = int(verb[2])
        b6 = int(verb[3])

        assert len(verb) == 4, (verb,)

        assert 0 <= r6 <= 5, (r6, verb)
        assert 0 <= g6 <= 5, (g6, verb)
        assert 0 <= b6 <= 5, (b6, verb)

        pn = 0x10 + (r6 * 36 + g6 * 6 + b6)

        return pn

    def twenty_four_bit_color_verb_to_r_g_b(self, verb: str) -> tuple[int, int, int]:
        """Eval a #RRGGBB color"""

        assert verb[0] == "#", (verb,)

        r = int(verb[1:][:2], base=0x10)
        g = int(verb[3:][:2], base=0x10)
        b = int(verb[5:][:2], base=0x10)

        assert len(verb) == 7, (verb,)

        return (r, g, b)


class SnuckLife:
    """Lead with one Sprite, and link more to follow in a chain"""

    screen_editor: ScreenEditor

    dy: int
    dx: int
    sprites: list[TerminalSprite]

    def __init__(self, screen_editor: ScreenEditor, dy: int, dx: int) -> None:

        self.screen_editor = screen_editor

        sprite0 = TerminalSprite(self, z_writes=("🟦",))
        sprite1 = TerminalSprite(self, z_writes=("⬜",))
        sprite2 = TerminalSprite(self, z_writes=("⬜",))
        sprites = [sprite0, sprite1, sprite2]

        self.dy = dy
        self.dx = dx
        self.sprites = sprites

    def play_snuck_life(self) -> None:
        """Play Conway's Game-of-Life"""

        sprites = self.sprites

        se = self.screen_editor
        pt = se.proxy_terminal

        # Say Hello

        se.print()
        se.print("Hello from Snuck")
        se.print()
        se.print("← ↑ → Arrows to move ahead or turn")
        se.print("Spacebar to step, ⌃Spacebar to make a half step, ⌥← to undo")
        se.print("Tab to step 8x Faster, ⇧Tab undo 8x Faster, ⌃D to quit")
        se.print()
        se.print()
        se.print()

        # Move enough to draw the whole Initial Snake

        (row_y, column_x) = pt.proxy_read_row_y_column_x()

        sprites[0].yx_leap_to(y=row_y, x=column_x)
        self.do_snuck_step_ahead()
        self.do_snuck_step_ahead()

        # Walk one step after another

        while True:
            try:
                se.read_eval_print_once()
            except SystemExit:
                break

        # Say Goodbye

        se.print()
        se.print("Goodbye from Snuck")

    def do_snuck_step_left(self) -> None:
        """Turn Left"""

        dy = self.dy
        dx = self.dx

        self.dy = -dx // 2
        self.dx = 2 * dy

        self.do_snuck_step_ahead()

    def do_snuck_step_right(self) -> None:
        """Turn Right"""

        dy = self.dy
        dx = self.dx

        self.dy = dx // 2
        self.dx = -2 * dy

        self.do_snuck_step_ahead()

    def do_snuck_8x_step_ahead(self) -> None:
        """Step ahead 8X"""

        for _ in range(8):
            self.do_snuck_step_ahead()

    def do_snuck_step_ahead(self) -> None:
        """Move the Head Sprite ahead, and have the rest follow"""

        se = self.screen_editor
        dy = self.dy
        dx = self.dx
        sprites = self.sprites

        assert DECSC == "\033" "7"  # DECSC 7 Cursor Save
        assert DECRC == "\033" "8"  # DECRC 8 Cursor Restore

        # Take in the next Move

        yx_list = list((_.row_ya, _.column_xa) for _ in sprites)

        (y, x) = yx_list[0]
        yx = (y + dy, x + dx)

        yx_list = [yx] + yx_list[:-1]

        # Move the Sprites

        se.write("\0337")

        for sprite, yx in zip(sprites, yx_list):
            (y, x) = yx
            if (y, x) != (-1, -1):
                sprite.yx_leap_to(y, x=x)

            # todo: When should we not-rewrite the Z Layer below?

        se.write("\0338")

    def form_snuck_func_by_str(self) -> dict[str, abc.Callable[[], None]]:
        "Bind Keycaps to Funcs"

        se = self.screen_editor
        func_by_str: dict[str, abc.Callable[[], None]] = {
            "⌃D": se.do_raise_system_exit,
            "Tab": self.do_snuck_8x_step_ahead,
            "Spacebar": self.do_snuck_step_ahead,
            "←": self.do_snuck_step_left,
            "↑": self.do_snuck_step_ahead,
            "→": self.do_snuck_step_right,
        }

        return func_by_str

    # riffing off the tradition of Emacs ⎋ X  S N A K E Return

    #
    # Halt at collision or edges - You lose if you give up, if you're cornered
    # Eat a Circle to grow a Square of the same Color
    # Mouse Click to copy and paste, Return Key to copy else paste
    # Start with three Squares
    #
    # Take over the Keyboard while Cursor on Head Sprite
    # From when Return is first pressed there, till it is pressed there again
    # Don't let go when other Keyboard Chords come here
    #


class TerminalSprite:
    """Move across the Screen in its own Z Layer"""

    proxy_terminal: ProxyTerminal
    z_writes: tuple[str]

    a_writes: tuple[str, ...] = tuple()
    row_ya: int = -1
    column_xa: int = -1

    b_writes: tuple[str, ...] = tuple()
    row_yb: int = -1
    column_xb: int = -1

    def __init__(self, snuck_life: SnuckLife, z_writes: tuple[str]) -> None:

        sl = snuck_life
        se = sl.screen_editor
        pt = se.proxy_terminal

        self.proxy_terminal = pt
        self.z_writes = z_writes

    def yx_leap_to(self, y: int, x: int) -> None:
        """Draw the Sprite at its new Y X Place"""

        pt = self.proxy_terminal

        z_writes = self.z_writes

        ya = self.row_ya
        xa = self.column_xa
        a_writes = self.a_writes

        yb = self.row_yb
        xb = self.column_xb
        b_writes = self.b_writes

        # Skip if already here

        if (ya, xa) == (y, x):
            return

        (yc, xc) = (y, x)
        (yd, xd) = (y, x + 1)

        # Read there

        default = (" ",)  # Single Wide Space
        ycxc_writes = pt.proxy_read_yx_writes(yc, x=xc, default=default)
        ydxd_writes = pt.proxy_read_yx_writes(yd, x=xd, default=default)

        # Write there

        pt.proxy_write(f"\033[{yc};{xc}H")  # for .yx_leap_to
        for write in z_writes:
            pt.proxy_write(write)

        # Erase here

        if (ya, xa) != (-1, -1):
            pt.proxy_write(f"\033[{ya};{xa}H")  # for .yx_leap_to
            for a_write in a_writes:
                pt.proxy_write(a_write)

        if (yb, xb) != (-1, -1):
            pt.proxy_write(f"\033[{yb};{xb}H")  # for .yx_leap_to
            for b_write in b_writes:
                pt.proxy_write(b_write)

        # Remember new

        self.a_writes = ycxc_writes  # replace
        self.row_ya = yc
        self.column_xa = xc

        self.b_writes = ydxd_writes  # replace
        self.row_yb = yd
        self.column_xb = xd


class ProxyTerminal:
    """Take in Writes to guess what the Screen looks like"""

    bytes_terminal: BytesTerminal  # .bt  # no Line Buffer on Input  # no implicit CR's in Output
    keyboard_bytes_log: typing.BinaryIO  # .klog  # logs Keyboard Delays & Bytes
    screen_bytes_log: typing.BinaryIO  # .slog  # logs Screen Delays & Bytes

    row_y: int  # Y places encoded as Southbound across 1 .. Height
    column_x: int  # X places encoded as Eastbound across 1 .. Width
    writes_by_y_x: dict[int, dict[int, list[str]]] = dict()  # mirrors the last Write at each Place

    toggles: list[str]  # Replacing/ Inserting/ etc
    styles: list[str]  # Foreground on Background Colors, etc

    y_height: int
    x_width: int

    was_y: int
    was_x: int

    def __init__(self) -> None:

        # Form some things

        bt = BytesTerminal()

        klog_path = pathlib.Path("__pycache__/k.keyboard")
        slog_path = pathlib.Path("__pycache__/s.screen")

        klog_path.parent.mkdir(exist_ok=True)
        slog_path.parent.mkdir(exist_ok=True)

        klog = klog_path.open("ab")
        slog = slog_path.open("ab")

        # Init per se

        self.bytes_terminal = bt
        self.keyboard_bytes_log = klog
        self.screen_bytes_log = slog

        self.row_y = -1
        self.column_x = -1
        self.writes_by_y_x = dict()

        self.toggles = list()
        self.styles = list()  # todo: or default to ⎋[⇧H ⎋[2⇧J ⎋[m etc but not ⎋[3⇧J

        self.y_height = -1
        self.x_width = -1

        self.was_y = -1
        self.was_x = -1

    def __enter__(self) -> typing.Self:
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

        sdata = b""

        # Guess at Normal after some Terminal Writes bypass our Screen Logs, if need be
        # Compare .slam_enough_stty_bits_to_normal

        assert DECSC == "\0337"
        assert DECRC == "\0338"

        assert RM_IRM == "\033[" "4l"
        assert _RM_SGR_MOUSE_ == "\033[" "?1000;1006l"
        assert _RM_XTERM_MAIN_ == "\033[" "?1049l"
        assert SGR_PS == "\033[" "{}" "m"

        sdata += b"\033[m"
        sdata += b"\033[4l"
        sdata += b"\0337"
        sdata += b"\033[?1049l"  # and implies \033[H at macOS Terminal
        sdata += b"\0338"
        sdata += b"\033[?1000;1006l"

        # Exit via 1st Column of 1 Row above the Last Row

        assert CUP_Y_X1 == "\033[" "{}" "H"
        assert CUU_Y == "\033[" "{}" "A"
        assert _PN_MAX_32100_ == 32100

        if exc_type is None:

            sdata += b"\033[32100H"
            sdata += b"\033[A"

        # Write last write, and then exit each, in reverse order of Enter's

        os.write(fileno, sdata)  # not:  os.write(fileno, b"ProxyTerminal.__exit__" b"\r\n")

        slog.flush()
        klog.flush()
        bt.__exit__(exc_type, exc_val, exc_tb)

        # Succeed

        # print(f"Exiting ProxyTerminal.__exit__ {exc_type}", file=sys.stderr)

        return None

    #
    # Sometimes bypass the Mirrors
    #

    def write_out(self, text: str) -> None:
        """Write the Bytes, and log them as written"""

        schars = text
        sdata = schars.encode()  # may raise UnicodeEncodeError

        slog = self.screen_bytes_log

        bt = self.bytes_terminal
        fileno = bt.fileno

        os.write(fileno, sdata)
        slog.write(sdata)

    def write_screen(self) -> None:
        """Redraw the Screen as mirrored, be that wrong or correct"""

        column_x = self.column_x
        writes_by_y_x = self.writes_by_y_x
        row_y = self.row_y
        styles = self.styles
        toggles = self.toggles
        y_height = self.y_height
        x_width = self.x_width

        tprint(f"{row_y=} {column_x=}  # write_screen")

        assert CUP_Y_X == "\033[" "{}" ";" "{}" "H"
        assert EL_PS == "\033[" "{}" "K"
        assert SGR_PS == "\033[" "{}" "m"
        assert RM_IRM == "\033[" "4l"

        # Redraw the Screen per se

        default = ["\033[48;5;255m", " "]

        self.write_out("\033[4l")
        self.write_out("\033[m")

        for y in range(Y1, y_height):
            writes_by_x = writes_by_y_x[y] if (y in writes_by_y_x.keys()) else dict()

            last_x = X1
            x_sorted = sorted(writes_by_x.keys())
            if not x_sorted:
                self.write_out(f"\033[{y}H")  # for .write_screen
            else:
                boring = False
                for x in range(X1, x_sorted[-1] + 1):
                    if x > x_width:
                        continue

                    x_writes = writes_by_x[x] if (x in writes_by_x.keys()) else default
                    assert x_writes[-1].isprintable(), (y, x, x_writes)  # todo6: check often

                    if not boring:  # todo7: stop redrawing Cursor unnecessarily
                        self.write_out(f"\033[{y};{x}H")  # for .write_screen

                    if not boring:  # todo7: stop redrawing Clear-Style unnecessarily
                        self.write_out("\033[m")

                    last_x_write = x_writes[-1]
                    for x_write in x_writes:
                        self.write_out(x_write)  # todo7: stop redrawing Style unnecessarily

                    g_width = self.str_guess_print_width(last_x_write)
                    last_x = x + g_width - 1

                    if len(x_writes) == 1:
                        if len(last_x_write) == 1:
                            if 0x20 <= ord(last_x_write) <= 0x7E:
                                boring = True

            if last_x < x_width:
                self.write_out("\033[m")  # SGR_PS before EL_X needed at macOS
                for x_write in default[:-1]:
                    self.write_out(x_write)
                self.write_out("\033[K")  # todo9: emulate at gCloud Shell

        self.write_out("\033[m")

        # Restore the Terminal Setup

        self.write_out(f"\033[{row_y};{column_x}H")

        for toggle in toggles:
            self.write_out(toggle)  # todo7: stop redrawing Toggles unnecessarily

        for style in styles:
            self.write_out(style)

        # todo4: .write_screen of Csi ⇧J ⇧H etc bypasses our mirrored writes

    #
    # Read from the Mirrors
    #

    def proxy_read_row_y(self) -> int:
        """Read the Terminal Cursor Y Row, but through the Mirrors"""

        (row_y, column_x) = self.proxy_read_row_y_column_x()

        return row_y

    def proxy_read_column_x(self) -> int:
        """Read the Terminal Cursor X Column, but through the Mirrors"""

        (row_y, column_x) = self.proxy_read_row_y_column_x()

        return column_x

    def proxy_read_row_y_column_x(self) -> tuple[int, int]:
        """Read the Terminal Cursor, but through the Mirrors"""

        bt = self.bytes_terminal

        (row_y, column_x) = bt.read_row_y_column_x()
        self.row_y = row_y  # for .proxy_read_row_y_column_x
        self.column_x = column_x  # for .proxy_read_row_y_column_x

        return (row_y, column_x)

    def proxy_read_y_height(self) -> int:
        """Read the Terminal Cursor Y Row, but through the Mirrors"""

        (y_height, x_width) = self.proxy_read_y_height_x_width()

        return y_height

    def proxy_read_x_width(self) -> int:
        """Read the Terminal Cursor X Column, but through the Mirrors"""

        (y_height, x_width) = self.proxy_read_y_height_x_width()

        return x_width

    def proxy_read_y_height_x_width(self) -> tuple[int, int]:
        """Read the Terminal Cursor, but through the Mirrors"""

        bt = self.bytes_terminal

        (y_height, x_width) = bt.read_y_height_x_width()
        self.y_height = y_height  # for .proxy_read_y_height_x_width
        self.x_width = x_width  # for .proxy_read_y_height_x_width

        return (y_height, x_width)

    def proxy_read_yx_pairs(self) -> tuple[tuple[int, int], ...]:
        """List the Y X Pairs written"""

        writes_by_y_x = self.writes_by_y_x

        yx_list = list()
        for y in writes_by_y_x.keys():
            writes_by_x = writes_by_y_x[y]
            for x in writes_by_x.keys():
                yx = (y, x)
                yx_list.append(yx)

        return tuple(yx_list)

    def proxy_read_yx_writes(self, y: int, x: int, default: tuple[str, ...]) -> tuple[str, ...]:
        """Read back Writes from one Y X Pair, else the Default"""

        writes_by_y_x = self.writes_by_y_x

        if y not in writes_by_y_x.keys():
            return default

        writes_by_x = writes_by_y_x[y]
        if x not in writes_by_x.keys():
            return default

        yx_writes = writes_by_x[x]

        return tuple(yx_writes)

    def proxy_read_y_row_text(self, y: int, default: str) -> str:
        """Read back just the Text Mirrored in the Row, without the Styling"""

        assert len(default.encode()) == 1, (default, len(default.encode()))  # todo: other defaults

        bt = self.bytes_terminal
        writes_by_y_x = self.writes_by_y_x

        x_width = bt.read_x_width()

        if y not in writes_by_y_x.keys():
            return x_width * default

        y_text = ""
        writes_by_x = writes_by_y_x[y]
        for x in range(1, x_width + 1):

            text = default
            if x in writes_by_x.keys():
                yx_writes = writes_by_x[x]
                if yx_writes:
                    text = yx_writes[-1]  # drops the Styling

            y_text += text

        return y_text

    def proxy_read_toggle_mirrors(self, stext0: str, stext1: str) -> str:
        """Read the present Mirror Setting of a pair:  the one, the other, else empty Bytes"""

        styles = self.styles

        zero = stext0 in styles
        one = stext1 in styles

        assert not (zero and one), (zero, one, stext0, stext1)
        if zero:
            return stext0
        if one:
            return stext1

        return ""

    #
    #  Write out at Y X Spots on into the Mirrors
    #

    def proxy_y_x_text_print(self, y: int, x: int, text: str) -> None:
        """Write Some Text Characters at one Y X Place"""

        assert CUP_Y_X == "\033[" "{}" ";" "{}" "H"

        self.proxy_write(f"\033[{y};{x}H")  # for .proxy_y_x_text_print
        self.proxy_write(text)

    def proxy_print(self, *args: object, end: str = "\r\n") -> None:
        """Join the Args by Space, add the End, and write the Encoded Chars"""

        schars = " ".join(str(_) for _ in args)
        self.proxy_write(schars)
        self.proxy_write(end)

    def proxy_write(self, text: str) -> None:
        """Write the Bytes, log them as written, and mirror them"""

        row_y = self.row_y
        column_x = self.column_x
        y_height = self.y_height
        x_width = self.x_width

        # Drop Texts and drop CR LF, when out of mirrored bounds

        if (y_height, x_width) != (-1, -1):

            if text.isprintable():
                self.proxy_write_printable(text=text)
                return

            if text == "\r\n":
                self.proxy_write_crlf()
                return

        # Else write the Bytes, and log them as written, and write them into the Mirrors

        self.write_out(text)
        self.y_x_write_mirrors(y=row_y, x=column_x, text=text)

    def proxy_write_printable(self, text: str) -> None:
        """Write Printable Text, but not CR LF, and log it as written"""

        row_y = self.row_y
        column_x = self.column_x

        tprint(f"{text!r}  # proxy_write_printable")

        # Split fitting from not-fitting

        prefix = ""
        suffix = ""
        for t in text:

            y = self.row_y
            x = self.column_x

            tprint(f"{y};{x} {t!r}  # proxy_write_printable")

            fitting = self.proxy_y_x_write_printable_t(y, x=x, t=t)

            if fitting:
                prefix += t
            else:
                suffix += t

        # Trace what's not fitting

        if suffix:
            (y, x) = (row_y, column_x)
            print(f"{y};{x} No proxy of {len(suffix)} {suffix!r} after {prefix!r}")

    def proxy_write_crlf(self) -> None:
        """Write CR LF if it fits"""

        column_x = self.column_x
        row_y = self.row_y
        y_height = self.y_height

        if row_y < y_height:
            self.write_out("\r\n")
        else:
            self.write_out("\r")

        self.y_x_write_mirrors(y=row_y, x=column_x, text="\r\n")

    def proxy_y_x_write_printable_t(self, y: int, x: int, t: str) -> bool:
        """Write & log a small Text if it fits, but mirror it always"""

        y_height = self.y_height
        x_width = self.x_width

        # Write the Bytes, and log them as written, only if they fit

        g_width = self.str_guess_print_width(t)
        last_x = x + g_width - 1

        fitting = False
        if 1 <= y <= y_height:
            if 1 <= last_x <= x_width:
                fitting = True

                self.write_out(t)  # trust caller to .tprint enough

        # Always do write the Mirrors

        self.y_x_write_mirrors(y=y, x=x, text=t)

        # End by saying if it fit

        return fitting

        # todo6: detect and mirror wrap effects at and past width of Row correctly

    def str_guess_print_width(self, text: str) -> int:
        """Guess the Width on Screen of printing a Text"""

        g_width = 0
        for t in text:
            eaw = unicodedata.east_asian_width(t)
            g_width += 1
            if eaw in ("F", "W"):
                g_width += 1

        return g_width

    def y_x_write_mirrors(self, y: int, x: int, text: str) -> None:
        """Mirror the Screen Panel"""

        matching = self.try_write_mirrors(text)

        if matching:
            tprint(f"{y};{x}", repr(text)[1:-1])
        else:
            tprint(f"{y};{x} No mirror of {text!r}")

    #
    # Write into the Mirrors
    #

    def try_write_mirrors(self, text: str) -> bool:
        """Mirror the Screen Panel"""

        stext = text
        sdata = stext.encode()  # may raise UnicodeEncodeError

        assert HT == "\t"
        assert LF == "\n"
        assert CR == "\r"

        # Write nothing, and write text, quite simply

        if not stext:
            return True

        if self.write_text_mirrors(stext):  # todo10: self._write_text_mirrors_ surely?
            return True

        # Take bursts of HT or LF, or a single CR LF

        if self.write_byte_burst_mirrors(sdata):
            return True

        if self.write_crlf_mirrors(sdata):
            return True

        # Take ⎋[{y};{x}H as meaningful, even when Y X negative, zero, or otherwise out of bounds

        if self.write_leap_csi_cup_y_x_mirrors(stext):
            return True

        # Write one whole Packet into the Mirrors

        tbp = TerminalBytePacket(sdata)

        if self.write_leap_byte_mirrors(tbp):
            return True

        if self.write_leap_csi_mirrors(tbp):
            return True

        if self.write_edit_csi_mirrors(tbp):
            return True

        if self.write_toggle_mirrors(tbp):
            return True

        if self.write_style_mirrors(tbp):
            return True

        # Else ask our caller to .tprint our confusion

        return False

    def write_text_mirrors(self, stext: str) -> bool:
        """Mirror the Text"""

        writes_by_y_x = self.writes_by_y_x
        styles = self.styles

        if not (stext and stext.isprintable()):
            return False

        for ch in stext:
            y = self.row_y
            x = self.column_x

            if y not in writes_by_y_x.keys():
                writes_by_y_x[y] = dict()

            writes_by_x = writes_by_y_x[y]

            writes_by_x[x] = list(styles) + [ch]  # replace  # todo6: prefer mutate?

            g_width = self.str_guess_print_width(ch)
            for x_plus in range(x + 1, x + g_width):  # encodes Wider Chars as "" Empty Str's
                writes_by_x[x_plus] = list(styles) + [""]  # replace

            self.column_x += g_width

        return True

    def write_byte_burst_mirrors(self, sdata: bytes) -> bool:
        """Write bursts of HT or LF"""

        pn = len(sdata)
        head = sdata[:1]
        if sdata == (pn * head):
            if sdata and (head in (b"\t", b"\n")):
                sdata_tbp = TerminalBytePacket(head)

                mirrored = 0
                for _ in range(pn):
                    if not self.write_leap_byte_mirrors(sdata_tbp):
                        mirrored += 1

                if mirrored < pn:
                    tprint(f"Only {mirrored} of {pn} * {head!r} mirrored")

                return True

        return False

    def write_crlf_mirrors(self, sdata: bytes) -> bool:
        """Write a single CR LF"""

        if sdata == b"\r\n":

            cr_tbp = TerminalBytePacket(b"\r")
            if self.write_leap_byte_mirrors(cr_tbp):

                lf_tbp = TerminalBytePacket(b"\n")
                mirrored = self.write_leap_byte_mirrors(lf_tbp)
                if not mirrored:
                    tprint("Only mirrored the CR, not the LF, of CR LF")

                return True

            assert False

            # todo: reconsider CR LF is 2 TerminalBytePacket, not 1

        return False

    def write_leap_csi_cup_y_x_mirrors(self, text: str) -> bool:
        """Mirror the ⇧H leaps to Y X into the Mirrors"""

        y_height = self.y_height
        x_width = self.x_width

        assert CUP_Y_X_REGEX == r"\033\[((-?[0-9]+)(;(-?[0-9]+))?)?H"
        assert _PN_MAX_32100_ == 32100

        m = re.fullmatch(r"\033\[((-?[0-9]+)(;(-?[0-9]+))?)?H", string=text)
        if m:  # as if searching for:  csi and tbp.tail == b"H"
            y = int(m.group(2)) if m.group(2) else Y1
            x = int(m.group(4)) if m.group(4) else X1

            row_y = y
            if y == 32100:
                row_y = y_height

            column_x = x
            if x == 32100:
                column_x = x_width

            self.row_y = row_y  # for .write_leap_csi_cup_y_x_mirrors
            self.column_x = column_x  # for .write_leap_csi_cup_y_x_mirrors

            return True

        return False

    def write_leap_byte_mirrors(self, tbp: TerminalBytePacket) -> bool:
        """Mirror the Control Byte Sequences that move the Terminal Cursor"""

        sdata = tbp.to_bytes()

        row_y = self.row_y
        column_x = self.column_x
        y_height = self.y_height
        x_width = self.x_width
        was_y = self.was_y
        was_x = self.was_x

        assert BEL == "\a"
        assert BS == "\b"
        assert HT == "\t"
        assert LF == "\n"
        assert CR == "\r"
        assert DEL == "\x7f"

        # Write BEL, HT, LF, or CR into the Mirrors

        if sdata == b"\a":
            return True

        if sdata == b"\b":
            self.column_x = max(X1, column_x - 1)
            return True

        if sdata == b"\t":
            tab_stop_1 = X1 + ((column_x - X1) // 8 + 1) * 8
            tab_stop_1 = min(x_width, tab_stop_1)

            while self.column_x < tab_stop_1:  # macOS writes Background Colors for b"\t"
                self.proxy_write_printable(text=" ")

            assert self.column_x == tab_stop_1, (self.column_x, tab_stop_1)

            return True

        if sdata == b"\n":
            if row_y < y_height:
                self.row_y = row_y + 1
                return True

            return False  # todo6: scroll the Mirrored Text at "\n" etc

        if sdata == b"\r":
            self.column_x = 1
            return True

            # todo6: scroll the Mirrored Text at "\n" etc

        # Checkpoint and revert the Y X Cursor

        if sdata == b"\0337":
            self.was_y = row_y
            self.was_x = column_x
            return True

        if sdata == b"\0338":
            self.row_y = was_y
            self.column_x = was_x
            return True

        # Else don't succeed here

        return False

    def write_leap_csi_mirrors(self, tbp: TerminalBytePacket) -> bool:
        """Mirror the Csi Esc Byte Sequences that move the Terminal Cursor"""

        if self.write_leap_csi_arrow_plus_mirrors(tbp):
            return True

        if self.write_leap_csi_tab_and_forth_mirrors(tbp):
            return True

        return False

        # omits .write_leap_csi_cup_y_x_mirrors

    def write_leap_csi_arrow_plus_mirrors(self, tbp: TerminalBytePacket) -> bool:
        """Mirror the plainest ← ↑ → ↓ Arrows, even with Repeat Counts, and the Y or X Leaps"""

        bt = self.bytes_terminal
        column_x = self.column_x
        row_y = self.row_y

        y_height = bt.read_y_height()
        x_width = bt.read_x_width()

        #

        assert CUU_Y == "\033[" "{}" "A"
        assert CUD_Y == "\033[" "{}" "B"
        assert CUF_X == "\033[" "{}" "C"
        assert CUB_X == "\033[" "{}" "D"

        assert CHA_X == "\033[" "{}" "G"
        assert VPA_Y == "\033[" "{}" "d"

        #

        csi = tbp.head == b"\033["  # takes Csi ⎋[, but not Esc Csi ⎋⎋[

        if csi and tbp.tail and (tbp.tail in b"ABCDGd"):  # "ABCD" Arrows per se, and also "Gd"
            if not tbp.back:
                pn = int(tbp.neck) if tbp.neck else PN1
                if pn:

                    if tbp.tail == b"A":
                        self.row_y = max(Y1, row_y - pn)
                        return True
                    if tbp.tail == b"B":
                        self.row_y = min(y_height, row_y + pn)
                        return True
                    if tbp.tail == b"C":
                        self.column_x = min(x_width, column_x + pn)
                        return True
                    if tbp.tail == b"D":
                        self.column_x = max(X1, column_x - pn)
                        return True

                    # And the leaps relative to Y1 X1 too

                    if tbp.tail == b"G":
                        self.column_x = min(x_width, pn)
                        return True
                    if tbp.tail == b"d":
                        self.row_y = min(y_height, pn)
                        return True

        return False

    def write_leap_csi_tab_and_forth_mirrors(self, tbp: TerminalBytePacket) -> bool:
        """Mirror the plainest ← ↑ → ↓ Arrows, even with Repeat Counts, and the Y or X Leaps"""

        bt = self.bytes_terminal
        column_x = self.column_x

        x_width = bt.read_x_width()

        #

        assert CHT_X == "\033[" "{}" "I"  # Cursor Forward [Horizontal] Tabulation
        assert CBT_X == "\033[" "{}" "Z"  # Cursor Backward [Horizontal] Tabulation

        csi = tbp.head == b"\033["  # takes Csi ⎋[, but not Esc Csi ⎋⎋[

        if csi and tbp.tail and (tbp.tail in b"IZ"):
            if not tbp.back:
                pn = int(tbp.neck) if tbp.neck else PN1
                if pn:

                    if tbp.tail == b"I":
                        tab_stop_n = X1 + ((column_x - X1) // 8 + pn) * 8
                        self.column_x = min(x_width, tab_stop_n)
                        return True

                    if tbp.tail == b"Z":
                        tab_stop_n = X1 + ((column_x + (8 - 1) - X1) // 8 - pn) * 8
                        self.column_x = max(X1, tab_stop_n)
                        return True

        return False

    def write_edit_csi_mirrors(self, tbp: TerminalBytePacket) -> bool:
        """Mirror the Csi Esc Byte Sequences that edit the Rows and Columns"""

        if self.write_erase_csi_mirrors(tbp):
            return True

        if self.write_delete_insert_csi_mirrors(tbp):
            return True

        return False

    def write_erase_csi_mirrors(self, tbp: TerminalBytePacket) -> bool:
        """Mirror the Csi Esc Byte Sequences that erase Rows and Columns"""

        column_x = self.column_x
        row_y = self.row_y
        y_height = self.y_height

        assert ED_PS == "\033[" "{}" "J"
        assert EL_PS == "\033[" "{}" "K"

        # Mirror ⇧K Erases of Head or Tail or Whole Row

        csi = tbp.head == b"\033["  # takes Csi ⎋[, but not Esc Csi ⎋⎋[

        if csi and ((tbp.tail == b"J") or (tbp.tail == b"K")):
            if not tbp.back:
                ps = int(tbp.neck) if tbp.neck else 0
                if ps in (0, 1, 2):

                    if tbp.tail == b"K":

                        self._write_row_erase_(ps)

                    if tbp.tail == b"J":

                        if ps == 0:
                            self._write_row_erase_(ps)
                            (ya, yb) = (row_y + 1, y_height)  # default to PS0 ⎋[⇧J after-erase
                        elif ps == 1:  # ⎋[1⇧J before-erase
                            self._write_row_erase_(ps)
                            (ya, yb) = (Y1, row_y - 1)  # includes the Character beneath the Cursor
                        else:
                            assert ps == 2, (ps,)  # ⎋[2⇧J screen-erase
                            # self._write_row_erase_(ps)  # harmless, but unneeded
                            (ya, yb) = (1, y_height)

                        for y in range(ya, yb + 1):
                            self.row_y = y
                            self.column_x = X1

                            self._write_row_erase_(ps=2)  # PS2 ⎋[2⇧K row-erase

                        self.column_x = column_x
                        self.row_y = row_y

                    return True

        return False

    def _write_row_erase_(self, ps: int) -> None:
        """Mirror ⇧K Erases of Head or Tail or Whole Row"""

        assert ps in (0, 1, 2), (ps,)

        column_x = self.column_x
        row_y = self.row_y
        writes_by_y_x = self.writes_by_y_x
        styles = self.styles
        x_width = self.x_width

        assert EL_PS == "\033[" "{}" "K"

        if ps == 0:

            (xa, xb) = (column_x, x_width)  # default to PS0 ⎋[⇧K row-tail-erase

            writes_by_x = dict()
            if row_y in writes_by_y_x.keys():
                writes_by_x = writes_by_y_x[row_y]

            max_x = -1
            if writes_by_x:
                max_x = max(writes_by_x.keys())

            if xa > max_x:
                if xa not in writes_by_x.keys():
                    while (xa > 1) and ((xa - 1) not in writes_by_x.keys()):
                        xa -= 1

        elif ps == 1:  # ⎋[1⇧K row-head-erase

            (xa, xb) = (X1, column_x)  # includes the Character beneath the Cursor

        else:

            assert ps == 2, (ps,)  # ⎋[2⇧K row-erase
            (xa, xb) = (1, x_width)

        y = row_y
        if y not in writes_by_y_x.keys():
            writes_by_y_x[y] = dict()

        writes_by_x = writes_by_y_x[y]
        for x in range(xa, xb + 1):
            writes_by_x[x] = list(styles) + [" "]

    def write_delete_insert_csi_mirrors(self, tbp: TerminalBytePacket) -> bool:
        """Mirror the Csi Esc Byte Sequences that delete or insert Rows and Columns"""

        column_x = self.column_x
        row_y = self.row_y
        writes_by_y_x = self.writes_by_y_x

        assert DCH_X == "\033[" "{}" "P"
        assert ECH_X == "\033[" "{}" "X"  # todo10: ⎋[⇧X columns-erase

        # Mirror ⇧P Deletes of Pn Characters in the Row

        csi = tbp.head == b"\033["  # takes Csi ⎋[, but not Esc Csi ⎋⎋[

        if csi and (tbp.tail == b"P"):
            if not tbp.back:
                pn = max(PN1, int(tbp.neck) if tbp.neck else PN1)
                if pn:

                    y = row_y
                    if y not in writes_by_y_x.keys():
                        writes_by_y_x[y] = dict()

                    writes_by_x = writes_by_y_x[y]

                    # Delete the Chars themselves

                    xpn = column_x + pn
                    for x in range(column_x, xpn):
                        if x in writes_by_x.keys():
                            del writes_by_x[x]

                    # Shift Left each Char that follows

                    x_list = sorted(_ for _ in writes_by_x.keys() if _ >= xpn)
                    for from_x in x_list:
                        to_x = from_x - pn

                        writes_by_x[to_x] = writes_by_x[from_x]
                        del writes_by_x[from_x]

                    # todo10: Mark the Row as ended with Background Color
                    # todo10: [..., ""] is the encoding
                    # todo10: replay it properly, encode it properly, be happier
                    # todo10: then go test at gShell too

                    # Succeed

                    return True

        return False

    def write_toggle_mirrors(self, tbp: TerminalBytePacket) -> bool:
        """Mirror the Replacing/ Inserting choice for before writing each Character"""

        sdata = tbp.to_bytes()

        toggles = self.toggles

        assert SM_IRM == "\033[" "4h"
        assert RM_IRM == "\033[" "4l"

        toggle_pairs = [
            ("\033[" "4h", "\033[" "4l"),
        ]

        # Find the Toggle Pair

        for toggle_pair in toggle_pairs:
            stext = sdata.decode()  # may raise UnicodeDecodeError
            if stext in toggle_pair:
                index = toggle_pair.index(stext)
                other = toggle_pair[1 - index]

                # Remove the Old Stale if need be, but add the New Fresh always

                if other in toggles:
                    toggles.remove(other)

                toggles.append(stext)

                # Succeed

                return True

        # Else don't succeed here

        return False

    def write_style_mirrors(self, tbp: TerminalBytePacket) -> bool:
        """Mirror the Foreground-on-Background Colors of the next Text"""

        sdata0 = tbp.to_bytes()
        stext0 = sdata0.decode()  # may raise UnicodeDecodeError

        styles = self.styles

        # Write only Sgr Styles into the Mirrors

        kind0 = self.tbp_to_sgr_kind(tbp)
        if not kind0:
            return False

        assert kind0 in ("Foreground", "Background", "Colorless"), (kind0,)

        # Take the cancellation of all Sgr Styles

        if kind0 == "Colorless":

            if sdata0 == b"\033[m":
                styles.clear()
                return True

            # Take the Text Effects apart from Colors

            if stext0 in styles:
                return True

            styles.append(stext0)
            styles.sort()

            return False

        # Remove the Old Stale Color if need be

        assert kind0 in ("Foreground", "Background"), (kind0,)

        removables = list(styles)
        for removable in removables:
            tbp1 = TerminalBytePacket()
            kind1 = self.tbp_to_sgr_kind(tbp1)
            if kind1 == kind0:
                styles.remove(removable)

        # Add the New Fresh Color always

        styles.append(stext0)
        styles.sort()

        return True

    def tbp_to_sgr_kind(self, tbp: TerminalBytePacket) -> str:
        """Say 'Foreground' or 'Background' or 'Colorless' or '' Empty Str"""

        assert SGR_PS == "\033[" "{}" "m"

        if tbp.head != b"\033[":
            return ""
        if tbp.back:
            return ""
        if tbp.tail != b"m":
            return ""

        neck_splits = tbp.neck.split(b";")
        assert neck_splits, (neck_splits, tbp.neck, tbp)  # because Split With Arg

        if neck_splits == [b""]:
            return "Colorless"

        if len(neck_splits) == 1:
            pn = int(tbp.neck)

            if (30 <= pn <= 37) or (90 <= pn <= 97):
                return "Foreground"

            if (40 <= pn <= 47) or (100 <= pn <= 107):
                return "Background"

            return "Colorless"

        if len(neck_splits) == 3:

            if bytes(neck_splits[0]) in (b"38", b"48"):
                ground = "Foreground" if (neck_splits[0] == b"38") else "Background"
                if neck_splits[1] == b"5":
                    pn = int(neck_splits[2])
                    assert 0 <= pn <= 0xFF, (pn, tbp)
                    return ground

            return "Colorless"

        if len(neck_splits) == 5:

            if bytes(neck_splits[0]) in (b"38", b"48"):
                ground = "Foreground" if (neck_splits[0] == b"38") else "Background"
                if neck_splits[1] == b"2":

                    r = int(neck_splits[2])
                    g = int(neck_splits[3])
                    b = int(neck_splits[4])

                    assert 0 <= r <= 0xFF, (r, tbp)
                    assert 0 <= g <= 0xFF, (g, tbp)
                    assert 0 <= b <= 0xFF, (b, tbp)

                    return ground

            return "Colorless"

        return "Colorless"


#

# todo9: (Inserting) query buttons, subscribe themselves to update streams when first clicked
# todo9: Press Return inside a Button to click it
# todo9: Press Return just after a Button to vanish and run it

# todo9: Small Int Literals alone track X if not an X tracker already. X= is explicit, but eraseable
# todo9: hh:mm and hh:mm:ss tracks local time, or UTC, can be marked with eraseable -07:00 etc

# todo9: Play Tetris as well as Emacs  ⎋ X  T E T R I S  Return

#

# todo8: open up |d |e |f |l |m |p |q |v |y |z- gateways do gateway only at left
# todo8: keep |a |c |g |h |i |j |k |n |o |r |s |t |u |w |x
# todo8: |g pattern pattern - we're saying patterns can't be single letters

# todo8: bin/xshverb.py conway
# todo8: bin/xshverb.py puckman
# todo8: bin/xshverb.py snake
# todo8: bin/xshverb.py tetris

# todo8: do we now want fill with Color or not, and do we get it natively, and squelch insert mode
# todo8: fix up all the fills, including \n
# todo8: bin/+: Tease out macOS v gCloud Shell @ BG + EL

# todo8: look to resize the Terminal to grow, vs such large F9 Help as ours

# todo8: Create Shell TPut buttons - Cup Bg Lf Lf Dch SLeep Lf Lf
# todo8: printf '\e[H''\e[46m''\n''\n''abcde\b\b\b'; sleep 1; printf '\e[P\e[2B'; sleep 1; printf '\n\n'

# todo8: click at cursor to vanish & run, click away to run without vanish

# todo8: draw the paint swatches of 6 R x 6x6 GB, 6 G x 6x6 RB, 6 B x 6x6 RG

# todo8: try a tree of #555 to #455 #545 #554
# todo8: and then then on to #445 #544 and #454 544 and #454 #554
# todo8: and then on to #444 at each but then pick one at random
# todo8: but first simulate all this with a click at cursor to vanish & run & add a full-block
# todo8: run in insert mode to delete the trace of the verb
# todo8: teach the mouseless Spacebar to look back for verb

# todo8: pick fun fg/bg mixes as our demos - how about green-on-black and yellow-on-blue ?

# todo8: glider, sw glider, ne nw se gliders
# todo8: circle triangle square rectangle polygon
# todo8: click on emoji to copy-paste them
# todo8: Unicode Medium & Large Circles ⚪ ⚫ 🔴 🔵 🟠 🟡 🟢 🟣 🟤
# todo8: Unicode Large Squares ⬛ ⬜ 🟥 🟦 🟧 🟨 🟩 🟪 🟫
# todo8: \e notation

#

# todo7: attach an emoji to drag behind a cursor

# todo7: plain bold italic
# todo7: <mark> flip spin

# todo7: more test of Disappearing Command Verbs
# todo7: more test of Arrow Bursts at ⌥ Mouse Release
# todo7: choose to cursor chase the ⌥ Mouse Release, or not - maybe when there is no button there?

#

# todo6: Bind repeated Vim ⎋ ⌃L like Emacs to Scroll to Center/ Top/ Bottom

# todo6: ⌃H K lookup of __doc__ per Keychord Sequence Bound, as in Emacs
# todo6: full UnicodeData Name as Verb, and partial

#

# todo3: Each Y X gets a List Str. Last Item of List Str is the Text written after the Controls
# todo3: Hide the Conway Cursor?
# todo3: Discover the same drawing but translated to new Y X or new Rotation


#
# Plot 6**3 Colors
#


color_picker_pns = list()


def color_picker_plot(se: ScreenEditor, ya: int, xa: int, yb: int, xb: int, dc: int) -> None:
    """Draw a Color Picker as Two Triangles, one with a Black Center, one with White"""

    xab = (xa + xb) // 2
    # yab = (ya + yb) // 2

    glyph = unicodedata.lookup("Full Block")

    max_rd = math.sqrt((yb - ya) ** 2 + (xb - xab) ** 2)
    max_gd = math.sqrt((ya - yb) ** 2 + (xab - xa) ** 2)
    max_bd = math.sqrt((ya - yb) ** 2 + (xab - xb) ** 2)

    sw_n_m = (yb - ya) / (xa - xab)  # slope to SW (yb, xa) from N (ya, xab)
    se_n_m = (yb - ya) / (xb - xab)  # slope to SE (yb, xb) from N (ya, xab)

    for y in range(ya, yb + 1):

        for x in range(xa, xab + 1):
            sw_n_y = ya + sw_n_m * (x - xab)
            if y >= sw_n_y:

                rd = math.sqrt((y - ya) ** 2 + (x - xab) ** 2)
                gd = math.sqrt((y - yb) ** 2 + (x - xa) ** 2)
                bd = math.sqrt((y - yb) ** 2 + (x - xb) ** 2)

                rf = rd / max_rd
                gf = gd / max_gd
                bf = bd / max_bd

                r6 = int(rf * 3 / 2 * 5.5) if (rf < 2 / 3) else 0
                g6 = int(gf * 3 / 2 * 5.5) if (gf < 2 / 3) else 0
                b6 = int(bf * 3 / 2 * 5.5) if (bf < 2 / 3) else 0

                # r6 = b6 = 0

                hy = y
                if dc < 0:
                    r6 = 5 - r6
                    g6 = 5 - g6
                    b6 = 5 - b6

                    hy = ya + (yb - y)

                pn = 0x10 + (r6 * 36 + g6 * 6 + b6)
                color_picker_pns.append(pn)

                se.write(f"\033[{hy};{x}H")
                se.write(f"\033[38;5;{pn}m")
                # se.write(str(g6))
                se.write(glyph)

        for x in range(xab + 1, xb + 1):
            se_n_y = ya + se_n_m * (x - xab)
            if y >= se_n_y:

                rd = math.sqrt((y - ya) ** 2 + (x - xab) ** 2)
                gd = math.sqrt((y - yb) ** 2 + (x - xa) ** 2)
                bd = math.sqrt((y - yb) ** 2 + (x - xb) ** 2)

                rf = rd / max_rd
                gf = gd / max_gd
                bf = bd / max_bd

                r6 = int(rf * 3 / 2 * 5.5) if (rf < 2 / 3) else 0
                g6 = int(gf * 3 / 2 * 5.5) if (gf < 2 / 3) else 0
                b6 = int(bf * 3 / 2 * 5.5) if (bf < 2 / 3) else 0

                # r6 = b6 = 0

                hy = y
                if dc < 0:
                    r6 = 5 - r6
                    g6 = 5 - g6
                    b6 = 5 - b6

                    hy = ya + (yb - y)

                pn = 0x10 + (r6 * 36 + g6 * 6 + b6)
                color_picker_pns.append(pn)

                se.write(f"\033[{hy};{x}H")
                se.write(f"\033[38;5;{pn}m")
                # se.write(str(g6))
                se.write(glyph)


# todo2: F1 F2 F3 F4 for the different pages and pages of Help

# todo2: elapsed time logs into k.keyboard and s.screen for record/replay

# todo2: Vim C0 C⇧$ D0 D⇧$ . . . Yea, sample Y X before/ after and do it


# Help with famous ⎋ 7 8 C L ⇧D ⇧E ⇧M (when not taken by Vim)
# Help with famous Csi ⎋[ ⇧@ ⇧A⇧B⇧C⇧D⇧E⇧G⇧H⇧I⇧J⇧K⇧L⇧M⇧P⇧S⇧T⇧Z ⇧}⇧~ and ⎋[ DHLMNQT

SCREEN_WRITER_HELP = r"""

    Keycap Symbols are ⎋ Esc, ⌃ Control, ⌥ Option/ Alt, ⇧ Shift, ⌘ Command/ Os, ␣ Spacebar

        ⌃G ⌃H ⌃I ⌃J ⌃M mean \a \b \t \n \r, and ⌃[ means \e, also known as ⎋ Esc
        Tab means ⌃I \t, and Return means ⌃M \r

        Minimal Emacs is ⌃A ⌃B ⌃D ⌃E ⌃F ⌃G ⌃J ⌃K ⌃M ⌃N ⌃O ⌃P ⌃Q ⌃V
        Minimal Vim is ⌃L and ⎋ I ⌃V  ⎋ 0  ⎋ A I J L O R S X  ⎋ ⇧ $ A C D H L M O Q R S X

    Esc ⎋ Byte Pairs

        ⎋7 cursor-checkpoint  ⎋8 cursor-revert (defaults to Y 1 X 1)
        ⎋C screen-erase  ⎋L row-column-leap
        ⎋⇧D ↓  ⎋⇧E \r\n else \r  ⎋⇧M ↑

    Csi ⎋[ Sequences

        ⎋[⇧A ↑  ⎋[⇧B ↓  ⎋[⇧C →  ⎋[⇧D ←  ⎋[⇧I ⌃I  ⎋[⇧Z ⇧Tab
        ⎋[D row-leap  ⎋[⇧G column-leap  ⎋[⇧H row-column-leap

        ⎋[⇧M rows-delete  ⎋[⇧L rows-insert  ⎋[⇧P chars-delete  ⎋[⇧@ chars-insert
        ⎋[⇧J after-erase  ⎋[1⇧J before-erase  ⎋[2⇧J screen-erase  ⎋[3⇧J scrollback-erase
        ⎋[⇧K row-tail-erase  ⎋[1⇧K row-head-erase  ⎋[2⇧K row-erase  ⎋[⇧X columns-erase
        ⎋[⇧T rows-down  ⎋[⇧S rows-up  ⎋['⇧} cols-insert  ⎋['⇧~ cols-delete

        ⎋[4H insert  ⎋[4L replace  ⎋[6␣Q bar  ⎋[4␣Q skid  ⎋[␣Q unstyled
        ⎋[?1049H screen-alt  ⎋[?1049L screen-main  ⎋[?25L cursor-hide  ⎋[?25H cursor-show

        ⎋[1M bold  ⎋[4M underline  ⎋[7M reverse/inverse  ⎋[38;5;231m max grayscale
        red green bright-blue  ⎋[31M  ⎋[32M  ⎋[94M  ⎋[30M  ⎋[97M  on rgb  ⎋[41M  ⎋[42M  ⎋[104M
        ⎋[M plain  <Jabberwocky>  #555 on #005  #003366 on #FFCC99

        ⎋[5N call for reply ⎋[0N
        ⎋[6N call for reply ⎋[{y};{x}⇧R
        ⎋[18T call for reply ⎋[8;{rows};{columns}T

        ⎋[?1000;1006H till ⎋[?1000;1006L for mouse ⎋[<{f};{x};{y} ⇧M to M of f = 0b⌃⌥⇧00
        or ⎋[?1000 H L by itself, or 1005, or 1015

"""

# todo10: #24 Grayscale as our reach for ⎋[38;5;231m


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
LF = "\n"  # 00/10 ⌃J Line Feed  # akin to ⌃K and CUD "\033[" "B"
CR = "\r"  # 00/13 ⌃M Carriage Return  # akin to CHA "\033[" "G"

ESC = "\033"  # 01/11  ⌃[ Escape  # often known as Shell printf '\e', but Python doesn't define \e
SS3 = "\033O"  # ESC 04/15 Single Shift Three  # ⎋⇧O in macOS F1 F2 F3 F4
CSI = "\033["  # ESC 05/11 Control Sequence Introducer

DECSC = "\033" "7"  # ESC 03/07 Save Cursor [Checkpoint] (DECSC)
DECRC = "\033" "8"  # ESC 03/08 Restore Cursor [Rollback] (DECRC)

CSI_PIF_REGEX = r"(\033\[)" r"([0-?]*)" r"([ -/]*)" r"(.)"  # Parameter/ Intermediate/ Final Bytes


class BytesTerminal:
    """Write/ Read Bytes at Screen/ Keyboard of the Terminal"""

    stdio: typing.TextIO
    fileno: int

    before: int  # for writing at Enter
    tcgetattr: list[int | list[bytes | int]]  # replaced by Enter
    after: int  # for writing at Exit  # todo: .TCSAFLUSH vs large Paste

    prefetches: list[TerminalBytePacket]
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

        self.prefetches = list()
        self.extras = bytearray()

        self.y_height = -1
        self.x_width = -1

    def __enter__(self) -> typing.Self:
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

        prefetches = self.prefetches
        if prefetches:
            tbp = prefetches.pop(0)
            return tbp

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
        #     if kdata in (b"\033", b"\033O", b"\033[", b"\033\033", b"\033\033O", b"\033\033["):
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
                    if kdata == b"\033O":  # ⎋⇧O for Vim
                        if not self.kbhit(timeout=0.333):
                            break  # rejects slow SS3 ⎋⇧O P Q R S of FnF1..FnF4

    def read_y_height(self) -> int:
        """Count Terminal Screen Pane Rows"""

        (y_height, x_width) = self.read_y_height_x_width()

        return y_height

    def read_x_width(self) -> int:
        """Count Terminal Screen Pane Columns"""

        (y_height, x_width) = self.read_y_height_x_width()

        return x_width

    def read_y_height_x_width(self) -> tuple[int, int]:
        """Count Terminal Screen Pane Rows & Columns"""

        fileno = self.fileno
        size = os.get_terminal_size(fileno)

        assert 20 <= size.columns <= _PN_MAX_32100_, (size,)  # 20 <= macOS Terminal Width
        assert 5 <= size.lines <= _PN_MAX_32100_, (size,)  # 5 <= macOS Terminal Height

        y_height = size.lines
        x_width = size.columns

        return (y_height, x_width)  # reversed from Python's (x, y) standard

    def read_column_x(self) -> int:
        """Find the Terminal Cursor Column"""

        (y, x) = self.read_row_y_column_x()

        return x

    def read_row_y_column_x(self) -> tuple[int, int]:
        """Find the Terminal Cursor"""

        stdio = self.stdio

        assert DSR_6 == "\033[" "6n"
        assert CPR_Y_X_REGEX == r"\033\[([0-9]+);([0-9]+)R"

        kbhit = self.kbhit(timeout=0.000)  # flushes output, then polls input
        assert not kbhit  # todo: cope when Mouse or Paste or Keyboard work disrupts replies to Csi

        stdio.write("\033[6n")  # bypass Screen Logs & Screen Mirrors above
        tbp = self.read_byte_packet(timeout=None)
        kdata = tbp.to_bytes()

        m = re.fullmatch(rb"\033\[([0-9]+);([0-9]+)R", string=kdata)
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
            raise ValueError(extras, data)  # for example, raises the b'\x80' of b'\xc0\x80'

        self._require_simple_()

        # doesn't take bytes([0x80 | 0x0B]) as meaning b"\033\x5b" CSI ⎋[
        # doesn't take bytes([0x80 | 0x0F]) as meaning b"\033\x4f" SS3 ⎋O

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

        # "b'\033[' b'6' b' q'"

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
        self._try_open_(b"\033")  # first Byte of Esc Sequence
        self._try_open_(b"\033\033")  # first Two Bytes of Esc-Esc Sequence
        self._try_open_(b"\033O")  # first Two Bytes of Three-Byte SS3 Sequence
        self._try_open_(b"\033[", b"6", b" ")  # CSI Head with Neck and Back but no Tail
        self._try_open_(b"\xed\x80")  # Head of >= 3 Byte UTF-8 Encoding
        self._try_open_(b"\xf4\x80\x80")  # Head of >= 4 Byte UTF-8 Encoding
        self._try_open_(b"\033[M#\xff")  # Undecodable Head, incomplete CSI Mouse Report
        self._try_open_(b"\033[M \xc4\x8a")  # Head only, 6 Byte incomplete CSI Mouse Report

        # Try some Packets closed against taking more Bytes

        self._try_closed_(b"\n")  # Head only, of 7-bit Control Byte
        self._try_closed_(b"\033\033[", b"3;5", b"~")  # CSI Head with Neck and Tail, no Back
        self._try_closed_(b"\xc0")  # Head only, of 8-bit Control Byte
        self._try_closed_(b"\xff")  # Head only, of 8-bit Control Byte
        self._try_closed_(b"\xc2\xad")  # Head only, of 2 Byte UTF-8 of U+00AD Soft-Hyphen Control
        self._try_closed_(b"\033", b"A")  # Head & Text Tail of a Two-Byte Esc Sequence
        self._try_closed_(b"\033", b"\t")  # Head & Control Tail of a Two-Byte Esc Sequence
        self._try_closed_(b"\033O", b"P")  # Head & Text Tail of a Three-Byte SS3 Sequence
        self._try_closed_(b"\033[", b"3;5", b"H")  # CSI Head with Next and Tail
        self._try_closed_(b"\033[", b"6", b" q")  # CSI Head with Neck and Back & Tail

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
        if head_plus.startswith(b"\033[M"):
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

        if (head == b"\033[") and (not neck) and (not back):
            if data == b"M":
                head.extend(data)
                return b""  # takes 3rd Byte of CSI Mouse Report here

        if not head.startswith(b"\033[M"):  # ⎋[M Mouse Report
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

        assert ESC == "\033"  # ⎋
        assert CSI == "\033["  # ⎋[
        assert SS3 == "\033O"  # ⎋⇧O

        # Look only outside of Mouse Reports

        assert not head.startswith(b"\033[M"), (head,)  # Mouse Report

        # Judge as printable or not

        printable = False
        if decodes:
            assert len(decodes) == 1, (decodes, data)
            printable = decodes.isprintable()

            # Require the Caller to route Printable Chars elsewhere till Head chosen

            assert head or not printable, (decodes, data, head, printable)

        # Take first 1 or 2 or 3 Bytes into Esc Sequences
        #
        #   ⎋ Esc  # ⎋⎋ Esc Esc
        #   ⎋O SS3  # ⎋⎋O Esc SS3
        #   ⎋[ CSI  # ⎋⎋[ Esc CSI
        #

        head_plus = bytes(head + data)
        if head_plus in (b"\033", b"\033\033", b"\033\033O", b"\033\033[", b"\033O", b"\033["):
            head.extend(data)
            return b""  # takes first 1 or 2 Bytes into Esc Sequences

        # Take & close 1 Unprintable Char as Head

        if not head:
            if not printable:
                head.extend(data)
                self.closed = True
                return b""  # takes & closes Unprintable Chars or 1..4 Undecodable Bytes

            # takes \b \t \n \r \x7f etc

        # Take & close 1 Escaped Printable Decoded Char,
        # as Tail after Head of  ⎋ Esc  ⎋⎋ Esc Esc  ⎋O SS3  ⎋⎋O Esc SS3

        if bytes(head) in (b"\033", b"\033\033", b"\033\033O", b"\033O"):
            if printable:
                tail.extend(data)
                self.closed = True
                return b""  # takes & closes 1 Escaped Printable Decoded Char

            # Take & close Unprintable Chars or 1..4 Undecodable Bytes, as Escaped Tail

            tail.extend(data)  # todo: test of Unprintable/ Undecodable after ⎋O SS3
            self.closed = True
            return b""  # takes & closes Unprintable Chars or 1..4 Undecodable Bytes

            # does take ⎋\x10 ⎋\b ⎋\t ⎋\n ⎋\r ⎋\x7f etc

            # doesn't take bytes([0x80 | 0x0B]) as meaning b"\033\x5b" CSI ⎋[
            # doesn't take bytes([0x80 | 0x0F]) as meaning b"\033\x4f" SS3 ⎋O

        # Decline 1..4 Undecodable Bytes, when escaped by CSI or Esc CSI

        if not decodes:
            return data  # declines 1..4 Undecodable Bytes

        decode = decodes
        assert len(decodes) == 1, (decodes, data)
        assert data == decode.encode(), (data, decodes)

        # Take or don't take 1 Decodable Char into CSI or Esc CSI Sequence

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

        assert CSI == "\033[", (CSI,)  # ⎋[
        if not head.startswith(b"\033\033["):  # ⎋⎋[ Esc CSI
            assert head.startswith(b"\033["), (head,)  # ⎋[ CSI

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
    "\033": "⎋",  # Esc  # Meta  # includes ⎋Spacebar ⎋Tab ⎋Return ⎋Delete without ⌥
    "\033" "\x01": "⌥⇧Fn←",  # ⎋⇧Fn←   # coded with ⌃A
    "\033" "\x03": "⎋FnReturn",  # coded with ⌃C  # not ⌥FnReturn
    "\033" "\x04": "⌥⇧Fn→",  # ⎋⇧Fn→   # coded with ⌃D
    "\033" "\x08": "⎋⌃Delete",  # ⎋⌃Delete  # coded with ⌃H  # aka \b
    "\033" "\x0b": "⌥⇧Fn↑",  # ⎋⇧Fn↑   # coded with ⌃K
    "\033" "\x0c": "⌥⇧Fn↓",  # ⎋⇧Fn↓  # coded with ⌃L  # aka \f
    "\033" "\x10": "⎋⇧Fn",  # ⎋ Meta ⇧ Shift of FnF1..FnF12  # not ⌥⇧Fn  # coded with ⌃P
    "\033" "\033": "⎋⎋",  # Meta Esc  # not ⌥⎋
    "\033" "\033O" "A": "⌃⌥↑",  # ESC SS3 ⇧A  # gCloud Shell
    "\033" "\033O" "B": "⌃⌥↓",  # ESC SS3 ⇧B  # gCloud Shell
    "\033" "\033O" "C": "⌃⌥→",  # ESC SS3 ⇧C  # gCloud Shell
    "\033" "\033O" "D": "⌃⌥←",  # ESC SS3 ⇧D  # gCloud Shell
    "\033" "\033[" "3;5~": "⎋⌃FnDelete",  # ⌥⌃FnDelete
    "\033" "\033[" "A": "⌥↑",  # CSI 04/01 Cursor Up (CUU)  # Option-as-Meta  # gCloud Shell
    "\033" "\033[" "B": "⌥↓",  # CSI 04/02 Cursor Down (CUD)  # Option-as-Meta  # gCloud Shell
    "\033" "\033[" "C": "⌥→",  # CSI 04/03 Cursor [Forward] Right (CUF_X)  # gCloud Shell
    "\033" "\033[" "D": "⌥←",  # CSI 04/04 Cursor [Back] Left (CUB_X)  # gCloud Shell
    "\033" "\033[" "Z": "⎋⇧Tab",  # ⇤  # CSI 05/10 CBT  # not ⌥⇧Tab
    "\033" "\x28": "⎋FnDelete",  # not ⌥FnDelete
    "\033O" "P": "F1",  # SS3 ⇧P
    "\033O" "Q": "F2",  # SS3 ⇧Q
    "\033O" "R": "F3",  # SS3 ⇧R
    "\033O" "S": "F4",  # SS3 ⇧S
    "\033[" "15~": "F5",  # Esc 07/14 is LS1R, but CSI 07/14 is unnamed
    "\033[" "17~": "F6",  # ⌥F1  # ⎋F1
    "\033[" "18~": "F7",  # ⌥F2  # ⎋F2
    "\033[" "19~": "F8",  # ⌥F3  # ⎋F3
    "\033[" "1;2C": "⇧→",  # CSI 04/03 Cursor [Forward] Right (CUF_YX) Y=1 X=2  # macOS
    "\033[" "1;2D": "⇧←",  # CSI 04/04 Cursor [Back] Left (CUB_YX) Y=1 X=2  # macOS
    "\033[" "20~": "F9",  # ⌥F4  # ⎋F4
    "\033[" "21~": "F10",  # ⌥F5  # ⎋F5
    "\033[" "23~": "F11",  # ⌥F6  # ⎋F6  # macOS takes F11
    "\033[" "24~": "F12",  # ⌥F7  # ⎋F7
    "\033[" "25~": "⇧F5",  # ⌥F8  # ⎋F8
    "\033[" "26~": "⇧F6",  # ⌥F9  # ⎋F9
    "\033[" "28~": "⇧F7",  # ⌥F10  # ⎋F10
    "\033[" "29~": "⇧F8",  # ⌥F11  # ⎋F11
    "\033[" "31~": "⇧F9",  # ⌥F12  # ⎋F12
    "\033[" "32~": "⇧F10",
    "\033[" "33~": "⇧F11",
    "\033[" "34~": "⇧F12",
    "\033[" "3;2~": "⇧FnDelete",
    "\033[" "3;5~": "⌃FnDelete",
    "\033[" "3~": "FnDelete",
    "\033[" "5~": "⇧Fn↑",  # macOS
    "\033[" "6~": "⇧Fn↓",  # macOS
    "\033[" "A": "↑",  # CSI 04/01 Cursor Up (CUU)  # also ⌥↑ macOS
    "\033[" "B": "↓",  # CSI 04/02 Cursor Down (CUD)  # also ⌥↓ macOS
    "\033[" "C": "→",  # CSI 04/03 Cursor Right [Forward] (CUF)  # also ⌥→ macOS
    "\033[" "D": "←",  # CSI 04/04 Cursor [Back] Left (CUB)  # also ⌥← macOS
    "\033[" "F": "⇧Fn→",  # macOS  # CSI 04/06 Cursor Preceding Line (CPL)
    "\033[" "H": "⇧Fn←",  # macOS  # CSI 04/08 Cursor Position (CUP)
    "\033[" "Z": "⇧Tab",  # ⇤  # CSI 05/10 Cursor Backward Tabulation (CBT)
    "\033" "b": "⌥←",  # ⎋B  # ⎋←  # Emacs M-b Backword-Word  # macOS
    "\033" "f": "⌥→",  # ⎋F  # ⎋→  # Emacs M-f Forward-Word  # macOS
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


def _kch_to_kcap_(t: str) -> str:  # noqa C901
    """Choose a Key Cap to speak of 1 Char read from the Keyboard"""

    o = ord(t)

    option_kchars_spaceless = OPTION_KCHARS_SPACELESS  # '∂' for ⌥D
    option_kstr_by_1_kchar = OPTION_KSTR_BY_1_KCHAR  # 'é' for ⌥EE
    kcap_by_kchars = KCAP_BY_KCHARS  # '\x7F' for 'Delete'

    # Show more Key Caps than US-Ascii mentions

    if t in kcap_by_kchars.keys():  # Mac US Key Caps for Spacebar, F12, etc
        s = kcap_by_kchars[t]  # '⌃Spacebar', 'Return', 'Delete', etc

    elif t in option_kstr_by_1_kchar.keys():  # Mac US Option Accents
        s = option_kstr_by_1_kchar[t]

    elif t in option_kchars_spaceless:  # Mac US Option Key Caps
        s = _spaceless_ch_to_option_kstr_(t)

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

    elif "A" <= t <= "Z":  # printable Upper Case English
        s = "⇧" + chr(o)  # shifted Key Cap '⇧A' from b'A'

    elif "a" <= t <= "z":  # printable Lower Case English
        s = chr(o ^ 0x20)  # plain Key Cap 'A' from b'a'

    # Test that no Keyboard sends the C1 Control Bytes, nor the Quasi-C1 Bytes

    elif o in range(0x80, 0xA0):  # C1 Control Bytes
        s = repr(bytes([o]))  # b'\x80'
    elif o == 0xA0:  # 'No-Break Space'
        s = "⌥Spacebar"
        assert False, (o, t)  # unreached because 'kcap_by_kchars'
    elif o == 0xAD:  # 'Soft Hyphen'  # near to a C1 Control Byte
        s = repr(bytes([o]))  # b'\xad'

    # Show the US-Ascii or Unicode Char as if its own Key Cap

    else:
        assert o < 0x11_0000, (o, t)
        s = chr(o)  # '!', '¡', etc

        # todo: have we fuzzed b"\xA1" .. FF vs "\u00A1" .. 00FF like we want?

    # Succeed, but insist that Blank Space is never a Key Cap

    assert s.isprintable(), (s, o, t)  # has no \x00..\x1f, \x7f, \xa0, \xad, etc
    assert " " not in s, (s, o, t)

    return s

    # '⌃L'  # '⇧Z'


def _spaceless_ch_to_option_kstr_(t: str) -> str:
    """Convert to Mac US Option Key Caps from any of OPTION_KCHARS_SPACELESS"""

    option_kchars = OPTION_KCHARS  # '∂' for ⌥D

    index = option_kchars.index(t)
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
        tlog.flush()


#
# Mention the unmentioned skidded names defined by this File, to please PyLance
#


_ = _ICF_RIS_, _ICF_CUP_, _SM_XTERM_ALT_, _RM_XTERM_MAIN_


#
# Run from the Shell Command Line, if not imported
#


if __name__ == "__main__":
    try_main_else_repl()
    # print("__main__: after try_main_else_repl", file=sys.stderr)


# todo8: Help people whose /usr/bin/python3 runs better than their /usr/local/bin/python3
# todo8: TUI for:  rgb = 104 - 0x10; print(rgb // 36, (rgb // 6) % 6, rgb % 6)
# todo8: TUI for:  print(0x10 + (2 * 36 + 2 * 6 + 4))


# 3456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789


# posted as:  https://github.com/pelavarre/xshverb/blob/main/bin/plus.py
# copied from:  git clone https://github.com/pelavarre/xshverb.git
