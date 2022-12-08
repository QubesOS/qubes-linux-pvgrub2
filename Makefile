NAME := grub2-xen
SPECFILE := grub2-xen.spec

VER_REL := $(shell rpm -q --qf "%{VERSION} %{RELEASE}\n" --specfile $(SPECFILE)| head -1)

ifndef NAME
$(error "You can not run this Makefile without having NAME defined")
endif
ifndef VERSION
VERSION := $(word 1, $(VER_REL))
endif
ifndef RELEASE
RELEASE := $(word 2, $(VER_REL))
endif

URL := $(shell spectool --list-files --source 0 $(SPECFILE) 2> /dev/null| cut -d ' ' -f 2- )

ifndef SRC_FILE
ifdef URL
SRC_FILE := $(notdir $(URL))
SIGN_FILE := $(SRC_FILE).sig
endif
endif

URL_SIGN := $(URL).sig

get-sources: $(SRC_FILE) $(SIGN_FILE)

$(if $(FETCH_CMD),,$(error You cannot run this makefile without having $$(FETCH_CMD) set))

$(SRC_FILE):
	${Q}$(FETCH_CMD) $(SRC_FILE) $(URL)

$(SIGN_FILE):
	${Q}$(FETCH_CMD) $(SIGN_FILE) $(URL_SIGN)

import-keys:
	${Q}if [ -n "$$GNUPGHOME" ]; then rm -f "$$GNUPGHOME/linux-pvgrub2-trustedkeys.gpg"; fi
	${Q}gpg --no-auto-check-trustdb --no-default-keyring --keyring linux-pvgrub2-trustedkeys.gpg -q --import *-key.asc

verify-sources: import-keys
	${Q}gpgv --keyring linux-pvgrub2-trustedkeys.gpg $(SIGN_FILE) $(SRC_FILE)

.PHONY: clean-sources
clean-sources:
ifneq ($(SRC_FILE), None)
	-rm $(SRC_FILE)
endif
