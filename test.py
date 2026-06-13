import random
import hashlib

# Senin modüllerinden importlar
from grapflar import dugum_ekle, kenar_ekle
from traversal import dijkstra, bfs
from cyrpto import affine_sifrele, affine_coz
from similasyon import M, GECERLI_A_DEGERLERI, checksum_hesapla


# 1. RASTGELE VE BOZUK DÜĞÜMLÜ GRAF OLUŞTURMA
def kaotik_ag_kur(dugum_sayisi=12, bozuk_oran=0.3):
    dugumler = {}
    komsular = {}
    kenarlar = []
    dugum_kayitlari = {}

    sehirler = [f"Node_{i}" for i in range(1, dugum_sayisi + 1)]

    for sehir in sehirler:
        dugum_ekle(dugumler, komsular, sehir)
        a = random.choice(GECERLI_A_DEGERLERI)
        b = random.randint(1, 94)
        durum = "BOZUK" if random.random() < bozuk_oran else "AKTIF"

        dugum_kayitlari[sehir] = {"a": a, "b": b, "durum": durum}

    # Rastgele Kenarlar
    for sehir in sehirler:
        adaylar = [s for s in sehirler if s != sehir]
        baglantilar = random.sample(adaylar, k=min(len(adaylar), random.randint(2, 4)))
        for hedef in baglantilar:
            mevcut_kenarlar = [(k["kaynak"], k["hedef"]) for k in kenarlar]
            if (sehir, hedef) not in mevcut_kenarlar and (hedef, sehir) not in mevcut_kenarlar:
                km = random.randint(100, 900)
                kenar_ekle(dugumler, komsular, kenarlar, sehir, hedef, km, yonlu=False)

    return dugumler, komsular, kenarlar, dugum_kayitlari


# 2. HATA TOLERANSLI GÖNDERİM SİMÜLASYONU
def guvenli_gonder_kaos(dugumler, komsular, kenarlar, dugum_kayitlari, kaynak, hedef, mesaj):
    print(f"\n🚀 TEST BAŞLADI: {kaynak} -> {hedef}")

    if dugum_kayitlari[kaynak]["durum"] == "BOZUK":
        print(f"❌ SİSTEM DURDU: Kaynak düğüm ({kaynak}) çalışmıyor!")
        return

    # ROTA HESAPLAMA (Sözlük yapısına göre güncellendi)
    print("Track: Rota hesaplanıyor...")
    sonuc = dijkstra(dugumler, komsular, kenarlar, kaynak, hedef)  # traversal.py'deki dijkstra sözlük döndürür

    rota = sonuc.get("yol", [])
    maliyet = sonuc.get("maliyet", float('inf'))

    if not rota or maliyet == float('inf'):
        print("❌ ROTA YOK: Hedefe giden fiziksel bir yol bulunamadı.")
        return

    print(f"📍 Bulunan Rota: {' -> '.join(rota)} (Toplam Maliyet: {maliyet})")

    # KRİPTOGRAFİ
    alici_anahtar = dugum_kayitlari[hedef]
    try:
        sifreli_veri = affine_sifrele(mesaj, alici_anahtar["a"], alici_anahtar["b"])
        csum = checksum_hesapla(mesaj)
    except Exception as e:
        print(f"❌ KRİPTO HATASI: {e}")
        return

    # YOLCULUK SİMÜLASYONU
    print("\n--- Paket Yola Çıktı ---")
    for durak in rota:
        durum = dugum_kayitlari[durak]["durum"]
        print(f"📦 Durak: {durak} | Durum: {durum}")

        if durum == "BOZUK":
            print(f"💥 ÇÖKÜŞ: Paket {durak} noktasında kayboldu! (Düğüm Arızalı)")
            return

    # VARIS
    print("\n--- Paket Teslim Edildi ---")
    try:
        cozulen_mesaj = affine_coz(sifreli_veri, alici_anahtar["a"], alici_anahtar["b"])
        if checksum_hesapla(cozulen_mesaj) == csum:
            print(f"✅ BAŞARI: Mesaj güvenle çözüldü: '{cozulen_mesaj}'")
        else:
            print("⚠️ UYARI: Veri bütünlüğü bozulmuş!")
    except Exception as e:
        print(f"❌ DEŞİFRE HATASI: {e}")


if __name__ == "__main__":
    d, k, kn, kayitlar = kaotik_ag_kur(dugum_sayisi=15, bozuk_oran=0.35)

    print("🌐 AĞ DURUMU:")
    for isim, info in kayitlar.items():
        simge = "🟢" if info["durum"] == "AKTIF" else "x"
        print(f"{simge} {isim}")

        # Sadece aktif düğümleri seç ki test başlar başlamaz bitmesin
        aktif_duraklar = [isim for isim, info in kayitlar.items() if info["durum"] == "AKTIF"]
        if len(aktif_duraklar) >= 2:
            s1, s2 = random.sample(aktif_duraklar, 2)
            guvenli_gonder_kaos(d, k, kn, kayitlar, s1, s2, "Yolculuk Testi")

    duraklar = list(d.keys())
    s1, s2 = random.sample(duraklar, 2)
    guvenli_gonder_kaos(d, k, kn, kayitlar, s1, s2, "Kaos Test Mesaji")

