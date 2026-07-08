SHELL := /bin/bash
RUN := PYTHONPATH=. python3 ./main.py
PROGRAM ?=

# Mirrors (reflector). Overrideable: make mirrors-update MIRROR_COUNTRIES="Argentina" MIRROR_AGE=6
MIRROR_COUNTRIES ?= Chile,Brazil,Argentina
MIRROR_AGE ?= 12

PROGRAMS := fonts bspwm sxhkd polybar kitty starship ranger picom rofi playerctl scrot thunar vscode xclip pulseaudio arandr xorg nvidia docker
PROGRAM_REQUIRED_TARGETS := install uninstall install-requirement uninstall-requirement install-files uninstall-files

# Allow `make <target> <program>` as shorthand for `make <target> PROGRAM=<program>`.
ifneq ($(strip $(filter $(PROGRAM_REQUIRED_TARGETS),$(firstword $(MAKECMDGOALS)))),)
ifeq ($(strip $(PROGRAM)),)
PROGRAM := $(word 2,$(MAKECMDGOALS))
endif
endif

# Usage: make <target> PROGRAM=<program> | make <target> <program>
define require_program
$(if $(strip $(PROGRAM)),,$(error Missing PROGRAM. Use: make <target> PROGRAM=<program> or make <target> <program>. Available: $(PROGRAMS)))
$(if $(filter $(PROGRAM),$(PROGRAMS)),,$(error Invalid PROGRAM '$(PROGRAM)'. Available: $(PROGRAMS)))
endef

.PHONY: \
	install uninstall install-requirement uninstall-requirement install-files uninstall-files \
	install-all install-core remove-core remove-core-purge wm-requirements-install \
	sddm-install sddm-enable sddm-start bspwm-bootstrap bspwm-install-session bspwm-check-display bspwm-restart \
	sxhkd-reload clock-set keyboard-set-latam scripts-chmod mirrors-update \
	$(PROGRAMS)

$(PROGRAMS):
	@:

install:
	$(call require_program)
	@$(RUN) --action install --program $(PROGRAM)

uninstall:
	$(call require_program)
	@$(RUN) --action uninstall --program $(PROGRAM)

install-requirement:
	$(call require_program)
	@$(RUN) --action install-requirement --program $(PROGRAM)

uninstall-requirement:
	$(call require_program)
	@$(RUN) --action uninstall-requirement --program $(PROGRAM)

install-files:
	$(call require_program)
	@$(RUN) --action install-files --program $(PROGRAM)

uninstall-files:
	$(call require_program)
	@$(RUN) --action uninstall-files --program $(PROGRAM)

install-all:
	@$(RUN) --action dirty_install_all_packages

install-core:
	@$(MAKE) install PROGRAM=bspwm
	@$(MAKE) install PROGRAM=sxhkd
	@$(MAKE) install PROGRAM=polybar
	@$(MAKE) install PROGRAM=picom

remove-core:
	@$(MAKE) uninstall PROGRAM=picom
	@$(MAKE) uninstall PROGRAM=polybar
	@$(MAKE) uninstall PROGRAM=sxhkd
	@$(MAKE) uninstall PROGRAM=bspwm

remove-core-purge:
	@WM_REMOVE_PACKAGES=1 $(MAKE) remove-core

wm-requirements-install:
	@$(MAKE) install-requirement PROGRAM=pulseaudio
	@$(MAKE) install-requirement PROGRAM=arandr
	@$(MAKE) install-requirement PROGRAM=nvidia

sddm-install:
	@sudo pacman -S --needed --noconfirm sddm

sddm-enable:
	@sudo systemctl enable sddm.service --force

sddm-start:
	@sudo systemctl start sddm.service

bspwm-bootstrap: install-core bspwm-install-session

bspwm-install-session:
	@./scripts/install_bspwm_session.sh

bspwm-check-display:
	@./scripts/check_display_stack.sh

bspwm-restart:
	@./scripts/check_display_stack.sh --quiet
	@if command -v bspc >/dev/null 2>&1; then \
		bspc wm -r; \
	else \
		echo "bspc no encontrado en PATH"; \
		exit 1; \
	fi

sxhkd-reload:
	@PYTHONPATH=. python3 -c "from src.app.drivers.repositories.programs._implementations.sxhkd_repository import SxhkdRepository; SxhkdRepository().reload_sxhkd()"

clock-set:
	@PYTHONPATH=. python3 ./scripts/set_clock.py

keyboard-set-latam:
	@PYTHONPATH=. python3 ./scripts/set_keyboard_layout.py --layout latam

scripts-chmod:
	@find ./scripts -maxdepth 1 -type f -exec chmod +x {} +

# Refresca la lista de mirrors con reflector y sincroniza el índice de pacman.
# Soluciona los 404 de "mirror viejo". Usá: make mirrors-update
mirrors-update:
	@command -v reflector >/dev/null 2>&1 || { echo "reflector no instalado: sudo pacman -S reflector"; exit 1; }
	@echo ">> Respaldando mirrorlist actual..."
	@sudo cp /etc/pacman.d/mirrorlist /etc/pacman.d/mirrorlist.bak
	@echo ">> Buscando mirrors ($(MIRROR_COUNTRIES), <$(MIRROR_AGE)h, https, por velocidad)..."
	@sudo reflector \
		--country $(MIRROR_COUNTRIES) \
		--age $(MIRROR_AGE) \
		--protocol https \
		--sort rate \
		--latest 20 \
		--download-timeout 10 \
		--save /etc/pacman.d/mirrorlist
	@echo ">> Refrescando índice de paquetes (pacman -Syy)..."
	@sudo pacman -Syy
	@echo ">> Mirrors actualizados. Backup en /etc/pacman.d/mirrorlist.bak"
