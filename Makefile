NAME := grub2-xen
SPECFILE := grub2-xen.spec


WORKDIR := $(shell pwd)
SPECDIR ?= $(WORKDIR)
SRCRPMDIR ?= $(WORKDIR)/srpm
BUILDDIR ?= $(WORKDIR)
RPMDIR ?= $(WORKDIR)/rpm
SOURCEDIR := $(WORKDIR)

NO_OF_CPUS := $(shell grep -c ^processor /proc/cpuinfo)

RPM_DEFINES := --define "_sourcedir $(SOURCEDIR)" \
		--define "_specdir $(SPECDIR)" \
		--define "_builddir $(BUILDDIR)" \
		--define "_srcrpmdir $(SRCRPMDIR)" \
		--define "_rpmdir $(RPMDIR)"

VER_REL := $(shell rpm $(RPM_DEFINES) -q --qf "%{VERSION} %{RELEASE}\n" --specfile $(SPECFILE)| head -1)

ifndef NAME
$(error "You can not run this Makefile without having NAME defined")
endif
ifndef VERSION
VERSION := $(word 1, $(VER_REL))
endif
ifndef RELEASE
RELEASE := $(word 2, $(VER_REL))
endif

all: help

URL := $(shell spectool $(RPM_DEFINES) --list-files --source 0 $(SPECFILE) 2> /dev/null| cut -d ' ' -f 2- )

ifndef SRC_FILE
ifdef URL
SRC_FILE := $(notdir $(URL))
SIGN_FILE := $(SRC_FILE).sig
endif
endif

URL_SIGN := $(URL).sig

get-sources: $(SRC_FILE) $(SIGN_FILE)

$(SRC_FILE):
	@wget -q -N $(URL)

$(SIGN_FILE):
	@wget -q -N $(URL_SIGN)

import-keys:
	@if [ -n "$$GNUPGHOME" ]; then rm -f "$$GNUPGHOME/linux-pvgrub2-trustedkeys.gpg"; fi
	@gpg --no-auto-check-trustdb --no-default-keyring --keyring linux-pvgrub2-trustedkeys.gpg -q --import *-key.asc

verify-sources: import-keys
	@gpgv --keyring linux-pvgrub2-trustedkeys.gpg $(SIGN_FILE) $(SRC_FILE) 2>/dev/null

.PHONY: clean-sources
clean-sources:
ifneq ($(SRC_FILE), None)
	-rm $(SRC_FILE)
endif


#RPM := rpmbuild --buildroot=/dev/shm/buildroot/
RPM := rpmbuild 

RPM_WITH_DIRS = $(RPM) $(RPM_DEFINES)

.PHONY : clean
clean ::
	@echo "Running the %clean script of the rpmbuild..."
	$(RPM_WITH_DIRS) --clean --nodeps $(SPECFILE)

help:
	@echo "Usage: make <target>"
	@echo
	@echo "get-sources      Download kernel sources from kernel.org"
	@echo "verify-sources"
