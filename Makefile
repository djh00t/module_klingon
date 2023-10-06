# Makefile for klingon_serial Python package

# Variables
TWINE_USERNAME ?= __token__
TEST_TWINE_PASSWORD ?= $(TEST_PYPI_USER_AGENT)
PYPI_TWINE_PASSWORD ?= $(PYPI_USER_AGENT)

# Clean up build files
clean:
	rm -rf build dist klingon_serial.egg-info .mypy_cache .pytest_cache klingon/__pycache__ tests/__pycache__

## check-packages: Check for required pip packages and requirements.txt, install if missing
check-packages:
	@echo "Checking for required pip packages and requirements.txt..."
	@if [ ! -f requirements.txt ]; then \
		echo "requirements.txt not found. Please add it to the project root."; \
		exit 1; \
	fi
	@echo "Installing missing packages from requirements.txt..."
	@pip install -r requirements.txt
	@echo "Installing twine and wheel..."
	@pip install twine wheel

## sdist: Create a source distribution package
sdist: clean
	python setup.py sdist

## wheel: Create a wheel distribution package
wheel: clean
	python setup.py sdist bdist_wheel

## upload-test: Run tests, if they pass update version number, echo it to console and upload the distribution package to TestPyPI
upload-test: test wheel
	@echo "Uploading Version $NEW_VERSION to TestPyPI..."
	twine upload --repository-url https://test.pypi.org/legacy/ --username $(TWINE_USERNAME) --password $(TEST_TWINE_PASSWORD) dist/*

## upload: Run tests, if they pass update version number and upload the distribution package to PyPI
upload: test wheel
	@echo "Uploading Version $NEW_VERSION to PyPI..."
	twine upload --username $(TWINE_USERNAME) --password $(PYPI_TWINE_PASSWORD) dist/*

## install: Install the package locally
install:
	pip install -e .


## uninstall: Uninstall the local package
uninstall:
	pip uninstall get-user-agent

# Run tests
test:
	@echo "Running unit tests..."
	pytest tests/



## update-version: Read the version number from VERSION file, it will look like A.B.C Increment the third (C) number by 1 and write it back to the VERSION file
update-version:
	@echo "Updating version number..."
	@NEW_VERSION=$$(awk -F. '{print $$1"."$$2"."$$3+1}' VERSION); \
	echo $$NEW_VERSION > VERSION; \
	@sed -i '' "s/version='[0-9]*\.[0-9]*\.[0-9]*'/version='$NEW_VERSION'/g" setup.py; \
	echo "New version number is $$NEW_VERSION"

.PHONY: clean check-packages sdist wheel upload-test upload install uninstall test update-version