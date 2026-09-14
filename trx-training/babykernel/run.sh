#!/bin/bash
set -euo pipefail

TMP=$(mktemp -d)
trap 'rm -rf $TMP' EXIT
mkdir $TMP/rootfs

gzip -dc initramfs.cpio.gz | (cd $TMP/rootfs && cpio -id --quiet)

cc -static -s -o exp exp.c
cp ./exp $TMP/rootfs/home/ctf/exp
cp flag $TMP/flag

(cd $TMP/rootfs &&
 find . | cpio -o -H newc --quiet | gzip -9 > ../initramfs.cpio.gz)

qemu-system-x86_64 \
  -s -m 64M -nographic -no-reboot \
  -kernel bzImage \
  -initrd "$TMP/initramfs.cpio.gz" \
  -append "console=ttyS0 oops=panic panic=1 quiet loglevel=3 kpti=off kaslr" \
  -monitor /dev/null \
  -drive file="$TMP/flag",format=raw,index=0,media=disk
