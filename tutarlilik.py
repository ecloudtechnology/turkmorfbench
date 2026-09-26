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

# --- TDK-doğrulamalı üç kovanın toplamı (kova_sayilari.json'dan) metindeki sayıyla eşleşmeli
def tdk_toplam_kontrol(kova, metinler):
    TDK_DOGRULAMALI = ("istisna_unlu_dusmesi", "istisna_uyum_kirici", "istisna_ikizlesme")
    toplam = sum(kova[k] for k in TDK_DOGRULAMALI)
    hata = []
    for ad, s in metinler.items():
        for kalip in ("**%d maddesinin tamamının**", "All %d items"):
            if (kalip % toplam) not in s:
                hata.append("%s: '%s' bulunamadı" % (ad, kalip % toplam))
        for eski in ("317",):
            if re.search(r"\b%s maddesinin|All %s items" % (eski, eski), s):
                hata.append("%s: eski TDK toplamı %s hâlâ metinde" % (ad, eski))
    return toplam, hata

SURUM_KISA = ".".join((json.load(open(KUNYE))["surum"] if KUNYE else "0.0").split(".")[:2])
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

# 4) TDK-dogrulamali uc kovanin toplami metindeki sayiyla ayni olmali (3.6.2'de 317 kalmisti; dogrusu 283)
_metin = {}
for yol in [y for y in (bul("HF-KART.md", "README.md"), bul("paket/README.md")) if y]:
    _metin[yol.split("/")[-1]] = open(yol).read()
_t, _h = tdk_toplam_kontrol(say, _metin)
hata.extend(_h)
print("TDK-doğrulamalı toplam: %d (unlu_dusmesi+uyum_kirici+ikizlesme)" % _t)

# jsonl disa aktarimlari json ile BIREBIR ayni mi (HF veri dosyasi jsonl'dir;
# uret.py yalniz json yazar — jsonl yenilenmezse kart ile veri ayrisir)
for _ad in ("tam", "cekirdek"):
    _j = bul("turkmorfbench_v3_%s.json" % _ad); _l = bul("turkmorfbench_v3_%s.jsonl" % _ad, "veri/turkmorfbench_v3_%s.jsonl" % _ad)
    if _j and _l:
        _n = sum(1 for _ in open(_l, encoding="utf8"))
        _m = json.load(open(_j)); _m = _m["maddeler"] if isinstance(_m, dict) else _m
        if _n != len(_m):
            hata.append("%s.jsonl %d satir, %s.json %d madde — jsonl ESKI" % (_ad, _n, _ad, len(_m)))

# 6) PAKET SABITLERI ve paket kaynak kodunda eski sayilar (veri.py TAM_N/CEKIRDEK_N veriyle ayni olmali)
import glob as _glob
for _py in _glob.glob(os.path.join(os.path.dirname(bul("paket/pyproject.toml") or "paket/pyproject.toml"), "turkmorfbench", "*.py")):
    _s = open(_py, encoding="utf8").read()
    for _eski in (r"465[.,]241", r"449[.,]?\d{3}", r"1[.,]856"):
        if re.search(_eski, _s):
            hata.append("%s: paket kodunda eski sayı %s" % (os.path.basename(_py), _eski))
    if _py.endswith("veri.py"):
        _m = re.search(r"TAM_N = ([\d_]+)", _s); _c = re.search(r"CEKIRDEK_N = ([\d_]+)", _s)
        if not _m or int(_m.group(1).replace("_", "")) != toplam:
            hata.append("veri.py: TAM_N %s, veri %s" % (_m.group(1) if _m else None, toplam))
        if not _c or int(_c.group(1).replace("_", "")) != cekirdek_n:
            hata.append("veri.py: CEKIRDEK_N %s, veri %s" % (_c.group(1) if _c else None, cekirdek_n))

# 5) model karsilastirma tablosu basligi guncel surumun cekirdegini gostermeli
for _ad, _s in _metin.items():
    for _eski in re.findall(r"TurkMorfBench (3\.\d) (?:çekirdek|core)", _s):
        if _eski != SURUM_KISA:
            hata.append("%s: karşılaştırma tablosu başlığı %s çekirdeğinde, veri %s" % (_ad, _eski, SURUM_KISA))

if hata:
    print("\nTUTARSIZLIK (%d):" % len(hata))
    for h in hata:
        print("  ✗", h)
    sys.exit(1)

print("\nTÜM KAYNAKLAR VERİYLE TUTARLI ✓")

# --------------------------------------------------------------- paket ----
def paket_denetle(hedef=None):
    """YAYIMLANAN paketin uzun aciklamasini da veriye karsi denetler.

    NEDEN AYRI
      Yerel dosyalar dogru olsa bile yayimlanan pakete ESKI bir README
      girebilir: surum kurulurken derleme baska bir dosyadan okuyabilir,
      onbellekli bir egg-info kalabilir, ya da yanlis dizinden derlenebilir.
      Okuyucunun gordugu sey PyPI'deki uzun aciklamadir; denetim oraya da
      bakmazsa bu sinif gerileme sessizce gecer.

    hedef: .tar.gz / .whl yolu, ya da None ise kurulu paketin ustverisi.
    """
    import io
    import tarfile
    import zipfile

    if hedef is None:
        from importlib import metadata
        acik = metadata.metadata("turkmorfbench").get_payload() or ""
        if not acik:
            acik = metadata.metadata("turkmorfbench").get("Description", "") or ""
        kaynak = "kurulu paket"
    elif hedef.endswith(".whl"):
        z = zipfile.ZipFile(hedef)
        ad = [n for n in z.namelist() if n.endswith(".dist-info/METADATA")][0]
        acik = z.read(ad).decode("utf8")
        kaynak = hedef
    else:
        t = tarfile.open(hedef)
        ad = [n for n in t.getnames() if n.endswith("PKG-INFO")][0]
        acik = t.extractfile(ad).read().decode("utf8")
        kaynak = hedef

    hata = []
    for kova, n in say.items():
        if "`%s`" % kova not in acik:
            hata.append("tabloda eksik kova: %s" % kova)
            continue
        for satir in acik.split("\n"):
            if "`%s`" % kova in satir and satir.strip().startswith("|"):
                if tr(n) not in satir:
                    hata.append("%s: %s beklenirdi, satir: %s" % (kova, tr(n), satir.strip()[:70]))
                break
    if tr(toplam) not in acik:
        hata.append("manset sayi %s gecmiyor" % tr(toplam))
    for kalip in ESKI:
        if re.search(kalip, acik):
            hata.append("ESKI sayi kalmis: %s" % kalip)
    return kaynak, hata


if __name__ == "__main__" and "--paket" in sys.argv:
    i = sys.argv.index("--paket")
    yol = sys.argv[i + 1] if len(sys.argv) > i + 1 else None
    kaynak, h = paket_denetle(yol)
    print("\nPAKET DENETIMI (%s)" % kaynak)
    if h:
        for x in h:
            print("  X", x)
        sys.exit(1)
    print("  yayimlanan aciklama veriyle TUTARLI ✓")

