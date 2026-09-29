# -*- coding: utf-8 -*-
"""İnsan tavanı — toplanan yargıları puanlar.

KULLANIM
    scp aigency-server:/home/morf.e-cloud.web.tr/veri/yargi.sqlite .
    python3 insan_puanla.py yargi.sqlite

GİRDİ   yargi.sqlite      : morf.e-cloud.web.tr'den çekilen veritabanı
                            (ya da aynı biçimde bir .json)
        insan_ornegi.json : altın anahtar — sayfaya HİÇ gönderilmedi,
                            yalnız burada durur

ÇIKTI   kova başına insan doğruluğu + Wilson aralığı
        Fleiss kappa (değerlendiriciler arası uyum)
        çift-bazlı ham uyum

NEDEN İKİ UYUM ÖLÇÜSÜ
  Fleiss kappa şansa göre düzeltir ama kategori kimliği maddeler arası
  ortak olmalı. Seçenekler madde başına karıştırıldığı için ham indeks
  ortak değil; bu yüzden her yargı KANONİK kategoriye çevrilir:
  0 = altın, 1..n = o maddenin çeldirici sırası. Altın her maddede 0'dır,
  dolayısıyla kategori kimliği anlamlıdır. Ham çift uyumu ise düzeltmesiz
  ve yorumu tartışmasız; ikisi birlikte verilir.

  Kappa paradoksu: değerlendiriciler çok doğruyken kategori marjinalleri
  çarpıklaşır, Fleiss'in şans terimi gözlenen uyuma yaklaşır ve kappa
  yüksek uyuma rağmen sıfıra iner. Bu bir arıza değil, o katsayının bilinen
  davranışı. Yanına Gwet AC1 konur; aynı gözlenen uyumu çarpıklığa dayanıklı
  bir şans terimiyle düzeltir. İkisi ayrıştığında ayrışma tek başına bilgidir.

  Tek bir sayı yayımlamıyoruz: insan tavanı bir aralıktır ve uyum ölçüsü
  olmadan "tavan" iddiası denetlenemez.
"""
import collections
import io
import json
import math
import sys


def wilson(basari, toplam, z=1.96):
    if toplam == 0:
        return (0.0, 0.0, 0.0)
    p = basari / toplam
    payda = 1 + z * z / toplam
    orta = (p + z * z / (2 * toplam)) / payda
    yari = z * math.sqrt(p * (1 - p) / toplam + z * z / (4 * toplam * toplam)) / payda
    return (p, max(0.0, orta - yari), min(1.0, orta + yari))


def fleiss(sayimlar, k):
    """sayimlar: madde başına [kategori sayıları]; k: kategori sayısı.

    Yalnız DEĞERLENDİRİCİ SAYISI EŞİT maddeler alınır — Fleiss bunu şart
    koşar. Eksik kalan maddeler sessizce karışırsa kappa bozulur.
    """
    sayimlar = [s for s in sayimlar if sum(s) >= 2]
    if not sayimlar:
        raise ValueError("madde başına en az iki yargı gerekir")
    N = len(sayimlar)
    toplam = sum(sum(s) for s in sayimlar)
    P = [(sum(x * x for x in s) - sum(s)) / (sum(s) * (sum(s) - 1)) for s in sayimlar]
    p = [sum(s[j] for s in sayimlar) / toplam for j in range(k)]
    Pbar = sum(P) / N
    Pe = sum(x * x for x in p)
    return (Pbar - Pe) / (1 - Pe) if Pe < 1 else 1.0


def gwet_ac1(sayimlar, k):
    """Gwet AC1 — Fleiss ile aynı gözlenen uyum, farklı şans terimi.

    Fleiss şansı `Σ p_j²` sayar; bir kategori baskınsa bu terim şişer ve
    katsayı çöker. AC1 şansı `Σ p_j(1-p_j)/(k-1)` sayar: baskın kategoride
    küçülür, tam da çarpık marjinallerin katsayıyı bozduğu yerde.
    """
    sayimlar = [s for s in sayimlar if sum(s) >= 2]
    N = len(sayimlar)
    toplam = sum(sum(s) for s in sayimlar)
    Pbar = sum((sum(x * x for x in s) - sum(s)) / (sum(s) * (sum(s) - 1))
               for s in sayimlar) / N
    p = [sum(s[j] for s in sayimlar) / toplam for j in range(k)]
    Pe = sum(x * (1 - x) for x in p) / (k - 1) if k > 1 else 0.0
    return (Pbar - Pe) / (1 - Pe) if Pe < 1 else 1.0


def cift_uyum(yargilar):
    """Aynı maddeye bakan her değerlendirici çifti hemfikir mi."""
    ayni = capraz = 0
    for v in yargilar:
        for a in range(len(v)):
            for b in range(a + 1, len(v)):
                capraz += 1
                ayni += int(v[a] == v[b])
    return ayni / capraz if capraz else 0.0


def binom_ust_p(basari, n, p0):
    """P(X >= basari | n, p0) — tek yönlü binom testi, kütüphanesiz."""
    from math import comb
    return sum(comb(n, i) * p0 ** i * (1 - p0) ** (n - i) for i in range(basari, n + 1))


def ele(kisi_yargi, ornek, en_az_sn=3.0, alfa=0.001):
    """Katılımcı taraması — ölçümü koruyan asıl savunma.

    İki ölçüt, ikisi de dışarıdan denetlenebilir:

      HIZ     soru başına medyan süre `en_az_sn`nin altındaysa elenir.
              Bir Türkçe çekim sorusunu okuyup üç şıkkı karşılaştırmak
              üç saniyeden kısa sürmez; altına inen kişi soruyu okumuyor.

      ŞANS    doğruluğu kendi şans düzeyini anlamlı biçimde geçemeyen
              elenir. Şans düzeyi kişiye özeldir: gördüğü maddelerin şık
              sayıları farklı olduğu için 1/n'lerin ortalamasıdır.

    Eşikler önceden yazılır ve sonuca bakılarak değiştirilmez; aksi hâlde
    eleme, istenen sayıyı üreten bir ayar düğmesine dönüşür.
    """
    import datetime
    from statistics import median
    tut, at = {}, {}
    for j, kayit in kisi_yargi.items():
        n = len(kayit)
        if n < 10:
            at[j] = ("az cevap", n, None, None)
            continue
        zaman = sorted(datetime.datetime.fromisoformat(a) for _, _, a in kayit)
        araliklar = [(zaman[i + 1] - zaman[i]).total_seconds() for i in range(len(zaman) - 1)]
        hiz = median(araliklar) if araliklar else 0.0
        dogru = sum(1 for k, sec, _ in kayit if sec == ornek[k]["dogru"])
        sans = sum(1.0 / len(ornek[k]["ops"]) for k, _, _ in kayit) / n
        pdeg = binom_ust_p(dogru, n, sans)
        if hiz < en_az_sn:
            at[j] = ("cok hizli (%.1f sn)" % hiz, n, dogru / n, pdeg)
        elif pdeg > alfa:
            at[j] = ("sanstan ayrilmiyor (p=%.3f)" % pdeg, n, dogru / n, pdeg)
        else:
            tut[j] = (n, dogru / n, hiz, pdeg)
    return tut, at


def oku_yargilar(yol):
    """SQLite ya da JSON — ikisini de kabul eder, aynı biçimi döndürür."""
    if yol.endswith((".sqlite", ".db", ".sqlite3")):
        import sqlite3
        b = sqlite3.connect("file:%s?mode=ro" % yol, uri=True)
        kisi = collections.defaultdict(dict)
        an = collections.defaultdict(dict)
        for jeton, madde, secim, t in b.execute(
                "SELECT jeton, madde, secim, an FROM yargi"):
            kisi[jeton][madde] = secim
            an[jeton][madde] = t
        b.close()
        return [{"uid": j, "cevap": c, "an": an[j]} for j, c in kisi.items()]
    return json.load(io.open(yol, encoding="utf8"))


def main(yargi_yolu="yargi.sqlite", ornek_yolu="insan_ornegi.json"):
    ornek = {m["k"]: m for m in json.load(io.open(ornek_yolu, encoding="utf8"))}
    belgeler = oku_yargilar(yargi_yolu)

    # --- tarama: ölçüme girecek katılımcıyı belirle ---
    ham = collections.defaultdict(list)
    for b in belgeler:
        u = b.get("uid") or "?"
        zamanlar = b.get("an") or {}
        for k, ix in (b.get("cevap") or {}).items():
            if k in ornek and k in zamanlar:
                ham[u].append((k, int(ix), zamanlar[k]))
    tut, at = ele(ham, ornek) if ham else ({}, {})

    print("KATILIMCI TARAMASI")
    for u, (n, dog, hiz, pd) in sorted(tut.items(), key=lambda x: -x[1][0]):
        print("   ALINDI   %-12s %4d cevap  %%%.1f  %.0f sn/soru  p=%.1e"
              % (u[:12], n, 100 * dog, hiz, pd))
    for u, (sebep, n, dog, pd) in sorted(at.items(), key=lambda x: -x[1][1]):
        print("   ELENDİ   %-12s %4d cevap  %s%s"
              % (u[:12], n, "%%%.1f  " % (100 * dog) if dog else "", sebep))
    if tut:
        belgeler = [b for b in belgeler if (b.get("uid") or "?") in tut]
        print("   -> ölçüme giren: %d kişi" % len(tut))

    toplu = collections.defaultdict(list)
    kisi = collections.Counter()
    for b in belgeler:
        uid = b.get("uid") or "?"
        for k, ix in (b.get("cevap") or {}).items():
            if k in ornek:
                toplu[k].append(int(ix))
                kisi[uid] += 1

    print("\nDEĞERLENDİRİCİ  %d kişi, %d yargı" % (len(kisi), sum(kisi.values())))

    dagilim = collections.Counter(len(v) for v in toplu.values())
    print("\nMADDE BAŞINA YARGI  " +
          "  ".join("%d yargı: %d madde" % (n, c) for n, c in sorted(dagilim.items())))
    print("kapsanan madde %d / %d" % (len(toplu), len(ornek)))

    # --- doğruluk: her yargı ayrı ayrı sayılır (kişi-madde birimi) ---
    print("\nİNSAN DOĞRULUĞU (kova bazında, %95 Wilson)")
    kova = collections.defaultdict(lambda: [0, 0])
    gercek = collections.defaultdict(lambda: [0, 0])
    for k, secimler in toplu.items():
        m = ornek[k]
        for s in secimler:
            d = int(s == m["dogru"])
            kova[m["kova"]][0] += d
            kova[m["kova"]][1] += 1
            g = "gerçek gövde" if m["gercek"] else "uydurma gövde"
            gercek[g][0] += d
            gercek[g][1] += 1

    t_d = sum(v[0] for v in kova.values())
    t_n = sum(v[1] for v in kova.values())
    for ad, (d, n) in sorted(kova.items(), key=lambda x: -x[1][0] / max(1, x[1][1])):
        p, a, u = wilson(d, n)
        print("  %-26s %4d/%-4d  %%%.1f   [%%%.1f – %%%.1f]" %
              (ad, d, n, 100 * p, 100 * a, 100 * u))
    print("  " + "-" * 62)
    for ad, (d, n) in sorted(gercek.items()):
        p, a, u = wilson(d, n)
        print("  %-26s %4d/%-4d  %%%.1f   [%%%.1f – %%%.1f]" %
              (ad, d, n, 100 * p, 100 * a, 100 * u))
    p, a, u = wilson(t_d, t_n)
    print("  %-26s %4d/%-4d  %%%.1f   [%%%.1f – %%%.1f]  <- İNSAN TAVANI" %
          ("TOPLAM", t_d, t_n, 100 * p, 100 * a, 100 * u))

    # --- uyum: yalnız tam yargılanmış maddeler ---
    tam_k = [k for k, v in toplu.items() if len(v) >= 2]
    if len(tam_k) < 2:
        print("\nUYUM  hesaplanamadı (iki ve üzeri yargı alan madde yok)")
        return
    hedef = sum(len(toplu[k]) for k in tam_k) / len(tam_k)
    K = max(len(ornek[k]["ops"]) for k in tam_k)

    # kanonik kategori: 0 = altın, 1.. = çeldirici sırası
    sayimlar = []
    kanonik = []
    for k in tam_k:
        m = ornek[k]
        sira = [m["dogru"]] + [i for i in range(len(m["ops"])) if i != m["dogru"]]
        eslesme = {ix: j for j, ix in enumerate(sira)}
        kat = [eslesme[s] for s in toplu[k]]
        kanonik.append(kat)
        c = [0] * K
        for j in kat:
            c[j] += 1
        sayimlar.append(c)

    kappa = fleiss(sayimlar, K)
    ac1 = gwet_ac1(sayimlar, K)
    altin_pay = sum(s[0] for s in sayimlar) / sum(sum(s) for s in sayimlar)
    print("\nDEĞERLENDİRİCİLER ARASI UYUM  (%d madde, madde başına ort. %.1f yargı)"
          % (len(tam_k), hedef))
    print("  Fleiss kappa        %.3f" % kappa)
    print("  Gwet AC1            %.3f" % ac1)
    print("  ham çift uyumu      %%%.1f" % (100 * cift_uyum(kanonik)))
    print("  tam ittifak         %%%.1f" %
          (100 * sum(len(set(v)) == 1 for v in kanonik) / len(kanonik)))
    print("  altın kategori payı %%%.1f" % (100 * altin_pay))
    if altin_pay > 0.8 and kappa < ac1 - 0.15:
        print("  NOT: marjinaller çarpık (altın payı yüksek). Fleiss kappa bu")
        print("       koşulda gözlenen uyumu olduğundan düşük gösterir; AC1 okunmalı.")


if __name__ == "__main__":
    main(*sys.argv[1:])
