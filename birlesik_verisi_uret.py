# -*- coding: utf-8 -*-
"""Tur 3 sentetik verisi: 3. tekil iyelik + hâl = ZAMİR n'Sİ (kapısına, buzdolabına, sığırödüne).
KIYAS DIŞI kaynak: kıyasın HİÇBİR kovasında gövde olarak geçmeyen sözlük adları (253) ve
CompoundP3sg birleşikleri (20) — birlesik_kaynak_disi.json. Biçimler kural motorundan (ad_cekim.cekim),
çerçeveler hâle bağlı. Kontaminasyon: üretilen her biçimin gövdesi kıyas dışı (yapısal garanti + denetim)."""
import json, random, gzip, sys
sys.path.insert(0, ".")
import sozluk, ad_cekim
from kural_verisi_uret import CERCEVE_HAL
rng = random.Random(20260927)
K = json.load(open("birlesik_kaynak_disi.json"))
ham = sozluk.yukle(("master", "non_tdk")); ix = {m.govde: m for m in ham}
kaynak = [ix[g] for g in K["ad"] + K["birlesik"] if g in ix]
HALLER = ["belirtme", "yonelme", "bulunma", "ayrilma", "tamlayan"]
bicimler = []
for m in kaynak:
    for cokluk in ("tek", "cok"):
        for hal in HALLER:
            try:
                b = ad_cekim.cekim(m, cokluk=cokluk, iyelik="3t", hal=hal)
            except Exception:
                continue
            if b and b.isalpha():
                bicimler.append((m.govde, cokluk, hal, b))
print("kaynak gövde:", len(kaynak), "· biçim:", len(bicimler), "· örnek:", [b for *_, b in bicimler[:6]])
# kontaminasyon: gövdeler kıyasta yok mu (tam veri)
kiyas = set()
for l in gzip.open("turkmorfbench_v3_tam.jsonl.gz", "rt", encoding="utf8"):
    if l.strip(): kiyas.add(json.loads(l)["govde"].lower())
ihlal = [g for g, *_ in bicimler if g.lower() in kiyas]
assert not ihlal, ihlal[:5]
N = 20000; out = []
for i in range(N):
    g, cokluk, hal, b = rng.choice(bicimler)
    out.append(rng.choice(CERCEVE_HAL[hal]).format(X=b))
with open("birlesik_verisi_metin.txt", "w", encoding="utf8") as f: f.write("\n".join(out) + "\n")
kural = [l.rstrip("\n") for l in open("kural_verisi_metin.txt", encoding="utf8") if l.strip()]
hepsi = kural + out; rng.shuffle(hepsi)
with open("kural_verisi_tur3_metin.txt", "w", encoding="utf8") as f: f.write("\n".join(hepsi) + "\n")
print("kontaminasyon: 0 ✓ · birlesik %d · tur3 toplam %d · örnek: %s" % (len(out), len(hepsi), out[:4]))
