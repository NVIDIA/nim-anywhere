default: help

.PHONY: help
help: # Show help for each of the Makefile recipes.
	@echo "NIM Anywhere Makefile"
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

.PHONY: upgrade
upgrade: # Upgrade the Python dependencies to their latests versions
	bump --file /project/requirements.txt


