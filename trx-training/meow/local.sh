#!/bin/sh
set -euo pipefail

TMP=$(mktemp -d)
INITRD="$TMP/initramfs.cpio.gz"

gcc -o exp -static ./exp.c

cd ./rootfs
cp ../exp .
chmod +x exp

find . | cpio -o --format=newc --owner=0:0 --quiet | gzip -9 > "$INITRD"
cd ../

qemu-system-x86_64 \
    -m 256M \
    -kernel ./bzImage \
    -initrd "$TMP/initramfs.cpio.gz" \
    -append "root=/dev/ram rw console=ttyS0 oops=panic panic=1 kaslr quiet" \
    -cpu kvm64,+smep,+smap \
    -monitor /dev/null \
    -nographic \
    -drive format=raw,file=./flag,index=0,media=disk \
    -s
