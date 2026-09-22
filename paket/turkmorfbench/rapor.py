# -*- coding: utf-8 -*-
"""Teşhis raporu — kıyasın asıl çıktısı. Puan değil, nerede düştüğü.

Bir model geliştiricisine "%43 aldın" demek işe yaramaz. "Ünsüz yumuşamasını
bilmiyorsun, hataların %81'i orada; ve sözlüğün gövdeyi bozduğu kelimelerde
başarın 22 puan düşük" demek işe yarar. Rapor bunu üretir.
"""
import collections


def _oran(d, t):
    return (100.0 * d / t) if t else 0.0


def kesitler(maddeler, secim, uretim=None, jetonla=None):
    """Bütün kesitleri hesaplar. `secim`: {kimlik: (dogru, secilen_celdirici)}"""
    ix = {m["kimlik"]: m for m in maddeler}
    K = collections.defaultdict(lambda: [0, 0])
    hata = collections.Counter()

    def ekle(ad, d):
        K[ad][1] += 1
        K[ad][0] += int(d)

    for k, (d, sec) in secim.items():
        m = ix.get(k)
        if not m:
            continue
        ekle("TOPLAM", d)
        ekle("kova: " + m["kova"], d)
        ekle("görev: " + m["gorev"], d)
        ekle("gerçek gövde" if m["gercek"] else "uydurma gövde", d)
        if m.get("derinlik"):
            ekle("zincir derinliği %d" % m["derinlik"], d)
        h = m.get("hucre")
        if h:
            ekle("son ses: " + h[1], d)
            ekle("hece %s" % h[2], d)
            ekle("iç uyum: " + h[3], d)
        for b in (m.get("bayrak") or []):
            ekle("sözlük bayrağı: " + b, d)
        if not d and sec:
            hata[sec] += 1

    cik = {"kesit": {a: (d, t, _oran(d, t)) for a, (d, t) in K.items()},
           "hata_turu": dict(hata)}

    if uretim:
        ok = sum(1 for o, _ in uretim.values() if o)
        dg = sum(1 for _, d in uretim.values() if d)
        n = len(uretim)
        cik["uretim"] = {"okunabilirlik": _oran(ok, n), "dogruluk": _oran(dg, n),
                         "n": n}

    if jetonla:
        from . import tokenizer_analiz as TA
        cik["tokenizer"] = TA.rapor(maddeler, jetonla,
                                    {k: d for k, (d, _) in secim.items()})
    return cik


def yazdir(r, ad="model"):
    K = r["kesit"]
    print("\n" + "=" * 66)
    print("TurkMorfBench v3 — %s" % ad)
    print("=" * 66)
    d, t, o = K.get("TOPLAM", (0, 0, 0))
    print("\nZORUNLU SEÇİM   %d / %d   %%%.1f" % (d, t, o))
    if "uretim" in r:
        u = r["uretim"]
        print("SERBEST ÜRETİM  %%%.1f doğru   (%%%.1f okunabilir, n=%d)"
              % (u["dogruluk"], u["okunabilirlik"], u["n"]))

    def blok(baslik, onek):
        satir = sorted((a for a in K if a.startswith(onek)),
                       key=lambda a: K[a][2])
        if not satir:
            return
        print("\n%s" % baslik)
        for a in satir:
            dd, tt, oo = K[a]
            print("  %-34s %5d/%-6d %%%.1f" % (a[len(onek):], dd, tt, oo))

    print("\nGÖVDE TÜRÜ")
    for a in ("gerçek gövde", "uydurma gövde"):
        if a in K:
            dd, tt, oo = K[a]
            print("  %-34s %5d/%-6d %%%.1f" % (a, dd, tt, oo))

    blok("KOVA", "kova: ")
    blok("İSTİSNA VE SES ORTAMI", "son ses: ")
    blok("SÖZLÜK BAYRAĞI", "sözlük bayrağı: ")
    blok("ZİNCİR DERİNLİĞİ", "zincir derinliği ")

    if r.get("hata_turu"):
        print("\nHANGİ KURAL BİLİNMİYOR  (seçilen çeldirici)")
        tt = sum(r["hata_turu"].values())
        for k, n in sorted(r["hata_turu"].items(), key=lambda x: -x[1]):
            print("  %-34s %5d   %%%.1f" % (k, n, _oran(n, tt)))

    if r.get("tokenizer"):
        print("\nTOKENIZER KIRILIMI")
        T = r["tokenizer"]
        for k in ("sınır korundu", "sınır KORUNMADI", "gövde bozulmadı", "gövde BOZULDU"):
            if k in T:
                dd, tt2, oo = T[k]
                print("  %-34s %5d/%-6d %%%.1f" % (k, dd, tt2, oo))
        if "gövde BOZULDU" in T and "gövde bozulmadı" in T:
            fark = T["gövde bozulmadı"][2] - T["gövde BOZULDU"][2]
            print("  %-34s %+.1f puan" % ("→ gövde bozulmasının bedeli", 100 * fark))
