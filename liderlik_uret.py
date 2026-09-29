# -*- coding: utf-8 -*-
"""Liderlik tablosu üretici: tablo37_ozet.json (15 model, 3.7.0 puanlama) + ek_satirlar.json (yeni Erk sürümleri)
→ LIDERLIK-TR.md / LIDERLIK-EN.md parçaları (README'ye yapıştırılır). Sıralama harf'e göre; boyut ve TurkishMMLU sütunlu;
açıklama cümlesi zorunlu. Eski Erk satırları 'önceki sürüm' olarak KALIR (şeffaflık)."""
import json, sys
R = json.load(open("tablo37_ozet.json"))
ek = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else []   # [{"ad","gel","boyut","oran","ci":[lo,hi],"te","mmlu","not"}]
satir = [{"ad": r["ad"], "gel": r["gel"], "boyut": r["boyut"], "oran": r["oran"], "ci": r["ci"], "te": r["te"].get("hucre", {}).get("genislik_kati"), "mmlu": r["mmlu"], "not": ("v1" if r["ad"] in ("Erk-14B","Erk-32B") else "")} for r in R] + ek
satir.sort(key=lambda s: -s["oran"])
def tr(x): return ("%.1f" % x).replace(".", ",")
def tab(dil):
    b = ["| # | model | " + ("geliştiren" if dil == "tr" else "developer") + " | " + ("boyut" if dil == "tr" else "size") + " | TurkMorfBench | %95 " + ("GA" if dil == "tr" else "CI") + " | TurkishMMLU |",
         "|---|---|---|---|---|---|---|"]
    for i, s in enumerate(satir, 1):
        ad = s["ad"] + ((" *(%s)*" % s["not"]) if s.get("not") else "")
        n = (lambda v: tr(v) if dil == "tr" else "%.1f" % v)
        b.append("| %d | %s | %s | %s | **%s** | %s–%s | %s |" % (i, ad, s["gel"], s["boyut"], n(100*s["oran"]), n(100*s["ci"][0]), n(100*s["ci"][1]), n(s["mmlu"]) if s["mmlu"] is not None else "—"))
    return "\n".join(b)
TR = """### Liderlik tablosu

3.6 çekirdeği (1.836 madde), `harf` kuralı, hücre kümeli %95 güven aralığı, tek sabit betik, bf16, şık sırası
dondurulmuş. TurkishMMLU: aynı sabit betikle 652 temiz soru (beş şık, şans %20). Erk modelleri bu kıyasın teşhis
çıktısıyla iyileştirildi; diğer modeller yayımlandıkları hâliyle ölçüldü.

""" + tab("tr") + """

İlk sıralar istatistiksel olarak beraberlik bandındadır; iki modeli karşılaştırırken aralıkların çakışmasına
değil, eşli farkın kümeli önyüklemesine bakılır (`esli_fark`). Morfoloji parametre sayısıyla ölçeklenmez:
TurkishMMLU'da şans düzeyindeki 0,8–2B modeller morfolojide 32B modellerle aynı banttadır.
"""
EN = """### Leaderboard

3.6 core (1,836 items), `harf` rule, cell-clustered 95% CI, one pinned script, bf16, option order frozen.
TurkishMMLU: the same pinned script on 652 clean questions (five-way, chance 20%). Erk models were improved
using this benchmark's diagnostic output; the other models were measured as published.

""" + tab("en") + """

The top ranks are a statistical tie; compare two models by the cluster bootstrap of the paired difference
(`esli_fark`), not by interval overlap. Morphology does not scale with parameter count: 0.8–2B models at chance
on TurkishMMLU sit in the same band as 32B models on morphology.
"""
open("LIDERLIK-TR.md", "w").write(TR); open("LIDERLIK-EN.md", "w").write(EN); print(TR)
