# -*- coding: utf-8 -*-
"""İstisna kovaları için KIYAS DIŞI sentetik eğitim verisi — TDK'dan.

NEDEN
  Erk-32B'nin kanarya-2b'ye kaybettiği en büyük kovalar ezberlenmiş istisnalar:
  uyum kırıcı (kalbi), ünlü düşmesi (aczi), ikizleşme (affı). Bunlar kural
  değil sözlük bilgisi; ancak maruz kalmayla öğrenilir. Külliyatta medyan 7–28
  kez geçiyorlar — az.

KAYNAK
  tdk_onbellek.json: gövde -> {madde, taki}. `taki` TDK'nın belirtme biçimidir
  (aciz -> "czi" -> aczi). Kıyasta olan 491 gövde (tdk_altin.json) DIŞLANIR;
  kalan gövdelerden taki'si olanlar kullanılır. Böylece model kıyas maddesini
  değil, aynı SINIFTAN başka kelimeleri görür; kıyasta iyileşme varsa alt-örüntü
  öğrenilmiştir, yoksa saf ezberdir — ikisi de bilgi.

BİÇİMLER
  belirtme  = taki hizalaması (TDK'nın kendisi)
  V-tabanı  = belirtme biçiminin son ünlüsü atılmış hâli (aczi -> acz, kalbi -> kalb, affı -> aff)
  yönelme   = V-tabanı + a/e         (taki ünlüsünün sınıfına göre)
  tamlayan  = belirtme + n           (aczin, kalbin, affın)
  bulunma   = özgün gövde + da/de/ta/te   (ünsüzle başlar: düşme/ikizleşme YOK)
  ayrılma   = özgün gövde + dan/den/tan/ten
"""
import json, os, random, sys
KOK = os.path.dirname(os.path.abspath(__file__))
ONB = json.load(open(os.path.join(KOK, "tdk_onbellek.json")))
KIYAS = set(json.load(open(os.path.join(KOK, "tdk_altin.json")))["altin"])
D = json.load(open(os.path.join(KOK, "kiyas_govdeleri_dislanacak.json")))
KIYAS |= set(D["istisna_uyum_kirici"]) | set(D["istisna_unlu_dusmesi"]) | set(D["istisna_ikizlesme"])
sys.path.insert(0, KOK)
import ad_cekim, itertools                      # noqa: E402
from tdk_bayrak import ADAY, _Sahte             # noqa: E402
HALLER = ["belirtme", "yonelme", "tamlayan", "bulunma", "ayrilma"]

def bayrak_sec(govde, taki):
    """Taki HİZALANMAZ, SEÇER: motorun ürettiği belirtme biçimi taki ile
    bitiyorsa o bayrak kümesi doğrudur. tdk_bayrak.bayrak_bul ile aynı felsefe."""
    for k in range(len(ADAY) + 1):
        for alt in itertools.combinations(ADAY, k):
            if "Voicing" in alt and "NoVoicing" in alt: continue
            try: b = ad_cekim.cekim(_Sahte(govde, alt), hal="belirtme")
            except Exception: continue
            if b and b.endswith(taki) and b != ad_cekim.cekim(_Sahte(govde, ()), hal="belirtme"):
                return frozenset(alt)
    return None

def bicimler(govde, taki):
    alt = bayrak_sec(govde, taki)
    if alt is None: return None
    try: return {h: ad_cekim.cekim(_Sahte(govde, alt), hal=h) for h in HALLER}
    except Exception: return None

CERCEVE = {"belirtme": ["{X} herkes bilir.", "O gün {X} gördük.", "Kimse {X} unutmadı."],
           "yonelme": ["{X} kadar yol var.", "Bunu {X} bağladılar.", "Sonunda {X} vardık."],
           "tamlayan": ["{X} sonucu belliydi.", "{X} etkisi büyüktü.", "{X} yerine başka şey koydular."],
           "bulunma": ["{X} bir şey kalmadı.", "Her şey {X} saklıydı.", "{X} ne varsa aldılar."],
           "ayrilma": ["{X} sonra ne oldu?", "Her şey {X} başladı.", "{X} uzak durdular."]}

def main(n_tekrar=int(os.environ.get("N_TEKRAR", "40")), tohum=20260925):
    rng = random.Random(tohum); adaylar = []
    for g, kayitlar in ONB.items():
        if g in KIYAS or not g.isalpha(): continue
        for k in kayitlar:
            if k.get("taki"):
                b = bicimler(g, k["taki"])
                if b: adaylar.append((g, b)); break
    print("kıyas DIŞI istisna gövdesi (taki'li, gerçekten istisna):", len(adaylar))
    for g, b in adaylar[:6]: print("   %-12s %s" % (g, " · ".join(b.values())))
    ihlal = [g for g, _ in adaylar if g in KIYAS]; assert not ihlal, ihlal
    cik = []
    for g, b in adaylar:
        for _ in range(n_tekrar):
            hal = rng.choice(list(b)); cik.append({"govde": g, "hal": hal, "bicim": b[hal],
                                                    "cumle": rng.choice(CERCEVE[hal]).format(X=b[hal])})
    rng.shuffle(cik)
    with open(os.path.join(KOK, "istisna_verisi.jsonl"), "w", encoding="utf8") as f:
        for o in cik: f.write(json.dumps(o, ensure_ascii=False) + "\n")
    with open(os.path.join(KOK, "istisna_verisi_metin.txt"), "w", encoding="utf8") as f:
        for o in cik: f.write(o["cumle"] + "\n")
    print("üretilen cümle: %d · kontaminasyon: 0 ✓ · yazıldı: istisna_verisi.jsonl / _metin.txt" % len(cik))

if __name__ == "__main__": main()
