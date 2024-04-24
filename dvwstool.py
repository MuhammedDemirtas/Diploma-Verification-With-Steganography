import reedsolo
import hashlib
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

# Metni ikili forma dönüştürme
def metni_ikiliye_donustur(metin):
    # Metindeki her karakteri ikili forma dönüştür
    ikili_metin = ''.join(format(ord(char), '08b') for char in metin)

    # İkili formata dönüştürülen metni bytes formatına çevirip döndür
    return bytes(int(ikili_metin[i:i+8], 2) for i in range(0, len(ikili_metin), 8))

# SHA-256 ile hashleme
def sha256_hash(data):
    hash_object = hashlib.sha256()
    hash_object.update(data)
    return hash_object.digest()

# AES ile şifreleme işlemi
def aes_encrypt(data):
    key = b".M2K5C_78_C3T5O."

    backend = default_backend()
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=backend)
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return encrypted_data

def aes_decrypt(data):
    key = b".M2K5C_78_C3T5O."

    backend = default_backend()
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=backend)
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(data) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()
    return unpadded_data


# Reed-Solomon kodlama
def reed_solomon_kodlama(metin):
    # Hata düzeltme kodlama özelliklerini belirle
    n = 16  # Veri uzunluğu
    k = 8   # Koddaki veri uzunluğu

    # Veriyi Reed-Solomon kodlama ile kodla
    rsc = reedsolo.RSCodec(n - k)
    encoded = rsc.encode(metin)

    return encoded

def reed_solomon_cozme(encoded):
    n = 16  # Veri uzunluğu
    k = 8   # Koddaki veri uzunluğu

    # Veriyi Reed-Solomon kodlama ile çöz
    rsc = reedsolo.RSCodec(n - k)
    decoded_tuple = rsc.decode(encoded)  # Demet olarak çözülen metni al

    # Demetin ilk elemanı çözülen metin olacak
    decoded = decoded_tuple[0]

    return decoded

