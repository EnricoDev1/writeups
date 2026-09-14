#!/bin/sh

qemu-system-x86_64 \
    -m 256M \
    -kernel ./bzImage \
    -initrd ./initramfs.cpio.gz \
    -append "root=/dev/ram rw console=ttyS0 oops=panic panic=1 kaslr quiet" \
    -cpu kvm64,+smep,+smap \
    -monitor /dev/null \
    -nographic \
    -drive format=raw,file=./flag,index=0,media=disk
