#!/usr/bin/env sh
lsblk -o PTTYPE,PATH,SIZE,PARTTYPENAME,FSTYPE,FSVER,MOUNTPOINT,PARTFLAGS; # does not work if your lsblk is garbage
