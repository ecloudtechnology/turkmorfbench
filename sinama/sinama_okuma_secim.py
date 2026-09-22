# -*- coding: utf-8 -*-
"""Okuma ve zorunlu seçim modüllerinin altın sınaması."""
import sys
import sozluk, oku, secim

# --- OKUMA: gerçek model çıktılarından alınmış örnekler
OKUMA = [
    # (ham çıktı, gövde, beklenen okuma, ne sınanıyor)
    (" ??\nKelime: zakak\nSonuc: zakaklar\n\nAçıklama: \"-lar\" eki",
     "zakak", "zakaklar", "dolgu '??' atlanır, doğru cevap bulunur"),
    (" ?\n\nEkler: ler, ımız, de, ki\n\nBu eklerin sırasıyla",
     "sövot", None, "cevap gerçekten yok -> okunamadı"),
    (" kalemler\n\nKelime: masa\nSonuc: masalar",
     "kalem", "kalemler", "doğrudan cevap"),
    (" vıseplerimizdaki\n\nKelime: kalem", "vısep", "vıseplerimizdaki",
     "yanlış ama okunabilir cevap okunur"),
    ("Sonuç: kitabı", "kitap", "kitabı", "etiket atlanır"),
    ("  kitabı.", "kitap", "kitabı", "noktalama temizlenir"),
    ("Cevap: bu kelimenin hali kitabı olur", "kitap", "kitabı",
     "cümle içinden çıkarılır"),
    ("evleri", "ev", "evleri", "kısa gövde"),
]

# --- SEÇİM: çeldiricilerin doğruluğu
SECIM = [
    ("kitap", "belirtme", "kitabı", {"uyum": "kitabi", "yumusama": "kitapı"}),
    ("araba", "belirtme", "arabayı", {"uyum": "arabayi"}),
    ("ev",    "belirtme", "evi",     {"uyum": "evı"}),
]


def main():
    h = 0
    print("OKUMA")
    for ham, gv, bek, ne in OKUMA:
        c = oku.cevap_bul(ham, gv)
        ok = (c == bek)
        h += 0 if ok else 1
        print("  %s %-28s -> %-22s [%s]" % ("✓" if ok else "✗", repr(ham[:26]),
                                            repr(c), ne))
        if not ok:
            print("      beklenen %r" % bek)

    print("\nSEÇİM")
    ham2 = sozluk.yukle(("master", "non_tdk"))
    adlar = sozluk.indeksle([m for m in ham2 if m.tur in ("Noun", "Adj")])
    for gv, hal, bek_altin, bek_cel in SECIM:
        m = adlar[gv]
        altin, cel = secim.celdiriciler(m, hal)
        ok = altin == bek_altin
        h += 0 if ok else 1
        print("  %s %-8s altın %-10s çeldirici %s" % ("✓" if ok else "✗", gv, altin, cel))
        for tur, bicim in bek_cel.items():
            var = cel.get(tur) == bicim
            h += 0 if var else 1
            if not var:
                print("      ✗ %s bekleniyordu %r, gelen %r" % (tur, bicim, cel.get(tur)))
        # altın çeldiriciler arasında OLMAMALI
        if altin in cel.values():
            h += 1
            print("      ✗ altın çeldirici listesinde!")

    print("\ndüşen: %d" % h)
    return 1 if h else 0


if __name__ == "__main__":
    sys.exit(main())
