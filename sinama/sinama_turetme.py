"""Çatı ve yapım eklerinin altın sınaması."""
import sys
import turetme as T

# --- çatı: (gövde, tür, beklenen, kural)
CATI_ALTIN = [
    ("yaz",   "edilgen", "yazıl",   "ünsüz sonrası -Il"),
    ("kes",   "edilgen", "kesil",   "ünsüz sonrası -Il"),
    ("gör",   "edilgen", "görül",   "ünsüz + yuvarlak uyum"),
    ("al",    "edilgen", "alın",    "-l sonrası -In"),
    ("bil",   "edilgen", "bilin",   "-l sonrası -In"),
    ("bul",   "edilgen", "bulun",   "-l sonrası yuvarlak"),
    ("oku",   "edilgen", "okun",    "ünlü sonrası -n"),
    ("bekle", "edilgen", "beklen",  "ünlü sonrası -n"),

    ("giy",   "donuslu", "giyin",   "dönüşlü -In"),
    ("yıka",  "donuslu", "yıkan",   "dönüşlü ünlü sonrası"),
    ("söv",   "donuslu", "sövün",   "dönüşlü yuvarlak"),

    ("gör",   "istes",   "görüş",   "işteş -Iş"),
    ("vur",   "istes",   "vuruş",   "işteş yuvarlak"),
    ("bak",   "istes",   "bakış",   "işteş kalın"),

    # ettirgen: kural
    ("bekle", "ettirgen", "beklet",  "ünlü + çok heceli -> -t"),
    ("otur",  "ettirgen", "oturt",   "-r + çok heceli -> -t"),
    ("kısal", "ettirgen", "kısalt",  "-l + çok heceli -> -t"),
    ("yaz",   "ettirgen", "yazdır",  "kalan -> -DIr"),
    ("sev",   "ettirgen", "sevdir",  "kalan -> -DIr"),
    ("kes",   "ettirgen", "kestir",  "-DIr benzeşmesi D->t"),
    # ettirgen: sözlüksel istisna
    ("iç",    "ettirgen", "içir",    "istisna -Ir"),
    ("kaç",   "ettirgen", "kaçır",   "istisna -Ir"),
    ("düş",   "ettirgen", "düşür",   "istisna -Ir"),
    ("kork",  "ettirgen", "korkut",  "istisna -It"),
    ("ak",    "ettirgen", "akıt",    "istisna -It"),
    ("çık",   "ettirgen", "çıkar",   "istisna -Ar"),
]

# --- yapım: (gövde, tür, beklenen, kural)
YAPIM_ALTIN = [
    ("göz",   "lik", "gözlük",   "-lIk ince yuvarlak"),
    ("kitap", "lik", "kitaplık", "-lIk: gövde BOZULMAZ"),
    ("burun", "lik", "burunluk", "-lIk: ünlü düşmesi YOK"),
    ("göz",   "ci",  "gözcü",    "-CI ötümlü sonrası c"),
    ("kitap", "ci",  "kitapçı",  "-CI ötümsüz sonrası ç"),
    ("yol",   "ci",  "yolcu",    "-CI kalın yuvarlak"),
    ("göz",   "li",  "gözlü",    "-lI"),
    ("kitap", "li",  "kitaplı",  "-lI"),
    ("göz",   "siz", "gözsüz",   "-sIz"),
    ("su",    "siz", "susuz",    "-sIz ünlü gövde"),
    ("kum",   "sal", "kumsal",   "-sAl kalın"),
    ("biçim", "sal", "biçimsel", "-sAl ince"),
    ("güzel", "les", "güzelleş", "-lAş ince"),
    ("taş",   "les", "taşlaş",   "-lAş kalın"),
    ("taş",   "le",  "taşla",    "-lA"),
    ("su",    "le",  "sula",     "-lA ünlü gövde"),
]


def kos(ad, altin, fn):
    gecen = 0
    hata = []
    for gv, tur, bek, kural in altin:
        cik = fn(gv, tur)
        if cik == bek:
            gecen += 1
        else:
            hata.append((gv, tur, bek, cik, kural))
    print("%s: geçen %d / %d" % (ad, gecen, len(altin)))
    for gv, tur, bek, cik, kural in hata:
        print("    %-8s %-9s beklenen %-12s üretilen %-12s  [%s]" % (gv, tur, bek, cik, kural))
    return len(hata)


h = kos("ÇATI ", CATI_ALTIN, lambda g, t: T.cati(g, t))
h += kos("YAPIM", YAPIM_ALTIN, lambda g, t: T.yapim(g, t))

# uydurma gövdede ettirgen her zaman üretilebilmeli
for w in ("çölgap", "zelbik", "krint", "fönük"):
    e = T.cati(w, "ettirgen", uydurma=True)
    print("  uydurma ettirgen  %-8s -> %s" % (w, e))
    if e is None:
        h += 1
sys.exit(1 if h else 0)
