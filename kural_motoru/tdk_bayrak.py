# -*- coding: utf-8 -*-
"""TDK'nin verdiği çekimli biçimden SÖZLÜK BAYRAKLARINI geri çıkarır.

NEDEN BAYRAK, NEDEN MADDE DEĞİL
  TDK yalnız belirtme hâlini veriyor (`kıraat, -ti`). O tek biçimi altın diye
  yapıştırmak istisna kovalarını düzeltir ama `kıraata`, `kıraatlarımızda`,
  `kıraatsız` gibi yüzlerce başka maddeyi yanlış bırakır — nitekim bıraktı:
  `kıraat` istisna kovasında `kıraati`, ad çekimi kovasında `kıraadi` oldu.
  Aynı gövdenin iki altını olması kıyası kullanılamaz yapar.

  Bayrak sözlüksel ilkeldir: doğru bayrak kümesi verilince motor her hâlde,
  her ek yığınında doğru biçimi üretir. Bu yüzden TDK'nin tek biçiminden
  bayrağı geri çıkarıyoruz.

NASIL
  Bayrak uzayı küçük (yumuşama/yumuşamama, ünlü düşmesi, ikizleşme, uyum
  kırıcılık). Her aday küme için motor çalıştırılır; TDK'nin biçimini üreten
  küme alınır. Birden fazla küme üretiyorsa EN KÜÇÜĞÜ seçilir — gereksiz
  bayrak eklemek, gövdeyi başka eklerde de sapmaya iter.
  Hiçbiri üretemiyorsa gövde işaretlenmez ve kıyasa girmez; kuralla
  açıklanamayan bir biçimi kural motoruna zorla söyletmek, ölçtüğümüz şeyi
  bozar.
"""
import itertools

import ad_cekim
import sozluk

ADAY = ["Voicing", "NoVoicing", "LastVowelDrop", "Doubling", "InverseHarmony"]


class _Sahte:
    """Yalnız bayrak denemek için geçici madde."""
    def __init__(self, govde, bayrak):
        self.govde, self.bayrak, self.tur = govde, set(bayrak), "Noun"
        self.okunus = self.kokler = None
        self.indeks = 0
        self.kaynak = "tdk"


def bayrak_bul(govde, tdk_belirtme):
    """TDK'nin belirtme hâlini üreten en küçük bayrak kümesi, yoksa None."""
    for k in range(len(ADAY) + 1):
        for alt in itertools.combinations(ADAY, k):
            if "Voicing" in alt and "NoVoicing" in alt:
                continue
            if ad_cekim.cekim(_Sahte(govde, alt), hal="belirtme") == tdk_belirtme:
                return frozenset(alt)
    return None


def tablo(tdk_altin):
    """{gövde: bayrak kümesi} — yalnız kuralla üretilebilenler."""
    cik, cozulemeyen = {}, []
    for g, b in tdk_altin.items():
        f = bayrak_bul(g, b)
        if f is None:
            cozulemeyen.append((g, b))
        else:
            cik[g] = f
    return cik, cozulemeyen
