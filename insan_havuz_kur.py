# -*- coding: utf-8 -*-
"""İnsan tavanı havuzunu GÜNCEL kıyas verisinden kurar.

NEDEN YENIDEN KURULUYOR
  Eski havuzun 520 maddesinin 257'si güncel kıyas verisinde yok: havuz bir
  önceki üretimden alınmıştı, kıyas sonra yeniden üretildi. İnsan tavanını
  yayımlanan kıyasta bulunmayan maddeler üzerinde ölçmek, tavanı kıyasa
  bağlayan bağı koparır. Üstelik gövde/hücre kümelemesi de yapılamaz.

  İkinci sorun: gerçek↔uydurma karşılaştırması havuz genelinde yapılamaz.
  Uydurma gövde yalnız ad_cekimi, ad_yuva ve ek_zinciri kovalarında vardır;
  istisna kovaları doğası gereği gerçek kelimelerdir (TDK doğrulamalı).
  Havuz genelinde oran tutturmak "gerçek/uydurma" farkını "istisna/düzenli"
  farkıyla karıştırır. Doğrusu, ikisinin de bulunduğu kovalarda EŞLEŞTIRILMIŞ
  karşılaştırmadır: aynı kova, aynı görev, yarısı gerçek yarısı uydurma.

  Üçüncü sorun: eski etiketlerin bir kısmı hangi istisnanın sınandığını
  katılımcıya söylüyordu ("belirtme (istisna: ikizlesme)"). Bu ipucu tavanı
  şişirir. Etiketler kovadan arındırıldı.

KORUNAN
  Güncel veride HÂLÂ bulunan eski maddeler kotaya öncelikle alınır; böylece
  o maddelere verilmiş yargılar bağlı kalır ve boşa gitmez.
"""
import collections
import json
import random
import sys

TOHUM = 20260924
KOVA_BASI = 40
CIK = "insan_ornegi_v2.json"
SITE = "maddeler_v2.json"

GOREV_ETIKET = {
    "yonelme": "yönelme hâli (-a/-e)", "belirtme": "belirtme hâli (-ı/-i/-u/-ü)",
    "bulunma": "bulunma hâli (-da/-de/-ta/-te)", "ayrilma": "ayrılma hâli (-dan/-den/-tan/-ten)",
    "tamlayan": "tamlayan hâli (-ın/-in/-un/-ün)", "vasita": "vasıta hâli (-la/-le)",
    "edilgen": "edilgen çatı", "ettirgen": "ettirgen çatı",
    "donuslu": "dönüşlü çatı", "istes": "işteş çatı",
    "genis": "geniş zaman, 1. tekil", "olumsuz_genis": "geniş zaman OLUMSUZ, 1. tekil",
    "ci": "-cı/-ci eki", "le": "-la/-le eki", "les": "-laş/-leş eki",
    "lik": "-lık/-lik eki", "li": "-lı/-li eki", "siz": "-sız/-siz eki", "sal": "-sal/-sel eki",
}
IYELIK = {"tek-1t": "benim (iyelik)", "tek-3t": "onun (iyelik)",
          "cog-1c": "çoğul + bizim (iyelik)", "cog-3t": "çoğul + onun (iyelik)"}


def etiket(m):
    """Katılımcıya gösterilen etiket — hangi KURALIN sınandığını ASLA söylemez."""
    kova, gorev = m["kova"], m.get("gorev", "")
    if kova == "ad_yuva" and "-" in gorev:
        *bas, hal = gorev.rsplit("-", 1)
        on = IYELIK.get("-".join(bas), "iyelik")
        return "%s + %s" % (on, GOREV_ETIKET.get(hal, hal).split(" (")[0])
    if kova == "ek_zinciri" and gorev.startswith("derinlik_"):
        return "%s ek arka arkaya" % gorev.split("_")[1]
    e = GOREV_ETIKET.get(gorev)
    if e:
        return e
    return gorev.replace("_", " ")


def main():
    rng = random.Random(TOHUM)
    M = json.load(open("turkmorfbench_v3_tam.json"))["maddeler"]
    eski = {m["k"] for m in json.load(open("insan_ornegi.json"))}

    kovaya = collections.defaultdict(list)
    for m in M:
        if len(m.get("secenek", [])) >= 3:          # 3+ şıklı maddeler
            kovaya[m["kova"]].append(m)

    KARISIK = ("ad_cekimi", "ad_yuva", "ek_zinciri")
    havuz = []
    for kova, hepsi in sorted(kovaya.items()):
        if len(hepsi) < 10:
            continue                                 # kaynastirma (2 madde) dışarıda
        if kova in KARISIK:
            # EŞLEŞTİRİLMİŞ: yarısı gerçek yarısı uydurma, görev dağılımı ortak
            g = [m for m in hepsi if m.get("gercek")]
            u = [m for m in hepsi if m.get("gercek") is False]
            n = KOVA_BASI // 2
            sec = _sec(g, n, eski, rng) + _sec(u, n, eski, rng)
        else:
            sec = _sec(hepsi, KOVA_BASI, eski, rng)
        havuz.extend(sec)

    rng.shuffle(havuz)
    cikti, site = [], []
    for i, m in enumerate(havuz):
        ops = list(m["secenek"])
        rng.shuffle(ops)
        cikti.append({"i": i, "k": m["kimlik"], "kova": m["kova"], "gorev": m.get("gorev"),
                      "govde": m["govde"], "ops": ops, "dogru": ops.index(m["altin"]),
                      "gercek": bool(m.get("gercek"))})
        site.append({"k": m["kimlik"], "govde": m["govde"], "ops": ops,
                     "gercek": bool(m.get("gercek")), "etiket": etiket(m)})

    json.dump(cikti, open(CIK, "w"), ensure_ascii=False)
    json.dump(site, open(SITE, "w"), ensure_ascii=False)

    c = collections.Counter((x["kova"], x["gercek"]) for x in cikti)
    print("havuz: %d madde" % len(cikti))
    print("%-28s %8s %9s" % ("kova", "gerçek", "uydurma"))
    for k in sorted({k for k, _ in c}):
        print("%-28s %8d %9d" % (k, c[(k, True)], c[(k, False)]))
    print("\nTOPLAM gerçek %d · uydurma %d" % (sum(v for (_, g), v in c.items() if g),
                                               sum(v for (_, g), v in c.items() if not g)))
    print("eski havuzdan korunan: %d" % sum(1 for x in cikti if x["k"] in eski))
    kalan = {x["k"] for x in cikti}
    tam = {m["kimlik"] for m in M}
    print("güncel kıyasta bulunmayan: %d" % len(kalan - tam))
    # ipucu sizintisi denetimi
    sizan = [x for x in site if "istisna" in x["etiket"].lower()]
    print("etiketinde kural sızdıran madde: %d" % len(sizan))


def _sec(havuz, n, eski, rng):
    """Önce eski havuzda da bulunanlar (yargıları bağlı kalsın), sonra rastgele."""
    kalan = list(havuz)
    rng.shuffle(kalan)
    oncelik = [m for m in kalan if m["kimlik"] in eski]
    digeri = [m for m in kalan if m["kimlik"] not in eski]
    return (oncelik + digeri)[:n]


if __name__ == "__main__":
    main()
