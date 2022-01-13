ROOT_DIR ?= $(shell git rev-parse --show-toplevel)

# The default is to download the official release binary
# for x86_64-unknown-linux-gnu. If that default is unsuitable,
# build your own binary and copy or symlink it here, or
# override the variable with "make DPRINT_BINARY=...".
DPRINT_BINARY = $(ROOT_DIR)/dprint

# The architecture can be changed. Only Linux and MacOS are currently supported, though.
# See https://github.com/dprint/dprint/releases for available architectures.
ifeq  ($(shell uname),Darwin)
DPRINT_ARCH = x86_64-apple-darwin
else
DPRINT_ARCH = x86_64-unknown-linux-gnu
endif

# The dprint version.
DPRINT_RELEASE = 0.19.2

# Download URL for dprint and resulting file.
DPRINT_FILE = dprint-$(DPRINT_ARCH).zip
DPRINT_URL = https://github.com/dprint/dprint/releases/download/$(DPRINT_RELEASE)/$(DPRINT_FILE)
# As an extra sanity check, the hash of the downloaded file must match before it is used.
ifeq  ($(shell uname),Darwin)
DPRINT_SHA256 = 0e6db7b5fb20598930f9c920369063bca9ef54714eb5091ca32fa24fc76494a4
else
DPRINT_SHA256 = 2c481ffe7b20c905ec8288281738f080a1bf650875c6c00a8728ca23d6fa8aed
endif


.PHONY: help
help:
	@echo "UK8S documents development makefile"
	@echo
	@echo "Usage: make <TARGET>"
	@echo
	@echo "Target:"
	@echo "  fmt                 Format markdown style."
	@echo "  lint                Check markdown style."
	@echo "  clean               Clear cache file."
	@echo


.PHONY: fmt
fmt: $(DPRINT_BINARY)
	$(DPRINT_BINARY) fmt


.PHONY: lint
lint: $(DPRINT_BINARY)
	$(DPRINT_BINARY) check


.PHONY: clean
clean: $(DPRINT_BINARY)
	$(DPRINT_BINARY) clear-cache


$(DPRINT_FILE):
	curl -L -O $(DPRINT_URL)


$(DPRINT_BINARY): $(DPRINT_FILE)
	@if [ "`sha256sum $(DPRINT_FILE) | awk '{print $$1}'`" != $(DPRINT_SHA256) ]; then \
		echo "ERROR: hash mismatch, check downloaded file $(DPRINT_FILE) and/or update DPRINT_SHA256"; \
		exit 1; \
	fi
	@unzip -q -n -d $(ROOT_DIR) $(DPRINT_FILE)
