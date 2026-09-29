# -*- coding: utf-8 -*-
"""Kural motorunun BAĞIMSIZ dış sınavı: Universal Dependencies Türkçe ağaç bankaları.

NEDEN
  Kıyasın altını kendi kural motorumuzdan geliyor. Motoru kendi testleriyle
  sınamak döngüseldir: 282 altın iddiayı da biz yazdık. UD ağaç bankaları
  başka ekiplerin elle etiketlediği, hakemli, yayımlanmış veridir — bizim
  hiçbir şekilde etkilemediğimiz bir kaynak.

NE SINANIYOR
  UD her kelime için yüzey biçimini, sözlük biçimini (lemma) ve biçimbirim
  özniteliklerini verir:
      FORM=kitabı  LEMMA=kitap  UPOS=NOUN  FEATS=Case=Acc|Number=Sing
  Bu üçlü bizim `ad_cekim.cekim(kitap, hal=belirtme)` çağrımızın tam
  karşılığıdır. Motor `kitabı` üretiyorsa uyuşur.

NE SINANMIYOR — ve neden
  UD Türkçe ağaç bankaları ekleri her zaman aynı çözümlemiyor; iyelik ve
  bazı hâller bankadan bankaya ayrışıyor. Bu yüzden yalnız ÜÇ BANKANIN DA
  aynı biçimde etiketlediği kalıplar alınır ve ayrışan kalıplar rapora
  "ayrıştı" diye yazılır, sessizce atılmaz.

  Ayrıca UD'de gövde sözlükte olmayabilir; bizim motor sözlük bayrağı
  olmadan düzensiz gövdeyi bilemez. O maddeler "sözlükte yok" diye ayrı
  sayılır — motorun hatası değil, kapsamının dışı.
"""
import collections
import glob
import io
import os
import sys

import ad_cekim
import sozluk

# UD öznitelik birleşimi -> bizim yuva adlarımız
HAL = {"Nom": "yalin", "Acc": "belirtme", "Dat": "yonelme", "Loc": "bulunma",
       "Abl": "ayrilma", "Gen": "tamlayan", "Ins": "vasita"}
COKLUK = {"Sing": "tek", "Plur": "cog"}
IYELIK = {("1", "Sing"): "1t", ("2", "Sing"): "2t", ("3", "Sing"): "3t",
          ("1", "Plur"): "1c", ("2", "Plur"): "2c", ("3", "Plur"): "3c"}


# UD metinleri tek biçimli değil: özel adlarda kesme işareti var
# (bey'in), bazı bölümler Türkçe harfsiz yazılmış (baliklarinin),
# düzeltme işareti bankadan bankaya değişiyor (hâl / hal) ve bazı
# dosyalar birleşik imli 'i' kullanıyor (i̇tfaiyesi). Bunlar YAZIM
# farkıdır, çekim farkı değil. İkisini ayrı raporlamak gerekiyor:
# ham uyum, motorun UD metnini birebir tutturma oranıdır; normalleşmiş
# uyum ise çekimi tutturma oranı.
import unicodedata

_KATLA = str.maketrans({"â": "a", "î": "i", "û": "u", "Â": "a", "Î": "i", "Û": "u",
                        "'": "", "’": "", "`": ""})


def duzle(x):
    x = unicodedata.normalize("NFC", x).lower().translate(_KATLA)
    return x


def turkcesiz(x):
    """Metinde hiç Türkçeye özgü harf yoksa ASCII'ye katlanmış demektir."""
    return not any(c in "çğıöşü" for c in x)


def oz(feats):
    d = {}
    for p in (feats or "").split("|"):
        if "=" in p:
            k, v = p.split("=", 1)
            d[k] = v
    return d


def oku(yol):
    """CoNLL-U'dan (banka, form, lemma, upos, öznitelikler) üretir."""
    banka = os.path.basename(yol).split("-")[0]
    for satir in io.open(yol, encoding="utf8"):
        satir = satir.strip()
        if not satir or satir.startswith("#"):
            continue
        p = satir.split("\t")
        if len(p) < 6 or "-" in p[0] or "." in p[0]:
            continue                      # çok sözcüklü öbek başlığı / boş düğüm
        yield banka, p[1], p[2], p[3], oz(p[5])


def yuva(f):
    """UD öznitelikleri -> (çokluk, iyelik, hâl) ya da None (kapsam dışı)."""
    if f.get("Case") not in HAL or f.get("Number") not in COKLUK:
        return None
    iy = "yok"
    if "Person[psor]" in f or "Number[psor]" in f:
        k = (f.get("Person[psor]"), f.get("Number[psor]"))
        if k not in IYELIK:
            return None
        iy = IYELIK[k]
    # türetme/birleşim taşıyan biçimler bu sınavın dışında
    for kotu in ("Polarity", "Aspect", "Mood", "Tense", "VerbForm", "Voice"):
        if kotu in f:
            return None
    return COKLUK[f["Number"]], iy, HAL[f["Case"]]


def main(dizin="ud"):
    ham = sozluk.yukle(("master", "non_tdk"))
    adlar = sozluk.indeksle([m for m in ham if m.tur in ("Noun", "Adj")])
    belirsiz = sozluk.belirsizler([m for m in ham if m.tur in ("Noun", "Adj")])

    # (lemma, yuva) -> {banka: {yüzey biçimleri}}
    kayit = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
    for yol in sorted(glob.glob(os.path.join(dizin, "*.conllu"))):
        for banka, form, lemma, upos, f in oku(yol):
            if upos not in ("NOUN", "PROPN", "ADJ"):
                continue
            y = yuva(f)
            if y is None:
                continue
            kayit[(lemma.lower(), y)][banka][form.lower()] += 1

    s = collections.Counter()
    ayrisan, uyusmayan = [], []
    for (lemma, y), bankalar in kayit.items():
        # bankalar arası uzlaşma: her bankanın en sık biçimi aynı mı?
        baskin = {b: c.most_common(1)[0][0] for b, c in bankalar.items()}
        if len(set(baskin.values())) > 1:
            s["bankalar ayrıştı"] += 1
            if len(ayrisan) < 20:
                ayrisan.append((lemma, y, baskin))
            continue
        gozlem = next(iter(baskin.values()))
        m = adlar.get(lemma)
        if m is None:
            s["sözlükte yok"] += 1
            continue
        if lemma in belirsiz:
            s["eş yazılışlı (kıyasa da girmiyor)"] += 1
            continue
        cokluk, iyelik, hal = y
        try:
            bizim = ad_cekim.cekim(m, cokluk=cokluk, iyelik=iyelik, hal=hal)
        except Exception:
            s["motor hatası"] += 1
            continue
        if bizim.lower() == gozlem:
            s["UYUYOR"] += 1
            s["normal UYUYOR"] += 1
        elif duzle(bizim) == duzle(gozlem):
            s["UYUŞMUYOR"] += 1
            s["normal UYUYOR"] += 1
            s["  yalnız yazım farkı (kesme/düzeltme imi)"] += 1
        elif turkcesiz(gozlem) and not turkcesiz(bizim):
            s["UYUŞMUYOR"] += 1
            s["  UD Türkçe harfsiz yazılmış"] += 1
        else:
            s["UYUŞMUYOR"] += 1
            s["normal UYUŞMUYOR"] += 1
            if len(uyusmayan) < 600:
                uyusmayan.append((lemma, y, gozlem, bizim, sorted(m.bayrak)))

    t = s["UYUYOR"] + s["UYUŞMUYOR"]
    print("UD TÜRKÇE AĞAÇ BANKALARI — bağımsız dış sınav")
    print("  incelenen (lemma, yuva) çifti: %d" % len(kayit))
    for k, v in s.most_common():
        print("    %-34s %6d" % (k, v))
    if t:
        print("\n  KARŞILAŞTIRILABİLİR %d madde" % t)
        print("    ham uyum (UD metnini birebir)        %%%.2f" % (100 * s["UYUYOR"] / t))
        nt = s["normal UYUYOR"] + s["normal UYUŞMUYOR"]
        if nt:
            print("    çekim uyumu (yazım normalleşmiş)     %%%.2f" %
                  (100 * s["normal UYUYOR"] / t))

    print("\n  uyuşmayanlardan örnek:")
    for lemma, y, g, b, bay in uyusmayan[:20]:
        print("    %-16s %-18s UD %-20s biz %-20s %s" %
              (lemma, "/".join(y), g, b, ",".join(bay) or "-"))
    print("\n  bankaların ayrıştığı örnekler (sınava alınmadı):")
    for lemma, y, bk in ayrisan[:8]:
        print("    %-16s %-18s %s" % (lemma, "/".join(y), bk))

    import json
    json.dump({"ozet": dict(s), "uyum": (100 * s["UYUYOR"] / t) if t else None,
               "uyusmayan": [(l, list(y), g, b, bay) for l, y, g, b, bay in uyusmayan]},
              io.open("ud_denetim_sonuc.json", "w", encoding="utf8"),
              ensure_ascii=False, indent=1)
    print("\nyazıldı: ud_denetim_sonuc.json")


if __name__ == "__main__":
    main(*sys.argv[1:])
