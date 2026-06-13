# -*- coding: utf-8 -*-
"""
**********Diğer moduller olmadan çalışmaz*************

Simülasyon şu adımları taklit eder:
  1. Graf oluştur (şehirler + yollar)
  2. Her şehre bir şifre anahtarı ata
  3. Paket oluştur (mesaj + kaynak + hedef)
  4. Rota bul (Dijkstra veya BFS)
  5. Mesajı şifrele (alıcının anahtarıyla)
  6. Ara düğümlerden geçir (transit)
  7. Hedefte şifreyi çöz
  8. Bütünlük kontrolü yap (checksum)
"""

import hashlib
import random
import time

from grapflar import dugum_ekle, kenar_ekle, kenar_agirlik
from traversal import bfs, dijkstra
from cyrpto import gcd, affine_sifrele, affine_coz


# SABITLER

M = 95  # Affine şifreleme alfabe büyüklüğü

# 95 ile aralarında asal olan geçerli 'a' değerleri
GECERLI_A_DEGERLERI = [a for a in range(1, 95) if gcd(a, 95) == 1]


# YARDIMCI: CHECKSUM

def checksum_hesapla(metin):
    """Metnin SHA-256 özetinin ilk 12 karakterini döndürür."""
    return hashlib.sha256(metin.encode()).hexdigest()[:12]


def butunluk_kontrol(orijinal_metin, mevcut_metin):
    """Mevcut metin orijinalle aynı mı? True/False döner."""
    return checksum_hesapla(orijinal_metin) == checksum_hesapla(mevcut_metin)


# DÜĞÜM KAYDI

def dugum_kaydet(dugum_kayitlari, ad, a=None, b=None, rol="relay"):
    if a is None:
        a = random.choice(GECERLI_A_DEGERLERI)
    if b is None:
        b = random.randint(1, 94)

    dugum_kayitlari[ad] = {
        "a": a,
        "b": b,
        "rol": rol,
        "gelen_paketler": [],
        "gonderi_sayisi": 0,
        "alim_sayisi": 0,
        "iletim_sayisi": 0,
    }


# PAKET OLUŞTURMA

paket_sayaci = 0

def paket_olustur(kaynak, hedef, mesaj, oncelik=2):
    global paket_sayaci
    paket_sayaci += 1

    return {
        "id": f"PKT-{paket_sayaci:04d}",
        "kaynak": kaynak,
        "hedef": hedef,
        "payload": mesaj,
        "orijinal": mesaj,
        "checksum": checksum_hesapla(mesaj),
        "sifreli_mi": False,
        "gidilen_yol": [],
        "hop_kaydi": [],
        "oncelik": oncelik,
        "olusturma_zamani": time.time(),
    }


def hop_kaydet(paket, dugum, eylem, detay=""):
    """Paketin geçtiği her adımı kayıt altına alır."""
    gecen_sure = round(time.time() - paket["olusturma_zamani"], 4)
    paket["hop_kaydi"].append({
        "dugum": dugum,
        "eylem": eylem,
        "detay": detay,
        "sure": gecen_sure,
    })
    if dugum not in paket["gidilen_yol"]:
        paket["gidilen_yol"].append(dugum)


# ROTA BULMA

def rota_bul(dugumler, komsular, kenarlar, kaynak, hedef, yontem="dijkstra"):
    if yontem == "dijkstra":
        sonuc = dijkstra(dugumler, komsular, kenarlar, kaynak, hedef)
    else:
        sonuc = bfs(komsular, kaynak, hedef)

    if not sonuc["yol"]:
        return None
    return sonuc["yol"]


# PAKET GÖNDERME (ANA FONKSİYON)

def gonder(dugumler, komsular, kenarlar, dugum_kayitlari,
           kaynak, hedef, mesaj, yontem="dijkstra", oncelik=2, ayrintili=True):

    # 1. Paket oluştur
    paket = paket_olustur(kaynak, hedef, mesaj, oncelik)

    if ayrintili:
        oncelik_etiketi = {1: "DUSUK", 2: "NORMAL", 3: "YUKSEK", 4: "KRITIK"}
        print(f"\n{'=' * 55}")
        print(f"  PAKET GONDERIMI  [{paket['id']}]")
        print(f"{'=' * 55}")
        print(f"  Gonderen : {kaynak}")
        print(f"  Alici    : {hedef}")
        print(f"  Oncelik  : {'*' * oncelik} {oncelik_etiketi.get(oncelik, '')}")
        print(f"  Yontem   : {yontem.upper()}")
        print(f"  Mesaj    : {mesaj[:50]}")
        print(f"  Checksum : {paket['checksum']}")
        print(f"  {'─' * 53}")

    # 2. Rota bul
    rota = rota_bul(dugumler, komsular, kenarlar, kaynak, hedef, yontem)
    if rota is None:
        print(f"  HATA: {kaynak} -> {hedef} arasi yol bulunamadi!")
        return None

    toplam_km = sum(
        kenar_agirlik(kenarlar, rota[i], rota[i + 1])
        for i in range(len(rota) - 1)
    )
    paket["maliyet"] = toplam_km

    if ayrintili:
        print(f"  Rota     : {' -> '.join(rota)}")
        print(f"  Durak    : {len(rota) - 1} hop")
        print(f"  Toplam   : {toplam_km:.0f} km\n")

    # 3. Şifrele — ASCII eylem adı kullan
    hedef_kayit = dugum_kayitlari[hedef]
    a = hedef_kayit["a"]
    b = hedef_kayit["b"]
    sifreli_mesaj = affine_sifrele(mesaj, a, b)

    paket["payload"] = sifreli_mesaj
    paket["sifreli_mi"] = True
    dugum_kayitlari[kaynak]["gonderi_sayisi"] += 1
    hop_kaydet(paket, kaynak, "SIFRELENDI", f"Anahtar(a={a}, b={b})")

    if ayrintili:
        print(f"  [SIFRELE @ {kaynak}]")
        print(f"     Anahtar : a={a}, b={b}")
        print(f"     Duz     : {mesaj[:45]}")
        print(f"     Sifreli : {sifreli_mesaj[:45]}")
        print()

    # 4. Ara düğümlerden geçir — ASCII eylem adı kullan
    for i in range(1, len(rota) - 1):
        ara_dugum = rota[i]
        dugum_kayitlari[ara_dugum]["iletim_sayisi"] += 1
        hop_kaydet(paket, ara_dugum, "TRANSIT",
                   f"{dugum_kayitlari[ara_dugum]['rol']} dugumunden iletildi")

        sonraki = rota[i + 1]
        km = kenar_agirlik(kenarlar, ara_dugum, sonraki)

        if ayrintili:
            print(f"  [TRANSIT @ {ara_dugum:<12}]  "
                  f"'{sifreli_mesaj[:25]}...'  -> {sonraki} ({km:.0f} km)")

    # 5. Hedefte teslim et — ASCII eylem adı kullan
    cozulmus_mesaj = affine_coz(sifreli_mesaj, a, b)
    paket["payload"] = cozulmus_mesaj
    paket["sifreli_mi"] = False

    dugum_kayitlari[hedef]["alim_sayisi"] += 1
    dugum_kayitlari[hedef]["gelen_paketler"].append(paket)
    hop_kaydet(paket, hedef, "TESLIM EDILDI", f"Cozuldu: '{cozulmus_mesaj[:30]}'")

    # 6. Bütünlük kontrolü
    butun_mu = butunluk_kontrol(paket["orijinal"], cozulmus_mesaj)

    if ayrintili:
        print()
        print(f"  [COZ @ {hedef}]")
        print(f"     Sifreli   : {sifreli_mesaj[:45]}")
        print(f"     Cozulmus  : {cozulmus_mesaj[:45]}")
        print(f"     Butunluk  : {'TAMAM' if butun_mu else 'BOZULMUS!'}")
        print(f"\n  {'─' * 53}")
        print(f"  TESLIMAT TAMAMLANDI")
        print(f"  Yol      : {' -> '.join(paket['gidilen_yol'])}")
        print(f"  Hop kaydi:")
        for h in paket["hop_kaydi"]:
            print(f"    t+{h['sure']:.4f}s  [{h['eylem']:<16}] @ {h['dugum']:<12}  {h['detay'][:40]}")
        print(f"{'=' * 55}\n")

    return paket


# BROADCAST

def yayin_gonder(dugumler, komsular, kenarlar, dugum_kayitlari,
                 kaynak, mesaj, hedefler=None):
    if hedefler is None:
        hedefler = [d for d in dugumler if d != kaynak]

    print(f"\n{'=' * 55}")
    print(f"  YAYIN: {kaynak} -> {len(hedefler)} dugum")
    print(f"{'=' * 55}")

    for hedef in hedefler:
        paket = gonder(
            dugumler, komsular, kenarlar, dugum_kayitlari,
            kaynak, hedef, mesaj, ayrintili=False
        )
        if paket:
            butun_mu = butunluk_kontrol(paket["orijinal"], paket["payload"])
            yol = " -> ".join(paket["gidilen_yol"])
            print(f"  {'OK' if butun_mu else 'FAIL'}  {kaynak} -> {hedef:<12}  "
                  f"({len(paket['gidilen_yol']) - 1} hop)  {yol}")
        else:
            print(f"  FAIL  {kaynak} -> {hedef:<12}  BASARISIZ")


# AĞ DURUMU

def ag_durumu_yazdir(dugumler, dugum_kayitlari, paket_listesi):
    print(f"\n{'=' * 55}")
    print(f"  AG DURUMU")
    print(f"{'=' * 55}")
    print(f"  Toplam dugum  : {len(dugumler)}")
    print(f"  Toplam paket  : {len(paket_listesi)}")
    print()

    print(f"  {'Dugum':<14} {'Rol':<10} {'Anahtar':<12} "
          f"{'Gonderim':>8} {'Alim':>5} {'Transit':>8}")
    print("  " + "-" * 58)
    for ad, kayit in dugum_kayitlari.items():
        anahtar = f"(a={kayit['a']}, b={kayit['b']})"
        print(f"  {ad:<14} {kayit['rol']:<10} {anahtar:<12} "
              f"{kayit['gonderi_sayisi']:>8} {kayit['alim_sayisi']:>5} "
              f"{kayit['iletim_sayisi']:>8}")

    print()
    print(f"  {'Paket':<10} {'Gonderen':<13} {'Alici':<13} {'Hop':>4} {'Durum':>6}")
    print("  " + "-" * 48)
    for p in paket_listesi:
        butun = "OK" if butunluk_kontrol(p["orijinal"], p["payload"]) else "FAIL"
        print(f"  {p['id']:<10} {p['kaynak']:<13} {p['hedef']:<13} "
              f"{len(p['hop_kaydi']):>4} {butun:>6}")


# AĞ KURULUMU

def ag_kur():
    dugumler = {}
    komsular = {}
    kenarlar = []

    sehirler = ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Mersin", "Konya"]
    for sehir in sehirler:
        dugum_ekle(dugumler, komsular, sehir)

    rotalar = [
        ("Istanbul", "Ankara",  450),
        ("Istanbul", "Bursa",   150),
        ("Istanbul", "Izmir",   480),
        ("Ankara",   "Izmir",   590),
        ("Ankara",   "Antalya", 550),
        ("Ankara",   "Konya",   260),
        ("Izmir",    "Antalya", 310),
        ("Antalya",  "Mersin",  190),
        ("Mersin",   "Konya",   270),
        ("Bursa",    "Ankara",  400),
    ]
    for kaynak, hedef, km in rotalar:
        kenar_ekle(dugumler, komsular, kenarlar, kaynak, hedef, km, yonlu=False)

    dugum_kayitlari = {}
    dugum_kaydet(dugum_kayitlari, "Istanbul", a=7,  b=3,  rol="hub")
    dugum_kaydet(dugum_kayitlari, "Ankara",   a=11, b=7,  rol="hub")
    dugum_kaydet(dugum_kayitlari, "Izmir",    a=13, b=11, rol="port")
    dugum_kaydet(dugum_kayitlari, "Bursa",    a=17, b=5,  rol="depot")
    dugum_kaydet(dugum_kayitlari, "Antalya",  a=18, b=9,  rol="resort")
    dugum_kaydet(dugum_kayitlari, "Mersin",   a=23, b=13, rol="port")
    dugum_kaydet(dugum_kayitlari, "Konya",    a=21, b=17, rol="relay")

    return dugumler, komsular, kenarlar, dugum_kayitlari