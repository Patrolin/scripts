#!/usr/bin/env sh
[ -e /sys/firmware/efi ] && echo "Firmware interface:  UEFI" || echo "Firmware interface:  BIOS/CSM/LEGACY";
lsblk -o PTTYPE,PATH,SIZE,PARTTYPENAME,FSTYPE,FSVER,MOUNTPOINT,PARTFLAGS; # does not work if your lsblk is garbage
lscpu | grep -e Architecture -e "Model name";
lspci | grep -e 3D -e VGA;
