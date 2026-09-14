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
    -m 64M \
    -nographic \
    -kernel ./bzImage \
    -append "console=ttyS0 loglevel=3 oops=panic panic=-1 pti=on page_alloc.shuffle=1 init_on_alloc=1" \
    -no-reboot \
    -cpu qemu64,+smap,+smep \
    -net nic,model=virtio \
    -net user \
    -monitor /dev/null \
    -initrd $INITRD \
    -s \
	-drive format=raw,file=./flag,if=virtio \
	
