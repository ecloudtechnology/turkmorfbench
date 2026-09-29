# -*- coding: utf-8 -*-
"""Tur 5 sentetik verisi: ÖZEL AD + kesme işaretli hâl eki, YUMUŞAMA YOK (Sinop'a, Ankara'ya, Ahmet'i).
Kaynak: Zemberek yer/kişi/özel ad sözlükleri; kıyasın HİÇBİR kovasında gövde olarak geçmeyenler.
Biçim istisna.ozel_ad motorundan, çerçeveler hâle bağlı. Kontaminasyon: yapısal + denetim."""
import json, random, gzip, sys, re
sys.path.insert(0, ".")
import sozluk, istisna
from kural_verisi_uret import CERCEVE_HAL
rng = random.Random(20260928)
kiyas = set()
for l in gzip.open("turkmorfbench_v3_tam.jsonl.gz", "rt", encoding="utf8"):
    if l.strip(): kiyas.add(json.loads(l)["govde"].lower())
adlar = set()
for m in sozluk.yukle(("yer", "kisi", "ozel")):
    g = m.govde
    if not g or not g[0].isupper() or not re.fullmatch(r"[A-ZÇĞİÖŞÜ][a-zçğıöşüâîû]{2,14}", g): continue
    if g.lower() in kiyas: continue
    adlar.add(g)
adlar = sorted(adlar); print("kıyas dışı özel ad:", len(adlar), adlar[:6])
HALLER = ["belirtme", "yonelme", "bulunma", "ayrilma", "tamlayan"]
out = []
for i in range(20000):
    g = rng.choice(adlar); hal = rng.choice(HALLER)
    out.append(rng.choice(CERCEVE_HAL[hal]).format(X=istisna.ozel_ad(g, hal)))
assert all(o.split("'")[0].split()[-1].lower() not in kiyas for o in out if "'" in o)
open("ozel_ad_verisi_metin.txt", "w", encoding="utf8").write("\n".join(out) + "\n")
kural = [l.rstrip("\n") for l in open("kural_verisi_tur3_metin.txt", encoding="utf8") if l.strip()]
hepsi = kural + out; rng.shuffle(hepsi)
open("kural_verisi_tur5_metin.txt", "w", encoding="utf8").write("\n".join(hepsi) + "\n")
print("kontaminasyon: 0 ✓ · özel ad %d · tur5 toplam %d · örnek: %s" % (len(out), len(hepsi), out[:4]))
