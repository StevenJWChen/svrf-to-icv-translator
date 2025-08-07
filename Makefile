# Makefile for SVRF to ICV Translator Project

.PHONY: help test demo install clean build upload docs validate

# Default target
help:
	@echo "SVRF to ICV Translator - Make Targets"
	@echo "===================================="
	@echo "help       - Show this help message"
	@echo "test       - Run comprehensive test suite"
	@echo "demo       - Run demonstration scripts"
	@echo "install    - Install package in development mode"
	@echo "clean      - Clean generated files"
	@echo "build      - Build distribution packages"
	@echo "upload     - Upload to PyPI (requires credentials)"
	@echo "docs       - Generate documentation"
	@echo "validate   - Validate project completion"

# Run comprehensive test suite
test:
	@echo "Running comprehensive test suite..."
	python test_suite.py

# Run demonstration scripts
demo:
	@echo "Running parser demo..."
	python demo_parser.py
	@echo ""
	@echo "Running translator demo..."
	python demo_translator.py

# Install package in development mode
install:
	pip install -e .

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	rm -f *.icv
	rm -rf __pycache__/
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

# Build distribution packages
build: clean
	@echo "Building distribution packages..."
	python setup.py sdist bdist_wheel

# Upload to PyPI (requires twine and credentials)
upload: build
	@echo "Uploading to PyPI..."
	twine upload dist/*

# Generate documentation
docs:
	@echo "Documentation available in README.md and other .md files"
	@ls -la *.md

# Validate project completion
validate:
	@echo "Validating project completion..."
	python test_suite.py
	@echo ""
	@echo "Checking file structure..."
	@ls -la *.py *.svrf *.md requirements.txt LICENSE setup.py
	@echo ""
	@echo "Testing main functionality..."
	python final_enhanced_translator.py test_comprehensive.svrf
	@echo ""
	@echo "🎯 Project validation complete!"

# Quick test with main files
quick-test:
	@echo "Quick functionality test..."
	python simple_svrf_parser.py example_drc_rules.svrf --layers --rules | head -20
	python svrf_to_icv_translator.py example_drc_rules.svrf --summary
	python final_enhanced_translator.py test_comprehensive.svrf | tail -10

# Show project statistics
stats:
	@echo "Project Statistics"
	@echo "=================="
	@echo "Python files: $(shell ls -1 *.py | wc -l)"
	@echo "SVRF files: $(shell ls -1 *.svrf | wc -l)" 
	@echo "Documentation files: $(shell ls -1 *.md | wc -l)"
	@echo "Total lines of code:"
	@wc -l *.py | tail -1
	@echo "Git status:"
	@git status --porcelain | wc -l | xargs echo "  Modified files:"