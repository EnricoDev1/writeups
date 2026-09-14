from pwn import *
from string import ascii_letters, digits

io = remote("geroglifici.challs.olicyber.it", 35000)
io.recvlines(3)

alph = "_{}" + ascii_letters + digits

ct = io.recvline()[:-1].split(b" ")[-1].decode()
io.sendlineafter(b"> ", alph)

res = io.recvline().decode()[:-1]
chars = {}

for i in range(len(alph)):
    chars[res[i]] = alph[i]

for c in ct:
    print(chars[c], end="")
