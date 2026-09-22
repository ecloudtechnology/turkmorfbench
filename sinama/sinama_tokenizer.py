# -*- coding: utf-8 -*-
"""Tokenizer çözümlemesinin altın sınaması — sahte bir jetonlayıcıyla.

Gerçek jetonlayıcı gerektirmeden mantığın doğruluğu sınanır: davranışı
bildiğimiz basit bir bölücü kurup beklenen çıktıyı kontrol ediyoruz.
"""
import sys
import tokenizer_analiz as TA

# Sahte jetonlayıcı: verilen sözlüğe göre açgözlü en uzun eşleşme
SOZLUK = ["kitap", "kitab", "kit", "ab", "ı", "ev", "i", "araba", "y",
          "burun", "burn", "u", "göz", "ü", "lük", "ler", "im", "de"]


def jetonla(s):
    cik, i = [], 0
    while i < len(s):
        for uz in range(min(8, len(s) - i), 0, -1):
            if s[i:i + uz] in SOZLUK:
                cik.append(s[i:i + uz]); i += uz; break
        else:
            cik.append(s[i]); i += 1
    return cik


ALTIN = [
    # (gövde, biçim, beklenen govde_jeton, bicim_jeton, sinir_korundu, govde_bozuldu, ne)
    ("kitap", "kitabı", 1, 2, False, True,
     "yumuşama gövdeyi bozuyor: kitap -> kitab|ı, ortak önek 'kitab' değil 'kita'"),
    ("ev", "evi", 1, 2, True, False, "temiz sınır: ev|i"),
    ("göz", "gözlük", 1, 2, True, False, "temiz sınır: göz|lük"),
    ("burun", "burnu", 1, 2, False, True, "ünlü düşmesi gövdeyi bozuyor"),
    ("araba", "arabayı", 1, 3, True, False, "araba|y|ı, gövde korunuyor"),
]


def main():
    h = 0
    for gv, bc, gj, bj, sk, gb, ne in ALTIN:
        o = TA.coz(jetonla, gv, bc)
        for alan, bek in (("govde_jeton", gj), ("bicim_jeton", bj),
                          ("sinir_korundu", sk), ("govde_bozuldu", gb)):
            ok = o[alan] == bek
            h += 0 if ok else 1
            if not ok:
                print("  ✗ %-8s %-10s %-16s beklenen %s, gelen %s"
                      % (gv, bc, alan, bek, o[alan]))
        print("  %s %-8s -> %-10s %s | %s   [%s]"
              % ("✓" if all(o[a] == b for a, b in (("govde_jeton", gj), ("bicim_jeton", bj),
                                                   ("sinir_korundu", sk), ("govde_bozuldu", gb)))
                 else "✗", gv, bc,
                 "|".join(o["govde_jetonlari"]), "|".join(o["bicim_jetonlari"]), ne))

    # rapor işlevi
    maddeler = [{"kimlik": "a", "govde": "kitap", "altin": "kitabı"},
                {"kimlik": "b", "govde": "ev", "altin": "evi"},
                {"kimlik": "c", "govde": "göz", "altin": "gözlük"}]
    r = TA.rapor(maddeler, jetonla, {"a": False, "b": True, "c": True})
    print("\n--- rapor ---")
    TA.yazdir(r)
    bekle = {"toplam": (2, 3), "gövde BOZULDU": (0, 1), "gövde bozulmadı": (2, 2)}
    for k, (d, t) in bekle.items():
        if k not in r or r[k][0] != d or r[k][1] != t:
            h += 1
            print("  ✗ %s beklenen %s, gelen %s" % (k, (d, t), r.get(k)))
    print("\ndüşen: %d" % h)
    return 1 if h else 0


if __name__ == "__main__":
    sys.exit(main())
