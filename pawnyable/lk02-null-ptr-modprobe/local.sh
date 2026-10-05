set -euo pipefail

musl-gcc -static -o exp exp.c

(
    cd rootfs
    cp ../exp ./exp
    find . | cpio -o --format=newc --owner=0:0 > ../new_rootfs.cpio
)

#!/bin/sh
qemu-system-x86_64 \
    -m 64M \
    -nographic \
    -kernel bzImage \
    -append "console=ttyS0 loglevel=3 oops=panic panic=-1 pti=on kaslr" \
    -no-reboot \
    -cpu kvm64,+smep \
    -monitor /dev/null \
    -initrd new_rootfs.cpio \
    -net nic,model=virtio \
    -net user \
    -drive format=raw,file=./flag,if=virtio \
    -s
