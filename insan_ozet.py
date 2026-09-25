# -*- coding: utf-8 -*-
"""İnsan tavanı — YAYIMLANAN sayıların tek kaynağı.

KURALLAR (önceden yazılı, sonuca bakılarak değiştirilmez)
  n ≥ 10 · soru başına medyan süre ≥ 3,0 sn · doğruluk kendi şans düzeyini
  binom testiyle geçmeli (tek yönlü, α = 0,001). Şans düzeyi kişiye özeldir:
  gördüğü maddelerin şık sayılarının 1/n ortalaması.

İKİ TUZAK, İKİSİ DE YAŞANDI
  1. `dogru` alanı bir DİZİNDİR, dize değil. Dize sanmak herkesi %0 gösterir.
  2. Havuz 24 Eyl 2026 13:31:48 +03'te yenilendi ve şık sıraları yeniden
     karıştırıldı. Ortak 257 maddenin 230'unda sıra farklı; hangi havuzun
     sırasına bakılacağı YARGININ ZAMANINA göre seçilir.

SÜRE HESABI
  Zaman damgaları saniye çözünürlüğünde. Sıfır saniyelik aralıklar ATILMAZ —
  111 soruyu 36 saniyede cevaplayan birinin aralıklarının çoğu sıfırdır ve
  tam da hızlı tıklamanın kanıtı odur.
"""
import collections
import json
import os
import statistics
import sys
from datetime import datetime, timezone
from math import comb

KOK = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(KOK, "paket"))
from turkmorfbench.istatistik import kume_bootstrap        # noqa: E402

HAM = os.environ.get("HAM", os.path.join(KOK, "insan_ham.json"))
DEGISIM = datetime(2026, 9, 24, 10, 31, 48, tzinfo=timezone.utc)
EN_AZ_N, EN_AZ_SN, ALFA = 10, 3.0, 0.001


def binom_ust(basari, n, p0):
    return sum(comb(n, i) * p0 ** i * (1 - p0) ** (n - i) for i in range(basari, n + 1))


def an(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def main():
    eski = {m["k"]: m for m in json.load(open(os.path.join(KOK, "insan_ornegi.json")))}
    yeni = {m["k"]: m for m in json.load(open(os.path.join(KOK, "insan_ornegi_v2.json")))}
    tam = {m["kimlik"]: m for m in
           json.load(open(os.path.join(KOK, "turkmorfbench_v3_tam.json")))["maddeler"]}
    ham = json.load(open(HAM))

    yargi = collections.defaultdict(list)
    for y in ham["yargi"]:
        yargi[y["jeton"]].append(y)

    def coz(y):
        h = eski if an(y["an"]) < DEGISIM else yeni
        m = h.get(y["madde"]) or (yeni if h is eski else eski).get(y["madde"])
        return (None, None) if m is None else ((y["secim"] == m["dogru"]), m)

    print("%-10s %5s %8s %8s %9s %10s  %s"
          % ("kişi", "n", "doğru", "şans", "medyan sn", "binom p", "karar"))
    gecerli, kisi_oran = [], []
    for j, ys in sorted(yargi.items(), key=lambda x: -len(x[1])):
        ys = sorted(ys, key=lambda y: y["an"])
        e = [(ok, m, y) for ok, m, y in ((coz(y) + (y,)) for y in ys) if ok is not None]
        if not e:
            continue
        n = len(e)
        dog = sum(x for x, _, _ in e)
        sans = sum(1 / len(m["ops"]) for _, m, _ in e) / n
        z = sorted(an(y["an"]) for _, _, y in e)
        ar = [(z[i + 1] - z[i]).total_seconds() for i in range(len(z) - 1)]
        ar = [x for x in ar if 0 <= x < 300]          # 0 DAHİL
        med = statistics.median(ar) if ar else 0.0
        p = binom_ust(dog, n, sans)
        if n < EN_AZ_N:
            k = "ELENDİ (az cevap)"
        elif med < EN_AZ_SN:
            k = "ELENDİ (çok hızlı)"
        elif p > ALFA:
            k = "ELENDİ (şanstan ayrılmıyor)"
        else:
            k = "geçerli"
        print("%-10s %5d %7.1f%% %7.1f%% %9.1f %10.1e  %s"
              % (j[:8], n, 100 * dog / n, 100 * sans, med, p, k))
        if k == "geçerli":
            kisi_oran.append(dog / n)
            for ok, m, _ in e:
                t = tam.get(m["k"])
                if t:
                    gecerli.append((t, ok))

    print("\nGEÇERLİ: %d yargı · %d/%d kişi · kişi başına doğruluk %s"
          % (len(gecerli), len(kisi_oran), len(yargi),
             ", ".join("%.1f%%" % (100 * x) for x in sorted(kisi_oran, reverse=True))))

    M = [m for m, _ in gecerli]
    D = [x for _, x in gecerli]
    ozet = {"n_yargi": len(gecerli), "n_kisi_gecerli": len(kisi_oran),
            "n_kisi_toplam": len(yargi), "kisi_oranlari": sorted(kisi_oran, reverse=True)}
    for a in ("madde", "govde", "hucre"):
        try:
            s = kume_bootstrap(M, D, a, b=5000)
            ozet[a] = {"oran": s.ortalama, "ci": list(s.ci), "n_kume": s.n_kume}
            print("  %-7s %.1f%% [%.1f%%, %.1f%%]  (%d küme)"
                  % (a, 100 * s.ortalama, 100 * s.ci[0], 100 * s.ci[1], s.n_kume))
        except ValueError as e:
            print("  %-7s atlandı: %s" % (a, e))

    for ad, bay in (("gercek", True), ("uydurma", False)):
        alt = [(m, x) for m, x in gecerli if m.get("gercek") is bay]
        if not alt:
            continue
        try:
            s = kume_bootstrap([m for m, _ in alt], [x for _, x in alt], "govde", b=5000)
            ozet[ad] = {"oran": s.ortalama, "ci": list(s.ci), "n": len(alt)}
            print("  %-8s %.1f%% [%.1f%%, %.1f%%]  (n=%d)"
                  % (ad, 100 * s.ortalama, 100 * s.ci[0], 100 * s.ci[1], len(alt)))
        except ValueError:
            ozet[ad] = {"oran": sum(x for _, x in alt) / len(alt), "ci": None, "n": len(alt)}

    json.dump(ozet, open(os.path.join(KOK, "insan_ozet.json"), "w"),
              ensure_ascii=False, indent=1)
    print("\nyazıldı: insan_ozet.json")


if __name__ == "__main__":
    main()
