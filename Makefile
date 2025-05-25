# xshverb/Makefile


default:
	@echo usage: make pips


pips:
	mkdir -p ~/.venvs/
	cd ~/.venvs/ && rm -fr pips
	cd ~/.venvs/ && python3 -m venv pips
	source ~/.venvs/pips/bin/activate && python3 -m pip install --upgrade pip
	:
	source ~/.pyvenvs/pips/bin/activate && pip install --upgrade black
	source ~/.pyvenvs/pips/bin/activate && pip install --upgrade flake8
	source ~/.pyvenvs/pips/bin/activate && pip install --upgrade flake8-import-order
	source ~/.pyvenvs/pips/bin/activate && pip install --upgrade mypy


smoke: black flake8
	:


black:
	~/.pyvenvs/black/bin/black \
		--line-length=101 \
			bin/

# --line-length=101  # my 2024 Window Width, over PyPi·Org Black Default of 89 != 80 != 71


flake8:
	~/.pyvenvs/flake8/bin/flake8 \
		--max-line-length=999 --max-complexity 15 --ignore=E203,E704,W503 \
			bin/

# --max-line-length=999  # Black max line lengths over Flake8 max line lengths
# --max-complexity 10  # limit how much McCabe Cyclomatic Complexity we accept
# --ignore=E203  # Black '[ : ]' rules over E203 whitespace before ':'
# --ignore=E704  # Black of typing.Protocol rules over E704 multiple statements on one line (def)
# --ignore=W503  # 2017 Pep 8 and Black over W503 line break before bin op


# posted as:  https://github.com/pelavarre/xshverb/blob/main/Makefile
# copied from:  git clone https://github.com/pelavarre/xshverb.git
