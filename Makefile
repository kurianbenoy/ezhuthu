.PHONY: help venv kamalam multiscript legacy test proofs specimen serve clean distclean \
	pdf pdf-multiscript qa qa-multiscript

PY := .venv/bin/python
PIP := .venv/bin/pip

help:
	@echo "targets:"
	@echo "  venv      create .venv and install build/proof dependencies"
	@echo "  kamalam   build the variable Ezhuthu Kamalam family + Spectrum"
	@echo "  multiscript build Devanagari, Tamil, Telugu and Kannada families"
	@echo "  legacy    rebuild the v0.2 parametric draft (legacy/fonts)"
	@echo "  test      run shaping, variation and colour tests"
	@echo "  proofs    render the specimen PNGs and the HTML specimen"
	@echo "  pdf       print the specimen to proofs/EzhuthuKamalam-Specimen.pdf"
	@echo "  pdf-multiscript print the multiscript specimen to PDF"
	@echo "  qa        run fontbakery on the Malayalam Regular and Bold"
	@echo "  qa-multiscript run fontbakery on the four script families"
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

multiscript: venv
	$(PY) tools/multiscript.py

legacy: venv
	$(PY) tools/build.py

test: venv kamalam multiscript
	$(PY) tests/test_kamalam.py
	$(PY) tests/test_multiscript.py
	@if test -f legacy/fonts/Ezhuthu-Regular.ttf; then \
		$(PY) tests/test_font.py legacy/fonts/Ezhuthu-Regular.ttf; \
	else \
		echo "legacy font not built; run: make legacy"; \
	fi

proofs: kamalam multiscript
	$(PY) tools/specimen.py
	$(PY) tools/specimen_multiscript.py
	$(PY) tools/specimen_html.py
	$(PY) tools/specimen_multiscript_html.py

pdf: proofs
	$(PIP) install -q playwright
	$(PY) -m playwright install chromium
	$(PY) tools/pdf.py

pdf-multiscript: proofs
	$(PIP) install -q playwright
	$(PY) -m playwright install chromium
	$(PY) tools/pdf.py specimen/multiscript.html \
		proofs/EzhuthuKamalam-Multiscript-Specimen.pdf

qa: kamalam
	$(PIP) install -q fontbakery
	$(PY) -m fontbakery check-universal fonts/EzhuthuKamalam-Regular.ttf \
		--no-progress -x opentype/fvar/regular_coords_correct -x alt_caron
	$(PY) -m fontbakery check-universal fonts/EzhuthuKamalam-Bold.ttf \
		--no-progress -x opentype/fvar/regular_coords_correct -x alt_caron \
		-x opentype/fsselection -x opentype/mac_style

qa-multiscript: multiscript
	$(PIP) install -q fontbakery
	@for f in \
		fonts/EzhuthuKamalamDevanagari-Regular.ttf \
		fonts/EzhuthuKamalamDevanagari-Bold.ttf \
		fonts/EzhuthuKamalamTamil-Regular.ttf \
		fonts/EzhuthuKamalamTamil-Bold.ttf \
		fonts/EzhuthuKamalamTelugu-Regular.ttf \
		fonts/EzhuthuKamalamTelugu-Bold.ttf \
		fonts/EzhuthuKamalamKannada-Regular.ttf \
		fonts/EzhuthuKamalamKannada-Bold.ttf; do \
		echo "== $$f"; \
		$(PY) -m fontbakery check-universal "$$f" --no-progress \
			-x opentype/fvar/regular_coords_correct -x alt_caron \
			-x opentype/fsselection -x opentype/mac_style \
			2>&1 | grep -E '^    (FAIL|WARN|PASS):|^Total:' | tail -5; \
	done

specimen: proofs
	@echo "open specimen/index.html in a browser (or run: make serve)"

serve: specimen
	$(PY) -m http.server 8000 --directory specimen

clean:
	rm -rf sources/ufo sources/masters

distclean: clean
	rm -rf fonts/*.ttf fonts/*.otf fonts/*.woff2 proofs/kamalam_*.png \
		proofs/EzhuthuKamalam-Specimen.pdf \
		proofs/EzhuthuKamalam-Multiscript-Specimen.pdf
