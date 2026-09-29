"""Zorunlu seçim — çeldiriciler tesadüfi değil, her biri BELİRLİ bir kural ihlali.

NEDEN ZORUNLU SEÇİM BİRİNCİL ÖLÇÜM
  Serbest üretimde modelin cevabını okumak kırılgan: model dolgu metin yazar,
  soruyu tekrarlar, açıklama ekler. Bugün bu yüzden bir ölçüm elli puan
  yanıldı. Zorunlu seçimde ayrıştırma yoktur — adaylar bizden, model yalnız
  aralarından seçer. Serbest üretim kıyasta kalır ama ikincildir.

NEDEN ÇELDİRİCİLER KURAL İHLALİ OLMALI
  Rastgele çeldirici "yanlış" der ve biter. Her çeldirici tek bir kuralı
  bozarsa, modelin hangi kuralı bilmediği doğrudan okunur. Kıyasın vaadi olan
  teşhis raporu buradan doğar:

    kitap + belirtme hâli
      altın            kitabı     doğru
      uyum_hatasi      kitabi     küçük ünlü uyumu bilinmiyor
      yumusama_yok     kitapı     ünsüz yumuşaması bilinmiyor
      kaynastirma      kitapyı    kaynaştırma ünsüzü yanlış yerde
      ikisi_birden     kitapi     ikisi de bilinmiyor

  Model "kitapı" seçtiyse uyumu biliyor ama yumuşamayı bilmiyor. Tek bir
  doğruluk sayısı bunu söylemez.

ÇELDİRİCİ GEÇERLİLİK KURALI
  Bir çeldirici altınla AYNI çıkarsa kullanılmaz. Örneğin yumuşamayan bir
  gövdede "yumusama_yok" çeldiricisi altının kendisidir; o madde o eksende
  sınanamaz ve sessizce elenir. Aksi hâlde doğru cevabı iki kez listelemiş
  oluruz ve madde ölçmez.
"""
import ses
import ad_cekim


def _uyum_bozuk(altin, govde, sablon):
    """Ek ünlüsünü yanlış uyuma çevir: kitabı -> kitabi."""
    dogru_ek = ses.coz(sablon, govde)
    ters_ek = ses.coz(sablon, govde, ters=True)
    if ters_ek == dogru_ek or not altin.endswith(dogru_ek):
        return None
    return altin[: len(altin) - len(dogru_ek)] + ters_ek


def _yumusama_bozuk(madde, hal):
    """Yumuşamayı uygulama (ya da uygulanmayan yerde uygula)."""
    gv = madde.govde
    sablon = ad_cekim.HAL[hal]
    if not sablon or not ses.unluyle_baslar(sablon, gv):
        return None
    yumusuyor = ad_cekim._yumusar_mi(madde)
    if yumusuyor:
        bozuk_govde = gv                       # yumuşatma
    else:
        if gv[-1] not in ses.YUMUSAMA:
            return None
        bozuk_govde = ses.yumusat(gv)          # olmaması gereken yerde yumuşat
    ters = "InverseHarmony" in madde.bayrak
    return bozuk_govde + ses.coz(sablon, bozuk_govde, ters)


def _benzesme_bozuk(madde, hal):
    """Ünsüz benzeşmesini bozar: kuşta -> kuşda, ağaçtan -> ağaçdan.

    Bu çeldirici ilk sürümde YOKTU ve dört temel kuraldan birini sınamıyorduk.
    Eksikliği madde üretiminde ortaya çıktı: 63 bin madde "yeterli çeldirici
    yok" diye eleniyordu, çünkü -DA ve -DAn eklerinde uyum dışında bozulacak
    bir şey kalmıyordu. Oysa benzeşme tam da o eklerin kuralı."""
    sablon = ad_cekim.HAL[hal]
    if not sablon or ("D" not in sablon and "C" not in sablon):
        return None
    hazir, ters = ad_cekim._govde_hazirla(madde, sablon)
    dogru = ses.coz(sablon, hazir, ters)
    # D/C'yi ters ötümlülükte çöz
    ters_sablon = sablon
    bozuk = []
    for c in sablon:
        if c == "D":
            bozuk.append("t" if not ses.otumsuz_biter(hazir) else "d")
        elif c == "C":
            bozuk.append("ç" if not ses.otumsuz_biter(hazir) else "c")
        else:
            bozuk.append(c)
    y = hazir + ses.coz("".join(bozuk), hazir, ters)
    return y if y != hazir + dogru else None


def _kaynastirma_bozuk(madde, hal):
    """Kaynaştırma ünsüzünü yanlış tarafa koy: araba -> arabaı, ev -> evyi."""
    gv = madde.govde
    sablon = ad_cekim.HAL[hal]
    if not sablon or "(" not in sablon:
        return None
    ic = sablon[sablon.index("(") + 1: sablon.index(")")]
    kalan = sablon[sablon.index(")") + 1:]
    unlu_bitti = gv[-1] in ses.UNLULER
    hazir, ters = ad_cekim._govde_hazirla(madde, sablon)
    if unlu_bitti:
        return hazir + ses.coz(kalan, hazir, ters)              # tamponu düşür
    return hazir + ses.coz(ic, hazir, ters) + ses.coz(kalan, hazir, ters)  # fazladan tampon


def celdiriciler(madde, hal="belirtme"):
    """Altın biçim + kural ihlali çeldiricileri.

    Döndürür: (altin, {hata_turu: bicim}). Altınla aynı çıkan ya da
    üretilemeyen çeldiriciler listeye girmez.
    """
    altin = ad_cekim.cekim(madde, hal=hal)
    gv = madde.govde
    sablon = ad_cekim.HAL[hal]
    cik = {}

    if sablon:
        u = _uyum_bozuk(altin, gv, sablon)
        if u and u != altin:
            cik["uyum"] = u
        y = _yumusama_bozuk(madde, hal)
        if y and y != altin:
            cik["yumusama"] = y
        k = _kaynastirma_bozuk(madde, hal)
        if k and k != altin:
            cik["kaynastirma"] = k
        b = _benzesme_bozuk(madde, hal)
        if b and b != altin and b not in cik.values():
            cik["benzesme"] = b
        if u and y:
            # iki kuralı birden bozan biçim: yumuşamasız gövdeye ters uyumlu ek
            gv2 = gv if ad_cekim._yumusar_mi(madde) else ses.yumusat(gv)
            if gv2 != gv:
                i = gv2 + ses.coz(sablon, gv2, ters=True)
                if i != altin and i not in cik.values():
                    cik["ikisi"] = i

    return altin, cik


def bilesik_celdiriciler(madde, cokluk="tek", iyelik="yok", hal="belirtme"):
    """Çokluk + iyelik + hâl yığını için çeldiriciler.

    Yalnız hâl ekini sınamak paradigmanın altıda birini kullanmak demekti;
    üstelik ZAMİR n'si hiç sınanmıyordu. Oysa 3. kişi iyeliğinden sonra hâl
    eki -n- ile bağlanır (kitab-ı-n-a) ve bunu bilmeyen model 'kitabıya'
    üretir — Türkçede en sık görülen model hatalarından biri.

    Çeldiriciler:
      zamir_n     3. kişi iyeliğinden sonra n düşürülür ya da olmayan yere konur
      uyum        son ekin ünlüsü ters uyuma çevrilir
      iyelik_unlu iyelik ekinin yardımcı ünlüsü düşürülür (evim -> evm)
    """
    altin = ad_cekim.cekim(madde, cokluk, iyelik, hal)
    cik = {}
    hs = ad_cekim.HAL[hal]
    if not hs:
        return altin, cik

    # zamir n'si: 3. kişi iyeliğinde n'yi düşür, diğerlerinde ekle
    govde_iy = ad_cekim.cekim(madde, cokluk, iyelik, "yalin")
    ucuncu = iyelik in ad_cekim.UCUNCU or "CompoundP3sg" in madde.bayrak
    if ucuncu:
        y = govde_iy + ses.coz(hs, govde_iy)            # n'siz
    else:
        sb = hs[hs.index(")") + 1:] if hs.startswith("(") else hs
        y = govde_iy + "n" + ses.coz(sb, govde_iy)      # gereksiz n
    if y != altin:
        cik["zamir_n"] = y

    # son ekin uyumu
    dogru = ses.coz(hs if not ucuncu else ("n" + (hs[hs.index(")")+1:] if hs.startswith("(") else hs)), govde_iy)
    ters = ses.coz(hs if not ucuncu else ("n" + (hs[hs.index(")")+1:] if hs.startswith("(") else hs)), govde_iy, ters=True)
    if ters != dogru and altin.endswith(dogru):
        u = altin[:len(altin) - len(dogru)] + ters
        if u != altin and u not in cik.values():
            cik["uyum"] = u

    # iyelik yardımcı ünlüsü düşürülmüş
    if iyelik != "yok":
        sab = ad_cekim.IYELIK[iyelik]
        if sab and sab.startswith("("):
            ic = sab[1:sab.index(")")]
            kalan = sab[sab.index(")") + 1:]
            on = ad_cekim.cekim(madde, cokluk, "yok", "yalin")
            bozuk = on + ses.coz(kalan, on)
            b2 = bozuk + ses.coz(("n" + (hs[hs.index(")")+1:] if hs.startswith("(") else hs)) if ucuncu else hs, bozuk)
            if b2 != altin and b2 not in cik.values():
                cik["iyelik_unlu"] = b2
    return altin, cik


def bilesik_madde_kur(madde, cokluk="tek", iyelik="yok", hal="belirtme", en_az=2):
    altin, cel = bilesik_celdiriciler(madde, cokluk, iyelik, hal)
    if len(cel) < en_az:
        return None
    return {"govde": madde.govde, "yuva": (cokluk, iyelik, hal), "altin": altin,
            "celdirici": cel, "secenek": [altin] + list(cel.values())}


def madde_kur(madde, hal="belirtme", en_az=2):
    """Kıyas maddesi: altın + çeldiriciler. Yeterli çeldirici yoksa None.

    `en_az` altında madde ölçmez — iki seçenekli bir soruda şans %50'dir ve
    o madde kıyasa bilgi katmaz.
    """
    altin, cel = celdiriciler(madde, hal)
    if len(cel) < en_az:
        return None
    return {"govde": madde.govde, "hal": hal, "altin": altin,
            "celdirici": cel, "secenek": [altin] + list(cel.values())}
