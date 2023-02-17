#!/usr/bin/env sh
[ -e /sys/firmware/efi ] && echo 'Firmware interface:  UEFI' || echo 'Firmware interface:  BIOS/CSM/LEGACY';
lsblk -o PTTYPE,PATH,SIZE,PARTTYPENAME,FSTYPE,FSVER,MOUNTPOINT; # does not work if your distro's lsblk is garbage
lscpu | grep -E '(Architecture|Model name)';
lspci -k | grep -A 2 -E '(VGA|3D)'
