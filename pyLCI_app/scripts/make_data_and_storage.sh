#!/bin/bash

#return 0: success
#return 1: notfile or wrong file passed
#return 2: fdisk failed
#return 3: mkfs.ext3 failed
#return 4: mount failed
#return 5: mkfs.vfat failed

test -f $1 && exit 1

#(
#echo o # Create a new empty DOS partition table
#echo n # Add a new partition
#echo p # Primary partition
#echo 1 # Partition number
#echo 1 # First sector
#echo 1000M  # Last sector (1GB size)
#echo n # Add a new partition
#echo p # Primary partition
#echo 2 # Partition number
#echo   # First usable sector (accept default)
#echo   # Last sector (accept default)
#echo w # Write changes
#) | sudo fdisk $1 || exit 2

FIRSTPART=$1"1"
SECONDPART=$1"1"
#mkfs.ext3 $FIRSTPART || exit 3
#mkdir -p /mnt/iceedata
#mount $FIRSTPART /mnt/iceedata -o rw || exit 4
#mkfs.vfat $SECONDPART || exit 5

exit 0
