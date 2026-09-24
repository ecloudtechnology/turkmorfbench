# -*- coding: utf-8 -*-
"""Yayimlanan her kaynaktaki sayilari URETILEN VERIYE karsi denetler.

NEDEN VAR
  HF karti 465.241 e guncellenmisti; PyPI README inin MANSETI guncellenmis ama
  KOVA TABLOSU eski dokumde kalmisti, site ise ucuncu bir sayi (449.233)
  gosteriyordu. Ucu de ayni anda yayindaydi. Sayi yayimlayan bir ekip icin bu,
  olcumun kendisinden daha cok zarar verir.

KURAL
  Tek dogru kaynak uretilen veridir. Belgeler ona uyar, tersi degil.
  Bu betik gecmeden surum cikarilmaz.
"""
import collections
import json
import re
import sys

import os

KOK = os.path.dirname(os.path.abspath(__file__))


def bul(*adaylar):
    """Dosyayi hem calisma kopyasinda hem depo duzeninde arar."""
    for a in adaylar:
        y = os.path.join(KOK, a)
        if os.path.exists(y):
            return y
    return None


VERI = bul("turkmorfbench_v3_tam.json", "veri/turkmorfbench_v3_tam.json")
KUNYE = bul("kova_sayilari.json", "veri/kova_sayilari.json")
CEKIRDEK = bul("turkmorfbench_v3_cekirdek.json",
               "veri/turkmorfbench_v3_cekirdek.json")

KAYNAKLAR = [y for y in (
    bul("HF-KART.md", "README.md"),
    bul("paket/README.md"),
    bul("morf-site/index.php"),
    bul("paket/turkmorfbench/veri.py"),
    bul("paket/turkmorfbench/__main__.py"),
) if y]


def tr(n):
    return format(n, ",d").replace(",", ".")


def oku(yol):
    d = json.load(open(yol))
    return d["maddeler"] if isinstance(d, dict) else d


# Tam kume depoda tasinmaz (HF de durur). Yoksa kunyeye duseriz; kunye de
# uret.py ciktisindan turetilir, yani dogru kaynak yine veridir.
if VERI:
    mad = oku(VERI)
    cek = oku(CEKIRDEK)
    say = collections.Counter(x["kova"] for x in mad)
    toplam = len(mad)
    cekirdek_n = len(cek)
    kaynak = "üretilen veri"
elif KUNYE:
    k = json.load(open(KUNYE))
    say = collections.Counter(k["kova"])
    toplam = k["tam"]
    cekirdek_n = k["cekirdek"]
    kaynak = "kova_sayilari.json künyesi"
else:
    sys.exit("ne tam veri ne künye bulundu")

print("KAYNAK (%s): %s madde · %d kova · çekirdek %s"
      % (kaynak, tr(toplam), len(say), tr(cekirdek_n)))
assert sum(say.values()) == toplam, "kova toplamı madde sayısını tutmuyor"

hata = []

# 1) manset sayi her kaynakta gecmeli ve ESKI sayilar hic gecmemeli
ESKI = [r"449[.,]?\d{3}", r"449k", r"~?449\.000"]
for yol in KAYNAKLAR:
    try:
        s = open(yol).read()
    except (FileNotFoundError, TypeError):
        continue
    for kalip in ESKI:
        for m in re.finditer(kalip, s):
            satir = s[: m.start()].count("\n") + 1
            hata.append("%s:%d eski sayı '%s'" % (yol.split("/")[-1], satir, m.group()))

# 2) kova tablosu satirlari veriyle bire bir tutmali
for yol in [y for y in (bul("HF-KART.md", "README.md"), bul("paket/README.md")) if y]:
    s = open(yol).read()
    gorulen = set()
    for satir in s.split("\n"):
        if not satir.startswith("|"):
            continue
        for kova in say:
            if "`%s`" % kova in satir:
                gorulen.add(kova)
                sayilar = re.findall(r"\b\d{1,3}(?:\.\d{3})*\b", satir)
                if tr(say[kova]) not in sayilar:
                    hata.append("%s: %s satırında %s beklenirdi, bulunan %s"
                                % (yol.split("/")[-1], kova, tr(say[kova]), sayilar))
    eksik = set(say) - gorulen
    if eksik:
        hata.append("%s: tabloda eksik kova: %s" % (yol.split("/")[-1], sorted(eksik)))

# 3) cekirdek sayisi
for yol in [y for y in (bul("HF-KART.md", "README.md"), bul("paket/README.md")) if y]:
    s = open(yol).read()
    if tr(cekirdek_n) not in s and format(cekirdek_n, ",d") not in s:
        hata.append("%s: çekirdek sayısı %s geçmiyor" % (yol.split("/")[-1], tr(cekirdek_n)))

if hata:
    print("\nTUTARSIZLIK (%d):" % len(hata))
    for h in hata:
        print("  ✗", h)
    sys.exit(1)

print("\nTÜM KAYNAKLAR VERİYLE TUTARLI ✓")
