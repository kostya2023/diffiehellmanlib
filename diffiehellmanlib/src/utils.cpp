#include "utils.h"
#include <openssl/bn.h>
#include <openssl/rand.h>
#include <openssl/sha.h>
#include <cstring>
#include <iostream>
#include <unordered_map>
#include <stdexcept>

// Макросы для логирования
#define LOG_START(func) std::cout << "[INFO] Starting " << func << std::endl;
#define LOG_END(func) std::cout << "[INFO] Finished " << func << std::endl;

// Кэш для простых чисел
static std::unordered_map<int, BIGNUM*> prime_cache;

// Освобождение памяти для строки
void free_memory(char* ptr) {
    LOG_START("free_memory");
    if (ptr) {
        OPENSSL_free(ptr);
    }
    LOG_END("free_memory");
}

// Генерация p, g, a
void generate_p_g_a(int bits, char** p, char** g, char** a) {
    LOG_START("generate_p_g_a");
    if (bits < 512 || bits > 8192) {
        throw std::invalid_argument("Invalid bit size. Must be between 512 and 8192.");
    }

    BIGNUM* bn_p = nullptr;
    BIGNUM* bn_g = nullptr;
    BIGNUM* bn_a = nullptr;

    if (prime_cache.count(bits)) {
        bn_p = BN_dup(prime_cache[bits]);
        std::cout << "[INFO] Found prime in cache for bits = " << bits << std::endl;
    } else {
        bn_p = BN_new();
        BN_generate_prime_ex(bn_p, bits, 1, nullptr, nullptr, nullptr);
        prime_cache[bits] = BN_dup(bn_p);
    }

    bn_g = BN_new();
    BN_set_word(bn_g, 2);

    bn_a = BN_new();
    BIGNUM* range = BN_new();
    BN_sub(range, bn_p, BN_value_one());
    BN_rand_range(bn_a, range);
    BN_free(range);

    *p = BN_bn2dec(bn_p);
    *g = BN_bn2dec(bn_g);
    *a = BN_bn2dec(bn_a);

    BN_free(bn_p);
    BN_free(bn_g);
    BN_free(bn_a);

    LOG_END("generate_p_g_a");
}

// Генерация b
void generate_b(const char* p, const char* g, char** b) {
    LOG_START("generate_b");

    BIGNUM* bn_p = nullptr;
    BIGNUM* bn_g = nullptr;
    BIGNUM* bn_b = nullptr;

    BN_CTX* ctx = BN_CTX_new();

    bn_p = BN_new();
    BN_dec2bn(&bn_p, p);

    bn_g = BN_new();
    BN_dec2bn(&bn_g, g);

    bn_b = BN_new();
    BIGNUM* range = BN_new();
    BN_sub(range, bn_p, BN_value_one());
    BN_rand_range(bn_b, range);
    BN_free(range);

    *b = BN_bn2dec(bn_b);

    BN_free(bn_p);
    BN_free(bn_g);
    BN_free(bn_b);
    BN_CTX_free(ctx);

    LOG_END("generate_b");
}

// Генерация A
void generate_A(const char* p, const char* g, const char* a, char** A) {
    LOG_START("generate_A");

    BIGNUM* bn_p = nullptr;
    BIGNUM* bn_g = nullptr;
    BIGNUM* bn_a = nullptr;
    BIGNUM* bn_A = nullptr;

    BN_CTX* ctx = BN_CTX_new();

    bn_p = BN_new();
    BN_dec2bn(&bn_p, p);

    bn_g = BN_new();
    BN_dec2bn(&bn_g, g);

    bn_a = BN_new();
    BN_dec2bn(&bn_a, a);

    bn_A = BN_new();
    BN_mod_exp(bn_A, bn_g, bn_a, bn_p, ctx);

    *A = BN_bn2dec(bn_A);

    BN_free(bn_p);
    BN_free(bn_g);
    BN_free(bn_a);
    BN_free(bn_A);
    BN_CTX_free(ctx);

    LOG_END("generate_A");
}

// Генерация общего ключа
void generate_shared_key(const char* A, const char* p, const char* g, const char* b, char** shared_key) {
    LOG_START("generate_shared_key");

    BIGNUM* bn_A = nullptr;
    BIGNUM* bn_p = nullptr;
    BIGNUM* bn_b = nullptr;
    BIGNUM* bn_shared_key = nullptr;

    BN_CTX* ctx = BN_CTX_new();

    bn_A = BN_new();
    BN_dec2bn(&bn_A, A);

    bn_p = BN_new();
    BN_dec2bn(&bn_p, p);

    bn_b = BN_new();
    BN_dec2bn(&bn_b, b);

    bn_shared_key = BN_new();
    BN_mod_exp(bn_shared_key, bn_A, bn_b, bn_p, ctx);

    *shared_key = BN_bn2dec(bn_shared_key);

    BN_free(bn_A);
    BN_free(bn_p);
    BN_free(bn_b);
    BN_free(bn_shared_key);
    BN_CTX_free(ctx);

    LOG_END("generate_shared_key");
}

// Хеширование общего ключа
void hash_shared_key(const char* shared_key, char** hash) {
    LOG_START("hash_shared_key");

    unsigned char digest[SHA256_DIGEST_LENGTH];
    SHA256((unsigned char*)shared_key, strlen(shared_key), digest);

    *hash = (char*)OPENSSL_malloc(SHA256_DIGEST_LENGTH * 2 + 1);
    for (int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
        snprintf(*hash + i * 2, 3, "%02x", digest[i]);
    }

    LOG_END("hash_shared_key");
}
