#include <stdio.h>
#include <stdint.h>

int main(void) {
  uint32_t id       = 0xa30b5e40;
  uint32_t ptr_low  = id * 0x66c88cc3U;
  uint32_t kaslr    = ptr_low - 0x8233cac0U;
  uint64_t kbase    = 0xffffffff81000000ULL + kaslr;

  printf("0x%lx", kbase);
}
