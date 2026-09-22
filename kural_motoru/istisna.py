"""İstisna kovaları — kıyası puan tablosundan teşhis aracına çeviren eksen.

SEKİZ KOVA, HER BİRİ ADLANDIRILMIŞ BİR DİLBİLİM OLGUSU
  1 ünlü düşmesi        burun -> burnu          sözlük: A:LastVowelDrop
  2 ünsüz ikizleşmesi   hak -> hakkı            sözlük: A:Doubling
  3 uyum kırıcı alıntı  kalp -> kalbi           sözlük: A:InverseHarmony
  4 kaynaştırma istisn. su -> suyu              elle, iki gövde
  5 birleşik isim       buzdolabı -> buzdolabına  sözlük: A:CompoundP3sg
  6 özel ad + kesme     Ankara'ya                 aşağıda
  7 kısaltma            TCDD'yi                   aşağıda, OKUNUŞA göre
  8 sayı                2026'da                   aşağıda, OKUNUŞA göre

  İlk beşi sözlük bayraklarından gelir ve `ad_cekim` zaten doğru üretir.
  Son üçü yeni kural gerektiriyor ve kıyasın en ayırt edici kısmı orası:
  kural basit ama OKUNUŞU bilmeyi gerektiriyor.

ÖZEL AD + KESME
  Özel ada gelen çekim eki kesme işaretiyle ayrılır: Ankara'ya, İzmir'e.
  Ek yine son ünlüye uyar ama YUMUŞAMA OLMAZ — özel adın yazılışı korunur:
    Sinop'a   (Sinob'a DEĞİL)      Zonguldak'a  (Zonguldağ'a DEĞİL)
  Bu, kuralı ezberden ayıran güzel bir sınama: model cins isimde yumuşatmayı
  öğrenmişse özel adda da yumuşatır ve düşer.

KISALTMA
  Ek kısaltmanın OKUNUŞUNA uyar, harflerine değil:
    TCDD'yi   "te ce de de" -> son ünlü e, ünlüyle biter -> -yi
    TÜBİTAK'ın "tübitak"    -> son ünlü a, ünsüzle biter -> -ın
    AB'ye     "a be"        -> son ünlü e, ünlüyle biter -> -ye
  Zemberek sözlüğü kısaltmaların okunuşunu `Pr:` alanında veriyor.

SAYI
  Ek sayının okunuşuna uyar: 2026'da ("… yirmi altı"), 6'yı ("altı"),
  100'ü ("yüz"), 1'e ("bir").
"""
import io
import json
import os
import re

import ses
import sozluk
import sayi as sayi_modul
import ad_cekim

# Kova 4: kuralla türetilemeyen iki gövde (ad_cekim.OZEL_GOVDE ile aynı liste)
KAYNASTIRMA_ISTISNA = ["su", "ne"]

# TDK Güncel Türkçe Sözlük'ün hakem olduğu kovalar.
#
# Bu üç kovanın altını Zemberek bayraklarından türetiliyordu ve YANLIŞTI.
# sozluk.gov.tr'nin `taki` alanı çekimli biçimi doğrudan verir ("kıraat, -ti")
# ve ölçtük: bayraktan türetilen altın TDK ile `uyum_kirici` kovasında yalnız
# %11, `unlu_dusmesi`nde %74, `ikizlesme`de %78 örtüşüyordu. Üç ayrı sistematik
# hata: olmayan yumuşamayı uygulamak (bidat->bidadi, doğrusu bidati), ince/kalın
# uyumu kaçırmak (aciz->aczı, doğrusu aczi), ikizleşirken ötümlüleştirmemek
# (ret->retti, doğrusu reddi).
#
# Hatayı insan tavanı ölçümü yakaladı: katılımcılar `uyum_kirici` kovasında
# ŞANS DÜZEYİNİN ALTINA düştü. Ana dili Türkçe olan insanlar bir kurala
# şanstan kötü uyuyorsa, sorun insanda değil altındadır.
#
# İlke: TDK tek bir `taki` veriyorsa altın odur ve madde kıyasa girer —
# gövde eş yazılışlı olsa bile, çünkü TDK belirsizliği çözmüştür. TDK
# susuyorsa ya da çelişiyorsa madde kıyasa GİRMEZ.
TDK_HAKEM = frozenset(["unlu_dusmesi", "ikizlesme", "uyum_kirici"])

_TDK = None


def tdk_altin():
    """(gövde -> TDK belirtme hâli, çok anlamlı gövdeler kümesi).

    `cok_anlam`: TDK'de başka anlamı da olan ve o anlamın ek notasyonu
    yazılmamış gövdeler. Altın birincil anlama göredir (sözlük geleneği);
    işaret, kıyas kullanıcısının isterse bu maddeleri süzebilmesi için.
    """
    global _TDK
    if _TDK is None:
        y = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tdk_altin.json")
        d = json.load(io.open(y, encoding="utf8")) if os.path.exists(y) else {}
        _TDK = (d.get("altin", {}), set(d.get("cok_anlam", [])))
    return _TDK


BAYRAK_KOVA = {
    "unlu_dusmesi": "LastVowelDrop",
    "ikizlesme": "Doubling",
    "uyum_kirici": "InverseHarmony",
    "birlesik_isim": "CompoundP3sg",
}


# --------------------------------------------------------------- özel ad ---

def ozel_ad(ad, hal="yonelme"):
    """Özel ada kesmeli çekim eki. YUMUŞAMA YOK — yazılış korunur.

    Ankara + yönelme -> Ankara'ya · Sinop + yönelme -> Sinop'a (Sinob'a değil)
    """
    sablon = ad_cekim.HAL[hal]
    if not sablon:
        return ad
    return ad + "'" + ses.coz(sablon, ad)


# -------------------------------------------------------------- kısaltma ---

def kisaltma(kis, okunus, hal="belirtme"):
    """Kısaltmaya ek: uyum OKUNUŞA göre, yazılış korunur, kesme işaretli.

    TCDD (okunuş "tecedede") + belirtme -> TCDD'yi
    """
    sablon = ad_cekim.HAL[hal]
    if not sablon or not okunus:
        return None
    return kis + "'" + ses.coz(sablon, okunus)


def okunus_temizle(pr):
    """Zemberek `Pr:` alanı bitişik yazılmış olabiliyor ('tecedede').
    Uyum için yalnız son ünlü ve son ses gerekiyor, ayırmaya gerek yok."""
    if not pr:
        return None
    s = re.sub(r"[^a-zçğıöşü]", "", pr.lower())
    return s or None


# ------------------------------------------------------------------ sayı ---

def sayi_eki(n, hal="bulunma"):
    """Sayıya ek: uyum OKUNUŞA göre, kesme işaretli.

    2026 + bulunma -> 2026'da  ("iki bin yirmi altı")
    6 + belirtme   -> 6'yı     ("altı", ünlüyle biter -> kaynaştırma)
    """
    sablon = ad_cekim.HAL[hal]
    if not sablon:
        return str(n)
    o = sayi_modul.oku(n)
    return "%d'%s" % (n, ses.coz(sablon, o))


# ------------------------------------------------------------- kova kurma ---

def kovalar(maddeler, kisaltmalar=None, yer_adlari=None, sayilar=None,
            hal_secimi=None):
    """Sekiz kovayı doldur. Döndürür: {kova: [(gosterim, altin, ek_bilgi)]}

    `hal_secimi` kova başına hangi hâlin sınanacağını söyler. Varsayılanlar
    her kovanın kendi kuralını en iyi açığa çıkaran hâl:
      ünlü düşmesi / ikizleşme / uyum kırıcı -> belirtme (ünlüyle başlar,
        yumuşama ve düşme ancak orada görünür)
      birleşik isim -> yönelme (zamir n'si orada ortaya çıkar)
      özel ad -> yönelme (kesme + yumuşamama en görünür)
      kısaltma / sayı -> belirtme ve bulunma
    """
    hal_secimi = hal_secimi or {}
    cik = {}

    # BİRİNCİL ANLAM + EŞ YAZILIŞLI ELEME.
    #
    # Bu iki süzgeç kıyasın geri kalanında uygulanıyordu ama istisna
    # kovaları sözlüğün HAM satırlarını geziyordu. Sonucu: ikincil anlamlar
    # ve eş yazılışlı gövdeler madde oluyordu, altın cevap ise tek değildi.
    #   ziraat  master [NoVoicing] -> ziraatı   ·  non_tdk#1 [InverseHarmony] -> ziraadi
    #   katil   birincil (fail)    -> katili    ·  #1 (katletme)             -> katlı
    #   ad      birincil           -> adı       ·  #1 [Doubling,InverseHarmony] -> addi
    # İkisi de gerçek kelime; hangisinin sorulduğu bağlamsız belli değil.
    # Bu maddeler kıyastan ÇIKAR — insan tavanı ölçümünde `uyum_kirici`
    # kovasında insanların şans düzeyinin ALTINA düşmesiyle yakalandı.
    birincil = sozluk.indeksle(maddeler)
    belirsiz = sozluk.belirsizler(maddeler)
    T, T_COK = tdk_altin()
    _dd = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tdk_disarida.json")
    T_DIS = set(json.load(io.open(_dd, encoding="utf8"))) if os.path.exists(_dd) else set()

    # 1-3, 5: sözlük bayraklarından
    for kova, bayrak in BAYRAK_KOVA.items():
        h = hal_secimi.get(kova, "yonelme" if kova == "birlesik_isim" else "belirtme")
        hakem = kova in TDK_HAKEM and bool(T)
        govdeler = sorted({m.govde for m in maddeler if bayrak in m.bayrak})
        L = []
        for g in govdeler:
            if " " in g or "-" in g or not g.isalpha():
                continue
            if hakem:
                altin = T.get(g)
                if altin is None or g in T_DIS:
                    continue                     # TDK susuyor ya da kuralla
                                                 # üretilemiyor: madde girmez
                kaynak = "TDK-GTS"
            else:
                # Birleşik isimde TDK `taki` vermiyor (zamir n'si sözlüksel
                # değil, dilbilgisel bir kural). Orada birincil anlam + eş
                # yazılışlı eleme uygulanır.
                if g in belirsiz or g not in birincil:
                    continue
                altin = ad_cekim.cekim(birincil[g], hal=h)
                kaynak = "kural+sozluk"
            bilgi = {"hal": h, "bayrak": bayrak, "kaynak": kaynak}
            if kaynak == "TDK-GTS" and g in T_COK:
                bilgi["cok_anlam"] = True
            L.append((g, altin, bilgi))
        cik[kova] = L

    # 4: kaynaştırma istisnası
    ad = {m.govde: m for m in maddeler}
    L = []
    for g in KAYNASTIRMA_ISTISNA:
        if g in ad:
            for h in ("belirtme", "tamlayan"):
                L.append((g, ad_cekim.cekim(ad[g], hal=h), {"hal": h}))
    cik["kaynastirma_istisna"] = L

    # 6: özel ad + kesme
    L = []
    for a in (yer_adlari or []):
        if not a or not a[0].isupper() or not a.isalpha():
            continue
        h = hal_secimi.get("ozel_ad", "yonelme")
        L.append((a, ozel_ad(a, h), {"hal": h}))
    cik["ozel_ad"] = L

    # 7: kısaltma (yalnız okunuşu bilinenler)
    L = []
    for kis, pr in (kisaltmalar or []):
        o = okunus_temizle(pr)
        if not o:
            continue
        for h in ("belirtme", "tamlayan"):
            b = kisaltma(kis, o, h)
            if b:
                L.append((kis, b, {"hal": h, "okunus": o}))
    cik["kisaltma"] = L

    # 8: sayı
    L = []
    for n in (sayilar or []):
        for h in ("bulunma", "belirtme", "yonelme"):
            L.append((str(n), sayi_eki(n, h), {"hal": h, "okunus": sayi_modul.oku(n)}))
    cik["sayi"] = L

    return cik
