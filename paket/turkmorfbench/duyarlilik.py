# -*- coding: utf-8 -*-
"""Puanlama kuralı duyarlılık çözümlemesi — sonuç kurala mı bağlı?

NEDEN BU MODÜL VAR
  3.3.0'da puanlama kuralı değişti: aday artık log P(aday | istem) toplamının
  ADAYIN KARAKTER SAYISINA bölünmesiyle puanlanıyor. Kural, doğruluğa göre
  değil uzunluk yanlılığına göre seçildi; bu doğru ölçüttü. Ama kalan yanlılık
  sıfırlanmadı: altın, uzunlukları farklı maddelerde %29,9 oranında en kısadır,
  seçilen kural ise %39-43 oranında en kısayı seçiyor.

  Asıl soru bu değil. Asıl soru şu: KURAL DEĞİŞİNCE SONUÇ DEĞİŞİYOR MU?
  İki modelin sıralaması, kova profili ve gerçek/uydurma farkı altı kuralın
  hepsinde aynı çıkıyorsa, kalan yanlılık bulguyu taşımıyor demektir ve kıyas
  ciddi biçimde güçlenir. Değişiyorsa, hangi bulgunun kurala bağlı olduğunu
  bilmek zorundayız — ve bunu okuyucudan önce biz söylemeliyiz.

TASARIM
  Model BİR KEZ koşar. Her aday için üç ham büyüklük saklanır:
      toplam   log P(aday | istem) toplamı
      n_jeton  adayın jeton sayısı
      n_harf   adayın karakter sayısı
      kosulsuz log P(aday) — yalnız PMI için, ayrı ve tarafsız bir istemle
  Altı kural bu üç büyüklükten TÜRETİLİR; model altı kez koşmaz.

ALTI KURAL
  ham          toplam                       ham koşullu log-olabilirlik
  jeton        toplam / n_jeton             jetona normalleştirme
  harf         toplam / n_harf              KARAKTERE (3.3.0'da seçilen)
  pmi          toplam - kosulsuz            koşulsuzla normalleştirme
  pmi_harf     (toplam - kosulsuz) / n_harf PMI + uzunluk düzeltmesi
  esli         ikili karşılaştırma          Copeland: her adayı her adaya karşı
"""
import itertools
import json


KURALLAR = ("ham", "jeton", "harf", "pmi", "pmi_harf", "esli")

# Uzunluğu farklı adayı olan maddelerde altının en kısa olma taban oranı.
# Yansız bir kuralın en kısayı seçme oranı bu civarda olmalıdır.
TABAN_EN_KISA = 0.299


def _puan(b, kural):
    """Tek adayın, tek kurala göre puanı."""
    if kural == "ham":
        return b["toplam"]
    if kural == "jeton":
        return b["toplam"] / max(1, b["n_jeton"])
    if kural == "harf":
        return b["toplam"] / max(1, b["n_harf"])
    if kural == "pmi":
        return b["toplam"] - b.get("kosulsuz", 0.0)
    if kural == "pmi_harf":
        return (b["toplam"] - b.get("kosulsuz", 0.0)) / max(1, b["n_harf"])
    raise ValueError(kural)


def _esli_sec(bilesenler):
    """Copeland: her aday her adaya karşı harf-normalize puanla yarışır.

    İkili karşılaştırma, tüm adayları tek ölçeğe koymak yerine yalnız ÇİFT
    içinde karşılaştırır; ölçek kayması çiftte sadeleşir.
    """
    adlar = list(bilesenler)
    galibiyet = dict.fromkeys(adlar, 0)
    for a, c in itertools.combinations(adlar, 2):
        pa = _puan(bilesenler[a], "harf")
        pc = _puan(bilesenler[c], "harf")
        if pa > pc:
            galibiyet[a] += 1
        elif pc > pa:
            galibiyet[c] += 1
    return max(adlar, key=lambda x: (galibiyet[x], _puan(bilesenler[x], "harf")))


def sec(bilesenler, kural):
    """Bir maddenin adayları arasından kurala göre seçim."""
    if kural == "esli":
        return _esli_sec(bilesenler)
    return max(bilesenler, key=lambda a: _puan(bilesenler[a], kural))


def bilesen_topla(arka, maddeler, kosulsuz_istem="", ilerleme=None):
    """Model BİR KEZ koşar; her adayın ham büyüklükleri toplanır."""
    from .olcum import ISTEM
    kayit = []
    for i, m in enumerate(maddeler):
        onek = ISTEM % (m["govde"], "")
        b = {}
        for aday in m["secenek"]:
            toplam = arka.olasilik(onek, aday) * max(1, len(aday))  # harf bölmesini geri al
            b[aday] = {
                "toplam": toplam,
                "n_harf": len(aday),
                "n_jeton": len(arka.jetonla(aday)),
                "kosulsuz": (arka.olasilik(kosulsuz_istem, aday)
                             * max(1, len(aday))) if kosulsuz_istem is not None else 0.0,
            }
        kayit.append({"kimlik": m["kimlik"], "altin": m["altin"], "bilesen": b})
        if ilerleme:
            ilerleme(i + 1, len(maddeler))
    return kayit


def en_kisa_orani(kayit, kural):
    """Kuralın 'en kısa adayı seçme' oranı — yalnız uzunluğu FARKLI olan maddelerde."""
    pay = top = 0
    for k in kayit:
        b = k["bilesen"]
        boy = {a: b[a]["n_harf"] for a in b}
        if len(set(boy.values())) < 2:
            continue                      # hepsi aynı uzunlukta: bilgi taşımaz
        top += 1
        secilen = sec(b, kural)
        if boy[secilen] == min(boy.values()):
            pay += 1
    return pay / top if top else float("nan")


def coz(kayit, maddeler=None):
    """Altı kuralın hepsi için doğruluk, uzunluk yanlılığı ve seçim vektörü."""
    cikti = {}
    for kural in KURALLAR:
        secim = [sec(k["bilesen"], kural) for k in kayit]
        dogru = [s == k["altin"] for s, k in zip(secim, kayit)]
        cikti[kural] = {
            "dogruluk": sum(dogru) / len(dogru) if dogru else float("nan"),
            "en_kisa_orani": en_kisa_orani(kayit, kural),
            "taban": TABAN_EN_KISA,
            "dogru": dogru,
        }
    # kurallar birbiriyle ne kadar uyuşuyor
    cikti["_uyum"] = {}
    for a, c in itertools.combinations(KURALLAR, 2):
        da, dc = cikti[a]["dogru"], cikti[c]["dogru"]
        cikti["_uyum"]["%s|%s" % (a, c)] = sum(x == y for x, y in zip(da, dc)) / len(da)
    return cikti


def karsilastir(kayit_a, kayit_b, maddeler, ad_a="A", ad_b="B", anahtar="hucre"):
    """İKİ sistemi altı kuralın HEPSİNDE karşılaştırır — sonuç kurala bağlı mı?

    Her kural için farkı küme bootstrap'ıyla verir. Sıralama bir kuralda
    tersine dönüyorsa, bulgu kurala bağlıdır ve öyle bildirilmelidir.
    """
    from .istatistik import esli_fark
    ca, cb = coz(kayit_a), coz(kayit_b)
    satir = []
    for kural in KURALLAR:
        f = esli_fark(maddeler, ca[kural]["dogru"], cb[kural]["dogru"],
                      anahtar=anahtar, b=2000)
        satir.append({
            "_kural": kural,   # "_" ile: model adı "kural" olursa çakışmasın
            ad_a: ca[kural]["dogruluk"],
            ad_b: cb[kural]["dogruluk"],
            "fark": f["fark"],
            "ci": f["ci"],
            "anlamli": f["anlamli"],
            "en_kisa_%s" % ad_a: ca[kural]["en_kisa_orani"],
            "en_kisa_%s" % ad_b: cb[kural]["en_kisa_orani"],
        })
    isaretler = {("+" if s["fark"] > 0 else "-") for s in satir if s["anlamli"]}
    return {
        "satir": satir,
        "yon_tutarli": len(isaretler) <= 1,
        "tum_kurallarda_anlamli": all(s["anlamli"] for s in satir),
        "anahtar": anahtar,
    }


def rapor(sonuc, ad_a="A", ad_b="B"):
    y = []
    y.append("%-9s %9s %9s %9s %-22s %s" % ("kural", ad_a, ad_b, "fark",
                                            "%95 GA", "en kısa (hedef %29,9)"))
    for s in sonuc["satir"]:
        y.append("%-9s %8.2f%% %8.2f%% %+8.2f%% [%+.2f%%, %+.2f%%]%s  %.1f%% / %.1f%%"
                 % (s["_kural"], 100 * s[ad_a], 100 * s[ad_b], 100 * s["fark"],
                    100 * s["ci"][0], 100 * s["ci"][1],
                    " *" if s["anlamli"] else "  ",
                    100 * s["en_kisa_%s" % ad_a], 100 * s["en_kisa_%s" % ad_b]))
    y.append("")
    y.append("yön tüm kurallarda aynı : %s" % ("EVET" if sonuc["yon_tutarli"] else "HAYIR"))
    y.append("tüm kurallarda anlamlı  : %s" % ("EVET" if sonuc["tum_kurallarda_anlamli"] else "HAYIR"))
    y.append("(küme: %s)" % sonuc["anahtar"])
    return "\n".join(y)
