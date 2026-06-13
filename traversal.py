"""
**************Graf modulu olmadan calismaz**********

Bu dosya şunları içeriyor:
  1. BFS  — Genişlik Öncelikli Arama (en kısa yol, hop sayısı)
  2. DFS  — Derinlik Öncelikli Arama (tam keşif, döngü tespiti)
  3. Dijkstra — En kısa AĞIRLIKLI yol
  4. Tüm basit yollar (all simple paths)
  5. Bağlı bileşenler (connected components)
  6. Topolojik sıralama (topological sort)
"""

import heapq
from grapflar import (
    dugum_ekle, kenar_ekle, kenar_agirlik,
    giren_derece
)

# YARDIMCI: Ebeveyn zincirinden yolu geri sar

def yolu_geri_sar(ebeveyn, baslangic, hedef):
    """
    ebeveyn sözlüğünden yolu geri sararak liste olarak döndürür.

    ebeveyn = { dugum: ebeveyn_dugum }
    Hedeften başlangıca kadar geriye gidip, sonra ters çeviririz.
    """
    yol = []
    mevcut = hedef

    while mevcut is not None:
        yol.append(mevcut)
        mevcut = ebeveyn.get(mevcut)

    yol.reverse()

    # Başlangıç yolda yoksa ulaşılamadı demektir
    if yol[0] != baslangic:
        return []

    return yol

# 1. BFS — Genişlik Öncelikli Arama

def bfs(komsular, baslangic, hedef=None):
    """
    BFS: Kuyruğa (queue) alarak katman katman gezinir.
    En az KENAR SAYISI ile hedefe ulaşan yolu bulur.

    Nasıl çalışır:
      - Başlangıç düğümü kuyruğa at.
      - Kuyruktan düğüm çek, komşularını kuyruğa at.
      - Daha önce görülenler tekrar eklenmez.
      - Hedefe ulaşınca dur (verilmişse).
    """
    ziyaret_edildi = set()
    ebeveyn = {baslangic: None}
    seviyeler = {baslangic: 0}
    kuyruk = [baslangic]
    ziyaret_sirasi = []

    while kuyruk:
        mevcut = kuyruk.pop(0)  # kuyruğun başından al (FIFO)

        if mevcut in ziyaret_edildi:
            continue

        ziyaret_edildi.add(mevcut)
        ziyaret_sirasi.append(mevcut)

        if hedef is not None and mevcut == hedef:
            break  # erken çıkış

        for komsu in komsular.get(mevcut, []):
            if komsu not in ziyaret_edildi and komsu not in ebeveyn:
                ebeveyn[komsu] = mevcut
                seviyeler[komsu] = seviyeler[mevcut] + 1
                kuyruk.append(komsu)

    yol = []
    if hedef is not None and hedef in ziyaret_edildi:
        yol = yolu_geri_sar(ebeveyn, baslangic, hedef)

    return {
        "ziyaret_sirasi": ziyaret_sirasi,
        "ebeveyn": ebeveyn,
        "seviyeler": seviyeler,
        "yol": yol,
        "bulundu": hedef in ziyaret_edildi if hedef else None,
    }



# 2. DFS — Derinlik Öncelikli Arama


def dfs(komsular, baslangic, hedef=None):
    """
    DFS: Yığıt (stack) kullanarak mümkün olduğu kadar derinde gider.

    Nasıl çalışır:
      - Başlangıç düğümü yığıta at.
      - Yığıttan düğüm çek (en üstten, LIFO), komşuları yığıta at.
      - Daha önce görülenler tekrar eklenmez.
      - Hedefe ulaşınca dur (verilmişse).
    """
    ziyaret_edildi = set()
    ebeveyn = {baslangic: None}
    ziyaret_sirasi = []
    yigit = [baslangic]
    dongu_var = False

    while yigit:
        mevcut = yigit.pop()  # yığıtın üstünden al (LIFO)

        if mevcut in ziyaret_edildi:
            continue

        ziyaret_edildi.add(mevcut)
        ziyaret_sirasi.append(mevcut)

        if hedef is not None and mevcut == hedef:
            break

        # Komşuları ters sırayla ekle → soldan sağa DFS sırası korunur
        for komsu in reversed(komsular.get(mevcut, [])):
            if komsu not in ziyaret_edildi:
                if komsu not in ebeveyn:
                    ebeveyn[komsu] = mevcut
                yigit.append(komsu)
            else:
                # Ziyaret edilmiş ama ebeveyn değilse → döngü
                if komsu != ebeveyn.get(mevcut):
                    dongu_var = True

    yol = []
    if hedef is not None and hedef in ziyaret_edildi:
        yol = yolu_geri_sar(ebeveyn, baslangic, hedef)

    return {
        "ziyaret_sirasi": ziyaret_sirasi,
        "ebeveyn": ebeveyn,
        "yol": yol,
        "bulundu": hedef in ziyaret_edildi if hedef else None,
        "dongu_var": dongu_var,
    }

# 3. DİJKSTRA — En Kısa Ağırlıklı Yol

def dijkstra(dugumler, komsular, kenarlar, baslangic, hedef=None):
    """
    Dijkstra: Kenar ağırlıklarını dikkate alarak en kısa yolu bulur.
    Nasıl çalışır:
      - Her düğümün mesafesi başta sonsur (inf).
      - Başlangıç düğümünün mesafesi 0.
      - En düşük maliyetli düğümü öncelik kuyruğundan çek.
      - Komşuların mesafelerini güncelle (daha kısa yol bulunduysa).
      - Hedefe ulaşınca dur.
    """
    SONSUZ = float("inf")

    # Başta her düğüme olan mesafe sonsuz
    mesafeler = {d: SONSUZ for d in dugumler}
    mesafeler[baslangic] = 0
    ebeveyn = {baslangic: None}
    ziyaret_sirasi = []

    # Öncelik kuyruğu: (maliyet, dugum)
    oncelik_kuyrugu = [(0, baslangic)]

    while oncelik_kuyrugu:
        maliyet, mevcut = heapq.heappop(oncelik_kuyrugu)

        # Eski (geçersiz) bir kayıtsa atla
        if maliyet > mesafeler[mevcut]:
            continue

        ziyaret_sirasi.append(mevcut)

        if hedef is not None and mevcut == hedef:
            break

        for komsu in komsular.get(mevcut, []):
            kenar_w = kenar_agirlik(kenarlar, mevcut, komsu)
            yeni_maliyet = mesafeler[mevcut] + kenar_w

            if yeni_maliyet < mesafeler[komsu]:
                mesafeler[komsu] = yeni_maliyet
                ebeveyn[komsu] = mevcut
                heapq.heappush(oncelik_kuyrugu, (yeni_maliyet, komsu))

    yol = []
    toplam_maliyet = SONSUZ
    if hedef is not None and mesafeler[hedef] < SONSUZ:
        yol = yolu_geri_sar(ebeveyn, baslangic, hedef)
        toplam_maliyet = mesafeler[hedef]

    return {
        "mesafeler": mesafeler,
        "ebeveyn": ebeveyn,
        "ziyaret_sirasi": ziyaret_sirasi,
        "yol": yol,
        "maliyet": toplam_maliyet,
        "bulundu": hedef in ebeveyn if hedef else None,
    }

# 4. TÜM BASİT YOLLAR

def tum_basit_yollar(komsular, kenarlar, baslangic, hedef, max_yol=20):
    """
    Başlangıç → hedef arasındaki tüm basit yolları bulur.
    Basit yol: aynı düğümden iki kez geçilmez.

    DFS kullanır ama her adımda "şu ana kadar gidilen yol"u takip eder.
    Hedefe ulaşıldığında yolu kayıt altına alır.
    """
    sonuclar = []

    # Yığıt: (mevcut_dugum, gidilen_yol, toplam_maliyet)
    yigit = [(baslangic, [baslangic], 0.0)]

    while yigit and len(sonuclar) < max_yol:
        mevcut, yol, maliyet = yigit.pop()

        if mevcut == hedef:
            sonuclar.append((list(yol), maliyet))
            continue

        for komsu in komsular.get(mevcut, []):
            if komsu not in yol:  # basit yol: tekrar geçme
                kenar_w = kenar_agirlik(kenarlar, mevcut, komsu)
                yigit.append((komsu, yol + [komsu], maliyet + kenar_w))

    # En kısa yoldan en uzuna sırala
    sonuclar.sort(key=lambda x: x[1])
    return sonuclar

# 5. BAĞLI BİLEŞENLER

def bagli_bilesenleri_bul(dugumler, komsular):
    """
    Grafın kaç ayrı bağlı parçası olduğunu bulur.

    Yöntem: Ziyaret edilmemiş bir düğüm bul, BFS yap.
    BFS'in ulaştığı her düğüm aynı bileşende.
    Sonra ziyaret edilmemişlerden tekrar başla.

    Döndürür:
      Liste of set → her set bir bileşendeki düğümleri içerir.
    """
    ziyaret_edilmemis = set(dugumler.keys())
    bilesenleri = []

    while ziyaret_edilmemis:
        baslangic = next(iter(ziyaret_edilmemis))  # herhangi bir başlangıç al
        sonuc = bfs(komsular, baslangic)
        bilesen = set(sonuc["ziyaret_sirasi"])
        bilesenleri.append(bilesen)
        ziyaret_edilmemis -= bilesen  # bu bileşeni çıkar

    # Büyükten küçüğe sırala
    bilesenleri.sort(key=len, reverse=True)
    return bilesenleri

# 6. TOPOLOJİK SIRALAMA (Kahn Algoritması)

def topolojik_siralama(dugumler, komsular, kenarlar):
    """
    Yönlü Asiklik Graf (DAG) için topolojik sıralama.
    Her u→v kenarı için u, v'den önce gelir.

    Kahn Algoritması (BFS tabanlı):
      1. Her düğümün giren derece sayısını hesapla.
      2. Giren derecesi 0 olan düğümleri kuyruğa al.
      3. Kuyruktan düğüm çek, çıktıya ekle.
         Bu düğümün komşularının giren derecesini 1 azalt.
         Giren derecesi 0 olan komşuları kuyruğa al.
      4. Tüm düğümler işlenene kadar devam et.

    Döngü varsa tüm düğümler işlenemez → ValueError fırlatır.
    """
    # Her düğümün giren derecesini hesapla
    giren = {d: 0 for d in dugumler}
    for k in kenarlar:
        giren[k["hedef"]] += 1

    # Giren derecesi 0 olanları kuyruğa al
    kuyruk = [d for d in dugumler if giren[d] == 0]
    sira = []

    while kuyruk:
        mevcut = kuyruk.pop(0)
        sira.append(mevcut)

        for komsu in komsular.get(mevcut, []):
            giren[komsu] -= 1
            if giren[komsu] == 0:
                kuyruk.append(komsu)

    if len(sira) != len(dugumler):
        raise ValueError("Grafta döngü var! Topolojik sıralama yapılamaz.")

    return sira

# 7. HAMİLTON YOLU VE DÖNGÜSÜ

def _hamilton_backtrack(komsular, dugum_listesi, mevcut, yol, ziyaret):
    """
    Hamilton için yardımcı backtracking fonksiyonu.
    Tüm düğümleri tam bir kez ziyaret eden yol arar.
    """
    if len(yol) == len(dugum_listesi):
        return yol  # tüm düğümler ziyaret edildi → yol bulundu

    for komsu in komsular.get(mevcut, []):
        if komsu not in ziyaret:
            ziyaret.add(komsu)
            yol.append(komsu)
            sonuc = _hamilton_backtrack(komsular, dugum_listesi, komsu, yol, ziyaret)
            if sonuc is not None:
                return sonuc
            yol.pop()
            ziyaret.remove(komsu)

    return None  # bu daldan yol yok, geri dön


def hamilton_yolu_bul(dugumler, komsular, baslangic=None):
    """
    Grafta Hamilton yolu arar: her düğümden tam bir kez geçen yol.

    baslangic=None ise tüm düğümlerden dener.

    Döndürür:
      { "yol": [...], "bulundu": True/False }
    """
    dugum_listesi = list(dugumler.keys())

    baslangiclar = [baslangic] if baslangic else dugum_listesi

    for b in baslangiclar:
        ziyaret = {b}
        yol = [b]
        sonuc = _hamilton_backtrack(komsular, dugum_listesi, b, yol, ziyaret)
        if sonuc is not None:
            return {"yol": sonuc, "bulundu": True}

    return {"yol": [], "bulundu": False}


def hamilton_dongusu_bul(dugumler, komsular, baslangic=None):
    """
    Grafta Hamilton döngüsü arar: her düğümden tam bir kez geçip
    başlangıç düğümüne dönen yol.

    Döndürür:
      { "yol": [...], "bulundu": True/False }
      yol'un son elemanı başlangıca eşittir (döngü kapalıdır)
    """
    dugum_listesi = list(dugumler.keys())

    baslangiclar = [baslangic] if baslangic else dugum_listesi

    for b in baslangiclar:
        ziyaret = {b}
        yol = [b]
        sonuc = _hamilton_backtrack(komsular, dugum_listesi, b, yol, ziyaret)
        if sonuc is not None:
            # Son düğümden başlangıca kenar var mı?
            if b in komsular.get(sonuc[-1], []):
                return {"yol": sonuc + [b], "bulundu": True}

    return {"yol": [], "bulundu": False}


# YAZDIRMA

def sonuc_yazdir(algoritma, baslangic, hedef, sonuc):
    """Algoritma sonucunu düzenli şekilde yazdırır."""
    print(f"\n── {algoritma}: {baslangic} → {hedef if hedef else '(tam keşif)'} ──")
    print(f"  Ziyaret sırası : {' → '.join(str(d) for d in sonuc['ziyaret_sirasi'])}")
    if sonuc.get("yol"):
        print(f"  Yol            : {' → '.join(str(d) for d in sonuc['yol'])}")
    if sonuc.get("maliyet") is not None and sonuc.get("maliyet") != float("inf"):
        print(f"  Maliyet        : {sonuc['maliyet']}")
    if sonuc.get("bulundu") is not None:
        print(f"  Bulundu mu?    : {'✓' if sonuc['bulundu'] else '✗'}")
    if "dongu_var" in sonuc:
        print(f"  Döngü var mı?  : {'Evet' if sonuc['dongu_var'] else 'Hayır'}")
# 8. GEZGİN SATICI PROBLEMİ (TSP) — En Yakın Komşu Sezgisel

def tsp_en_yakin_komsu(dugumler, komsular, kenarlar, baslangic=None):
    """
    TSP: Tüm şehirleri tam bir kez ziyaret edip başa dönen
    en kısa turu bulur (nearest neighbor sezgisel algoritma).

    Nasıl çalışır:
      1. Başlangıç düğümünden başla.
      2. Her adımda henüz ziyaret edilmemiş en yakın komşuya git.
      3. Tüm düğümler ziyaret edilince başa dön.

    Döndürür:
      { "yol": [..., baslangic], "maliyet": toplam_km, "bulundu": True/False }
    """
    dugum_listesi = list(dugumler.keys())
    if not dugum_listesi:
        return {"yol": [], "maliyet": float("inf"), "bulundu": False}

    baslangic = baslangic or dugum_listesi[0]
    ziyaret_edildi = {baslangic}
    yol = [baslangic]
    mevcut = baslangic
    toplam_km = 0.0

    while len(ziyaret_edildi) < len(dugum_listesi):
        en_yakin = None
        en_kisa = float("inf")

        for komsu in komsular.get(mevcut, []):
            if komsu not in ziyaret_edildi:
                mesafe = kenar_agirlik(kenarlar, mevcut, komsu)
                if mesafe == float("inf"):
                    mesafe = kenar_agirlik(kenarlar, komsu, mevcut)
                if mesafe < en_kisa:
                    en_kisa = mesafe
                    en_yakin = komsu

        if en_yakin is None:
            return {"yol": yol, "maliyet": float("inf"), "bulundu": False}

        ziyaret_edildi.add(en_yakin)
        yol.append(en_yakin)
        toplam_km += en_kisa
        mevcut = en_yakin

    # Başa dön
    donus = kenar_agirlik(kenarlar, mevcut, baslangic)
    if donus == float("inf"):
        donus = kenar_agirlik(kenarlar, baslangic, mevcut)
    if donus == float("inf"):
        return {"yol": yol, "maliyet": float("inf"), "bulundu": False}

    toplam_km += donus
    yol.append(baslangic)

    return {"yol": yol, "maliyet": toplam_km, "bulundu": True}