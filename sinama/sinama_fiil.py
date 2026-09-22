"""Fiil çekim motorunun altın sınaması.

Her satır belirli bir kuralı hedefliyor ve hangi kuralı sınadığı yanında yazılı.
Özellikle geniş zaman ve olumsuz geniş zaman üzerinde duruldu: kıyasın en
ayırt edici maddeleri orada.
"""
import sys
import sozluk
import fiil_cekim as F

# (mastar, zaman, kişi, olumsuz, beklenen, sınanan kural)
ALTIN = [
    # --- belirli geçmiş, iki kişi takımı
    ("gitmek", "belirli_gecmis", "1t", False, "gittim",      "1. takım kişi eki"),
    ("gitmek", "belirli_gecmis", "3c", False, "gittiler",    "1. takım 3. çoğul"),
    ("gelmek", "belirli_gecmis", "1t", False, "geldim",      "ötümlü gövde, D->d"),
    ("bakmak", "belirli_gecmis", "1c", False, "baktık",      "benzeşme k -> t"),
    ("okumak", "belirli_gecmis", "1t", False, "okudum",      "ünlü sonrası D"),

    # --- belirsiz geçmiş, 2. takım
    ("gitmek", "belirsiz_gecmis", "1t", False, "gitmişim",   "2. takım kişi eki"),
    ("gelmek", "belirsiz_gecmis", "3c", False, "gelmişler",  "2. takım 3. çoğul"),
    ("okumak", "belirsiz_gecmis", "2c", False, "okumuşsunuz","2. takım 2. çoğul"),

    # --- şimdiki zaman: yumuşama + yardımcı ünlü
    ("gitmek", "simdiki", "1t", False, "gidiyorum",  "Voicing t->d + -Iyor"),
    ("gitmek", "simdiki", "2t", False, "gidiyorsun", "-Iyor sonrası uyum (o->u)"),
    ("gitmek", "simdiki", "1c", False, "gidiyoruz",  "-Iyor sonrası 1. çoğul"),
    ("bakmak", "simdiki", "1t", False, "bakıyorum",  "yumuşama YOK (bayraksız)"),
    ("görmek", "simdiki", "1t", False, "görüyorum",  "yuvarlak uyum"),
    ("gelmek", "simdiki", "1t", False, "geliyorum",  "ince uyum"),

    # --- şimdiki zaman: gövde sonu ünlü daralması
    ("beklemek", "simdiki", "1t", False, "bekliyorum", "geniş ünlü daralması e->i"),
    ("anlamak",  "simdiki", "1t", False, "anlıyorum",  "geniş ünlü daralması a->ı"),
    ("söylemek", "simdiki", "1t", False, "söylüyorum", "daralma + yuvarlaklık"),
    ("okumak",   "simdiki", "1t", False, "okuyorum",   "dar ünlü korunur"),
    ("yürümek",  "simdiki", "1t", False, "yürüyorum",  "dar ünlü korunur"),

    # --- gelecek: k -> ğ yumuşaması
    ("gitmek", "gelecek", "1t", False, "gideceğim",  "-AcAk + ünlü -> k->ğ"),
    ("gitmek", "gelecek", "3t", False, "gidecek",    "-AcAk yalın 3. tekil"),
    ("gitmek", "gelecek", "1c", False, "gideceğiz",  "-AcAk + 1. çoğul"),
    ("bakmak", "gelecek", "1t", False, "bakacağım",  "kalın uyumda -AcAk"),
    ("okumak", "gelecek", "1t", False, "okuyacağım", "ünlü gövde + kaynaştırma"),

    # --- GENİŞ ZAMAN: kural
    ("bakmak",   "genis", "3t", False, "bakar",   "tek heceli -> -Ar"),
    ("yazmak",   "genis", "3t", False, "yazar",   "tek heceli -> -Ar"),
    ("gitmek",   "genis", "3t", False, "gider",   "tek heceli -Ar + yumuşama"),
    ("oturmak",  "genis", "3t", False, "oturur",  "çok heceli -> -Ir"),
    ("çalışmak", "genis", "3t", False, "çalışır", "çok heceli -> -Ir"),
    ("okumak",   "genis", "3t", False, "okur",    "ünlü gövde -> -r"),
    ("beklemek", "genis", "3t", False, "bekler",  "ünlü gövde -> -r"),

    # --- GENİŞ ZAMAN: on üç istisna (A:Aorist_I)
    ("gelmek", "genis", "3t", False, "gelir", "istisna: tek heceli ama -Ir"),
    ("almak",  "genis", "3t", False, "alır",  "istisna"),
    ("bilmek", "genis", "3t", False, "bilir", "istisna"),
    ("bulmak", "genis", "3t", False, "bulur", "istisna"),
    ("görmek", "genis", "3t", False, "görür", "istisna"),
    ("olmak",  "genis", "3t", False, "olur",  "istisna"),
    ("vermek", "genis", "3t", False, "verir", "istisna"),
    ("vurmak", "genis", "3t", False, "vurur", "istisna"),
    ("kalmak", "genis", "3t", False, "kalır", "istisna"),
    ("ölmek",  "genis", "3t", False, "ölür",  "istisna"),
    # ters yön: çok heceli ama -Ar (A:Aorist_A)
    ("etmek",     "genis", "3t", False, "eder",     "Aorist_A"),
    ("affetmek",  "genis", "3t", False, "affeder",  "Aorist_A + Voicing"),

    # --- geniş zaman kişili
    ("gelmek", "genis", "1t", False, "gelirim",   "istisna + 1. tekil"),
    ("bakmak", "genis", "1t", False, "bakarım",   "kural + 1. tekil"),
    ("görmek", "genis", "1t", False, "görürüm",   "istisna + yuvarlak"),
    ("okumak", "genis", "1t", False, "okurum",    "ünlü gövde + 1. tekil"),

    # --- OLUMSUZ GENİŞ ZAMAN: üç ayrı düzensizlik
    ("gitmek", "genis", "3t", True, "gitmez",     "olumsuz geniş -mAz"),
    ("gelmek", "genis", "3t", True, "gelmez",     "olumsuz geniş -mAz"),
    ("bakmak", "genis", "3t", True, "bakmaz",     "olumsuz geniş -mAz"),
    ("gitmek", "genis", "1t", True, "gitmem",     "1. tekil -mAm (-mAzIm DEĞİL)"),
    ("gelmek", "genis", "1t", True, "gelmem",     "1. tekil -mAm"),
    ("bakmak", "genis", "1t", True, "bakmam",     "1. tekil -mAm"),
    ("gitmek", "genis", "1c", True, "gitmeyiz",   "1. çoğul -mAyIz"),
    ("bakmak", "genis", "1c", True, "bakmayız",   "1. çoğul -mAyIz"),
    ("gitmek", "genis", "2t", True, "gitmezsin",  "olumsuz geniş 2. tekil"),
    ("gitmek", "genis", "3c", True, "gitmezler",  "olumsuz geniş 3. çoğul"),

    # --- diğer olumsuzlar
    ("gitmek", "belirli_gecmis", "1t", True, "gitmedim",     "olumsuz + geçmiş"),
    ("gitmek", "simdiki", "1t", True, "gitmiyorum",   "olumsuz -mA daralır"),
    ("bakmak", "simdiki", "1t", True, "bakmıyorum",   "olumsuz -mA daralır (kalın)"),
    ("gitmek", "gelecek", "1t", True, "gitmeyeceğim", "olumsuz + gelecek"),
    ("gitmek", "belirsiz_gecmis", "1t", True, "gitmemişim", "olumsuz + belirsiz"),

    # --- gereklilik ve şart
    ("gitmek", "gereklilik", "1t", False, "gitmeliyim", "-mAlI + 2. takım"),
    ("bakmak", "gereklilik", "1t", False, "bakmalıyım", "-mAlI kalın"),
    ("gitmek", "sart", "1t", False, "gitsem",  "-sA + 1. takım"),
    ("bakmak", "sart", "1c", False, "baksak",  "-sA + 1. çoğul"),
]


def main():
    ham = sozluk.yukle(("master", "non_tdk"))
    fiiller = sozluk.indeksle([m for m in ham if m.tur == "Verb"])
    gecen = kalan = 0
    eksik, hatalar = [], []
    for mastar, z, k, o, bek, kural in ALTIN:
        m = fiiller.get(mastar)
        if m is None:
            eksik.append(mastar); continue
        cik = F.cekim(m, z, k, o)
        if cik == bek:
            gecen += 1
        else:
            kalan += 1
            hatalar.append((mastar, z, k, o, bek, cik, kural, sorted(m.bayrak)))

    print("ALTIN SINAMA — fiil çekimi")
    print("  geçen %d / %d" % (gecen, gecen + kalan))
    if eksik:
        print("  SÖZLÜKTE YOK: %s" % ", ".join(sorted(set(eksik))))
    if hatalar:
        print("\n  DÜŞENLER:")
        for mastar, z, k, o, bek, cik, kural, bayrak in hatalar:
            print("    %-10s %-17s %-3s %-6s beklenen %-14s üretilen %-14s  [%s] %s"
                  % (mastar, z, k, "olumsuz" if o else "olumlu", bek, cik, kural, bayrak))
    return 1 if (hatalar or eksik) else 0


if __name__ == "__main__":
    sys.exit(main())
