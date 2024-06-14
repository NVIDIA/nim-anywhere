
SHELL=/bin/bash

.PHONY: clean update serve stop status
.SILENT: update serve stop status
.ONESHELL: update serve stop status

all: clean update build

clean:
	rm -rf ../README.md ../.static _build

# render all dynamic documentation. Convert .md.py to .md.
render:
	# find all executable python files
	all_scripts=$$(find . -maxdepth 1 -perm -111 -type f -name '*.md.py')

	# run each .py file found and save output to .md file
	for script in $$all_scripts; do
		echo "Running $$script"
		fname=$(basename $${script::-3})

		echo "↪ " $$fname
		$$script > $$fname

		echo ""
	done

# build the html docs. convert .md to .html
build: ../README.md _build/index.html _build/_static
../README.md:
	file_list=$$(ls *.md | grep -v README.md); \
	pandoc \
		--from markdown --to gfm \
		--toc -sN \
		-o ../README.md \
		--extract-media=.static \
		--self-contained \
		$$file_list
	mv .static ..
_build/index.html:
	mkdir -p _build
	file_list=$$(ls *.md | grep -v README.md); \
	export MERMAID_FILTER_FORMAT=png; export MERMAID_FILTER_WIDTH=1200; \
	pandoc \
		--from=markdown --to=html \
		--template=.template.html \
		--filter=mermaid-filter \
		--standalone --toc \
		--metadata title="User Guide" \
		-o _build/index.html \
		$$file_list
_build/_static:
	cp -rav ./_static _build/_static

# force render and build the docs
update: clean render build

#  manage a local webserver for reading docs
serve: all
	cd _build
	python3 -m http.server 7777
stop:
	kill -2 $$(ps -eo pid,command  | grep -P "^\s*\d+\s+python3 -m http.server 7777" | awk '{print $$1}') 2> /dev/null || true
status:
	curl localhost:7777 &> /dev/null
