.PHONY: help venv kamalam legacy test proofs specimen serve clean distclean

PY := .venv/bin/python
PIP := .venv/bin/pip

help:
	@echo "targets:"
	@echo "  venv      create .venv and install build/proof dependencies"
	@echo "  kamalam   build the variable Ezhuthu Kamalam family + Spectrum"
	@echo "  legacy    rebuild the v0.2 parametric draft (legacy/fonts)"
	@echo "  test      run shaping, variation and colour tests"
	@echo "  proofs    render the specimen PNGs and the HTML specimen"
	@echo "  pdf       print the specimen to proofs/EzhuthuKamalam-Specimen.pdf"
	@echo "  qa        run fontbakery on Regular and Bold (see NOTES.md)"
	@echo "  specimen  alias for proofs"
	@echo "  serve     serve specimen/ on http://localhost:8000"
	@echo "  clean     remove generated UFOs and masters"
	@echo "  distclean remove generated fonts and proofs too"

venv:
	test -d .venv || { python3 -m venv .venv; $(PIP) install -U pip; }
	$(PIP) install -q ufoLib2 ufo2ft fonttools fontFeatures munch PyYAML \
		uharfbuzz freetype-py pillow booleanOperations Brotli scipy

kamalam: venv
	$(PY) tools/kamalam.py all

legacy: venv
	$(PY) tools/build.py

test: venv kamalam legacy
	$(PY) tests/test_kamalam.py
	$(PY) tests/test_font.py legacy/fonts/Ezhuthu-Regular.ttf

proofs: kamalam
	$(PY) tools/specimen.py
	$(PY) tools/specimen_html.py

pdf: proofs
	$(PIP) install -q playwright
	$(PY) -m playwright install chromium
	$(PY) tools/pdf.py

qa: kamalam
	$(PIP) install -q fontbakery
	$(PY) -m fontbakery check-universal fonts/EzhuthuKamalam-Regular.ttf \
		--no-progress -x opentype/fvar/regular_coords_correct -x alt_caron
	$(PY) -m fontbakery check-universal fonts/EzhuthuKamalam-Bold.ttf \
		--no-progress -x opentype/fvar/regular_coords_correct -x alt_caron \
		-x opentype/fsselection -x opentype/mac_style

specimen: proofs
	@echo "open specimen/index.html in a browser (or run: make serve)"

serve: specimen
	$(PY) -m http.server 8000 --directory specimen

clean:
	rm -rf sources/ufo sources/masters

distclean: clean
	rm -rf fonts/*.ttf fonts/*.otf fonts/*.woff2 proofs/kamalam_*.png
