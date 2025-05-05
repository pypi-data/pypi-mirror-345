###
#  general configuration of the makefile itself
###
SHELL := /bin/bash
.DEFAULT_GOAL := help

PROJECTNAME := pyproject2ebuild

.PHONY: help
help:
	@mh -f $(MAKEFILE_LIST) $(target) || echo "Please install mh from https://github.com/oz123/mh/releases/latest"
ifndef target
	@(which mh > /dev/null 2>&1 && echo -e "\nUse \`make help target=foo\` to learn more about foo.")
endif

.PHONY: build
build: ## build the program
	python -m build

.PHONY: install 
install:  ## install the project
	pip install -e .

.PHONY: test 
test: ## run the tests
	pytest -v tests/

.PHONY: clean 
clean:  ## clean the build directory
	rm -fRv dist
	rm -Rv src/$(PROJECTNAME).egg-info/

