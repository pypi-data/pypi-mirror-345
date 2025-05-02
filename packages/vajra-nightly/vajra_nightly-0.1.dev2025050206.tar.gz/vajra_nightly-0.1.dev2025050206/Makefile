.PHONY: help lint lint/black lint/isort lint/autoflake lint/pyright lint/cpplint lint/clang-format lint/codespell \
       format format/black format/isort format/autoflake format/clang-format \
       docs docs/build docs/clean \
       build build/native build/native_test \
       test test/performance test/correctness test/functional test/pyunit test/ctest test/unit \
       test_reports

.DEFAULT_GOAL := help

CPP_FILES := $(shell find csrc -type f \( -name "*.cpp" -o -name "*.h" \) -not -path "*/third_party/*")

# Use environment variables if defined, otherwise use defaults
ifdef VAJRA_CI_CUDA_VERSION
  CUDA_MAJOR := $(shell echo $(VAJRA_CI_CUDA_VERSION) | cut -d. -f1)
  CUDA_MINOR := $(shell echo $(VAJRA_CI_CUDA_VERSION) | cut -d. -f2)
  CUDA_VERSION := cu$(CUDA_MAJOR)$(CUDA_MINOR)
else
  CUDA_VERSION := cu124
endif

TORCH_VERSION ?= $(if $(VAJRA_CI_TORCH_VERSION),$(VAJRA_CI_TORCH_VERSION),2.4)

# Build type configuration
BUILD_TYPE ?= Debug

lint/black: ## check style with black
	black --check vajra test

lint/isort: ## check style with isort
	isort --check-only --profile black vajra test

lint/autoflake: ## check for unused imports
	autoflake --recursive --remove-all-unused-imports --check vajra test

lint/pyright: ## run type checking
	pyright

lint/cpplint:
	cpplint \
	--recursive \
	--exclude=csrc/third_party \
	--exclude=csrc/include/vajra/kernels \
	--exclude=csrc/vajra/kernels \
	--filter="-build/include_what_you_use,-whitespace/parens,-whitespace/braces,-runtime/references" \
	csrc

lint/clang-format: ## check C++ format with clang-format
	clang-format -n -Werror $(CPP_FILES)

lint/codespell:
	codespell \
	--skip './csrc/third_party/**,./csrc/test/testdata/**,./build/**,*.log,./env*/**,./docs/_build/**,./test_reports/**' \
	-L inout

lint: lint/isort lint/black lint/autoflake lint/codespell lint/pyright lint/clang-format lint/cpplint ## lint code

format/black: ## format code with black
	black vajra test

format/isort: ## format code with isort
	isort --profile black vajra test

format/autoflake: ## remove unused imports
	autoflake --in-place --recursive --remove-all-unused-imports vajra test

format/clang:
	clang-format -i $(CPP_FILES)

format: format/isort format/autoflake format/black format/clang ## format code

docs: docs/build ## build documentation

docs/build: ## build documentation
	make -C docs html

docs/clean: ## clean documentation
	make -C docs clean

build/native:
	mkdir -p build && cd build \
	&& cmake -G Ninja -DCMAKE_BUILD_TYPE=$(BUILD_TYPE) -DVAJRA_PYTHON_EXECUTABLE=`which python3` -DCMAKE_LIBRARY_OUTPUT_DIRECTORY=../vajra .. \
	&& cmake --build . --target default

build/native_incremental:
	mkdir -p build && cd build \
	&& cmake --build . --target default

build/native_test:
	mkdir -p build && cd build \
	&& cmake -G Ninja -DCMAKE_BUILD_TYPE=${BUILD_TYPE} -DVAJRA_PYTHON_EXECUTABLE=`which python3` -DCMAKE_LIBRARY_OUTPUT_DIRECTORY=../vajra .. \
	&& cmake --build . --target all_tests

build/native_test_incremental:
	mkdir -p build && cd build \
	&& cmake --build . --target all_tests

build/wheel:
	python -m build --no-isolation --wheel
	python -m build --no-isolation --sdist

build/dependencies:
	pip install -r requirements.txt --extra-index-url https://flashinfer.ai/whl/$(CUDA_VERSION)/torch$(TORCH_VERSION)/ \

build: build/dependencies ## build the project
	pip install -e . --extra-index-url https://flashinfer.ai/whl/$(CUDA_VERSION)/torch$(TORCH_VERSION)/

# Pytest commands use configuration from pytest.ini
test/performance: ## run performance tests
	pytest -m performance --junitxml=test_reports/performance-results.xml

test/correctness: ## run correctness tests
	@echo "correctness tests not yet implemented!\n"

test/functional: test/performance test/correctness ## run all functional tests

# Create test_reports directory
test_reports:
	mkdir -p test_reports

test/pyunit: test_reports ## run python unit tests with JUnit XML and coverage reporting
	pytest -m "unit" --junitxml=test_reports/pytest-results.xml --cov=vajra --cov-report=xml:test_reports/python_coverage.xml --cov-report=html:test_reports/python_coverage_html

test/pyintegration: test_reports ## run python integration tests with JUnit XML and coverage reporting
	pytest -m "integration" --junitxml=test_reports/pytest-results.xml --cov=vajra --cov-report=xml:test_reports/python_coverage.xml --cov-report=html:test_reports/python_coverage_html

test/ctest: test_reports build/native_test ## run ctest tests with JUnit XML and coverage reporting
	cd build \
	&& ctest -R "kernel_tests|native_tests" --output-on-failure --timeout 180 --test-dir ../build --output-junit ../test_reports/ctest-results.xml

test/unit: test/pyunit test/ctest

test/integration: test/pyintegration

test: test/unit test/integration test/functional ## run all tests

help: ## show this help
	@grep -E '^[a-zA-Z_/]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

