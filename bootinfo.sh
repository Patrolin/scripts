#!/usr/bin/env sh
[ -e /sys/firmware/efi ] && echo "Firmware interface:  UEFI" || echo "Firmware interface:  BIOS/CSM/LEGACY";
lscpu | grep Architecture:
lsblk -o PTTYPE,PATH,SIZE,PARTTYPENAME,FSTYPE,FSVER,MOUNTPOINT,PARTFLAGS; # does not work if your lsblk is garbage
