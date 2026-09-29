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
import os
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
    """Tek madde. ŞIKLAR KARIŞTIRILIR.

    Şık listesi `[altın] + çeldiriciler` olarak kuruluyordu; yani altın her
    maddede birinci şıktı. Zorunlu seçim kipinde şıklar tek tek puanlandığı
    için sıra önemsizdir ve bu gözden kaçmıştı — ama şık listesini A/B/C diye
    harflendiren herkes, hep A diyerek %100 alırdı. Kıyası kullanan
    kişinin protokolüne güvenmek yerine sırayı biz bozuyoruz.

    Karıştırma KİMLİĞE BAĞLI: aynı madde her üretimde aynı sırayı alır,
    sürümler arası karşılaştırma bozulmaz. `altin_sira` altının kaçıncı
    şık olduğunu söyler; altın dizgesi `altin` alanında zaten duruyor.
    """
    kimlik = _kimlik(kova, gorev, govde, altin)
    secenek = [altin] + list(celdirici.values())
    karistir = random.Random(int(kimlik, 16))
    karistir.shuffle(secenek)
    return dict(kimlik=kimlik, kova=kova, gorev=gorev,
                govde=govde, altin=altin, celdirici=celdirici,
                secenek=secenek, altin_sira=secenek.index(altin), **ek)


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

    # NEDEN DEĞİŞTİ (3.5.0)
    #   Önceki çeldiriciler "bir basamak eksik" ve "bir basamak fazla" idi —
    #   ikisi de DİLBİLGİSEL biçimler. İstem hedef derinliği söylemediği için
    #   model en olası GEÇERLİ biçimi seçiyor ve bu yanlış sayılıyordu. Beş
    #   farklı model derinlik 2/3/5/7'de tam %0, 6/8'de ~%100 aldı: model
    #   özelliği değil, kova tasarımının artefaktı. Çeldirici kural İHLALİ
    #   olmalı — diğer kovalardaki gibi. Son ekin uyumu bozulur, kaynaştırma
    #   yanlış seçilir, sıra bozulur. Hepsi aynı derinlikte, hepsi geçersiz.
    for g, gercek in adaylar:
        basamak = zincir.basamaklar(g)
        for d, ad, altin in basamak:
            cel = {}
            onceki_bicim = basamak[d - 2][2] if d >= 2 else g
            son_ek = altin[len(onceki_bicim):]
            if son_ek:
                # uyum ihlali: son ekteki ünlüleri karşı sınıfa çevir
                bozuk = "".join(_UNLU_ESI.get(c, c) for c in son_ek)
                if bozuk != son_ek:
                    cel["uyum"] = onceki_bicim + bozuk
                # kaynaştırma ihlali: sınırda y/s/n varsa düşür, yoksa 'y' sok
                if son_ek[0] in "ysn" and len(son_ek) > 1:
                    kay = onceki_bicim + son_ek[1:]
                else:
                    kay = onceki_bicim + "y" + son_ek
                if kay != altin and kay not in cel.values():
                    cel["kaynastirma"] = kay
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


# ters uyum eşleri: ek ünlüsünü ince<->kalın çevirmek
_UNLU_ESI = {"i": "ı", "ı": "i", "ü": "u", "u": "ü", "e": "a", "a": "e",
             "ö": "o", "o": "ö"}
# yumuşama eşleri: gövde son ünsüzünü ötümlü<->ötümsüz çevirmek
_UNSUZ_ESI = {"b": "p", "p": "b", "c": "ç", "ç": "c", "d": "t", "t": "d",
              "ğ": "k", "k": "ğ", "g": "k"}


def celdirici_altindan(govde, altin, hal):
    """Altın biçimi TEK BİR kuralla bozan çeldiriciler.

    Her biri adını bozduğu kuraldan alır; model hangisini seçtiyse hangi
    kuralı bilmediği doğrudan okunur.
        uyum        ek ünlüsü ince<->kalın çevrilir   kıraati -> kıraatı
        yumusama    gövde son ünsüzü çevrilir          kıraati -> kıraadi
        kural_yok   gövde hiç değişmeden düz çekilir   aczi    -> acizi
    """
    cik = []

    # uyum: son ünlüyü çevir
    for i in range(len(altin) - 1, -1, -1):
        if altin[i] in _UNLU_ESI:
            cik.append(("uyum", altin[:i] + _UNLU_ESI[altin[i]] + altin[i + 1:]))
            break

    # yumuşama: YALNIZ ek sınırındaki ünsüz — ekten hemen önceki harf.
    # Serbest arama gövdenin içine dalıyordu (burnu -> purnu, baştaki b'yi
    # çevirmişti). İkizleşmede iki harf birden çevrilir, yoksa `redti` gibi
    # yarım bir biçim çıkar; doğru çeldirici `retti`dir.
    if len(altin) >= 2 and altin[-2] in _UNSUZ_ESI:
        e = _UNSUZ_ESI[altin[-2]]
        if len(altin) >= 3 and altin[-3] == altin[-2]:
            cik.append(("yumusama", altin[:-3] + e + e + altin[-1]))
        else:
            cik.append(("yumusama", altin[:-2] + e + altin[-1]))

    # kural yok: gövde olduğu gibi kalır, ek uyumla eklenir
    duz = govde + ses.coz(ad_cekim.HAL[hal], govde)
    cik.append(("kural_yok", duz))
    return cik


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
                # Çeldiriciler ALTINDAN türetilir, gövdeden değil.
                #
                # Eskiden "ham gövdeye ters uyum uygula" biçimi çeldirici
                # sayılıyordu. Altın TDK'ye geçince o biçim maddelerin
                # çoğunda altının KENDİSİ oldu (kıraat -> kıraati), çeldirici
                # sayısı bire düştü ve kova neredeyse tümüyle elendi.
                # Altını tek bir kuralla bozmak hem sağlam hem teşhis edici:
                # hangi çeldirici seçildiyse hangi kural bilinmiyor bellidir.
                for ad, y in celdirici_altindan(gosterim, altin, hal):
                    if y != altin and y not in cel.values():
                        cel[ad] = y
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


def tdk_bayrak_uygula(maddeler):
    """TDK ile doğrulanmış bayrakları sözlük maddelerinin üzerine yazar.

    NEDEN BÜTÜN KOVALARA
      TDK düzeltmesi önce yalnız istisna kovalarına uygulanmıştı ve aynı
      gövde iki farklı altın veriyordu: `kıraat` istisna kovasında
      `kıraati`, ad çekimi kovasında `kıraadi`. Bir kıyasta aynı gövdenin
      iki altını olması onu kullanılamaz yapar.

      Bayrak sözlüksel ilkeldir; kaynakta düzeltilince motor her kovada,
      her hâlde, her ek yığınında doğru biçimi üretir. Ölçtük: düzeltme
      öncesi 105 gövde genel kovalarda TDK ile çelişiyordu ve bu 1.451
      maddeyi etkiliyordu.

      Yalnız TDK'nin AÇIKÇA biçim verdiği gövdeler düzeltilir. TDK'nin
      sustuğu gövdede Zemberek bayrağı korunur — sözlüğün ek notasyonu
      yazmaması "düzenli" demek değil, "öngörülebilir" demektir ve
      öngörülen şey zaten varsayılan kuraldır.
    """
    y = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tdk_bayrak.json")
    if not os.path.exists(y):
        return 0
    with open(y, encoding="utf8") as f:
        tablo = json.load(f)
    n = 0
    for m in maddeler:
        b = tablo.get(m.govde)
        if b is not None and m.tur in ("Noun", "Adj"):
            yeni = set(b) | (m.bayrak - sozluk.SES_BAYRAK)
            if yeni != m.bayrak:
                m.bayrak = yeni
                n += 1
    return n


# ------------------------------------------------------------------- kurma ---

def kur():
    rng = random.Random(TOHUM)
    ham = sozluk.yukle(("master", "non_tdk"))
    tdk_bayrak_uygula(ham)
    adlar = sozluk.indeksle([m for m in ham if m.tur in ("Noun", "Adj")])
    fiiller = sozluk.indeksle([m for m in ham if m.tur == "Verb"])
    # UYDURMA DENETİMİ BÜTÜN SÖZLÜKLERE BAKAR.
    # Eskiden yalnız master+non_tdk'ya bakılıyordu; eskimiş, gayriresmî, özel
    # ad, yer adı ve kişi adı dosyalarındaki gövdeler "uydurma" sayılıp
    # kıyasa giriyordu. Yirmi gövde bu yolla kaçmıştı (ba, civ, kop, liç…) ve
    # o maddelerde ezber kontrolü hiç çalışmıyordu — wug testinin tek işi
    # gövdenin külliyatta GEÇMEMESİNİ garanti etmek.
    tum_govde = {m.govde for m in ham}
    for ad in ("eskimis", "gayriresmi", "ozel", "ozel_kulliyat", "yer", "kisi", "kisaltma"):
        try:
            tum_govde |= {m.govde.lower() for m in sozluk.yukle((ad,))}
        except Exception:
            pass
    tum_govde |= {g.lower() for g in tum_govde}
    belirsiz = sozluk.belirsizler([m for m in ham if m.tur in ("Noun", "Adj")])
    # çekimi ayrışan eş yazılışlılar kıyasa GİRMEZ: altın cevap tek olmaz
    # TDK'nin verdiği biçim hiçbir bayrak kümesiyle üretilemiyorsa gövde
    # kuralla açıklanamıyor demektir; kural motoruna zorla söyletmek
    # ölçtüğümüz şeyi bozar. ÇIKAR. (raptı, veçhi, hüsnühâli…)
    _d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tdk_disarida.json")
    tdk_dis = set(json.load(open(_d, encoding="utf8"))) if os.path.exists(_d) else set()
    birincil = {g: m for g, m in adlar.items() if g not in belirsiz and g not in tdk_dis}

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
            # KARARLI SEÇİM (3.5.0): rng.shuffle eklemeye duyarlıydı — tam
            # kümeye 1.193 madde girince çekirdek BÜTÜN kovalarda kaydı
            # (1.856'nın yalnız 1.214'ü ortak kaldı). Sıra artık her maddenin
            # kendi kimliğinden türeyen özetle belirlenir: madde başına sabit,
            # başka ne eklenirse eklensin. Yeni madde ancak özeti üst bölgeye
            # düşerse eskisini iter; kayma eklemeyle orantılı, toptan değil.
            L = sorted(ikili[bayrak],
                       key=lambda m: hashlib.sha256(
                           ("%s|%s" % (tohum, m["kimlik"])).encode()).hexdigest())
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
