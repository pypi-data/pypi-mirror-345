################################################################################
#  Makefile for firestarter (jasmit_firestarter on PyPi)
################################################################################

include .env

app_name := 'firestarter'

################################################################################

.PHONY: test
test: ## Test code with pytest 👍
	@echo "🚀 Testing code: Running pytest..."
	@uv run python -m pytest 

.PHONY: run 
run: ## Uh... 😁  
	@echo "🚀 Running FireStarter..."
	@uv run src/firestarter/firestarter.py -e devl

.PHONY: clean
clean: ## Clean up crap from previous builds
	@echo "🚀 Removing any crap from previous builds..."
	@rm logs/*.log 2>/dev/null
	@- rm -rf src/firestarter/__pycache__
	@uv run python -c "import shutil; import os; shutil.rmtree('dist') if os.path.exists('dist') else None"

.PHONY: build
build: ## Build package for distrbution
	@echo "🚀 Building the package for distribution..."
	@uvx --from build pyproject-build --installer uv

.PHONY: publish
publish: ## Publish release to PyPi
	@echo "🚀 Publishing: Dry run..."
	@uvx --from build pyproject-build --installer uv
	@echo "🚀 Publishing..."
	@uvx twine upload --repository-url https://upload.pypi.org/legacy/ dist/*

.PHONY: docs-test
docs-test: ## Test documentation build  👍
	@uv run mkdocs build -s

.PHONY: docs-publish
docs-publish: ## Publish documentation
	@echo "🚀 Generating the PDF documentation..."
	@pandoc --toc=true -o '/Volumes/SharedSpace/Users/jeff/Project Documentation/Active/FireStarter System Guide.pdf' 'docs/FireStarter System Guide.md'
	@pandoc --toc=true -o "/Volumes/SharedSpace/Users/jeff/Project Documentation/Active/FireStarter User's Guide.pdf" "docs/FireStarter User's Guide.md"
	@uv run mkdocs serve

################################################################################

.PHONY: help
help:
	@uv run python -c "import re; \
	[[print(f'\033[36m{m[0]:<20}\033[0m {m[1]}') for m in re.findall(r'^([a-zA-Z_-]+):.*?## (.*)$$', open(makefile).read(), re.M)] for makefile in ('$(MAKEFILE_LIST)').strip().split()]"

.DEFAULT_GOAL := help

################################################################################
# 👋
# 👍
# 😁.
# 🚀
