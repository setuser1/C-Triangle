.PHONY: run install test lint all build build-x86_64-elf binary clean full-install full-install-x86_64-elf uninstall

# Path to the canonical example (quoted where expanded to the shell so paths
# containing spaces work).
BASELINE := $(CURDIR)/test/baseline.ix
PYINSTALLER_NAME := hypotenuse
X86_64_ELF_NAME := hypotenuse-x86_64-elf
X86_64_ELF_IMAGE ?= python:3.14-slim
X86_64_ELF_PLATFORM ?= linux/amd64

# ---------------------------------------------------------------
# install: install Python dependencies needed to build and lint
# ---------------------------------------------------------------
install:
	pip install --quiet pyflakes pyinstaller

# ---------------------------------------------------------------
# run: compile the canonical example file and print the object graph
# ---------------------------------------------------------------
run: install
	python3 src/main.py -t "$(BASELINE)"

# ---------------------------------------------------------------
# test: compile eleven focused cases locally (not run by GitHub Actions)
# ---------------------------------------------------------------
test:
	@set -e; \
	for source in \
		test/baseline.ix \
		test/full_c11.ix \
		test/allocate_free.ix \
		test/base_string_ops.ix \
		test/test_at_match_funcname.ix \
		test/test_asm_param_len.ix \
		test/test_at_namespace.ix \
		test/test_no_libc_strings.ix \
		test/issue-109-selective-import-full.ix \
		test/window_rect.ix; do \
		echo "Checking $$source"; \
		PYTHONPATH=src/codegen python3 src/main.py "$$source" > /dev/null; \
	done
	@PYTHONPATH=src/codegen python3 src/main.py test/allocate_int_small_overflow.ix 2>&1 | grep -F "exceeds 1-byte int range" > /dev/null
	@echo "All eleven compiler cases passed"

# ---------------------------------------------------------------
# lint: catch syntax errors and undefined names across all source files
# ---------------------------------------------------------------
lint:
	python3 -m pyflakes src/lexer.py src/parser.py src/structure.py src/codegen.py src/assembler.py src/main.py


# ---------------------------------------------------------------
# all: install, lint, and build (used by CI)
# ---------------------------------------------------------------
all: install lint build

# ---------------------------------------------------------------
# build: build PyInstaller executable
# ---------------------------------------------------------------
build: install
	pyinstaller --onefile --name $(PYINSTALLER_NAME) --add-data "src:src" src/main.py

# ---------------------------------------------------------------
# build-x86_64-elf: cross-build Linux x86_64 ELF compiler from ARM64
# ---------------------------------------------------------------
build-x86_64-elf:
	docker run --rm --platform $(X86_64_ELF_PLATFORM) \
		-v "$(CURDIR):/work" \
		-w /work \
		$(X86_64_ELF_IMAGE) \
		sh -c 'apt-get update && apt-get install -y --no-install-recommends binutils && python -m pip install --quiet pyinstaller && pyinstaller --clean --onefile --name $(X86_64_ELF_NAME) --add-data "src:src" src/main.py'

# ---------------------------------------------------------------
# binary: run the compiled binary (must run 'make build' first)
# ---------------------------------------------------------------
binary: build
	./dist/hypotenuse

# ---------------------------------------------------------------
# container-build: build the compiler using Apple's container CLI (macOS Apple Silicon)
# ---------------------------------------------------------------
container-build:
	@if command -v container >/dev/null 2>&1; then \
		@echo "Building compiler with Apple's container CLI..."; \
		container build --platform linux/amd64 \
			-t "hypotenuse-container" \
			-f "$(CURDIR)/Containerfile" \
			"$(CURDIR)"; \
	else if command -v docker >/dev/null 2>&1; then \
		@echo "Using Docker as fallback (Apple container CLI not found). Consider installing https://github.com/apple/container for native Apple Silicon support."; \
		docker build \
			--platform linux/amd64 \
			-t "hypotenuse-container" \
			--file "$(CURDIR)/Containerfile" \
			"$(CURDIR)"; \
	else \
		echo "Error: Neither 'container' CLI (Apple Silicon) nor 'docker' found."; \
		echo "Install the Apple container tool from https://github.com/apple/container"; \
		exit 1; \
	fi

# ---------------------------------------------------------------
# container-run: run the containerized compiler
# ---------------------------------------------------------------
container-run:
	@if command -v container >/dev/null 2>&1; then \
		container run --platform linux/amd64 \
			--rm \
			-v "$(CURDIR):/work" \
			-w /work \
			hypotenuse-container "$@"; \
	else if command -v docker >/dev/null 2>&1; then \
		docker run --rm \
			--platform linux/amd64 \
			-v "$(CURDIR):/work" \
			-w /work \
			hypotenuse-container "$@"; \
	else \
		echo "Error: Neither 'container' CLI nor 'docker' found"; \
		exit 1; \
	fi


# ---------------------------------------------------------------
# container-lint: run linting inside the container
# ---------------------------------------------------------------
container-lint: container-build
	@if command -v container >/dev/null 2>&1; then \
		@echo "Running linting with Apple's container CLI..."; \
		container run --platform linux/amd64 \
			--rm \
			-v "$(CURDIR):/work" \
			-w /work \
			hypotenuse-container \
			sh -c "python3 -m pyflakes src/lexer.py src/parser.py src/structure.py src/codegen.py src/assembler.py src/main.py"; \
	else if command -v docker >/dev/null 2>&1; then \
		@echo "Using Docker as fallback..."; \
		docker run --rm \
			--platform linux/amd64 \
			-v "$(CURDIR):/work" \
			-w /work \
			hypotenuse-container \
			sh -c "python3 -m pyflakes src/lexer.py src/parser.py src/structure.py src/codegen.py src/assembler.py src/main.py"; \
	else \
		echo "Error: Neither 'container' CLI nor 'docker' found"; \
		exit 1; \
	fi

# ---------------------------------------------------------------
# clean: remove build artifacts
# ---------------------------------------------------------------
clean:
	rm -rf build dist *.spec __pycache__ release
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# ---------------------------------------------------------------
# full-install: install the binary to system and set up PLIBS folder
# ---------------------------------------------------------------
full-install: build
	@if [ -w /usr/local/bin ]; then \
		cp dist/hypotenuse /usr/local/bin/hypotenuse; \
		chmod +x /usr/local/bin/hypotenuse; \
		echo "Installed to /usr/local/bin/hypotenuse"; \
		sudo mkdir -p /usr/lib/PLIBS; \
		echo "Created /usr/lib/PLIBS"; \
		sudo cp -r iodine /usr/lib/PLIBS/; \
		echo "Copied iodine folder to /usr/lib/PLIBS"; \
	else \
		mkdir -p ~/.local/bin; \
		cp dist/hypotenuse ~/.local/bin/hypotenuse; \
		chmod +x ~/.local/bin/hypotenuse; \
		echo "Installed to ~/.local/bin/hypotenuse"; \
		mkdir -p ~/.local/lib/PLIBS; \
		echo "Created ~/.local/lib/PLIBS"; \
		cp -r iodine ~/.local/lib/PLIBS/; \
		echo "Copied iodine folder to ~/.local/lib/PLIBS"; \
		echo "Add ~/.local/bin to your PATH if not already present"; \
	fi

# ---------------------------------------------------------------
# full-install-x86_64-elf: install the cross-built Linux x86_64 ELF compiler
# ---------------------------------------------------------------
full-install-x86_64-elf: build-x86_64-elf
	@if [ -w /usr/local/bin ]; then \
		cp dist/$(X86_64_ELF_NAME) /usr/local/bin/hypotenuse; \
		chmod +x /usr/local/bin/hypotenuse; \
		echo "Installed Linux x86_64 ELF compiler to /usr/local/bin/hypotenuse"; \
		sudo mkdir -p /usr/lib/PLIBS; \
		echo "Created /usr/lib/PLIBS"; \
		sudo cp -r iodine /usr/lib/PLIBS/; \
		echo "Copied iodine folder to /usr/lib/PLIBS"; \
	else \
		mkdir -p ~/.local/bin; \
		cp dist/$(X86_64_ELF_NAME) ~/.local/bin/hypotenuse; \
		chmod +x ~/.local/bin/hypotenuse; \
		echo "Installed Linux x86_64 ELF compiler to ~/.local/bin/hypotenuse"; \
		mkdir -p ~/.local/lib/PLIBS; \
		echo "Created ~/.local/lib/PLIBS"; \
		cp -r iodine ~/.local/lib/PLIBS/; \
		echo "Copied iodine folder to ~/.local/lib/PLIBS"; \
		echo "Add ~/.local/bin to your PATH if not already present"; \
	fi

# ---------------------------------------------------------------
# uninstall: remove the binary from system
# ---------------------------------------------------------------
uninstall:
	@if [ -f /usr/local/bin/hypotenuse ]; then \
		rm /usr/local/bin/hypotenuse; \
		echo "Removed /usr/local/bin/hypotenuse"; \
	elif [ -f ~/.local/bin/hypotenuse ]; then \
		rm ~/.local/bin/hypotenuse; \
		echo "Removed ~/.local/bin/hypotenuse"; \
	else \
		echo "hypotenuse not found in /usr/local/bin or ~/.local/bin"; \
	fi
