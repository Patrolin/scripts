#!/usr/bin/env sh
[ -e /sys/firmware/efi ] && echo "Running UEFI." || echo "Running BIOS.";
