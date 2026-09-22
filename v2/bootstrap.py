"""İki sonuç dosyası arasında EŞLİ bootstrap güven aralığı (%95, 10.000 yeniden örnekleme).

  python bootstrap.py sonuc_A.json sonuc_B.json

İki dosya aynı kıyas ve aynı kip ile üretilmiş olmalı; maddeler birebir eşleşir,
her yeniden örneklemede aynı madde indeksleri iki tarafa da uygulanır. Aralık
sıfırı içeriyorsa fark "gösterilemedi" olarak raporlanır — "fark yok" değil.
"""
import json, sys
import numpy as np

A = json.load(open(sys.argv[1], encoding="utf-8"))
B = json.load(open(sys.argv[2], encoding="utf-8"))
assert A["kip"] == B["kip"] and len(A["vec"]) == len(B["vec"]), "aynı kip ve madde sayısı gerekir"
va, vb = np.asarray(A["vec"], float), np.asarray(B["vec"], float)
tip = np.asarray(A["tip"])
rng = np.random.default_rng(0)
print("%s  vs  %s   [%s]" % (A["model"], B["model"], A["kip"]))
for ad, sec in (("toplam", None), ("gercek", "gercek"), ("wug", "wug")):
    m = np.ones(len(va), bool) if sec is None else (tip == sec)
    x, y = va[m], vb[m]; n = len(x)
    idx = rng.integers(0, n, size=(10000, n))
    d = (x[idx].mean(1) - y[idx].mean(1)) * 100
    lo, hi = np.percentile(d, [2.5, 97.5])
    print("  %-7s n=%3d  fark %+6.2f  [%+6.2f, %+6.2f]  %s"
          % (ad, n, (x.mean() - y.mean()) * 100, lo, hi,
             "ANLAMLI" if (lo > 0 or hi < 0) else "gösterilemedi"))
