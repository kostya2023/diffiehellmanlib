use pyo3::{exceptions::*, prelude::*};
use num_bigint::{BigUint, RandBigInt};
use num_prime::{nt_funcs::is_prime, PrimalityTestConfig};
use num_traits::One;
use rand::{thread_rng, Rng};
use sha2::Sha256;
use hkdf::Hkdf;
use hex;
use std::{
    collections::HashMap,
    fs::{File, OpenOptions},
    io::{BufReader, BufWriter, Read, Write},
    path::Path,
    time::{Duration, Instant, SystemTime, UNIX_EPOCH},
};
use serde::{Deserialize, Serialize};
use bincode;

type PyResult<T> = Result<T, PyErr>;

const CACHE_FILE: &str = "cache_DH.dat";
const CACHE_EXPIRATION: Duration = Duration::from_secs(3600); // 1 час

#[derive(Serialize, Deserialize)]
struct CacheEntry {
    value: BigUint,
    timestamp: u64, // epoch seconds
}

// Загрузка кеша из файла
fn load_cache() -> HashMap<u32, CacheEntry> {
    let path = Path::new(CACHE_FILE);
    if !path.exists() {
        return HashMap::new();
    }

    let file = match File::open(path) {
        Ok(f) => f,
        Err(_) => {
            eprintln!("Failed to open cache file. Starting with an empty cache.");
            return HashMap::new();
        }
    };

    let reader = BufReader::new(file);
    match bincode::deserialize_from(reader) {
        Ok(cache) => cache,
        Err(_) => {
            eprintln!("Failed to deserialize cache. Starting with an empty cache.");
            HashMap::new()
        }
    }
}

// Сохранение кеша в файл
fn save_cache(cache: &HashMap<u32, CacheEntry>) {
    let path = Path::new(CACHE_FILE);
    let file = match OpenOptions::new()
        .write(true)
        .create(true)
        .truncate(true)
        .open(path)
    {
        Ok(f) => f,
        Err(e) => {
            eprintln!("Failed to open cache file for writing: {}. Cache will not be persisted.", e);
            return;
        }
    };

    let writer = BufWriter::new(file);
    if let Err(e) = bincode::serialize_into(writer, cache) {
        eprintln!("Failed to serialize cache: {}. Cache will not be persisted.", e);
    }
}

// Получение из кеша с проверкой времени
fn get_cached_p(bits: u32) -> Option<BigUint> {
    let mut cache = load_cache();
    if let Some(entry) = cache.get(&bits) {
        let now = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();
        if now - entry.timestamp < CACHE_EXPIRATION.as_secs() {
            return Some(entry.value.clone());
        } else {
            // Срок действия истек, удаляем из кеша и сохраняем
            cache.remove(&bits);
            save_cache(&cache);
        }
    }
    None
}

// Добавление в кеш
fn cache_p(bits: u32, p: BigUint) {
    let mut cache = load_cache();
    let now = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();
    cache.insert(bits, CacheEntry { value: p, timestamp: now });
    save_cache(&cache);
}


fn parse_bigint(s: &str) -> PyResult<BigUint> {
    BigUint::parse_bytes(s.as_bytes(), 10)
        .ok_or_else(|| PyValueError::new_err("Invalid numeric format"))
}

#[pyfunction]
fn generate_p_g(bits: u32) -> PyResult<(String, i32)> {
    if !(512..=8192).contains(&bits) {
        return Err(PyValueError::new_err("Bits must be between 512 and 8192"));
    }

    // Проверяем кеш
    if let Some(cached_p) = get_cached_p(bits) {
        return Ok((cached_p.to_str_radix(10), 2));
    }

    let mut rng = thread_rng();
    
    // Генерация простого числа
    let p = loop {
        let candidate = rng.gen_biguint(bits as u64);
        if is_prime(&candidate, Some(PrimalityTestConfig::strict())).probably() {
            break candidate;
        }
    };

    // Сохраняем в кеш
    cache_p(bits, p.clone());

    Ok((p.to_str_radix(10), 2))
}

#[pyfunction]
fn generate_a_or_b(p: String) -> PyResult<String> {
    let p = parse_bigint(&p)?;
    let key = thread_rng().gen_biguint_range(&BigUint::one(), &(&p - 1u32));
    Ok(key.to_str_radix(10))
}

#[pyfunction]
fn generate_A_or_B(p: String, g: i32, key: String) -> PyResult<String> {
    let (p, g, key) = (parse_bigint(&p)?, BigUint::from(g as u32), parse_bigint(&key)?);
    Ok(g.modpow(&key, &p).to_str_radix(10))
}

#[pyfunction]
fn generate_shared_key(public: String, p: String, private: String) -> PyResult<String> {
    let (public, p, private) = (parse_bigint(&public)?, parse_bigint(&p)?, parse_bigint(&private)?);
    
    let mut derived = [0u8; 32];
    Hkdf::<Sha256>::new(Some(b"dh-salt"), &public.modpow(&private, &p).to_bytes_be())
        .expand(b"dh-context", &mut derived)
        .map_err(|_| PyRuntimeError::new_err("HKDF error"))?;

    Ok(hex::encode(derived))
}

#[pymodule]
fn diffiehellmanlib(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(generate_p_g, m)?)?;
    m.add_function(wrap_pyfunction!(generate_a_or_b, m)?)?;
    m.add_function(wrap_pyfunction!(generate_A_or_B, m)?)?;
    m.add_function(wrap_pyfunction!(generate_shared_key, m)?)?;
    Ok(())
}