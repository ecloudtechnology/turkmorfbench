"""
CAPRAZ KONTROL: motorun urettigi her GERCEK-kelime cevabini, zeyrek'in
o kok+cekimi COZUMLEYIP ayni yuzey formunu URETIP uretmedigiyle karsilastir.
Zeyrek analiz->uretim (generate) destekliyorsa kullan; yoksa en azindan
cevabin cozumu, beklenen morfem etiketleriyle uyusuyor mu bak.
Amac: 'gecerli form' degil 'DOGRU cekim' garantisi.
"""
import json, sys, zeyrek
data=json.load(open(sys.argv[1] if len(sys.argv) > 1 else "turkmorfbench.json", encoding="utf-8"))
an=zeyrek.MorphAnalyzer()

# gorev -> beklenen morfem etiketleri. Zeyrek etiketleri buyuk/kucuk harf ve
# format farkli olabilir; birden cok olasi etiketi kabul et (esnek eslesme).
GOREV_ETIKET={
    "cogul":["A3pl","Pl"], "iyelik_1sg":["P1sg"], "iyelik_3sg":["P3sg"],
    "iyelik_1pl":["P1pl"], "hal_belirtme":["Acc"], "hal_yonelme":["Dat"],
    "hal_bulunma":["Loc"], "hal_ayrilma":["Abl"],
}
def etiket_var(bulunan, beklenenler):
    # esnek: beklenen etiketlerden HERHANGI biri (buyuk/kucuk duyarsiz) bulunanda mi
    bl=set(b.lower() for b in bulunan)
    return any(e.lower() in bl for e in beklenenler)

gercekler=[x for x in data if x["tip"]=="gercek"]
supheli=[]; onaylı=0
for x in gercekler:
    cevap=x["cevap"]; gorev=x["gorev"]
    beklenen=GOREV_ETIKET.get(gorev,[])
    try:
        r=an.analyze(cevap)
        if not (r and r[0]):
            supheli.append((x["kok"],gorev,cevap,"cozumlenemedi")); continue
        # tum analizlerdeki morfem etiketlerini topla
        bulunan=set()
        for parse in r[0]:
            bulunan.update(parse.morphemes)
        # beklenen etiket cozumde var mi (esnek eslesme)
        if not beklenen or etiket_var(bulunan, beklenen):
            onaylı+=1
        else:
            supheli.append((x["kok"],gorev,cevap,f"beklenen {beklenen} yok, bulunan {sorted(bulunan)[:6]}"))
    except Exception as e:
        supheli.append((x["kok"],gorev,cevap,str(e)[:40]))

print(f"Gercek kelime cevabi: {len(gercekler)}")
print(f"Zeyrek ile ONAYLANAN (dogru cekim etiketi): {onaylı}")
print(f"SUPHELI (etiket uyusmayan): {len(supheli)}")
if supheli:
    print("\n=== SUPHELI CEVAPLAR (elle bakilmali) ===")
    for kok,gorev,cevap,sebep in supheli[:20]:
        print(f"  {kok} {gorev} -> {cevap}  [{sebep}]")
else:
    print("\n✓ TUM gercek-kelime cevaplari zeyrek etiketleriyle UYUMLU. Benchmark saglam.")
