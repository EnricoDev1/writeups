#include <stdio.h>
#include <stdlib.h>

void bar() {
    int a;
    int b;
    char c;
    printf("%d - %d - %c", a, b, c);
}

void foo() {
    int a = 123123123;
    int b = 9999;
    char c = 'A';
}

int main(void) {
    foo();
    bar();
    return 0;
}
