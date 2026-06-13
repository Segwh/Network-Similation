"""

Kullanıcıdan şunları sorar:
  1. Gönderen şehir
  2. Alıcı şehir
  3. Mesaj
  4. Rota yöntemi (Dijkstra / BFS)
  5. Öncelik seviyesi

Sistem:
  · Mesajı alıcının Affine anahtarıyla şifreler
  · Paketi ağ üzerinden yönlendirir
  · Her durağı gösterir
  · Hedefte şifreyi çözer
  · Bütünlük kontrolü yapar
"""

from similasyon import ag_kur, gonder, ag_durumu_yazdir

# YARDIMCI FONKSİYONLAR

def baslik(yazi):
    print("█" * 55)
    print(f"  {yazi}")
    print("█" * 55)


def ayirici():
    print("─" * 55)


def menu_sec(baslik_yazi, secenekler):
    """
    Numaralı menü gösterir, kullanıcının seçimini döndürür (0'dan başlar).
    Geçerli bir seçim yapılana kadar tekrar sorar.
    """
    print(f"\n  {baslik_yazi}")
    ayirici()
    for i, secenek in enumerate(secenekler, 1):
        print(f"  [{i}] {secenek}")
    ayirici()

    while True:
        girdi = input("  Seçiminiz: ").strip()
        if girdi.lower() == "cikis":
            raise KeyboardInterrupt
        try:
            idx = int(girdi) - 1
            if 0 <= idx < len(secenekler):
                return idx
            print(f"  ✗ 1 ile {len(secenekler)} arasında bir sayı girin.")
        except ValueError:
            print("  ✗ Lütfen bir sayı girin.")

# TEK GÖNDERİM AKIŞI

def gonderi_akisi(dugumler, komsular, kenarlar, dugum_kayitlari,
                  sehirler, paket_listesi):
    """
    Kullanıcıdan bilgi alır ve bir paket gönderir.
    Adım adım, lineer: sor → gönder → bitir.
    """
    print()
    ayirici()
    print("  YENİ PAKET")
    ayirici()

    # ── 1. Gönderen şehir
    kaynak_idx = menu_sec("GÖNDEREN şehri seçin:", sehirler)
    kaynak = sehirler[kaynak_idx]

    # ── 2. Alıcı şehir (göndereni listeden çıkar)
    hedef_secenekleri = [s for s in sehirler if s != kaynak]
    hedef_idx = menu_sec("ALICI şehri seçin:", hedef_secenekleri)
    hedef = hedef_secenekleri[hedef_idx]

    # ── 3. Mesaj
    print(f"\n  Mesajınızı yazın ({kaynak} → {hedef}):")
    ayirici()
    mesaj = input("  > ").strip()
    if mesaj.lower() == "cikis":
        raise KeyboardInterrupt
    if not mesaj:
        print("  ✗ Mesaj boş olamaz.")
        return

    # ── 4. Rota yöntemi
    yontem_idx = menu_sec("ROTA yöntemi seçin:", [
        "dijkstra  (en kısa km)",
        "bfs       (en az durak)",
    ])
    yontem = "dijkstra" if yontem_idx == 0 else "bfs"

    # ── 5. Öncelik
    oncelik_secenekleri = [
        " DÜŞÜK",
        " NORMAL",
        " YÜKSEK",
        " KRİTİK",
    ]
    oncelik_idx = menu_sec("ÖNCELİK seviyesi seçin:", oncelik_secenekleri)
    oncelik = oncelik_idx + 1  # 1-4 arası

    # ── 6. Gönder
    print()
    paket = gonder(
        dugumler, komsular, kenarlar, dugum_kayitlari,
        kaynak=kaynak,
        hedef=hedef,
        mesaj=mesaj,
        yontem=yontem,
        oncelik=oncelik,
        ayrintili=True,
    )
    if paket:
        paket_listesi.append(paket)

# ANA LOOP
def main():
    print("\n  Ağ yükleniyor...")
    dugumler, komsular, kenarlar, dugum_kayitlari = ag_kur()
    sehirler = list(dugumler.keys())
    paket_listesi = []
    print(f"  Ağ hazır — {len(sehirler)} şehir aktif.\n")

    baslik("GÜVENLİ LOJİSTİK MESSENGER")
    print(f"\n  Şehirler: {', '.join(sehirler)}")
    print("  Herhangi bir adımda 'cikis' yazarak çıkabilirsiniz.\n")

    while True:
        try:
            gonderi_akisi(
                dugumler, komsular, kenarlar, dugum_kayitlari,
                sehirler, paket_listesi
            )
            tekrar = input("\n  Başka paket göndermek ister misiniz? [e/h]: ").strip().lower()
            if tekrar != "e":
                break
        except (KeyboardInterrupt, EOFError):
            break

    # Oturum özeti
    if paket_listesi:
        ag_durumu_yazdir(dugumler, dugum_kayitlari, paket_listesi)

    print("\n  Oturum sonlandı. Güle güle.\n")


if __name__ == "__main__":
    main()