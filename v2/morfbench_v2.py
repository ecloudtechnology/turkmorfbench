"""
TurkMorfBench v2 — KUSURSUZ referans cevaplar.
v1'in kusurlari: unlu-dusmesi kelimeleri (nehir->nehiri yanlis), istisnalar.
v2 duzeltmeleri:
  1. Unlu-dusmesi ve istisna kelimeler havuzdan CIKARILDI.
  2. Sadece KURALLI kelimeler + fonolojik motor tam.
  3. Her gercek-kelime cevabi zeyrek ile CIFT dogrulama.
  4. Wug kelimeleri unlu-dusmesi tetiklemeyecek desende secildi.
  5. Cift-kontrol: uretilen form + zeyrek analizi + insan-okunabilir kural etiketi.
"""
import json, random
random.seed(1337)

BACK_UNROUND="aı"; BACK_ROUND="ou"; FRONT_UNROUND="ei"; FRONT_ROUND="öü"
VOWELS=BACK_UNROUND+BACK_ROUND+FRONT_UNROUND+FRONT_ROUND
HARD="fstkçşhp"

def last_vowel(w):
    for c in reversed(w.lower()):
        if c in VOWELS: return c
    return "a"
def vowel_a(w): return "a" if last_vowel(w) in BACK_UNROUND+BACK_ROUND else "e"
def vowel_i(w):
    lv=last_vowel(w)
    if lv in BACK_UNROUND: return "ı"
    if lv in BACK_ROUND: return "u"
    if lv in FRONT_UNROUND: return "i"
    return "ü"
def hece_sayisi(w):
    return sum(1 for c in w.lower() if c in VOWELS)
# Yumusama ISTISNALARI: yumusamayan cok-heceli kelimeler
YUMUSAMAZ={"bulut","sepet","millet","devlet","sıfat","tabiat","hukuk","merak",
           "iştirak","cumhuriyet"}
def soften(w):
    m={"p":"b","t":"d","k":"ğ","ç":"c"}
    # Yumusama SADECE: cok heceli (>1) + istisna degil + son harf p/t/k/ç
    if w[-1] in m and hece_sayisi(w)>1 and w.lower() not in YUMUSAMAZ:
        return w[:-1]+m[w[-1]]
    return w  # tek heceli (top,süt,at) ve istisnalar yumusamaz
def hard_dt(w): return "t" if w[-1] in HARD else "d"
def ends_vowel(w): return w[-1].lower() in VOWELS

def cogul(w): return w+("lar" if vowel_a(w)=="a" else "ler")
def iyelik(w,k):
    s=soften(w); I=vowel_i(w)
    if ends_vowel(w):
        if k=="1sg": return w+"m"
        if k=="2sg": return w+"n"
        if k=="3sg": return w+"s"+I
        if k=="1pl": return w+"m"+I+"z"
        if k=="3pl": return w+"lar"+("ı" if vowel_a(w)=="a" else "i")
    if k=="1sg": return s+I+"m"
    if k=="2sg": return s+I+"n"
    if k=="3sg": return s+I
    if k=="1pl": return s+I+"m"+I+"z"
    if k=="3pl": return s+"lar"+("ı" if vowel_a(w)=="a" else "i")
def hal(w,d):
    s=soften(w); I=vowel_i(w); A=vowel_a(w); dt=hard_dt(w)
    # belirtme ve yonelme unluyle baslar -> yumusama (s). bulunma/ayrilma unsuzle -> yumusama YOK (w).
    if d=="belirtme": return (w+"y"+I) if ends_vowel(w) else s+I
    if d=="yonelme": return (w+"y"+A) if ends_vowel(w) else s+A   # köpek->köpeğe (s kullan!)
    if d=="bulunma": return w+dt+A   # köpekte (yumusama yok)
    if d=="ayrilma": return w+dt+A+"n"
    return w

# ---- KURALLI kelime havuzu (unlu-dusmesi ve istisna OLMAYAN) ----
# Cikarilanlar: nehir,sehir,burun,ogul,beyin,akil,isim,resim,fikir,sabir,omur,
#               kalp,saat,harf,hal,vakit (unlu dusmesi VEYA uyum istisnasi)
# SADECE yumusama davranisi NET olan kelimeler:
# - Sonu p/t/k/ç OLMAYAN (yumusama sorusu hic yok): ev,göz,yol,masa,deniz...
# - Sonu p/t/k/ç olup COK HECELI ve KESIN yumusayan: kitap->kitabı,çocuk->çocuğu,ağaç->ağacı
# Cikarilanlar: bulut,süt,top (tek-hece/istisna belirsizligi)
GERCEK=["ev","göz","araba","yol","masa","deniz","kuş","çiçek","dağ","okul",
        "balık","elma","ekmek","kapı","pencere","duvar","yaprak","taş","kum","ateş",
        "kalem","defter","sıra","orman","yıldız","güneş","toprak","kedi","kuzu","aslan",
        "kartal","kitap","çocuk","ağaç","köpek","yaprak","bardak","sokak","durak","yatak"]
# Wug: fonotaktik uygun, unlu-dusmesi TETIKLEMEYEN (son hece cift-unsuz degil, CVC duzenli)
UYDURMA=["blan","krint","şupa","zompar","fönük","tırmaz","glodek","pürsat","zelbik",
         "mırdel","nyupra","flözek","gadros","brelak","yontuç","şimtül","dratok",
         "kevlan","torbuk","çamdur","pislen","gürtan","möşkül","zabrek"]

def uret(kelimeler,tip):
    out=[]
    for w in kelimeler:
        out.append({"kok":w,"gorev":"cogul","cevap":cogul(w),"tip":tip,
                    "soru":f"'{w}' kelimesinin çoğulunu yaz.","kural":"çoğul eki + ünlü uyumu"})
        for k,ad in [("1sg","benim"),("3sg","onun"),("1pl","bizim")]:
            out.append({"kok":w,"gorev":f"iyelik_{k}","cevap":iyelik(w,k),"tip":tip,
                        "soru":f"'{w}' kelimesini '{ad}' iyelik ekiyle çek.",
                        "kural":"iyelik + " + ("ünsüz yumuşaması" if w[-1] in "ptkç" else "ünlü uyumu")})
        for d,ad in [("belirtme","-i/-ı belirtme"),("yonelme","-e/-a yönelme"),
                     ("bulunma","-de/-da bulunma"),("ayrilma","-den/-dan ayrılma")]:
            out.append({"kok":w,"gorev":f"hal_{d}","cevap":hal(w,d),"tip":tip,
                        "soru":f"'{w}' kelimesine {ad} eki ekle.",
                        "kural":"hal eki + " + ("sertleşme" if d in ("bulunma","ayrilma") and w[-1] in HARD else "ünlü uyumu")})
    return out

test=uret(GERCEK,"gercek")+uret(UYDURMA,"wug")

# ZEYREK CIFT DOGRULAMA (gercek kelimeler)
import zeyrek
an=zeyrek.MorphAnalyzer()
def zeyrek_ok(form):
    try:
        r=an.analyze(form); return bool(r and r[0])
    except: return False

onceki=len(test); temiz=[]; elenen=[]
for x in test:
    if x["tip"]=="wug":
        temiz.append(x)
    elif zeyrek_ok(x["cevap"]):
        temiz.append(x)
    else:
        elenen.append(f"{x['kok']}/{x['gorev']}={x['cevap']}")
test=temiz
random.shuffle(test)

from collections import Counter
print(f"Uretilen: {onceki} -> zeyrek dogrulamasi sonrasi: {len(test)}")
print(f"Elenen (zeyrek gecersiz): {len(elenen)}")
if elenen: print("  ornek elenenler:", elenen[:8])
print(f"Tip: {dict(Counter(x['tip'] for x in test))}")
print(f"Gorev turu: {len(set(x['gorev'] for x in test))}")

# KRITIK fonolojik dogrulama
print("\n=== KRITIK KURAL KONTROLU ===")
checks=[("kitap","iyelik_1sg","kitabım","ünsüz yumuşaması p->b"),
        ("çocuk","iyelik_1sg","çocuğum","k->ğ"),
        ("ağaç","hal_bulunma","ağaçta","sertleşme ç+t"),
        ("kitap","hal_ayrilma","kitaptan","sertleşme p+t"),
        ("göz","iyelik_1sg","gözüm","ünlü uyumu ö->ü"),
        ("araba","iyelik_3sg","arabası","ünlü sonrası -sı"),
        ("köpek","hal_yonelme","köpeğe","yönelme + k->ğ yumuşaması"),
        ("yatak","hal_yonelme","yatağa","yönelme + k->ğ"),
        ("köpek","hal_bulunma","köpekte","bulunma yumuşama YOK"),
        ("kitap","hal_belirtme","kitabı","belirtme + p->b"),
        ("fönük","iyelik_1sg","fönüğüm","WUG: k->ğ + uyum")]
def cek(kok,gorev):
    if gorev=="cogul": return cogul(kok)
    if gorev.startswith("iyelik_"): return iyelik(kok, gorev.split("_")[1])
    if gorev.startswith("hal_"): return hal(kok, gorev.split("_")[1])
    return kok
hepsi_ok=True
for kok,gorev,beklenen,kural in checks:
    got=cek(kok,gorev); ok=got==beklenen
    hepsi_ok=hepsi_ok and ok
    print(f"  {kok} {gorev}: {got} {'✓' if ok else '✗ (bekl: '+beklenen+')'} [{kural}]")

json.dump(test,open("turkmorfbench.json","w",encoding="utf-8"),ensure_ascii=False,indent=2)
print(f"\n{'✓ TUM KURALLAR DOGRU' if hepsi_ok else '✗ HATA VAR'} — kaydedildi: turkmorfbench_v2.json ({len(test)} ornek)")
