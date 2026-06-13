"""
Bu dosya şunları içeriyor:
  1. Genişletilmiş Öklid Algoritması
  2. Modüler Ters (Modular Inverse)
  3. Hızlı Üs Alma (Fast Modular Exponentiation)
  4. Affine Şifreleme
  6. Çin Kalan Teoremi (CRT)
  7. Asal Sayı Testi (basit versiyon)
  8. Mini RSA
"""

import random

# GENİŞLETİLMİŞ ÖKLİD ALGORİTMASI

def extended_gcd(a, b):
    """
    a*x + b*y = gcd(a, b) eşitliğini sağlayan x ve y'yi bulur.
    Döndürür: (gcd, x, y)

    Örnek: extended_gcd(35, 15) → (5, 1, -2)
           çünkü 35*1 + 15*(-2) = 5
    """
    if b == 0:
        return a, 1, 0

    old_r = a
    r = b
    old_s = 1
    s = 0
    old_t = 0
    t = 1

    while r != 0:
        bolum = old_r // r

        yeni_r = old_r - bolum * r
        old_r = r
        r = yeni_r

        yeni_s = old_s - bolum * s
        old_s = s
        s = yeni_s

        yeni_t = old_t - bolum * t
        old_t = t
        t = yeni_t

    # old_r = gcd,  old_s = x,  old_t = y
    return old_r, old_s, old_t


def gcd(a, b):
    """İki sayının ebob'unu (gcd) döndürür."""
    sonuc, _, _ = extended_gcd(abs(a), abs(b))
    return sonuc

# MODÜLER TERS

def modular_inverse(a, m):
    """
    a'nın m'ye göre modüler tersini bulur.
    Yani: a * x ≡ 1 (mod m) koşulunu sağlayan x'i bulur.

    Bu sadece gcd(a, m) = 1 ise mümkündür.
    """
    a = a % m
    ebob, x, _ = extended_gcd(a, m)

    if ebob != 1:
        print(f"HATA: {a} sayısının mod {m} tersi yok! gcd={ebob}")
        return None

    return x % m  # sonucu [0, m) aralığına çek



# HIZLI MODÜLER ÜS ALMA


def fast_mod_exp(taban, us, mod):
    """
    taban us mod m hesaplar. Büyük sayılar için bile hızlı çalışır.

    Nasıl çalışır:
      - Üssü ikili (binary) olarak düşün.
      - Her adımda tabanı karele al, üssü 2'ye böl.
      - Üssün mevcut biti 1 ise sonuca çarp.

    Örnek: fast_mod_exp(2, 10, 1000) → 24
           (2^10 = 1024, 1024 mod 1000 = 24)
    """
    if mod == 1:
        return 0

    sonuc = 1
    taban = taban % mod

    while us > 0:
        # Üssün son biti 1 mi? (tek sayı mı?)
        if us % 2 == 1:
            sonuc = (sonuc * taban) % mod

        taban = (taban * taban) % mod  # tabanı karele al
        us = us // 2                   # üssü ikiye böl

    return sonuc

# 4. AFFİNE ŞİFRELEME

" Kullanacağımız alfabe: yazdırılabilir ASCII karakterler (95 adet) "

ALFABE = "".join(chr(i) for i in range(32, 127))
M = len(ALFABE)  # 95


def affine_sifrele(metin, a, b):
    """
    Affine şifreleme: E(x) = (a*x + b) mod m
    Her karakteri sayıya çevir, formülü uygula, tekrar karaktere dönüştür.
    """
    # Önce a'nın geçerli olduğunu kontrol et
    if gcd(a, M) != 1:
        print(f"HATA: a={a} geçersiz! gcd(a, m) = 1 olmalı.")
        return None

    sonuc = ""
    for karakter in metin:
        if karakter in ALFABE:
            x = ALFABE.index(karakter)          # karakteri sayıya çevir
            y = (a * x + b) % M                 # formülü uygula
            sonuc += ALFABE[y]                   # sayıyı tekrar karaktere çevir
        else:
            sonuc += karakter                    # alfabede yoksa olduğu gibi bırak
    return sonuc


def affine_coz(sifreli_metin, a, b):
    """
    Affine çözme: D(y) = a_ters * (y - b) mod m

    Şifrelemenin tersi.
    """
    a_ters = modular_inverse(a, M)
    if a_ters is None:
        return None

    sonuc = ""
    for karakter in sifreli_metin:
        if karakter in ALFABE:
            y = ALFABE.index(karakter)
            x = (a_ters * (y - b)) % M
            sonuc += ALFABE[x]
        else:
            sonuc += karakter
    return sonuc


# 6. ÇİN KALAN TEOREMİ (CRT)

def cin_kalan_teoremi(kalanlar, moduller):
    """
  x ≡ 2 (mod 3)
  x ≡ 3 (mod 5)
  x ≡ 2 (mod 7)
  → x = 23
    """
    " Tüm modüllerin çarpımı"
    M_toplam = 1
    for m in moduller:
        M_toplam *= m

    x = 0
    for i in range(len(kalanlar)):
        r = kalanlar[i]
        m = moduller[i]
        Mi = M_toplam // m                # M'yi bu modüle böl
        yi = modular_inverse(Mi, m)       # Mi'nin modüler tersi
        x += r * Mi * yi                  # katkıyı ekle

    return x % M_toplam

# 7. ASAL SAYI TESTİ


def asal_mi(n):
    """
    n sayısının asal olup olmadığını kontrol eder.

    Yöntem: 2'den sqrt(n)'e kadar bölünebiliyor mu diye bakar.
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False

    " 3'ten sqrt(n)'e kadar tek sayılarla"
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2

    return True


def sonraki_asal(n):
  #  n'den büyük ilk asal sayıyı döndürür.
    aday = n + 1
    while not asal_mi(aday):
        aday += 1
    return aday



# 8. MİNİ RSA

def rsa_anahtarlari_olustur(p, q):
    """
    İki asal sayıdan RSA anahtar çifti oluşturur.

    Adımlar:
      1. n = p * q  (modül)
      2. phi = (p-1) * (q-1)  (Euler totient)
      3. e: phi ile aralarında asal olan küçük bir sayı (public exponent)
      4. d = e'nin phi'ye göre modüler tersi (private exponent)

    Döndürür: (public_key, private_key) şeklinde ((e, n), (d, n))
    """
    n = p * q
    phi = (p - 1) * (q - 1)

    # Geçerli bir e bul (phi ile aralarında asal)
    e = 3
    while gcd(e, phi) != 1:
        e += 2

    d = modular_inverse(e, phi)

    public_key = (e, n)
    private_key = (d, n)
    return public_key, private_key


def rsa_sifrele(mesaj, public_key):
    """RSA şifreleme: C = mesaj^e mod n"""
    e, n = public_key
    return fast_mod_exp(mesaj, e, n)


def rsa_coz(sifreli, private_key):
    """RSA çözme: M = sifreli^d mod n"""
    d, n = private_key
    return fast_mod_exp(sifreli, d, n)
