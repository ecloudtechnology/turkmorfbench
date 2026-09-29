# -*- coding: utf-8 -*-
"""Küme (cluster) bootstrap — 466.517 madde 466.517 bağımsız gözlem DEĞİLDİR.

NEDEN BU MODÜL VAR
  Kıyastaki maddeler birbirinden bağımsız üretilmez. Tek bir gövde (*kitap*)
  çokluk × iyelik × hâl çaprazından yüzlerce madde doğurur; tek bir fonolojik
  hücre (son ünlü, son ünsüz sınıfı, derinlik, uyum) yüzlerce gövdeyi aynı
  kurala bağlar. Bir model *kitap* gövdesinde yumuşamayı kaçırıyorsa, o
  gövdeden türeyen maddelerin çoğunda birlikte kaçırır.

  Madde düzeyinde klasik bootstrap bunu görmezden gelir: her maddeyi ayrı bir
  gözlem sayar, örneklem büyüklüğünü olduğundan büyük gösterir ve güven
  aralığını gereğinden dar üretir. Bu, sahte kesinliktir (pseudo-replication).
  Yayımlanan bir sayının en kolay çürütülen yeri de burasıdır.

  Doğrusu, yeniden örnekleme birimini maddeden KÜMEYE taşımaktır. Kümeyi
  seçerken soru şudur: hangi birim tekrarlanabilir bir gözlemdir? Yeni bir
  gövde çekmek yeni bir gözlemdir; aynı gövdenin 300 çekimi değildir.

KULLANIM
    from turkmorfbench.istatistik import kume_bootstrap, esli_fark, tasarim_etkisi
    s = kume_bootstrap(maddeler, dogru, anahtar="govde")
    print(s.ortalama, s.ci)            # gövde kümeli güven aralığı
    print(tasarim_etkisi(maddeler, dogru, "govde"))   # kaç kat şişirme vardı

ANAHTAR SEÇENEKLERİ
    "madde"        kümeleme yok — yalnız KARŞILAŞTIRMA için, yayın için değil
    "govde"        gövde (birincil öneri)
    "hucre"        fonolojik hücre
    "kova"         kova
    "govde_gorev"  gövde × görev ÇAPRAZ anahtarı — tek aşamalı küme bootstrap'ı, iki aşamalı
                   (hiyerarşik) yeniden örnekleme DEĞİL; küme sayısı en çok olan anahtar
"""
import math
import random
from dataclasses import dataclass


def _anahtar_al(m, anahtar):
    if anahtar == "madde":
        return m.get("kimlik")
    if anahtar == "govde":
        return m.get("govde")
    if anahtar == "kova":
        return m.get("kova")
    if anahtar == "hucre":
        h = m.get("hucre")
        return tuple(h) if isinstance(h, list) else h
    if anahtar == "govde_gorev":
        return (m.get("govde"), m.get("gorev"))
    raise ValueError("bilinmeyen anahtar: %s" % anahtar)


def kumele(maddeler, dogru, anahtar):
    """{küme: [0/1, ...]} — her kümenin içindeki madde sonuçları."""
    if len(maddeler) != len(dogru):
        raise ValueError("madde ve sonuç sayısı farklı: %d vs %d"
                         % (len(maddeler), len(dogru)))
    kume = {}
    for m, d in zip(maddeler, dogru):
        kume.setdefault(_anahtar_al(m, anahtar), []).append(1 if d else 0)
    return kume


@dataclass
class Sonuc:
    ortalama: float
    ci: tuple
    n_madde: int
    n_kume: int
    anahtar: str
    b: int

    def __str__(self):
        return ("%.4f [%.4f, %.4f] · %s kümeli · %d madde / %d küme"
                % (self.ortalama, self.ci[0], self.ci[1],
                   self.anahtar, self.n_madde, self.n_kume))


def kume_bootstrap(maddeler, dogru, anahtar="govde", b=5000, tohum=20260924,
                   guven=0.95):
    """Küme yeniden örneklemeli bootstrap güven aralığı.

    Kümeler YERİNE KONARAK çekilir; seçilen kümenin TÜM maddeleri alınır.
    Böylece küme içi bağımlılık korunur ve aralık dürüst genişler.
    """
    kume = kumele(maddeler, dogru, anahtar)
    adlar = list(kume)
    if len(adlar) < 2:
        raise ValueError("bootstrap için en az 2 küme gerekir (bulunan: %d)"
                         % len(adlar))
    toplam = sum(sum(v) for v in kume.values())
    n = sum(len(v) for v in kume.values())
    nokta = toplam / n

    # Küme içi toplamlar bir kez hesaplanır; bootstrap O(B*K) olur, O(B*N) değil.
    # 465 bin maddede aradaki fark dakikalarla saatler arasındadır.
    ozet = [(sum(kume[a]), len(kume[a])) for a in adlar]
    rng = random.Random(tohum)
    k = len(ozet)
    ornekler = []
    for _ in range(b):
        pay = top = 0
        for _ in range(k):
            p, t = ozet[rng.randrange(k)]
            pay += p
            top += t
        if top:
            ornekler.append(pay / top)
    ornekler.sort()
    alt = ornekler[int((1 - guven) / 2 * len(ornekler))]
    ust = ornekler[min(len(ornekler) - 1,
                       int((1 + guven) / 2 * len(ornekler)))]
    return Sonuc(nokta, (alt, ust), n, k, anahtar, b)


def tasarim_etkisi(maddeler, dogru, anahtar="govde", b=2000, tohum=20260924):
    """Küme aralığı, madde aralığının kaç katı genişliğinde.

    1'e yakınsa kümeleme fark etmiyor demektir. Büyükse madde düzeyi
    bootstrap o oranda sahte kesinlik üretiyordur.
    """
    k = kume_bootstrap(maddeler, dogru, anahtar, b=b, tohum=tohum)
    m = kume_bootstrap(maddeler, dogru, "madde", b=b, tohum=tohum)
    gk = k.ci[1] - k.ci[0]
    gm = m.ci[1] - m.ci[0]
    kat = gk / gm if gm > 0 else float("inf")
    return {
        "anahtar": anahtar,
        "madde_ci": m.ci,
        "kume_ci": k.ci,
        "genislik_kati": kat,
        "etkin_n": int(k.n_madde / (kat ** 2)) if kat > 0 else 0,
        "n_madde": k.n_madde,
        "n_kume": k.n_kume,
    }


def esli_fark(maddeler, dogru_a, dogru_b, anahtar="govde", b=5000,
              tohum=20260924, guven=0.95):
    """İki sistemin FARKI için küme bootstrap — eşli, aynı maddeler üzerinde.

    İki ayrı güven aralığına bakıp 'çakışıyor mu' demek yanlıştır: bu, eşli
    tasarımın gücünü atar ve gerçek farkı gizleyebilir. Fark doğrudan
    örneklenir.
    """
    if not (len(maddeler) == len(dogru_a) == len(dogru_b)):
        raise ValueError("uzunluklar farklı")
    kume = {}
    for m, a, c in zip(maddeler, dogru_a, dogru_b):
        kume.setdefault(_anahtar_al(m, anahtar), []).append(
            ((1 if a else 0), (1 if c else 0)))
    adlar = list(kume)
    k = len(adlar)
    pa = sum(x for v in kume.values() for x, _ in v)
    pb = sum(y for v in kume.values() for _, y in v)
    n = sum(len(v) for v in kume.values())
    nokta = (pa - pb) / n

    ozet = [(sum(x for x, _ in kume[a]), sum(y for _, y in kume[a]), len(kume[a]))
            for a in adlar]
    rng = random.Random(tohum)
    ornekler = []
    for _ in range(b):
        sa = sb = top = 0
        for _ in range(k):
            p, q, t = ozet[rng.randrange(k)]
            sa += p
            sb += q
            top += t
        if top:
            ornekler.append((sa - sb) / top)
    ornekler.sort()
    alt = ornekler[int((1 - guven) / 2 * len(ornekler))]
    ust = ornekler[min(len(ornekler) - 1,
                       int((1 + guven) / 2 * len(ornekler)))]
    return {
        "fark": nokta,
        "ci": (alt, ust),
        "anlamli": (alt > 0) or (ust < 0),
        "anahtar": anahtar,
        "n_madde": n,
        "n_kume": k,
    }


def katmanli(maddeler, dogru, katman, anahtar="govde", b=2000, en_az_kume=5):
    """Katman katman (kova / gerçek-uydurma / derinlik) küme bootstrap."""
    gruplar = {}
    for m, d in zip(maddeler, dogru):
        gruplar.setdefault(katman(m), []).append((m, d))
    cikti = {}
    for ad, ciftler in sorted(gruplar.items(), key=lambda x: -len(x[1])):
        mm = [m for m, _ in ciftler]
        dd = [d for _, d in ciftler]
        if len(set(_anahtar_al(m, anahtar) for m in mm)) < en_az_kume:
            cikti[ad] = {"n": len(mm), "not": "küme sayısı yetersiz"}
            continue
        s = kume_bootstrap(mm, dd, anahtar, b=b)
        cikti[ad] = {"ortalama": s.ortalama, "ci": s.ci,
                     "n": s.n_madde, "n_kume": s.n_kume}
    return cikti
