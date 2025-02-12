#ifndef UTILS_H
#define UTILS_H

#include <string>

// Макрос для экспорта функций в зависимости от платформы
#ifdef _WIN32
    #ifdef UTILS_EXPORTS
        #define UTILS_API __declspec(dllexport)
    #else
        #define UTILS_API __declspec(dllimport)
    #endif
#else
    #define UTILS_API
#endif

// Объявление функций с использованием UTILS_API
extern "C" {
    UTILS_API void generate_p_g_a(int bits, char** p, char** g, char** a);
    UTILS_API void generate_b(const char* p, const char* g, char** b);
    UTILS_API void generate_A(const char* p, const char* g, const char* a, char** A);
    UTILS_API void generate_shared_key(const char* A, const char* p, const char* g, const char* b, char** shared_key);
    UTILS_API void hash_shared_key(const char* shared_key, char** hash);
    UTILS_API void free_memory(char* ptr);
}

#endif // UTILS_H