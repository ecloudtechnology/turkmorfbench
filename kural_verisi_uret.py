# -*- coding: utf-8 -*-
"""Kural kovaları için KIYAS DIŞI sentetik eğitim verisi: kısaltma, sayı, çatı.

NEDEN BU ÜÇÜ
  Erk-32B'nin kanarya-2b'ye kaybettiği beş kovanın üçü ezber değil KURAL:
    kisaltma  harfler okunur, son harfin ADINA uyum: TCDD -> te-ce-de-de -> TCDD'yi
    sayi      sayı okunur, son KELİMEYE uyum:        2026 -> yirmi altı -> 2026'da
    cati      edilgen biçimbirimi -l/-n, ettirgen -DIr
  Külliyatta bu biçimler kıt değil (200 MB'de ~17 bin kısaltma+ek, ~17 bin
  sayı+ek); model onları görmüş ama kuralı içselleştirmemiş. Sentetik veri
  kuralı yoğun ve temiz gösterir.

KONTAMİNASYON SIFIR
  Kıyastaki 152 kısaltma, 304 sayı, 452 çatı gövdesi `kiyas_govdeleri_dislanacak.json`
  ile DIŞLANIR; üretilen her örnek bu listeye karşı denetlenir. Sayılar sonsuz,
  kısaltmalar rastgele harf dizisi (harf-harf okunur), fiiller kıyas dışından.
  Amaç modelin KURALI öğrenmesi; kıyas maddesini görmesi değil.
"""
import json
import os
import random
import re
import sys

KOK = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, KOK)
import ad_cekim  # noqa: E402
import ses  # noqa: E402
import sayi as sayi_mod  # noqa: E402

try:
    import turetme  # noqa: E402
except Exception:
    turetme = None

DISLA = json.load(open(os.path.join(KOK, "kiyas_govdeleri_dislanacak.json")))
DISLA_KIS = {x.upper() for x in DISLA["istisna_kisaltma"]}
DISLA_SAYI = set(DISLA["istisna_sayi"])
DISLA_CATI = set(DISLA["cati"])

# Türk alfabesinde harf ADLARI — kısaltma harf harf okunur, uyum son harfin adına
HARF_ADI = {"A": "a", "B": "be", "C": "ce", "Ç": "çe", "D": "de", "E": "e", "F": "fe",
            "G": "ge", "H": "he", "I": "ı", "İ": "i", "J": "je", "K": "ke", "L": "le",
            "M": "me", "N": "ne", "O": "o", "Ö": "ö", "P": "pe", "R": "re", "S": "se",
            "Ş": "şe", "T": "te", "U": "u", "Ü": "ü", "V": "ve", "Y": "ye", "Z": "ze"}
HALLER = ["belirtme", "yonelme", "bulunma", "ayrilma", "tamlayan"]

CERCEVE_AD = ["{X} hakkında yeni bir karar alındı.", "Toplantı {X} yapıldı.",
              "Rapor {X} gönderildi.", "{X} gelen açıklama şöyle:",
              "Bu konu {X} görüşülecek.", "{X} sorumluluğu artırıldı.",
              "Verilerin çoğu {X} alındı.", "{X} ilgili düzenleme yürürlükte."]


def kisaltma_ornek(rng):
    for _ in range(50):
        n = rng.choice([2, 3, 3, 4])
        kis = "".join(rng.choice("BCDFGHJKLMNPRSTVYZ") for _ in range(n))
        if kis in DISLA_KIS:
            continue
        okunus = "".join(HARF_ADI[c] for c in kis)
        hal = rng.choice(HALLER)
        ek = ses.coz(ad_cekim.HAL[hal], okunus)
        bicim = kis + "'" + ek
        return {"kova": "kisaltma", "govde": kis, "okunus": okunus, "hal": hal,
                "bicim": bicim, "cumle": rng.choice(CERCEVE_AD).format(X=bicim)}
    return None


def sayi_ornek(rng):
    for _ in range(50):
        n = rng.choice([rng.randint(10, 99), rng.randint(100, 999), rng.randint(1000, 9999),
                        rng.choice([1000, 2000, 5000]) * rng.randint(1, 9)])
        if str(n) in DISLA_SAYI:
            continue
        okunus = sayi_mod.oku(n)
        if not okunus:
            continue
        son = okunus.split()[-1]
        hal = rng.choice(HALLER)
        ek = ses.coz(ad_cekim.HAL[hal], son)
        bicim = "%d'%s" % (n, ek)
        return {"kova": "sayi", "govde": str(n), "okunus": okunus, "hal": hal,
                "bicim": bicim, "cumle": rng.choice(CERCEVE_AD).format(X=bicim)}
    return None


def fiil_kaynagi():
    """Kıyas dışı fiil gövdeleri — kıyasın kendi sözlük kaynağından, kıyas
    gövdeleri DIŞLANARAK. Aynı kaynak, ayrı gövdeler: kural aynı, madde farklı."""
    import sozluk
    ham = sozluk.yukle(("master", "non_tdk"))
    govdeler = set()
    for m in ham:
        if m.tur != "Verb":
            continue
        g = m.govde.lower()
        if g.endswith(("mak", "mek")):          # sözlük mastar tutar; gövde soyulur
            g = g[:-3]
        if g in DISLA_CATI or len(g) < 2 or not g.isalpha():
            continue
        if g[-1] in "aeıioöuü":          # ünlüyle biten fiiller: edilgen -n; ayrı sınıf, dahil
            pass
        govdeler.add(g)
    return sorted(govdeler)


CERCEVE_FIIL = ["Kapı {X}.", "İş dün {X}.", "Sonunda her şey {X}.", "Konu {X}.",
                "Mektup {X}.", "Bu yıl plan {X}."]


def cati_ornek(rng, fiiller):
    if not fiiller or turetme is None:
        return None
    for _ in range(50):
        g = rng.choice(fiiller)
        tur = rng.choice(["edilgen", "edilgen", "ettirgen"])
        try:
            if tur == "edilgen":
                govde = g + ses.coz(turetme.edilgen_ek(g), g)
            else:
                govde = g + ses.coz("DIr", g)
        except Exception:
            continue
        # geçmiş zaman 3. tekil: -DI
        bicim = govde + ses.coz("DI", govde)
        return {"kova": "cati_" + tur, "govde": g, "bicim": bicim,
                "cumle": rng.choice(CERCEVE_FIIL).format(X=bicim)}
    return None


def main(n_her=int(os.environ.get("N_HER", "20000")), tohum=20260925):
    rng = random.Random(tohum)
    fiiller = fiil_kaynagi()
    print("kıyas dışı fiil gövdesi:", len(fiiller))
    cik = {"kisaltma": [], "sayi": [], "cati": []}
    while len(cik["kisaltma"]) < n_her:
        o = kisaltma_ornek(rng)
        if o: cik["kisaltma"].append(o)
    while len(cik["sayi"]) < n_her:
        o = sayi_ornek(rng)
        if o: cik["sayi"].append(o)
    while fiiller and turetme is not None and len(cik["cati"]) < n_her:
        o = cati_ornek(rng, fiiller)
        if o: cik["cati"].append(o)

    # KONTAMİNASYON DENETİMİ — her örnek kıyas listesine karşı
    # KOVA BAZLI: kısaltma yalnız kısaltma listesine, sayı sayıya, fiil fiile
    # bakılır. Üç listeye birden bakmak yanlış pozitif üretiyordu ("kes" fiili
    # büyük harfe çevrilince bir kısaltmayla çakışıyordu).
    ihlal = 0
    for k, L in cik.items():
        for o in L:
            g = o["govde"]
            if k == "kisaltma" and g.upper() in DISLA_KIS: ihlal += 1
            elif k == "sayi" and g in DISLA_SAYI: ihlal += 1
            elif k == "cati" and g in DISLA_CATI: ihlal += 1
    assert ihlal == 0, "KONTAMİNASYON: %d örnek kıyas gövdesi taşıyor" % ihlal

    with open(os.path.join(KOK, "kural_verisi.jsonl"), "w", encoding="utf8") as f:
        for k, L in cik.items():
            for o in L:
                f.write(json.dumps(o, ensure_ascii=False) + "\n")
    with open(os.path.join(KOK, "kural_verisi_metin.txt"), "w", encoding="utf8") as f:
        for k, L in cik.items():
            for o in L:
                f.write(o["cumle"] + "\n")
    for k, L in cik.items():
        print("  %-9s %6d örnek · örnek: %s" % (k, len(L), L[0]["cumle"] if L else "-"))
    print("kontaminasyon: 0 ✓ · yazıldı: kural_verisi.jsonl, kural_verisi_metin.txt")


if __name__ == "__main__":
    main()
