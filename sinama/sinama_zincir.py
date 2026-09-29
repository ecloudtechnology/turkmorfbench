"""Ek zinciri merdiveninin altın sınaması.

Sekiz basamağın her biri elle doğrulandı. Merdiven bozulursa bütün derinlik
ekseni çöker, o yüzden her basamak ayrı bir iddia.
"""
import sys
import sozluk, zincir

ALTIN = {
    "ev": ["evler", "evlerimiz", "evlerimizde", "evlerimizdeki",
           "evlerimizdekiler", "evlerimizdekilerden", "evlerimizdekilerdenmiş",
           "evlerimizdekilerdenmişsiniz"],
    "kitap": ["kitaplar", "kitaplarımız", "kitaplarımızda", "kitaplarımızdaki",
              "kitaplarımızdakiler", "kitaplarımızdakilerden",
              "kitaplarımızdakilerdenmiş", "kitaplarımızdakilerdenmişsiniz"],
    "kuş": ["kuşlar", "kuşlarımız", "kuşlarımızda", "kuşlarımızdaki",
            "kuşlarımızdakiler", "kuşlarımızdakilerden",
            "kuşlarımızdakilerdenmiş", "kuşlarımızdakilerdenmişsiniz"],
    "göz": ["gözler", "gözlerimiz", "gözlerimizde", "gözlerimizdeki",
            "gözlerimizdekiler", "gözlerimizdekilerden",
            "gözlerimizdekilerdenmiş", "gözlerimizdekilerdenmişsiniz"],
    "araba": ["arabalar", "arabalarımız", "arabalarımızda", "arabalarımızdaki",
              "arabalarımızdakiler", "arabalarımızdakilerden",
              "arabalarımızdakilerdenmiş", "arabalarımızdakilerdenmişsiniz"],
}


def main():
    ham = sozluk.yukle(("master", "non_tdk"))
    adlar = sozluk.indeksle([m for m in ham if m.tur in ("Noun", "Adj")])
    gecen = kalan = 0
    for gv, bek in ALTIN.items():
        m = adlar.get(gv)
        # merdivenin ilk eki -lAr, ünsüzle başlar: gövde bozulmaz
        hazir = gv
        for (d, ad, cik), b in zip(zincir.basamaklar(hazir), bek):
            if cik == b:
                gecen += 1
            else:
                kalan += 1
                print("    %-8s derinlik %d (%s)  beklenen %-32s üretilen %s"
                      % (gv, d, ad, b, cik))
    print("ALTIN SINAMA — ek zinciri")
    print("  geçen %d / %d" % (gecen, gecen + kalan))
    return 1 if kalan else 0


if __name__ == "__main__":
    sys.exit(main())
