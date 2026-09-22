"""TurkMorfBench v3 madde kümesini üretir — dondurulmuş, iki katmanlı.

İKİ KATMAN, BİR GERGİNLİĞİN ÇÖZÜMÜ
  Kıyasın hem KAPSAMLI hem KOŞULABİLİR olması gerekiyor. 250 bin maddelik bir
  kıyası kimse koşmaz: bir modeli değerlendirmek günler sürer ve benimsenmez.
  İki bin maddelik bir kıyas ise tasarlanan kapsamı taşıyamaz.

    çekirdek  ~2.000 madde   dakikalar içinde koşar, herkesin raporladığı sayı
    tam       250.000+       tasarlanan kapsamın tamamı, derin teşhis

  Çekirdek TAM kümeden tabakalı çekilir; yani çekirdek sonucu tam kümenin
  yansız bir tahmini olur, ayrı bir kıyas değil.

EKSENLER
  görev      ad çekimi (98 yuva) · fiil çekimi (84) · çatı (4) · yapım (7) ·
             ek zinciri (8 derinlik) · 8 istisna kovası
  gövde      gerçek · uydurma (wug)
  ses ortamı 320 hücrelik kapsam dizeyi
  kip        zorunlu seçim (birincil) · serbest üretim (ikincil)

HER MADDE NE TAŞIR
  altın biçim, kural ihlali çeldiricileri, hangi hücreye düştüğü, gerçek mi
  uydurma mı, hangi sözlük bayrakları var. Bu üstveri olmadan teşhis raporu
  üretilemez — puan çıkar ama "nerede düşüyor" çıkmaz.

ÜRETİLEMEYEN MADDE SESSİZCE ATILMAZ
  Çeldirici sayısı ikinin altında kalan madde (o eksende sınanamayan gövde)
  ve ettirgende güvenilmeyen tek heceli gerçek gövdeler AYRI sayılır ve
  raporlanır. Sessizce elemek, kapsamı olduğundan geniş göstermek olur.
"""
import collections
import hashlib
import json
import random

import ses
import sozluk
import kapsam
import ad_cekim
import fiil_cekim
import turetme
import zincir
import secim
import istisna
import sayi as sayi_modul

TOHUM = 20260922


class Sahte:
    """Uydurma gövde: sözlükte yok, dolayısıyla sözlüksel düzensizliği de yok."""
    __slots__ = ("govde", "tur", "bayrak", "indeks", "okunus", "kokler")

    def __init__(self, g, tur="Noun"):
        self.govde, self.tur, self.bayrak, self.indeks = g, tur, set(), 0
        self.okunus = self.kokler = None


def _kimlik(*parcalar):
    """Madde kimliği içerikten türetilir: aynı madde her üretimde aynı kimliği
    alır, sürümler arası karşılaştırma mümkün olur."""
    h = hashlib.sha1("|".join(str(p) for p in parcalar).encode("utf8"))
    return h.hexdigest()[:12]


def _madde(kova, gorev, govde, altin, celdirici, **ek):
    return dict(kimlik=_kimlik(kova, gorev, govde, altin), kova=kova, gorev=gorev,
                govde=govde, altin=altin, celdirici=celdirici,
                secenek=[altin] + list(celdirici.values()), **ek)


# --------------------------------------------------------------- üreteçler ---

# Sınanan paradigma yuvaları. Altı yalın hâl + zamir n'sini ve yardımcı ünlüyü
# açığa çıkaran bileşik yuvalar. Doksan sekiz yuvanın hepsi alınmıyor: çoğu aynı
# kuralı tekrar sınar, kıyası şişirir ve koşma maliyetini boşuna artırır.
BILESIK_YUVA = [
    ("tek", "3t", "yonelme"), ("tek", "3t", "bulunma"),
    ("tek", "3t", "belirtme"), ("tek", "3t", "ayrilma"),
    ("tek", "1t", "bulunma"), ("tek", "1t", "yonelme"),
    ("cog", "3t", "yonelme"), ("cog", "3t", "bulunma"),
    ("cog", "1c", "ayrilma"), ("cog", "1c", "bulunma"),
]


def ad_cekimi(birincil, hucre_ix, rng, wug_basi=8, tum_govde=None):
    """Ad çekimi: gerçek gövdeler + her hücre için uydurma gövdeler."""
    cik, elenen = [], collections.Counter()
    HALLER = [h for h in ad_cekim.HAL if h != "yalin"]

    for g, m in birincil.items():
        if " " in g or "-" in g or not g.isalpha():
            continue
        h = kapsam.hucre_sinifla(g)
        for hal in HALLER:
            md = secim.madde_kur(m, hal=hal)
            if md is None:
                elenen["az_celdirici"] += 1
                continue
            cik.append(_madde("ad_cekimi", hal, g, md["altin"], md["celdirici"],
                              gercek=True, hucre=list(h) if h else None,
                              bayrak=sorted(m.bayrak & sozluk.SES_BAYRAK)))
        for yuva in BILESIK_YUVA:
            md = secim.bilesik_madde_kur(m, *yuva)
            if md is None:
                elenen["az_celdirici"] += 1
                continue
            cik.append(_madde("ad_yuva", "-".join(yuva), g, md["altin"],
                              md["celdirici"], gercek=True,
                              hucre=list(h) if h else None,
                              bayrak=sorted(m.bayrak & sozluk.SES_BAYRAK)))

    for hucre in kapsam.hucreler():
        for _ in range(wug_basi):
            w = kapsam.uydurma_uret(hucre, rng, tum_govde)
            if not w:
                elenen["uydurma_uretilemedi"] += 1
                continue
            for hal in HALLER:
                md = secim.madde_kur(Sahte(w), hal=hal)
                if md is None:
                    elenen["az_celdirici"] += 1
                    continue
                cik.append(_madde("ad_cekimi", hal, w, md["altin"], md["celdirici"],
                                  gercek=False, hucre=list(hucre), bayrak=[]))
            for yuva in BILESIK_YUVA:
                md = secim.bilesik_madde_kur(Sahte(w), *yuva)
                if md is None:
                    elenen["az_celdirici"] += 1
                    continue
                cik.append(_madde("ad_yuva", "-".join(yuva), w, md["altin"],
                                  md["celdirici"], gercek=False,
                                  hucre=list(hucre), bayrak=[]))
    return cik, elenen


def _olumsuz_lemma(g, fiiller):
    """Sözlükte bazı fiiller ZATEN olumsuz biçimiyle kayıtlı (tiplememek).
    Üstüne bir olumsuzluk daha eklemek 'tiplememem' gibi çift olumsuz
    üretir ve madde anlamsız olur.

    Yalnız -memek/-mamak ile bitene bakmak yetmez: 'yamamak' da öyle biter
    ama olumlu bir fiildir. Ölçüt, -me/-ma atılınca sözlükte FİİL kalması:
      tiplememek -> tiplemek  (sözlükte var)  -> olumsuz lemma
      yamamak    -> yamak     (sözlükte fiil yok) -> olumlu
    """
    if not g.endswith(("memek", "mamak")):
        return False
    kok = g[:-5] + ("mek" if g.endswith("memek") else "mak")
    return kok in fiiller


def fiil_cekimi(fiiller, rng, n_fiil=1200):
    """Fiil çekimi. Çeldirici: yanlış zaman eki ve yanlış kişi takımı."""
    cik, elenen = [], collections.Counter()
    sec = [m for m in fiiller.values() if not _olumsuz_lemma(m.govde, fiiller)]
    rng.shuffle(sec)
    for m in sec[:n_fiil]:
        if " " in m.govde or not m.govde.replace("â", "a").isalpha():
            continue
        for z in fiil_cekim.ZAMAN:
            for olumsuz in (False, True):
                altin = fiil_cekim.cekim(m, z, "1t", olumsuz)
                cel = {}
                # yanlış kişi takımı: 1. takım yerine 2. takım
                ters = fiil_cekim.ZAMAN[z][1]
                ke = (fiil_cekim.KISI2 if ters == 1 else fiil_cekim.KISI1)["1t"]
                govde_ek = fiil_cekim.cekim(m, z, "3t", olumsuz)
                y = govde_ek + ses.coz(ke, govde_ek)
                if y != altin:
                    cel["kisi_takimi"] = y
                # geniş zamanda ek seçimi hatası
                if z == "genis" and not olumsuz:
                    gv = fiil_cekim.govde(m)
                    dogru = fiil_cekim.genis_ek(m, gv)
                    yanlis = "Ir" if dogru == "Ar" else "Ar"
                    if gv and gv[-1] not in ses.UNLULER:
                        b = gv + ses.coz(yanlis, gv)
                        b += ses.coz(fiil_cekim.KISI2["1t"], b)
                        if b != altin:
                            cel["genis_zaman_eki"] = b
                # olumsuz geniş zamanda -mAz kullanma hatası
                if z == "genis" and olumsuz:
                    gv = fiil_cekim.govde(m)
                    b = gv + ses.coz("mAz", gv)
                    b += ses.coz(fiil_cekim.KISI2["1t"], b)
                    if b != altin:
                        cel["olumsuz_genis"] = b
                if len(cel) < 2:
                    elenen["az_celdirici"] += 1
                    continue
                cik.append(_madde("fiil_cekimi", ("olumsuz_" if olumsuz else "") + z,
                                  m.govde, altin, cel, gercek=True,
                                  bayrak=sorted(m.bayrak & sozluk.SES_BAYRAK)))
    return cik, elenen


def zincir_maddeleri(birincil, rng, hucre_ix, tum_govde, n_gercek=600, n_wug=600):
    """Ek zinciri derinliği 1..8. Çeldirici: bir basamak eksik / fazla."""
    cik, elenen = [], collections.Counter()
    gercekler = [g for g in birincil if g.isalpha() and len(g) > 2]
    rng.shuffle(gercekler)
    adaylar = [(g, True) for g in gercekler[:n_gercek]]
    hs = kapsam.hucreler()
    for _ in range(n_wug):
        w = kapsam.uydurma_uret(rng.choice(hs), rng, tum_govde)
        if w:
            adaylar.append((w, False))

    for g, gercek in adaylar:
        basamak = zincir.basamaklar(g)
        for d, ad, altin in basamak:
            cel = {}
            if d > 1:
                cel["basamak_eksik"] = basamak[d - 2][2]
            if d < zincir.EN_DERIN:
                cel["basamak_fazla"] = basamak[d][2]
            # sıra bozuk: son iki eki yer değiştir
            if d >= 2:
                b = basamak[d - 2][2]
                s1, s2 = zincir.MERDIVEN[d - 2][0], zincir.MERDIVEN[d - 1][0]
                onceki = basamak[d - 3][2] if d >= 3 else g
                ters = onceki + ses.coz(s2, onceki)
                ters = ters + ses.coz(s1, ters)
                if ters != altin and ters not in cel.values():
                    cel["sira_bozuk"] = ters
            if len(cel) < 2:
                elenen["az_celdirici"] += 1
                continue
            h = kapsam.hucre_sinifla(g)
            cik.append(_madde("ek_zinciri", "derinlik_%d" % d, g, altin, cel,
                              gercek=gercek, derinlik=d,
                              hucre=list(h) if h else None, bayrak=[]))
    return cik, elenen


def turetme_maddeleri(birincil, fiiller, rng, n=900):
    """Çatı ve yapım ekleri."""
    cik, elenen = [], collections.Counter()
    adlar = [m for g, m in birincil.items() if g.isalpha() and len(g) > 2]
    rng.shuffle(adlar)
    for m in adlar[:n]:
        for tur in turetme.YAPIM:
            altin = turetme.yapim(m.govde, tur)
            cel = {}
            # uyum bozuk
            y = m.govde + ses.coz(turetme.YAPIM[tur], m.govde, ters=True)
            if y != altin:
                cel["uyum"] = y
            # yumuşama olmaması gerekirken yumuşatma
            if m.govde[-1] in ses.YUMUSAMA:
                gy = ses.yumusat(m.govde)
                y2 = gy + ses.coz(turetme.YAPIM[tur], gy)
                if y2 != altin:
                    cel["yumusama_fazla"] = y2
            if len(cel) < 2:
                elenen["az_celdirici"] += 1
                continue
            cik.append(_madde("yapim_eki", tur, m.govde, altin, cel, gercek=True,
                              bayrak=sorted(m.bayrak & sozluk.SES_BAYRAK)))

    fl = list(fiiller.values())
    rng.shuffle(fl)
    for m in fl[:n]:
        gv = fiil_cekim.govde(m)
        if not gv.isalpha() or len(gv) < 2:
            continue
        for tur in ("edilgen", "donuslu", "istes", "ettirgen"):
            altin = turetme.cati(gv, tur, gozden_gecirmeye_izin=False)
            if altin is None:
                elenen["ettirgen_guvenilmez"] += 1
                continue
            cel = {}
            y = gv + ses.coz({"edilgen": turetme.edilgen_ek(gv),
                              "donuslu": "(I)n", "istes": "(I)ş",
                              "ettirgen": "DIr"}[tur], gv, ters=True)
            if y != altin:
                cel["uyum"] = y
            if tur == "edilgen":
                # yanlış edilgen eki: -l yerine -n ya da tersi
                alt = "(I)n" if turetme.edilgen_ek(gv) != "(I)n" else "(I)l"
                y2 = gv + ses.coz(alt, gv)
                if y2 != altin:
                    cel["edilgen_eki"] = y2
            if tur == "ettirgen":
                y2 = gv + ses.coz("t", gv)
                if y2 != altin:
                    cel["ettirgen_eki"] = y2
            if len(cel) < 2:
                elenen["az_celdirici"] += 1
                continue
            cik.append(_madde("cati", tur, gv, altin, cel, gercek=True, bayrak=[]))
    return cik, elenen


def istisna_maddeleri(maddeler, kisaltmalar, yer_adlari, rng, n_yer=1200, n_sayi=400):
    """Sekiz istisna kovası. Çeldirici: o kovanın kuralını UYGULAMAMAK."""
    cik, elenen = [], collections.Counter()
    sayilar = sorted({rng.randint(1, 9999) for _ in range(n_sayi)}) + \
              [1, 2, 3, 6, 7, 10, 40, 100, 1000, 2026, 1453]
    yer = [a for a in yer_adlari if a and a[0].isupper() and a.isalpha()]
    rng.shuffle(yer)

    K = istisna.kovalar(maddeler, kisaltmalar=kisaltmalar,
                        yer_adlari=yer[:n_yer], sayilar=sayilar)

    for kova, liste in K.items():
        for gosterim, altin, bilgi in liste:
            hal = bilgi.get("hal", "belirtme")
            cel = {}
            if kova in ("unlu_dusmesi", "ikizlesme", "uyum_kirici", "birlesik_isim",
                        "kaynastirma_istisna"):
                # kuralı uygulamayan biçim: bayraksız sahte gövde gibi çek
                y = ad_cekim.cekim(Sahte(gosterim), hal=hal)
                if y != altin:
                    cel["kural_uygulanmadi"] = y
                y2 = ad_cekim.cekim(Sahte(gosterim), hal=hal)
                y2 = gosterim + ses.coz(ad_cekim.HAL[hal], gosterim, ters=True)
                if y2 != altin and y2 not in cel.values():
                    cel["uyum"] = y2
            elif kova == "ozel_ad":
                y = gosterim + ses.coz(ad_cekim.HAL[hal], gosterim)      # kesmesiz
                if y != altin:
                    cel["kesme_yok"] = y
                gy = ses.yumusat(gosterim)
                if gy != gosterim:
                    y2 = gy + "'" + ses.coz(ad_cekim.HAL[hal], gy)
                    if y2 != altin:
                        cel["yumusatildi"] = y2
                y3 = gosterim + "'" + ses.coz(ad_cekim.HAL[hal], gosterim, ters=True)
                if y3 != altin and y3 not in cel.values():
                    cel["uyum"] = y3
            elif kova in ("kisaltma", "sayi"):
                # yazılışa göre uyum (okunuşa değil) — asıl sınanan hata
                y = gosterim + "'" + ses.coz(ad_cekim.HAL[hal], gosterim.lower())
                if y != altin:
                    cel["yazilisa_gore"] = y
                o = bilgi.get("okunus", "")
                y2 = gosterim + "'" + ses.coz(ad_cekim.HAL[hal], o, ters=True)
                if y2 != altin and y2 not in cel.values():
                    cel["uyum"] = y2
            if len(cel) < 2:
                elenen[kova + "_az_celdirici"] += 1
                continue
            cik.append(_madde("istisna_" + kova, hal, gosterim, altin, cel,
                              gercek=True, istisna_kovasi=kova,
                              okunus=bilgi.get("okunus")))
    return cik, elenen


# ------------------------------------------------------------------- kurma ---

def kur():
    rng = random.Random(TOHUM)
    ham = sozluk.yukle(("master", "non_tdk"))
    adlar = sozluk.indeksle([m for m in ham if m.tur in ("Noun", "Adj")])
    fiiller = sozluk.indeksle([m for m in ham if m.tur == "Verb"])
    tum_govde = {m.govde for m in ham}
    belirsiz = sozluk.belirsizler([m for m in ham if m.tur in ("Noun", "Adj")])
    # çekimi ayrışan eş yazılışlılar kıyasa GİRMEZ: altın cevap tek olmaz
    birincil = {g: m for g, m in adlar.items() if g not in belirsiz}

    kisaltma_m = sozluk.yukle(("kisaltma",))
    kisaltmalar = [(m.govde, m.okunus) for m in kisaltma_m if m.okunus]
    yer = [m.govde for m in sozluk.yukle(("yer",))]

    hucre_ix = None
    tum, elenen = [], collections.Counter()
    for ad, fn in [
        ("ad_cekimi", lambda: ad_cekimi(birincil, hucre_ix, rng, tum_govde=tum_govde)),
        ("fiil_cekimi", lambda: fiil_cekimi(fiiller, rng)),
        ("ek_zinciri", lambda: zincir_maddeleri(birincil, rng, hucre_ix, tum_govde)),
        ("turetme", lambda: turetme_maddeleri(birincil, fiiller, rng)),
        ("istisna", lambda: istisna_maddeleri(ham, kisaltmalar, yer, rng)),
    ]:
        m, e = fn()
        print("  %-14s %7d madde" % (ad, len(m)), flush=True)
        tum += m
        elenen.update(e)

    # kimlik çakışması olmasın (aynı madde iki yoldan üretilmiş olabilir)
    gorulen, benzersiz = set(), []
    for m in tum:
        if m["kimlik"] in gorulen:
            elenen["yinelenen"] += 1
            continue
        gorulen.add(m["kimlik"])
        benzersiz.append(m)
    return benzersiz, elenen, len(belirsiz)


def cekirdek_sec(maddeler, hedef=2000, taban=90, tohum=TOHUM):
    """Çekirdek katman: KOVA DENGELİ, orantılı değil.

    İlk sürüm orantılı çekiyordu ve çekirdeğin %96'sı ad çekimi oluyordu;
    istisna kovalarında bir-beş madde kalıyordu. Kova başına teşhis
    yapılamıyordu — oysa kıyasın bütün vaadi o.

    Şimdi: her kovaya önce TABAN pay (varsayılan 90 madde) verilir, kalan
    bütçe orantılı dağıtılır. Böylece en küçük kova bile ölçülebilir bir
    tahmin verir (90 maddede %95 aralık kabaca ±10 puan), en büyük kova da
    baskın kalmaz. Kova içinde gerçek/uydurma yarı yarıya.

    DİKKAT — bu çekirdeği tam kümenin yansız tahmini OLMAKTAN çıkarır.
    Bilerek: çekirdek TEŞHİS içindir, manşet sayı için değil. Rapor
    çekirdekte kova ortalamasını (makro) verir; tam kümede mikro ortalama
    anlamlıdır. İkisi karşılaştırılmaz ve kartta böyle yazar.
    """
    rng = random.Random(tohum)
    kova_ix = collections.defaultdict(lambda: {True: [], False: []})
    for m in maddeler:
        kova_ix[m["kova"]][m["gercek"]].append(m)

    n_kova = len(kova_ix)
    taban = min(taban, hedef // max(n_kova, 1))
    kalan = max(0, hedef - taban * n_kova)
    toplam = len(maddeler)

    cik = []
    for kova, ikili in sorted(kova_ix.items()):
        n = len(ikili[True]) + len(ikili[False])
        pay = taban + round(kalan * n / toplam)
        pay = min(pay, n)
        yari = pay // 2
        for bayrak, istek in ((True, pay - yari), (False, yari)):
            L = list(ikili[bayrak])
            rng.shuffle(L)
            alinan = L[:istek]
            cik += alinan
            eksik = istek - len(alinan)
            if eksik > 0:
                O = [x for x in ikili[not bayrak] if x not in cik]
                rng.shuffle(O)
                cik += O[:eksik]
    rng.shuffle(cik)
    return cik


if __name__ == "__main__":
    print("TurkMorfBench v3 üretiliyor…", flush=True)
    maddeler, elenen, n_belirsiz = kur()
    cekirdek = cekirdek_sec(maddeler)

    kova = collections.Counter(m["kova"] for m in maddeler)
    print("\nTAM KÜME: %d madde" % len(maddeler))
    for k, n in kova.most_common():
        print("  %-26s %7d" % (k, n))
    print("\nÇEKİRDEK: %d madde" % len(cekirdek))
    print("\nELENEN:")
    for k, n in elenen.most_common():
        print("  %-28s %7d" % (k, n))
    print("  %-28s %7d" % ("belirsiz eş yazılışlı gövde", n_belirsiz))

    for ad, veri in (("turkmorfbench_v3_tam.json", maddeler),
                     ("turkmorfbench_v3_cekirdek.json", cekirdek)):
        json.dump({"surum": "3.0.0", "tohum": TOHUM, "madde": len(veri),
                   "maddeler": veri}, open(ad, "w"), ensure_ascii=False)
        print("yazıldı: %s" % ad)
