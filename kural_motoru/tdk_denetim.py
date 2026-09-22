# -*- coding: utf-8 -*-
"""İstisna kovalarının altınını TDK Güncel Türkçe Sözlük'e karşı denetler.

NEDEN
  İstisna kovalarının altını Zemberek bayraklarından türetiliyor. Zemberek
  bayrakları eksik olabiliyor: Arapça `-at` alıntılarının çoğunda NoVoicing
  yazmamış, bizim motor da çok heceli varsayılanıyla yumuşatmış —
  `kıraat -> kıraadi` ürettik, TDK `kıraati` diyor. İnsan tavanı ölçümünde
  bu kovada katılımcıların ŞANS DÜZEYİNİN ALTINA düşmesiyle yakalandı.

KAYNAK
  sozluk.gov.tr/gts sorgusunun `taki` alanı, sözlüğün maddeden hemen sonra
  verdiği çekim ipucudur: `kıraat, -ti` -> `taki: "ti"`. Bu, ünlüyle başlayan
  ek önündeki gövde biçimini doğrudan söyler ve türetmeye gerek bırakmaz.

KARAR
  TDK konuşuyorsa TDK bağlayıcıdır. Susuyorsa (taki boş) madde kıyasta kalır
  ama işaretlenir. Çelişki varsa madde ya düzeltilir ya çıkarılır — sessizce
  bırakılmaz.
"""
import io, json, os, sys, time, urllib.parse, urllib.request

ONBELLEK = "tdk_onbellek.json"
UC = "https://sozluk.gov.tr/gts?ara="


def getir(kelime, onbellek):
    if kelime in onbellek:
        return onbellek[kelime]
    url = UC + urllib.parse.quote(kelime)
    try:
        istek = urllib.request.Request(url, headers={"User-Agent": "TurkMorfBench/3.0"})
        with urllib.request.urlopen(istek, timeout=25) as y:
            d = json.load(y)
        v = [{"madde": x.get("madde"), "taki": x.get("taki") or None,
              "telaffuz": x.get("telaffuz")} for x in d] if isinstance(d, list) and d and "madde" in d[0] else []
    except Exception as e:
        v = {"hata": str(e)[:80]}
    onbellek[kelime] = v
    return v


def main(kaynak="turkmorfbench_v3_tam.json"):
    veri = json.load(io.open(kaynak, encoding="utf8"))["maddeler"]
    hedef = sorted({m["govde"] for m in veri
                    if m["kova"] in ("istisna_uyum_kirici", "istisna_ikizlesme",
                                     "istisna_unlu_dusmesi", "istisna_birlesik_isim")})
    onbellek = json.load(io.open(ONBELLEK, encoding="utf8")) if os.path.exists(ONBELLEK) else {}
    print("denetlenecek gövde: %d (önbellekte %d)" % (len(hedef), len(onbellek)), flush=True)
    for i, g in enumerate(hedef):
        if g not in onbellek:
            getir(g, onbellek)
            time.sleep(0.35)                      # kaynağa saygılı hız
        if (i + 1) % 100 == 0:
            json.dump(onbellek, io.open(ONBELLEK, "w", encoding="utf8"), ensure_ascii=False)
            print("  %d/%d" % (i + 1, len(hedef)), flush=True)
    json.dump(onbellek, io.open(ONBELLEK, "w", encoding="utf8"), ensure_ascii=False)
    print("bitti: %d kayıt" % len(onbellek))


if __name__ == "__main__":
    main(*sys.argv[1:])
