# -*- coding: utf-8 -*-
"""TurkMorfBench iç tutarlılık denetimi.

Dış denetimler (TDK, UD) altının DOĞRU olup olmadığına bakar. Bu betik farklı
bir soru soruyor: kıyas kendi içinde tutarlı mı? Bir kıyas doğru altınla bile
kullanılamaz hâle gelebilir —

  · aynı soru iki farklı altınla iki kez sorulursa
  · çeldirici aslında geçerli bir başka biçimse (iki doğru cevap)
  · altın şıklar arasında yoksa
  · "uydurma" dediğimiz gövde aslında Türkçe bir kelimeyse (ezber kontrolü çöker)
  · şıklar birbirinin aynısıysa
  · altın hep aynı sırada duruyorsa (konum ipucu)

Bunların hiçbiri altının yanlışlığından anlaşılmaz; ayrıca aranması gerekir.
"""
import collections
import io
import json
import sys


def yukle(yol):
    d = json.load(io.open(yol, encoding="utf8"))
    return d["maddeler"] if isinstance(d, dict) else d


def main(yol="turkmorfbench_v3_tam.json"):
    M = yukle(yol)
    print("madde: %d" % len(M))
    bulgu = collections.Counter()
    ornek = collections.defaultdict(list)

    def bul(ad, m, ek=""):
        bulgu[ad] += 1
        if len(ornek[ad]) < 6:
            ornek[ad].append("%s %s -> %s %s" % (m["kova"], m["govde"], m["altin"], ek))

    # 1. yapısal bütünlük
    kimlikler = collections.Counter(m["kimlik"] for m in M)
    for k, n in kimlikler.items():
        if n > 1:
            bulgu["yinelenen kimlik"] += n - 1
    for m in M:
        sec = m.get("secenek") or []
        if m["altin"] not in sec:
            bul("altın şıklar arasında değil", m)
        if len(sec) != len(set(sec)):
            bul("aynı şık iki kez", m, str(sec))
        if len(sec) < 3:
            bul("üçten az şık", m, str(sec))
        if m["altin"] in (m.get("celdirici") or {}).values():
            bul("altın aynı zamanda çeldirici", m)
        for c in (m.get("celdirici") or {}).values():
            if not c or c == m["govde"]:
                bul("çeldirici boş ya da çıplak gövde", m, repr(c))

    # 2. aynı soru, iki altın
    soru = collections.defaultdict(set)
    for m in M:
        soru[(m["govde"], m["gorev"])].add(m["altin"])
    for (g, t), a in soru.items():
        if len(a) > 1:
            bulgu["aynı soruya iki altın"] += 1
            if len(ornek["aynı soruya iki altın"]) < 6:
                ornek["aynı soruya iki altın"].append("%s %s -> %s" % (g, t, sorted(a)))

    # 3. altının şıklar içindeki konumu — ipucu vermemeli
    konum = collections.Counter()
    for m in M:
        sec = m.get("secenek") or []
        if m["altin"] in sec:
            konum[(sec.index(m["altin"]), len(sec))] += 1
    print("\nALTININ ŞIK SIRASI (konum ipucu olmamalı)")
    for n in sorted({u for _, u in konum}):
        toplam = sum(v for (i, u), v in konum.items() if u == n)
        if toplam < 100:
            continue
        pay = [100 * konum.get((i, n), 0) / toplam for i in range(n)]
        print("  %d şıklı %7d madde: %s" % (n, toplam, "  ".join("%%%.1f" % p for p in pay)))

    # 4. uydurma gövdeler gerçekten uydurma mı
    try:
        import sozluk
        ham = sozluk.yukle(("master", "non_tdk", "eskimis", "gayriresmi",
                            "ozel", "yer", "kisi"))
        tum = {m.govde.lower() for m in ham}
        kacak = {m["govde"] for m in M if not m.get("gercek", True)
                 and m["govde"].lower() in tum}
        if kacak:
            bulgu["uydurma sayılan gövde sözlükte VAR"] = len(kacak)
            ornek["uydurma sayılan gövde sözlükte VAR"] = sorted(kacak)[:10]
    except Exception as h:
        print("  (uydurma denetimi atlandı: %s)" % h)

    # 5. kova × gövde türü dengesi
    print("\nKOVA × GÖVDE TÜRÜ")
    kv = collections.Counter((m["kova"], "gerçek" if m.get("gercek", True) else "uydurma") for m in M)
    for k in sorted({a for a, _ in kv}):
        g, u = kv.get((k, "gerçek"), 0), kv.get((k, "uydurma"), 0)
        print("  %-26s gerçek %7d · uydurma %6d" % (k, g, u))

    print("\nBULGULAR")
    if not bulgu:
        print("  temiz")
    for k, n in bulgu.most_common():
        print("  %-38s %6d" % (k, n))
        for o in ornek[k]:
            print("       %s" % o)


if __name__ == "__main__":
    main(*sys.argv[1:])
