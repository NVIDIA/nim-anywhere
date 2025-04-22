.PHONY: build
build: dist/live_labs-0.0.1-py3-none-any.whl dist/live_labs-0.0.1.tar.gz
dist/live_labs-0.0.1-py3-none-any.whl dist/live_labs-0.0.1.tar.gz:
	python3 -m build

.venv:
	python3 -m venv .venv
	cd .venv/bin && ./pip install -e ../..[build]

clean:
	rm -rf *.egg-info build dist
clean-venv:
	rm -rf .venv
clean-all: clean clean-venv
