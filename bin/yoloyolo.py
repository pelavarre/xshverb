#!/usr/bin/env python3

r"""
usage: yoloyolo.py --

do what's popular now

examples:
  bin/yoloyolo.py --yolo
"""

# code reviewed by People, Black, Flake8, MyPy-Strict, & PyLance-Standard


from __future__ import annotations  # backports new datatype syntaxes into old Pythons

import os
import pdb
import signal
import sys
import termios
import types

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

    when = termios.TCSADRAIN  # undoes tty.setraw
    attributes = with_tcgetattr
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

    assert sys.argv[1:], sys.argv
    assert "--yolo".startswith(sys.argv[1]) and sys.argv[1].startswith("--"), sys.argv

    # Emulate having imported the enclosing Module as ./yoloyolo.py

    assert "yoloyolo" not in sys.modules.keys()
    yoloyolo = sys.modules["__main__"]
    sys.modules["yoloyolo"] = yoloyolo

    # Land the Repl into a small new Module of its own

    module = types.ModuleType("yoloyolo.repl")
    sys.modules["__main__"] = module

    d = vars(module)

    d["__file__"] = __file__  # almost correct
    d["__main__"] = module
    d["yoloyolo"] = yoloyolo

    d["passme"] = passme
    d["failme"] = failme

    # Launch the Py Repl at Process Exit, as if:  python3 -i -c ''

    os.environ["PYTHONINSPECT"] = str(True)

    print("To get started, press Return after typing:  passme(); failme()", file=sys.stderr)


def passme() -> None:
    """Pass when called"""

    pass


def failme() -> None:
    """Fail when called"""

    countdown = 54321
    _ = countdown

    raise Exception("Intentionally Left Mostly Blank")


#
# Run from the Shell Command Line, if not imported
#


if __name__ == "__main__":
    main()


_ = """

Example Input

    bin/yoloyolo.py --

    passme()

    dir()  # small, by our design
    dir(yoloyolo)  # large, all of our imports here, etc

    failme()  # raises Exception and launches the Pdb-Pm Post-Mortem Debugger
    dir()  # just our own 'countdown' and '_' examples
    p countdown
    pass

Example Output

    % bin/yoloyolo.py --
    To get started, press Return after typing:  passme(); failme()
    >>>

    >>> passme()
    >>>
    >>> dir()
    ['__builtins__', '__doc__', '__file__', '__loader__', '__main__', '__name__', '__package__',
        '__spec__', 'failme', 'passme', 'yoloyolo']
    >>>
    >>> dir(yoloyolo)
    ['_', '__annotations__', '__builtins__', '__doc__', '__loader__', '__name__', '__package__',
        '__spec__', 'annotations', 'excepthook', 'failme', 'main', 'os', 'passme', 'pdb', 'signal',
         'sys', 'termios', 'types', 'with_exc_hook', 'with_stderr', 'with_tcgetattr']
    >>>

    >>> failme()
    Traceback (most recent call last):
    File "<python-input-7>", line 1, in <module>
        failme()
        ~~~~~~^^
    File ".../xshverb/bin/yoloyolo.py", line 128, in failme
        raise Exception("Intentionally Left Mostly Blank")
    Exception: Intentionally Left Mostly Blank
    >>> pdb.pm()
    > .../xshverb/bin/yoloyolo.py(128)failme()
    -> raise Exception("Intentionally Left Mostly Blank")
    (Pdb)

    (Pdb) dir()
    ['_', 'countdown']
    (Pdb) p countdown
    54321
    (Pdb) pass
    (Pdb)
    (Pdb)

"""


# 3456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789


# posted as:  https://github.com/pelavarre/xshverb/blob/main/bin/yoloyolo.py
# copied from:  git clone https://github.com/pelavarre/xshverb.git
