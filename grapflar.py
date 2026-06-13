"""
Bu modul şunları içeriyor:
  - Düğüm (node) ve kenar (edge) ekleme/silme
  - Yönlü / yönsüz graf
  - Komşuluk matrisi (adjacency matrix)
  - İçerme matrisi (incidence matrix)
  - Derece hesaplama
  - El Sıkışma Teoremi (Handshaking Lemma)
  - Basit graf / multigraf / bağlantılılık kontrolü
"""



# VERİ YAPISI: Graf sözlük olarak tutulur


# Graf bu iki veri yapısıyla temsil edilir:
#
#   dugumler  → { dugum_adi: {} }   (şimdilik metadata yok, sadece varlık)
#   kenarlar  → liste of dict, her dict bir kenarı temsil eder:
#               { "kaynak": ..., "hedef": ..., "agirlik": ... }
#
# Komşuluk listesi (adjacency):
#   komsular  → { dugum: [komsu1, komsu2, ...] }



# DÜĞÜM İŞLEMLERİ


def dugum_ekle(dugumler, komsular, ad):
    """Grafa yeni bir düğüm ekler."""
    if ad not in dugumler:
        dugumler[ad] = {}
        komsular[ad] = []


def dugum_sil(dugumler, komsular, kenarlar, ad):
    """Bir düğümü ve ona bağlı tüm kenarları siler."""
    if ad not in dugumler:
        print(f"HATA: '{ad}' düğümü bulunamadı.")
        return

    # Bu düğüme ait kenarları temizle
    yeni_kenarlar = []
    for k in kenarlar:
        if k["kaynak"] != ad and k["hedef"] != ad:
            yeni_kenarlar.append(k)
    kenarlar.clear()
    kenarlar.extend(yeni_kenarlar)

    # Komşuluk listesinden de sil
    del dugumler[ad]
    del komsular[ad]
    for d in komsular:
        if ad in komsular[d]:
            komsular[d].remove(ad)

# KENAR İŞLEMLERİ

def kenar_ekle(dugumler, komsular, kenarlar, kaynak, hedef, agirlik=1.0, yonlu=False):
    """
    Grafa kenar ekle.
    Düğümler yoksa otomatik oluşturur.
    Yönsüz grafta her iki yönde de komşuluk eklenir.
    """
    dugum_ekle(dugumler, komsular, kaynak)
    dugum_ekle(dugumler, komsular, hedef)

    kenarlar.append({"kaynak": kaynak, "hedef": hedef, "agirlik": agirlik})

    if hedef not in komsular[kaynak]:
        komsular[kaynak].append(hedef)

    if not yonlu and kaynak != hedef:
        if kaynak not in komsular[hedef]:
            komsular[hedef].append(kaynak)


def kenar_var_mi(komsular, kaynak, hedef):
    """İki düğüm arasında kenar var mı?"""
    return hedef in komsular.get(kaynak, [])


def kenar_agirlik(kenarlar, kaynak, hedef):
    """İki düğüm arasındaki kenarın ağırlığını döndürür. Yoksa sonsuz.
    Yönsüz graflar için her iki yönde de arar."""
    for k in kenarlar:
        if (k["kaynak"] == kaynak and k["hedef"] == hedef) or            (k["kaynak"] == hedef  and k["hedef"] == kaynak):
            return k["agirlik"]
    return float("inf")

# DERECE HESAPLAMA

def derece(komsular, kenarlar, dugum, yonlu=False):
    """
    Bir düğümün derecesini hesaplar.

    Yönsüz: o düğüme bağlı kenar sayısı (self-loop 2 sayılır)
    Yönlü : giren + çıkan kenar sayısı
    """
    if yonlu:
        return cikan_derece(kenarlar, dugum) + giren_derece(kenarlar, dugum)

    # Yönsüz: komşuluk listesini kullan, self-loop için +1 ekstra
    derece_sayisi = len(komsular[dugum])
    for k in kenarlar:
        if k["kaynak"] == dugum and k["hedef"] == dugum:  # self-loop
            derece_sayisi += 1  # zaten 1 sayıldı, +1 daha ekle
    return derece_sayisi


def cikan_derece(kenarlar, dugum):
    """Düğümden çıkan kenar sayısı (yönlü graf için)."""
    return sum(1 for k in kenarlar if k["kaynak"] == dugum)


def giren_derece(kenarlar, dugum):
    """Düğüme giren kenar sayısı (yönlü graf için)."""
    return sum(1 for k in kenarlar if k["hedef"] == dugum)


def derece_dizisi(dugumler, komsular, kenarlar, yonlu=False):
    """Tüm düğümlerin derecelerini büyükten küçüğe sıralar."""
    dereceler = [derece(komsular, kenarlar, d, yonlu) for d in dugumler]
    return sorted(dereceler, reverse=True)

# EL SIKSMA TEOREMİ (HANDSHAKING LEMMA)

def el_siksma_teoremi(dugumler, komsular, kenarlar, yonlu=False):
    """
    El Sıkışma Teoremi:
      Yönsüz: Tüm derecelerin toplamı = 2 * kenar sayısı
      Yönlü : Σ(çıkan dereceler) = Σ(giren dereceler) = kenar sayısı

    Teoremi doğrular ve sonucu yazdırır.
    """
    kenar_sayisi = len(kenarlar)

    if not yonlu:
        derece_toplami = sum(derece(komsular, kenarlar, d, yonlu=False) for d in dugumler)
        beklenen = 2 * kenar_sayisi
        gecerli = derece_toplami == beklenen

        print(f"El Sıkışma Teoremi (Yönsüz):")
        print(f"  Derece toplamı : {derece_toplami}")
        print(f"  2 × |E|        : {beklenen}")
        print(f"  Teorem geçerli : {'✓' if gecerli else '✗'}")
        for d in dugumler:
            print(f"    {d}: derece = {derece(komsular, kenarlar, d, yonlu=False)}")
    else:
        cikan_toplam = sum(cikan_derece(kenarlar, d) for d in dugumler)
        giren_toplam = sum(giren_derece(kenarlar, d) for d in dugumler)
        gecerli = (cikan_toplam == giren_toplam == kenar_sayisi)

        print(f"El Sıkışma Teoremi (Yönlü):")
        print(f"  Σ çıkan derece : {cikan_toplam}")
        print(f"  Σ giren derece : {giren_toplam}")
        print(f"  |E|            : {kenar_sayisi}")
        print(f"  Teorem geçerli : {'✓' if gecerli else '✗'}")

# GRAF ÖZELLİKLERİ

def basit_mi(dugumler, komsular, kenarlar):
    """
    Basit graf: self-loop yok, iki düğüm arasında en fazla bir kenar var.
    """
    for d in dugumler:
        if d in komsular[d]:
            return False

    # Çift kenar kontrolü: aynı (kaynak, hedef) çifti birden fazla var mı?
    ciftler = [(k["kaynak"], k["hedef"]) for k in kenarlar]
    return len(ciftler) == len(set(ciftler))


def multigraf_mi(kenarlar):
    """İki düğüm arasında birden fazla kenar varsa multigraf."""
    ciftler = [(k["kaynak"], k["hedef"]) for k in kenarlar]
    return len(ciftler) != len(set(ciftler))


def self_loop_var_mi(kenarlar):
    """Herhangi bir self-loop (A→A) var mı?"""
    return any(k["kaynak"] == k["hedef"] for k in kenarlar)


def tam_graf_mi(dugumler, kenarlar):
    """
    Tam graf (complete graph): her düğüm çifti arasında kenar var mı?
    Yönsüz basit graflar için geçerli.
    """
    n = len(dugumler)
    beklenen_kenar = n * (n - 1) // 2
    return len(kenarlar) == beklenen_kenar


def baglanti_var_mi(dugumler, komsular):
    """
    BFS ile grafın bağlantılı olup olmadığını kontrol eder.
    Tüm düğümlere ulaşılabiliyorsa True döner.
    """
    if len(dugumler) == 0:
        return True

    baslangic = list(dugumler.keys())[0]
    ziyaret_edildi = set()
    kuyruk = [baslangic]

    while kuyruk:
        mevcut = kuyruk.pop(0)
        if mevcut in ziyaret_edildi:
            continue
        ziyaret_edildi.add(mevcut)
        for komsu in komsular[mevcut]:
            if komsu not in ziyaret_edildi:
                kuyruk.append(komsu)

    return ziyaret_edildi == set(dugumler.keys())



# MATRİS TEMSİLLERİ


def komşuluk_matrisi(dugumler, kenarlar):
    """
    Komşuluk matrisi oluşturur.
    A[i][j] = o kenara ait ağırlık, yoksa 0.

    Döndürür: (matris, dugum_sirasi)
    """
    dugum_listesi = list(dugumler.keys())
    n = len(dugum_listesi)
    indeks = {d: i for i, d in enumerate(dugum_listesi)}

    # Sıfırlarla dolu n×n matris oluştur
    matris = [[0.0] * n for _ in range(n)]

    for k in kenarlar:
        i = indeks[k["kaynak"]]
        j = indeks[k["hedef"]]
        matris[i][j] += k["agirlik"]  # çoklu kenarda topla

    return matris, dugum_listesi


def icerik_matrisi(dugumler, kenarlar, yonlu=False):
    """
    İçerme (incidence) matrisi oluşturur.
    Satır = düğüm, Sütun = kenar

    Yönsüz: düğüm kenara bağlıysa 1 (self-loop için 2)
    Yönlü : kaynak için +1, hedef için -1

    Döndürür: (matris, dugum_sirasi, kenar_sirasi)
    """
    dugum_listesi = list(dugumler.keys())
    n = len(dugum_listesi)
    m = len(kenarlar)
    indeks = {d: i for i, d in enumerate(dugum_listesi)}

    matris = [[0] * m for _ in range(n)]

    for j, k in enumerate(kenarlar):
        kaynak = k["kaynak"]
        hedef = k["hedef"]
        i_k = indeks[kaynak]
        i_h = indeks[hedef]

        if kaynak == hedef:  # self-loop
            matris[i_k][j] = 2
        elif yonlu:
            matris[i_k][j] = 1
            matris[i_h][j] = -1
        else:
            matris[i_k][j] = 1
            matris[i_h][j] = 1

    return matris, dugum_listesi, kenarlar



# YAZDIRMA YARDIMCILARI


def komsuluk_matrisini_yazdir(dugumler, kenarlar):
    """Komşuluk matrisini tablo olarak yazdırır."""
    matris, dugum_listesi = komşuluk_matrisi(dugumler, kenarlar)
    genislik = 8

    # Başlık satırı
    print(" " * genislik + "".join(f"{str(d):>{genislik}}" for d in dugum_listesi))
    print("─" * (genislik * (len(dugum_listesi) + 1)))

    for i, satir in enumerate(matris):
        degerler = ""
        for v in satir:
            goster = int(v) if v == int(v) else v
            degerler += f"{goster:>{genislik}}"
        print(f"{str(dugum_listesi[i]):<{genislik}}{degerler}")


def icerik_matrisini_yazdir(dugumler, kenarlar, yonlu=False):
    """İçerme matrisini tablo olarak yazdırır."""
    matris, dugum_listesi, kenar_listesi = icerik_matrisi(dugumler, kenarlar, yonlu)
    kenar_etiketleri = [f"e{i+1}" for i in range(len(kenar_listesi))]
    genislik = 5

    print(" " * 8 + "".join(f"{e:>{genislik}}" for e in kenar_etiketleri))
    print("─" * (8 + genislik * len(kenar_etiketleri)))

    for i, satir in enumerate(matris):
        degerler = "".join(f"{v:>{genislik}}" for v in satir)
        print(f"{str(dugum_listesi[i]):<8}{degerler}")

    print("\nKenar açıklamaları:")
    for etiket, k in zip(kenar_etiketleri, kenar_listesi):
        print(f"  {etiket}: {k['kaynak']} --[{k['agirlik']}]--> {k['hedef']}")


def graf_ozeti(dugumler, komsular, kenarlar, ad="Graf", yonlu=False):
    """Grafın genel özetini yazdırır."""
    print(f"── {ad} ──────────────────────────")
    print(f"  Tür        : {'Yönlü' if yonlu else 'Yönsüz'}")
    print(f"  Düğümler   : {list(dugumler.keys())}")
    print(f"  Kenar sayısı: {len(kenarlar)}")
    print(f"  Basit mi?  : {basit_mi(dugumler, komsular, kenarlar)}")
    print(f"  Multigraf? : {multigraf_mi(kenarlar)}")
    print(f"  Self-loop? : {self_loop_var_mi(kenarlar)}")
    print(f"  Bağlantılı?: {baglanti_var_mi(dugumler, komsular)}")
    print(f"  Derece dizisi: {derece_dizisi(dugumler, komsular, kenarlar, yonlu)}")