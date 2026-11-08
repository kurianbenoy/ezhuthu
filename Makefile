.PHONY: help build test bite proofs clean

PY := python3
PIP ?= .venv/bin/pip

help:
	@echo "targets: venv build [style...] test proofs otf|webfonts|all clean"

venv:
	test -d .venv || { $(PY) -m venv .venv; .venv/bin/pip install -U pip; }
	.venv/bin/pip install ufoLib2 ufo2ft fonttools fontFeatures munch PyYAML uharfbuzz freetype-py pillow booleanOperations Brotli

build: venv
	.venv/bin/python tools/build.py

otf: venv
	.venv/bin/python -c "import os,sys; sys.path.insert(0,'tools'); from build import compile_fonts; compile_fonts(['Regular'], ('otf','woff2'))"

test: build
	.venv/bin/python tests/test_font.py

proofs: test
	.venv/bin/python tools/ab.py proofs/ab.png
	.venv/bin/python tools/render.py fonts/Ezhuthu-Regular.ttf "മലയാളത്തിന്റെ ലിപി എഴുത്താണിത്" proofs/ezh_malayalam.png --size 72 --baseline

clean:
	rm -rf sources/ufo fonts/*/*.tmp
