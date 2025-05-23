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


# posted as:  https://github.com/pelavarre/xshverb/blob/main/Makefile
# copied from:  git clone https://github.com/pelavarre/xshverb.git
