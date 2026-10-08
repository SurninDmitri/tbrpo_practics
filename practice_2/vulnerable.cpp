#include <iostream>
#include <cstring>
#include <cstdio>

using namespace std;

// УЯЗВИМОСТЬ #1: Buffer Overflow (CWE-120)
void vulnerable_copy(char* input) {
    char buffer[10];
    strcpy(buffer, input);  // ❌ Переполнение буфера
    cout << "Copied: " << buffer << endl;
}

// УЯЗВИМОСТЬ #2: Format String (CWE-134)
void vulnerable_printf(char* input) {
    printf(input);  // ❌ Format string vulnerability
}

// УЯЗВИМОСТЬ #3: Command Injection (CWE-78)
void vulnerable_system(char* input) {
    char command[100];
    sprintf(command, "echo %s", input);
    system(command);  // ❌ Command injection
}

int main(int argc, char* argv[]) {
    if (argc < 2) return 1;
    vulnerable_copy(argv[1]);
    vulnerable_printf(argv[1]);
    vulnerable_system(argv[1]);
    return 0;
}
