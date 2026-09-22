"""Ad çekimi — çokluk, iyelik, hâl. Türkçe ad paradigmasının tamamı.

YUVA SAYISI
  2 çokluk × 7 iyelik × 7 hâl = 98 biçim. UniMorph Türkçe 186 yuva kullanıyor
  ama yalnız 3.017 sözlükbirimde; bizde 32.346 sözlükbirim var.

EK SIRASI KATIDIR
  gövde + çokluk + iyelik + hâl.  ev-ler-imiz-de doğru, *ev-de-ler-imiz değil.
  Sıranın kendisi ayrıca sınanacak bir görev (bkz. tasarım belgesi, madde E).

DÜZENSİZLİKLER YALNIZ GÖVDEYE DOĞRUDAN EKLENEN EKTE İŞLER
  Bu ince ama kritik: `kitap` yumuşar (kitab-ı) ama çokluk araya girince
  yumuşamaz (kitap-lar-ı), çünkü artık gövdenin ardından ünlü gelmiyor.
  Aynısı ünlü düşmesi, ikizleşme ve uyum kırıcılık için de geçerli:
  `kalp-ler-de` — ince ek yalnız ilk ekte, sonrakiler ona uyuyor.

ZAMİR n'Sİ
  3. kişi iyeliğinden (-(s)I, -lArI) ve birleşik isim 3. tekilinden sonra hâl
  eki -n- ile bağlanır: kitab-ı-n-a, kitap-lar-ı-n-a, buzdolab-ı-n-a.
  Bu kural atlanırsa 'buzdolabına' yerine 'buzdolabıya' üretilir.
"""
import ses

COKLUK = {"tek": None, "cog": "lAr"}

IYELIK = {
    "yok": None,
    "1t": "(I)m",     # ev-im    / araba-m
    "2t": "(I)n",     # ev-in    / araba-n
    "3t": "(s)I",     # ev-i     / araba-sı
    "1c": "(I)mIz",   # ev-imiz  / araba-mız
    "2c": "(I)nIz",   # ev-iniz  / araba-nız
    "3c": "lArI",     # ev-leri  / araba-ları
}

HAL = {
    "yalin": None,
    "belirtme": "(y)I",     # ev-i      / araba-yı
    "yonelme": "(y)A",      # ev-e      / araba-ya
    "bulunma": "DA",        # ev-de     / araba-da
    "ayrilma": "DAn",       # ev-den    / araba-dan
    "tamlayan": "(n)In",    # ev-in     / araba-nın
    "vasita": "(y)lA",      # ev-le     / araba-yla
}

# 3. kişi iyeliği — sonrasında hâl eki zamir n'si ile bağlanır
UCUNCU = {"3t", "3c"}

# Kuralla türetilemeyen, sözlükte de bayrakla tam karşılanmayan birkaç gövde.
# Sayıları az ve hepsi belgeli; gizli bir "düzeltme tablosu" değil, açık liste.
OZEL_GOVDE = {
    "su": {"3t": "suyu", "tamlayan": "suyun", "belirtme": "suyu", "yonelme": "suya"},
    "ne": {"3t": "neyi", "tamlayan": "neyin", "belirtme": "neyi", "yonelme": "neye"},
}


def _govde_hazirla(madde, ek_sablon):
    """Gövdeyi ilk ekin ses ortamına göre hazırlar.

    Döndürür: (hazır gövde, ters_uyum).
    Yalnız ünlüyle başlayan ek gövdeyi değiştirir; ünsüzle başlayan ek
    (-lAr, -DA, -DAn) gövdeye dokunmaz."""
    gv = madde.govde
    ters = "InverseHarmony" in madde.bayrak
    if ek_sablon is None:
        return gv, ters
    if not ses.unluyle_baslar(ek_sablon, gv):
        return gv, ters

    # Üç değişim BİRLİKTE olabilir; eskiden if/elif zinciriyle birbirini
    # dışlıyorlardı ve bütün bir sınıf yanlış çıkıyordu:
    #     nakit -> naktı  (doğrusu nakdi: ünlü düşer VE t yumuşar)
    #     ret   -> retti  (doğrusu reddi: t yumuşar VE ikizleşir)
    # TDK ile karşılaştırma yapılınca 24 gövdenin hiçbir bayrak kümesiyle
    # üretilemediği görüldü; hepsi bu iki birleşimdendi.
    #
    # Sıra: yumuşama -> ünlü düşmesi -> ikizleşme.
    #   nakit -> nakid -> nakd           (önce yumuşar, sonra ünlü düşer)
    #   ret   -> red   -> redd           (yumuşar, sonra ikizleşir)
    #   hak   -> hak   -> hakk           (yumuşamaz: bayrağı yok, tek heceli)
    #
    # Yumuşamanın ÖNCE gelmesi şart. `ses.yumusat` ünsüzden sonra gelen
    # p/ç/t/k'yi yumuşatmaz — `üst -> üstü`, `dost -> dostu` için doğru olan
    # kural budur. Ama `nakit`teki küme ünlü DÜŞTÜĞÜ İÇİN oluşur; düşmeden
    # sonra yumuşatmaya kalkarsak o kural yanlışlıkla devreye girer ve
    # `naktı` çıkar. Sözlük biçiminde 't' ünlüler arasındadır, orada yumuşar.
    if _yumusar_mi(madde, gv):
        gv = ses.yumusat(gv)
    if "LastVowelDrop" in madde.bayrak:
        gv = ses.son_unlu_dusur(gv)
    if "Doubling" in madde.bayrak:
        gv = ses.ikizlestir(gv)
    return gv, ters


def _yumusar_mi(madde, gv=None):
    """Zemberek sözleşmesi — asimetrik, bire bir uyulmalı.

    Çok heceli p/ç/t/k gövdeler VARSAYILAN yumuşar; yumuşamayanlar NoVoicing.
    Tek heceli gövdeler VARSAYILAN yumuşamaz; yumuşayanlar Voicing.
    Ters çevrilirse 'devleti' -> 'devledi', 'kabı' -> 'kapı' olur.

    `gv` verilirse son sesi ONUN üzerinden bakılır (ünlü düşmesinden sonraki
    biçim); hece sayısı ise her zaman SÖZLÜK biçiminden sayılır — düşmüş
    biçim tek heceli görünüp varsayılanı ters çevirmesin diye."""
    gv = madde.govde if gv is None else gv
    if not gv or gv[-1] not in ses.YUMUSAMA:
        return False
    if "NoVoicing" in madde.bayrak:
        return False
    if "Voicing" in madde.bayrak:
        return True
    if ses.nk_ile_biter(gv):
        return True            # renk->rengi: ses kuralı, bayraktan bağımsız
    return ses.hece_sayisi(madde.govde) > 1


def cekim(madde, cokluk="tek", iyelik="yok", hal="yalin"):
    """Tek bir paradigma yuvası üretir. Sıra: gövde + çokluk + iyelik + hâl."""
    ozel = OZEL_GOVDE.get(madde.govde)
    if ozel and cokluk == "tek":
        if iyelik == "3t" and hal == "yalin" and "3t" in ozel:
            return ozel["3t"]
        if iyelik == "yok" and hal in ozel:
            return ozel[hal]

    birlesik = "CompoundP3sg" in madde.bayrak
    if birlesik:
        # buzdolabı zaten 3. tekil iyelikli; üstüne iyelik eklenmez,
        # hâl eki doğrudan zamir n'si ile bağlanır.
        iyelik = "yok"

    ekler = [(COKLUK[cokluk], "cokluk"), (IYELIK[iyelik], "iyelik"), (HAL[hal], "hal")]
    ekler = [(s, t) for s, t in ekler if s]

    if not ekler:
        return madde.govde

    ilk_sablon = ekler[0][0]
    bicim, ters = _govde_hazirla(madde, ilk_sablon)

    ucuncu_gordu = birlesik
    ilk = True
    for sablon, tur in ekler:
        if tur == "hal" and ucuncu_gordu:
            # zamir n'si: kitab-ı-n-a, buzdolab-ı-n-a
            if sablon.startswith("("):
                sablon = sablon[sablon.index(")") + 1:]
            sablon = "n" + sablon
        bicim += ses.coz(sablon, bicim, ters if ilk else False)
        if tur == "iyelik" and iyelik in UCUNCU:
            ucuncu_gordu = True
        ilk = False
    return bicim


def paradigma(madde):
    """98 yuvanın hepsi. Anahtar: (cokluk, iyelik, hal)."""
    cik = {}
    for c in COKLUK:
        for i in IYELIK:
            for h in HAL:
                cik[(c, i, h)] = cekim(madde, c, i, h)
    return cik
