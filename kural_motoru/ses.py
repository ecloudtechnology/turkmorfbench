"""Türkçe ses bilgisi — ek seçimini belirleyen bütün kurallar tek yerde.

NEDEN AYRI DOSYA
  Bütün üretim buradan geçer. Kıyasın altın verisi LLM'den değil bu dosyadan
  gelecek, dolayısıyla burada tek bir hata milyonlarca biçimi zehirler. Kural
  motoru ikinci kez bağımsız yazılıp karşılaştırılacak (`ses2.py`); iki uygulama
  aynı sonucu vermezse madde insana gider.

NEDEN ÇÖZÜMLEYİCİ KULLANMIYORUZ
  Açık Türkçe morfolojik çözümleyicilerin doğruluğu %38-72 aralığında ölçülmüş
  (TRmorph %38, TRMOR %72, 2019). Böyle bir aracı altın kaynak yapmak külliyata
  %28-62 hata enjekte eder. Bunun yerine: keyfi kelimeyi ÇÖZÜMLEMİYORUZ, altını
  inşadan belli olan biçimi ÜRETİYORUZ. Gövdeyi ve kuralı biz seçiyoruz.

  Zemberek'ten aldığımız tek şey SÖZLÜK — yani hangi gövdenin düzensiz
  davrandığı (Apache-2.0). Çözümleyicisini kullanmıyoruz. Sözlükteki bayraklar
  insan tarafından işaretlenmiş sözlüksel bilgi; çözümleyici doğruluğuyla ilgisi
  yok.

GÖSTERİM
  Ek şablonlarında büyük harfler değişkendir:
    A -> a/e      büyük ünlü uyumu (2 yönlü)
    I -> ı/i/u/ü  küçük ünlü uyumu (4 yönlü)
    D -> d/t      ünsüz benzeşmesi
    C -> c/ç      ünsüz benzeşmesi
  Parantezli harf düşebilir: "(y)A" ünlüyle biten gövdede y alır.
"""

# DÜZELTME İMLİ ÜNLÜLER ENVANTERE DAHİLDİR.
#   â î û alıntı kelimelerde yazılır ve uyumu BELİRLER. Envanterde
#   olmadıklarında görünmez oluyorlar ve bir önceki ünlü son ünlü sanılıyordu:
#   `rüzgâr`ın son ünlüsü `ü` okunup `rüzgâre` üretiliyordu; doğrusu
#   `rüzgâra`. UD Türkçe ağaç bankalarıyla karşılaştırmada yakalandı.
#
#   Sınıflandırma sesletime göre: â uzun /a/ (kalın, düz), î uzun /i/
#   (ince, düz), û uzun /u/ (kalın, yuvarlak). `hâl -> hâli` gibi ince ek
#   alan istisnalar bu kuralla değil, sözlüğün InverseHarmony bayrağıyla
#   karşılanır — yeri orasıdır.
UNLULER = "aeıioöuüâîû"
KALIN = set("aıouâû")
INCE = set("eiöüî")
YUVARLAK = set("oöuüû")
DUZ = set("aeıiâî")

# Ötümsüz ünsüzler — ekin d/c ile değil t/ç ile başlamasına yol açar.
# "Fıstıkçı Şahap" belleği: f s t k ç ş h p
OTUMSUZ = set("fstkçşhp")

# Ünlüyle başlayan ek önünde yumuşayan ünsüzler ve karşılıkları.
# k -> ğ genel kural, ama n'den sonra k -> g (renk -> rengi).
YUMUSAMA = {"p": "b", "ç": "c", "t": "d", "k": "ğ", "g": "ğ"}


def unluler(s):
    return [c for c in s if c in UNLULER]


def son_unlu(s):
    for c in reversed(s):
        if c in UNLULER:
            return c
    return None


def hece_sayisi(s):
    """Türkçede hece sayısı = ünlü sayısı. Ünsüz kümesi hece açmaz."""
    return len(unluler(s))


def buyuk_uyum(gv, ters=False):
    """A -> a/e. `ters` bayrağı uyum kırıcı alıntılar içindir (kalp -> kalbe)."""
    v = son_unlu(gv)
    kalin = (v in KALIN) if v else True
    if ters:
        kalin = not kalin
    return "a" if kalin else "e"


def kucuk_uyum(gv, ters=False):
    """I -> ı/i/u/ü. Son ünlünün hem kalınlığı hem yuvarlaklığı belirler."""
    v = son_unlu(gv)
    if v is None:
        return "ı" if not ters else "i"
    kalin = v in KALIN
    yuvarlak = v in YUVARLAK
    if ters:
        kalin = not kalin
    if kalin:
        return "u" if yuvarlak else "ı"
    return "ü" if yuvarlak else "i"


def otumsuz_biter(gv):
    return bool(gv) and gv[-1] in OTUMSUZ


def yumusat(gv):
    """Ünlüyle başlayan ek önünde son ünsüzü yumuşatır.

    n'den sonra k -> g (renk->rengi, ahenk->ahengi), diğer yerlerde k -> ğ.
    Bu ayrım önemli: tek kural yazılırsa 'rengi' yerine 'renği' üretilir.

    ÖTÜMSÜZ ÜNSÜZDEN SONRA YUMUŞAMA OLMAZ. üst->üstü, dost->dostu, çift->çifti,
    taht->tahtı. Bu denetim yokken uydurma gövdelerde 'caşost' -> 'caşosdu'
    üretiliyordu; ölçüm sırasında yakalandı."""
    if not gv or gv[-1] not in YUMUSAMA:
        return gv
    if len(gv) >= 2 and gv[-2] in OTUMSUZ:
        return gv
    son = gv[-1]
    if son == "k" and len(gv) >= 2 and gv[-2] == "n":
        return gv[:-1] + "g"
    return gv[:-1] + YUMUSAMA[son]


def nk_ile_biter(gv):
    """-nk her zaman yumuşar: renk->rengi, denk->dengi, ahenk->ahengi.

    Sözlükte bu gövdeler bayraksız duruyor; 'tek heceli yumuşamaz'
    varsayılanına takılırsak 'renki' üretiriz. Ses bilgisel kural, sözlüksel
    bilgi değil — bu yüzden burada, bayraklarda değil."""
    return len(gv) >= 2 and gv[-2:] == "nk"


def son_unlu_dusur(gv):
    """Son hecenin ünlüsünü düşürür: burun -> burn, ağız -> ağz, akıl -> akl.

    Yalnız A:LastVowelDrop bayraklı gövdelerde çağrılır; kuralla tahmin
    edilemez, sözlüksel bilgidir."""
    for i in range(len(gv) - 1, -1, -1):
        if gv[i] in UNLULER:
            return gv[:i] + gv[i + 1:]
    return gv


def ikizlestir(gv):
    """Son ünsüzü ikizler: hak -> hakk, sır -> sırr, af -> aff, his -> hiss.

    Arapça kökenli tek heceli gövdelerde ünlüyle başlayan ek önünde olur.
    A:Doubling bayrağına bağlı."""
    return gv + gv[-1] if gv else gv


def _parantez_yazilir(ic, unlu_bitti):
    """Parantez İKİ AYRI İŞ yapıyor ve yönleri terstir — karıştırılırsa
    'evim' yerine 'evm', 'arabam' yerine 'arabaIm' çıkar.

      (y) (s) (n) (l)  kaynaştırma ÜNSÜZÜ  -> gövde ÜNLÜYLE bitiyorsa yazılır
                                              araba-y-ı, araba-s-ı, araba-n-ın
      (I) (A)          yardımcı ÜNLÜ       -> gövde ÜNSÜZLE bitiyorsa yazılır
                                              ev-i-m, ev-i-miz
    """
    unlu_sablonu = ic in ("I", "A") or (ic and ic[0] in UNLULER)
    return (not unlu_bitti) if unlu_sablonu else unlu_bitti


def coz(sablon, gv, ters=False):
    """Ek şablonunu gövdeye göre somutlaştırır."""
    cik = []
    i = 0
    unlu_bitti = bool(gv) and gv[-1] in UNLULER
    while i < len(sablon):
        c = sablon[i]
        if c == "(":
            kapali = sablon.index(")", i)
            ic = sablon[i + 1:kapali]
            if _parantez_yazilir(ic, unlu_bitti):
                cik.append(coz(ic, gv, ters))
            i = kapali + 1
            continue
        if c == "A":
            cik.append(buyuk_uyum(gv, ters))
        elif c == "I":
            cik.append(kucuk_uyum(gv, ters))
        elif c == "D":
            cik.append("t" if otumsuz_biter(gv) else "d")
        elif c == "C":
            cik.append("ç" if otumsuz_biter(gv) else "c")
        else:
            cik.append(c)
        i += 1
    return "".join(cik)


def unluyle_baslar(sablon, gv):
    """Şablon bu gövdeye eklendiğinde ünlüyle mi başlıyor? Yumuşamayı bu belirler.

    "(y)I" ünsüzle biten gövdede 'ı' ile başlar -> yumuşama olur (kitap->kitabı).
    Ünlüyle biten gövdede 'y' ile başlar -> yumuşama sorusu zaten doğmaz.
    Tek doğru yol şablonu gerçekten çözmek; elle kestirmek yukarıdaki iki yönlü
    parantez kuralını ikinci kez yazmak demek olur ve orada hata yapılmıştı."""
    somut = coz(sablon, gv)
    return bool(somut) and somut[0] in UNLULER
