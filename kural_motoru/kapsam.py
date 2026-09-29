"""Ses ortamı kapsam dizeyi ve uydurma (wug) gövde üretimi.

RAKİPTEN AYRILDIĞIMIZ ASIL YER BURASI
  arXiv 2410.12656 uydurma gövdeyi şöyle üretiyor: gerçek kökün SON ÜNLÜSÜNÜ ve
  SON ÜNSÜZÜNÜ koruyup gerisini harf sıklığına göre rastgele değiştiriyor.
  Ama Türkçede ek seçimini belirleyen şey tam da son ünlü ve son ünsüzdür. Yani
  sınanan ses ortamı gerçek kökten miras alınıyor, bağımsız örneklenmiyor;
  kural uzayı taranmıyor ve taranan yerler gerçek kelime dağılımının gölgesinde
  kalıyor.

  Burada tersi yapılıyor: ek seçimini belirleyen eksenler ÖNCE tanımlanıp
  çaprazlanıyor, gövdeler sonra o hücreleri doldurmak için üretiliyor.

EKSENLER
  son ünlü        8   a e ı i o ö u ü        -> iki uyumu birden belirler
  son ses sınıfı  8   ünlü · p · ç · t · k · ötümsüz-diğer · ötümlü · küme
                      p/ç/t/k ayrı tutuluyor çünkü yumuşama karşılıkları farklı
                      (p->b, ç->c, t->d, k->ğ) ve k'nin n sonrası ayrı davranışı var
  hece sayısı     3   1 · 2 · 3+             -> tek hecelilik yumuşama ve geniş
                                                zaman kurallarında belirleyici
  iç uyum         2   uyumlu · kırık         -> yalnız 2+ hecede anlamlı

  Hücre sayısı: 8 × 8 × (1×1 + 2×2) = 320

NEDEN "KIRIK UYUM" EKSENİ ŞART
  Türkçede ek, gövdenin SON ünlüsüne uyar. "kitap" gibi kendi içinde uyumsuz bir
  gövdede ilk ünlü ince, son ünlü kalındır ve ek kalın gelir (kitab-ı). İlk ünlüye
  bakan bir model burada düşer. Uydurma gövdeyi gerçek kökten türetince bu ayrım
  denetimli biçimde kurulamaz; burada kurulabiliyor.

FONOTAKTİK
  Hece: (C)V(C)(C). Türkçe kökte söz başı ünsüz kümesi yoktur. Söz sonu kümeler
  sınırlıdır ve listelenmiştir. 'ğ' söz başında bulunmaz.
  Üretilen her gövde sözlüğe karşı denetlenir: gerçek bir kelimeye denk gelen
  aday atılır — wug'un tanımı gereği külliyatta geçmemesi gerekir.
"""
import random

import ses

# ünsüz envanteri
OTUMSUZ_DIGER = "fhsş"
OTUMLU = "bcdgjlmnrvyz"
# Uydurma gövdede kullanılmaz: Türkçe kökte bulunmaz, yalnız alıntılarda geçer.
YERLI_DISI = "j"
YUMUSAYAN = "pçtk"
TUM_UNSUZ = OTUMSUZ_DIGER + OTUMLU + YUMUSAYAN
BAS_UNSUZ = [c for c in TUM_UNSUZ if c != "ğ"]          # ğ söz başında olmaz

# söz sonunda geçerli ünsüz kümeleri (Türkçe kökte dar bir küme)
KUMELER = ["rt", "rk", "rp", "rç", "lt", "lk", "lp", "lç",
           "nt", "nk", "nç", "st", "şt", "ft", "ht"]

SON_SES = ["unlu", "p", "ç", "t", "k", "otumsuz_diger", "otumlu", "kume"]
HECE = [1, 2, 3]
UYUM = ["uyumlu", "kirik"]


def hucreler():
    """320 hücre. Tek hecelide iç uyum ekseni anlamsız, o yüzden yalnız 'uyumlu'."""
    cik = []
    for sv in ses.UNLULER:
        for ss in SON_SES:
            for h in HECE:
                for u in (UYUM if h > 1 else ["uyumlu"]):
                    cik.append((sv, ss, h, u))
    return cik


def _uyumlu_unlu(onceki, rng):
    """Önceki ünlüye uyan bir ünlü seç (büyük + küçük uyum)."""
    kalin = onceki in ses.KALIN
    yuvarlak = onceki in ses.YUVARLAK
    if yuvarlak:
        # yuvarlaktan sonra ya dar-yuvarlak ya geniş-düz gelir
        aday = ("u", "a") if kalin else ("ü", "e")
    else:
        aday = ("ı", "a") if kalin else ("i", "e")
    return rng.choice(aday)


def _kirik_unlu(onceki, rng):
    """Kasten uyumu bozan bir ünlü seç — son ünlü kalınsa öncekini ince yap."""
    karsi = [v for v in ses.UNLULER
             if (v in ses.KALIN) != (onceki in ses.KALIN)]
    return rng.choice(karsi)


def _son_parca(son_ses, rng):
    """Hücrenin gerektirdiği son ses parçasını döndür."""
    if son_ses == "unlu":
        return ""
    if son_ses in ("p", "ç", "t", "k"):
        return son_ses
    if son_ses == "otumsuz_diger":
        return rng.choice(OTUMSUZ_DIGER)
    if son_ses == "otumlu":
        return rng.choice([c for c in OTUMLU if c not in "ğ" + YERLI_DISI])
    return rng.choice(KUMELER)


def uydurma_uret(hucre, rng, sozluk_govdeler, deneme=200):
    """Hücrenin tarifine uyan bir uydurma gövde üret.

    Gövde sondan kurulur: önce son ünlü ve son ses sabitlenir (hücrenin tanımı
    bunlar), sonra öne doğru heceler eklenir. Ters yönde kurmak şart — hücreyi
    belirleyen şey sondur.
    """
    son_unlu, son_ses, hece, uyum = hucre
    for _ in range(deneme):
        son = _son_parca(son_ses, rng)
        # son hece: C + son_unlu + son
        parcalar = [rng.choice(BAS_UNSUZ) + son_unlu + son]
        onceki = son_unlu
        for _ in range(hece - 1):
            v = (_kirik_unlu(onceki, rng) if uyum == "kirik" and len(parcalar) == hece - 1
                 else _uyumlu_unlu(onceki, rng))
            # içteki heceler: C V (C) — kapalı hece bazen, kümesiz
            kapali = rng.random() < 0.45
            kod = [c for c in OTUMLU + OTUMSUZ_DIGER if c not in YERLI_DISI]
            h = rng.choice(BAS_UNSUZ) + v + (rng.choice(kod) if kapali else "")
            parcalar.insert(0, h)
            onceki = v
        g = "".join(parcalar)

        if g in sozluk_govdeler:
            continue                      # gerçek kelime: wug olamaz
        if not gecerli(g):
            continue
        return g
    return None


def gecerli(g):
    """Fonotaktik ve yerlilik denetimi."""
    if not g or g[0] == "ğ":
        return False
    if "j" in g:
        return False                       # Türkçe kökte j yok
    if len(g) >= 2 and g[-1] == "y" and g[-2] in "ıiuü":
        return False                       # söz sonu -iy/-ıy/-uy/-üy Türkçe kökte bulunmaz
    # üç ünsüz yan yana gelmez
    ard = 0
    for c in g:
        ard = 0 if c in ses.UNLULER else ard + 1
        if ard >= 3:
            return False
    # aynı ünsüz iki kez yan yana (kökte ikizleşme yok)
    for i in range(len(g) - 1):
        if g[i] == g[i + 1] and g[i] not in ses.UNLULER:
            return False
    return True


def hucre_sinifla(govde):
    """Gerçek bir gövdenin hangi hücreye düştüğünü söyler."""
    if not govde:
        return None
    sv = ses.son_unlu(govde)
    if sv is None:
        return None
    son = govde[-1]
    # SIRA ONEMLI: kume denetimi tek unsuz denetiminden ONCE gelmeli.
    # "ust" son harfi t oldugu icin once 't' hucresine dusuyordu ve hicbir
    # govde 'kume' hucresine girmiyordu. Sonuc: 40 kume hucresi "Turkcede
    # karsiligi yok" gibi gorundu; oysa ust, dost, kurt, renk, harp, sevinc
    # hepsi var. Kapsam iddiasini 2,5 kat sisiren hata buydu.
    if son in ses.UNLULER:
        ss = "unlu"
    elif len(govde) >= 2 and govde[-2:] in KUMELER:
        ss = "kume"
    elif son in YUMUSAYAN:
        ss = son
    elif son in OTUMSUZ_DIGER:
        ss = "otumsuz_diger"
    else:
        ss = "otumlu"
    h = min(ses.hece_sayisi(govde), 3)
    if h == 1:
        u = "uyumlu"
    else:
        vs = ses.unluler(govde)
        u = "uyumlu" if all((v in ses.KALIN) == (vs[-1] in ses.KALIN) for v in vs) else "kirik"
    return (sv, ss, h, u)
