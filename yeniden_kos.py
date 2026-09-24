# -*- coding: utf-8 -*-
"""Erk-32B vs Qwen3-32B — TurkMorfBench 3.3.0'da SIFIRDAN, sabitlenmiş koşulda.

NEDEN
  Kıyasın puanlama kuralı 3.3.0'da değişti (dizi ortalaması -> adayın karakter
  sayısına bölme). Daha önce farklı bir kuralla alınmış sayılarla 3.3.0
  sayılarını aynı kefeye koymak yanlıştır. İki model de BAŞTAN, aynı motorla,
  aynı kesinlikle, aynı bağlamla, aynı puanlama koduyla ve aynı veri
  sürümüyle koşulur.

  Ayrıca genel doğruluk tek başına az şey söyler. Erk'in Türkçe morfolojide
  NEYİ değiştirdiğini görmek için kırılım gerekir: gerçek/uydurma, 14 kova,
  fonolojik hücre, jeton parçalanması, ek zinciri derinliği.

SABITLENENLER (koşum künyesine yazılır)
  motor · kesinlik · bağlam · model yapılandırması · puanlama kodu özeti
  · veri dosyası özeti (sha256) · kıyas sürümü · tohum
"""
import hashlib
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "paket"))

from turkmorfbench import olcum
from turkmorfbench.duyarlilik import KURALLAR, bilesen_topla, coz, karsilastir, rapor
from turkmorfbench.istatistik import esli_fark, katmanli, kume_bootstrap, tasarim_etkisi

VERI = os.environ.get("VERI", "turkmorfbench_v3_tam.json")
CIK = os.environ.get("CIK", "yeniden_kos_sonuc")
DTYPE = os.environ.get("DTYPE", "bfloat16")
N_ORNEK = int(os.environ.get("N_ORNEK", "0"))        # 0 = tamamı
TOHUM = int(os.environ.get("TOHUM", "20260924"))
MODELLER = json.loads(os.environ.get("MODELLER", "{}"))


def ozet(yol):
    h = hashlib.sha256()
    with open(yol, "rb") as f:
        for p in iter(lambda: f.read(1 << 20), b""):
            h.update(p)
    return h.hexdigest()[:16]


def kunye(maddeler):
    import torch
    import transformers
    return {
        "kiyas_surum": "3.3.1",
        "veri_dosyasi": os.path.basename(VERI),
        "veri_ozeti_sha256_16": ozet(VERI),
        "madde": len(maddeler),
        "puanlama_kodu_ozeti": hashlib.sha256(
            open(olcum.__file__, "rb").read()).hexdigest()[:16],
        "motor": "transformers %s" % transformers.__version__,
        "torch": torch.__version__,
        "kesinlik": DTYPE,
        "tohum": TOHUM,
        "an": time.strftime("%Y-%m-%d %H:%M:%S"),
    }


# ---------------------------------------------------------------- katmanlar --
def k_gercek(m):
    return "gerçek gövde" if m.get("gercek") else "uydurma gövde"


def k_kova(m):
    return m.get("kova")


def k_derinlik(m):
    h = m.get("hucre")
    if isinstance(h, list) and len(h) > 2 and isinstance(h[2], int):
        return "derinlik %d" % h[2]
    return "derinlik yok"


def k_uyum(m):
    h = m.get("hucre")
    return h[3] if isinstance(h, list) and len(h) > 3 else "yok"


def parcalanma_katmani(arka):
    """Gövdenin kaç jetona bölündüğü — jetonlayıcı verimi sınıfı."""
    onbellek = {}

    def f(m):
        g = m.get("govde")
        if g not in onbellek:
            n = len(arka.jetonla(g))
            onbellek[g] = "1 jeton" if n <= 1 else ("2 jeton" if n == 2 else "3+ jeton")
        return onbellek[g]
    return f


def main():
    maddeler = json.load(open(VERI))
    maddeler = maddeler["maddeler"] if isinstance(maddeler, dict) else maddeler
    if N_ORNEK:
        import random
        maddeler = random.Random(TOHUM).sample(maddeler, min(N_ORNEK, len(maddeler)))

    os.makedirs(CIK, exist_ok=True)
    k = kunye(maddeler)
    print("KÜNYE:", json.dumps(k, ensure_ascii=False, indent=2), flush=True)
    json.dump(k, open(os.path.join(CIK, "kunye.json"), "w"),
              ensure_ascii=False, indent=2)

    kayitlar, arkalar = {}, {}
    for ad, yol in MODELLER.items():
        print("\n===== %s — %s" % (ad, yol), flush=True)
        t0 = time.time()
        arka = olcum.Yerel(yol, dtype=DTYPE)
        arkalar[ad] = arka
        kayit = bilesen_topla(
            arka, maddeler,
            ilerleme=lambda i, n: (i % 2000 == 0) and
            print("   %d/%d  (%.1f dk)" % (i, n, (time.time() - t0) / 60), flush=True))
        kayitlar[ad] = kayit
        json.dump(kayit, open(os.path.join(CIK, "bilesen_%s.json" % ad), "w"))
        c = coz(kayit)
        print("   %s" % "  ".join("%s %.2f%%" % (r, 100 * c[r]["dogruluk"])
                                  for r in KURALLAR), flush=True)
        del arka, arkalar[ad]

    adlar = list(kayitlar)
    if len(adlar) < 2:
        print("tek model koşuldu; karşılaştırma yapılmadı")
        return

    a, b = adlar[0], adlar[1]
    tum = {}

    # 1) puanlama kurali duyarliligi
    for anahtar in ("govde", "hucre"):
        s = karsilastir(kayitlar[a], kayitlar[b], maddeler, a, b, anahtar=anahtar)
        print("\n--- PUANLAMA KURALI DUYARLILIĞI (%s kümeli) ---" % anahtar, flush=True)
        print(rapor(s, a, b), flush=True)
        tum["duyarlilik_%s" % anahtar] = s

    # 2) tasarim etkisi: madde duzeyi bootstrap ne kadar sahte kesinlik uretiyor
    ca = coz(kayitlar[a])
    print("\n--- TASARIM ETKİSİ (%s, harf kuralı) ---" % a, flush=True)
    tum["tasarim_etkisi"] = {}
    for anahtar in ("govde", "hucre", "kova"):
        t = tasarim_etkisi(maddeler, ca["harf"]["dogru"], anahtar, b=1000)
        tum["tasarim_etkisi"][anahtar] = t
        print("   %-6s aralık %.1f kat geniş · etkin n = %d (ham %d)"
              % (anahtar, t["genislik_kati"], t["etkin_n"], t["n_madde"]), flush=True)

    # 3) katmanli kirilim — genel dogruluk tek basina az sey soyler
    cb = coz(kayitlar[b])
    katmanlar = [("gercek_uydurma", k_gercek), ("kova", k_kova),
                 ("derinlik", k_derinlik), ("uyum", k_uyum)]
    tum["katmanli"] = {}
    for ad, f in katmanlar:
        print("\n--- KATMAN: %s ---" % ad, flush=True)
        sa = katmanli(maddeler, ca["harf"]["dogru"], f, anahtar="govde", b=800)
        sb = katmanli(maddeler, cb["harf"]["dogru"], f, anahtar="govde", b=800)
        satir = {}
        for k2 in sa:
            if "ortalama" not in sa[k2] or "ortalama" not in sb.get(k2, {}):
                continue
            ix = [i for i, m in enumerate(maddeler) if f(m) == k2]
            fk = esli_fark([maddeler[i] for i in ix],
                           [ca["harf"]["dogru"][i] for i in ix],
                           [cb["harf"]["dogru"][i] for i in ix],
                           anahtar="govde", b=800)
            satir[k2] = {a: sa[k2], b: sb[k2], "fark": fk}
            print("   %-22s %s %6.2f%%  %s %6.2f%%  fark %+6.2f%% [%+.2f, %+.2f]%s"
                  % (k2, a, 100 * sa[k2]["ortalama"], b, 100 * sb[k2]["ortalama"],
                     100 * fk["fark"], 100 * fk["ci"][0], 100 * fk["ci"][1],
                     " *" if fk["anlamli"] else ""), flush=True)
        tum["katmanli"][ad] = satir

    json.dump(tum, open(os.path.join(CIK, "cozumleme.json"), "w"),
              ensure_ascii=False, indent=2, default=str)
    print("\nyazıldı: %s" % CIK, flush=True)


if __name__ == "__main__":
    main()
