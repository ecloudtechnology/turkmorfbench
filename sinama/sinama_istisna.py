# -*- coding: utf-8 -*-
"""İstisna kovalarının altın sınaması — özellikle okunuşa bağlı üç kova."""
import sys
import sozluk, istisna, sayi

# --- sayı okunuşu
SAYI_OKU = [
    (0, "sıfır"), (1, "bir"), (6, "altı"), (10, "on"), (11, "on bir"),
    (20, "yirmi"), (100, "yüz"), (101, "yüz bir"), (200, "iki yüz"),
    (1000, "bin"), (2000, "iki bin"), (2026, "iki bin yirmi altı"),
    (1453, "bin dört yüz elli üç"), (1000000, "bir milyon"),
    (12345, "on iki bin üç yüz kırk beş"),
]

# --- sayı + ek  (okunuşa göre uyum)
SAYI_EK = [
    (2026, "bulunma", "2026'da",  "…yirmi altı -> kalın"),
    (1,    "yonelme", "1'e",      "bir -> ince"),
    (100,  "belirtme","100'ü",    "yüz -> ince yuvarlak"),
    (6,    "belirtme","6'yı",     "altı -> ünlüyle biter, kaynaştırma"),
    (3,    "bulunma", "3'te",     "üç -> ötümsüz, benzeşme"),
    (1000, "bulunma", "1000'de",  "bin -> ince"),
    (40,   "yonelme", "40'a",     "kırk -> kalın"),
    (7,    "yonelme", "7'ye",     "yedi -> ünlüyle biter"),
]

# --- özel ad + kesme (YUMUŞAMA YOK)
OZEL = [
    ("Ankara",     "yonelme",  "Ankara'ya",     "ünlüyle biter, kaynaştırma"),
    ("İzmir",      "yonelme",  "İzmir'e",       "ince"),
    ("Sinop",      "yonelme",  "Sinop'a",       "YUMUŞAMA YOK (Sinob'a değil)"),
    ("Zonguldak",  "yonelme",  "Zonguldak'a",   "YUMUŞAMA YOK (Zonguldağ'a değil)"),
    ("Sinop",      "belirtme", "Sinop'u",       "ünlüyle başlayan ekte de yumuşama yok"),
    ("Bolu",       "bulunma",  "Bolu'da",       "yuvarlak"),
    ("Uşak",       "belirtme", "Uşak'ı",        "YUMUŞAMA YOK"),
]

# --- kısaltma (OKUNUŞA göre)
KIS = [
    ("TCDD",    "tecedede", "belirtme", "TCDD'yi",    "okunuş ünlüyle biter"),
    ("TÜBİTAK", "tübitak",  "tamlayan", "TÜBİTAK'ın", "okunuş ünsüzle biter, kalın"),
    ("AB",      "abe",      "yonelme",  "AB'ye",      "okunuş ünlüyle biter, ince"),
    ("TBMM",    "tebememe", "belirtme", "TBMM'yi",    "okunuş ünlüyle biter"),
    ("SMS",     "semese",   "belirtme", "SMS'yi",     "okunuş ünlüyle biter"),
]


def main():
    h = 0
    print("SAYI OKUNUŞU")
    for n, bek in SAYI_OKU:
        c = sayi.oku(n)
        ok = c == bek
        h += 0 if ok else 1
        print("  %s %-8d -> %-26s %s" % ("✓" if ok else "✗", n, c, "" if ok else "beklenen: " + bek))

    print("\nSAYI + EK")
    for n, hal, bek, ne in SAYI_EK:
        c = istisna.sayi_eki(n, hal)
        ok = c == bek
        h += 0 if ok else 1
        print("  %s %-10s -> %-12s [%s]%s" % ("✓" if ok else "✗", n, c, ne,
                                              "" if ok else "  beklenen: " + bek))

    print("\nÖZEL AD + KESME")
    for a, hal, bek, ne in OZEL:
        c = istisna.ozel_ad(a, hal)
        ok = c == bek
        h += 0 if ok else 1
        print("  %s %-12s -> %-16s [%s]%s" % ("✓" if ok else "✗", a, c, ne,
                                              "" if ok else "  beklenen: " + bek))

    print("\nKISALTMA")
    for k, pr, hal, bek, ne in KIS:
        c = istisna.kisaltma(k, pr, hal)
        ok = c == bek
        h += 0 if ok else 1
        print("  %s %-10s -> %-14s [%s]%s" % ("✓" if ok else "✗", k, c, ne,
                                              "" if ok else "  beklenen: " + bek))

    print("\ndüşen: %d" % h)
    return 1 if h else 0


if __name__ == "__main__":
    sys.exit(main())
