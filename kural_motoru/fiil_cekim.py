"""Fiil çekimi — Türkçe morfolojisinin asıl derinliği burada.

NEDEN AD ÇEKİMİNDEN ÖNEMLİ
  Rakip çalışmada (arXiv 2410.12656) ayrı bir fiil ekseni yok. Oysa Türkçede
  kuralın sözlüksel istisnayla çarpıştığı yer fiildir ve bir modelin kuralı mı
  ezberi mi kullandığını en iyi orası ayırır.

GENİŞ ZAMAN — kıyasın en değerli maddesi
  Kural:
    ünlüyle biten gövde            -> -r        (oku-r, bekle-r, yürü-r)
    çok heceli, ünsüzle biten      -> -Ir       (otur-ur, çalış-ır, öğren-ir)
    tek heceli, ünsüzle biten      -> -Ar       (bak-ar, yaz-ar, git-er->gider)
  İstisna: on üç tek heceli fiil kurala rağmen -Ir alır —
    al-ır · bil-ir · bul-ur · dur-ur · gel-ir · gör-ür · kal-ır · ol-ur ·
    öl-ür · san-ır · var-ır · ver-ir · vur-ur
  Bu on üçü sözlükte A:Aorist_I ile işaretli; doğrulandı, birebir tutuyor.
  Ters yönde A:Aorist_A, kurala göre -Ir alması gereken çok heceli fiilleri
  -Ar'a çeker (et-mek -> eder, addet-mek -> addeder). 133 madde.

OLUMSUZ GENİŞ ZAMAN — ikinci istisna katmanı
  Olumsuzu -mA + -Ir değil, apayrı bir biçim: -mAz.
    git-mez · gel-mez · bak-maz
  Üstelik 1. kişilerde -mAz de kullanılmaz:
    1 tekil  -mAm    (gitmem, gelmem)     -mAzIm DEĞİL
    1 çoğul  -mAyIz  (gitmeyiz, gelmeyiz) -mAzIz DEĞİL
  Yani tek bir zamanda üç ayrı düzensizlik var. Kuralı bilmeyen model
  "gitmezim" üretir; ezberleyen model doğru üretir ama uydurma gövdede düşer.

ŞİMDİKİ ZAMAN — ünlü daralması
  -Iyor önünde gövde sonundaki GENİŞ ünlü (a/e) daralır:
    bekle -> bekliyor · anla -> anlıyor · söyle -> söylüyor
  Dar ünlü (ı/i/u/ü) olduğu gibi kalır: oku -> okuyor · yürü -> yürüyor
  Olumsuzluk eki de aynı daralmaya uğrar: -mA + -Iyor -> gitmiyor

KİŞİ EKLERİ İKİ AYRI TAKIM
  1. takım (-DI, -sA sonrası): -m · -n · ∅ · -k · -nIz · -lAr
  2. takım (-mIş, -Iyor, -AcAk, -Ir, -mAlI sonrası): -(y)Im · -sIn · ∅ ·
     -(y)Iz · -sInIz · -lAr
  Yanlış takım seçilirse "gittim" yerine "gittiyim" çıkar.
"""
import ses

KISI1 = {"1t": "m", "2t": "n", "3t": "", "1c": "k", "2c": "nIz", "3c": "lAr"}
KISI2 = {"1t": "(y)Im", "2t": "sIn", "3t": "", "1c": "(y)Iz", "2c": "sInIz", "3c": "lAr"}

# zaman/kip -> (olumlu ek, kişi takımı)
ZAMAN = {
    "belirli_gecmis": ("DI",     1),   # gittim
    "belirsiz_gecmis": ("mIş",   2),   # gitmişim
    "simdiki":        ("(I)yor", 2),   # gidiyorum
    "gelecek":        ("(y)AcAk", 2),  # gideceğim
    "genis":          (None,     2),   # gider / gelir  — kural aşağıda
    "gereklilik":     ("mAlI",   2),   # gitmeliyim
    "sart":           ("sA",     1),   # gitsem
}

GENIS_UNLU = set("ae")


def govde(madde):
    """Sözlük maddesi -mAk/-mEk ile biter; gövde onu atınca kalan."""
    g = madde.govde
    return g[:-3] if g.endswith(("mak", "mek")) else g


def _yumusar(madde, gv):
    """Fiillerde yumuşama yalnız sözlük bayrağına bakar; adlardaki
    'çok heceli varsayılan yumuşar' kuralı fiillerde geçerli değil.
    git-mek -> gider (A:Voicing) ama bak-mak -> bakar (bayrak yok)."""
    return "Voicing" in madde.bayrak and bool(gv) and gv[-1] in ses.YUMUSAMA


def _ekle(bicim, sablon, yumusama=False):
    """Şablonu biçime ekler; istenirse ünlü önünde son ünsüzü yumuşatır.

    Yumuşama fiil zincirinde tek yerde şart: -AcAk + ünlüyle başlayan kişi eki.
    gidecek + im -> gideceğim. Atlanırsa 'gideceğim' yerine 'gidecekim' çıkar."""
    if yumusama and ses.unluyle_baslar(sablon, bicim):
        bicim = ses.yumusat(bicim)
    return bicim + ses.coz(sablon, bicim)


def _darlastir(gv):
    """-Iyor önünde gövde sonundaki geniş ünlüyü daraltır.
    bekle -> bekli · anla -> anlı · söyle -> söylü · başla -> başlı"""
    if not gv or gv[-1] not in GENIS_UNLU:
        return gv
    kok = gv[:-1]
    return kok + ses.kucuk_uyum(kok or gv)


def genis_ek(madde, gv):
    """Geniş zaman ekini seçer. Kıyasın en ayırt edici kuralı."""
    if gv and gv[-1] in ses.UNLULER:
        return "r"
    if "Aorist_I" in madde.bayrak:
        return "Ir"
    if "Aorist_A" in madde.bayrak:
        return "Ar"
    return "Ar" if ses.hece_sayisi(gv) <= 1 else "Ir"


def cekim(madde, zaman="belirli_gecmis", kisi="1t", olumsuz=False):
    gv = govde(madde)
    ek, takim = ZAMAN[zaman]

    # --- olumsuz geniş zaman: bütünüyle ayrı biçim ---------------------------
    if zaman == "genis" and olumsuz:
        if kisi == "1t":
            return gv + ses.coz("mAm", gv)          # gitmem
        if kisi == "1c":
            return gv + ses.coz("mAyIz", gv)        # gitmeyiz
        b = gv + ses.coz("mAz", gv)                 # gitmez
        return _ekle(b, KISI2[kisi]) if kisi != "3t" else b

    # --- olumsuzluk eki ------------------------------------------------------
    if olumsuz:
        if zaman == "simdiki":
            gv = gv + ses.coz("m", gv)              # git + m
            gv = gv + ses.kucuk_uyum(gv)            # -> gitmi, daralmış -mA
        else:
            gv = gv + ses.coz("mA", gv)             # gitme-

    # --- gövdeye doğrudan eklenen ekte yumuşama ------------------------------
    elif _yumusar(madde, gv):
        deneme = ek if ek else genis_ek(madde, gv)
        if ses.unluyle_baslar(deneme, gv):
            gv = ses.yumusat(gv)                    # git -> gid (gider, gidiyor)

    # --- zaman eki -----------------------------------------------------------
    if zaman == "genis":
        b = gv + ses.coz(genis_ek(madde, gv), gv)
    elif zaman == "simdiki":
        b = _darlastir(gv)
        b = b + ses.coz("(I)yor", b)
    else:
        b = gv + ses.coz(ek, gv)

    # --- kişi eki ------------------------------------------------------------
    ke = (KISI1 if takim == 1 else KISI2)[kisi]
    if not ke:
        return b
    return _ekle(b, ke, yumusama=(zaman == "gelecek"))


def paradigma(madde):
    """7 zaman/kip × 2 olumsuzluk × 6 kişi = 84 yuva."""
    cik = {}
    for z in ZAMAN:
        for o in (False, True):
            for k in KISI1:
                cik[(z, o, k)] = cekim(madde, z, k, o)
    return cik
