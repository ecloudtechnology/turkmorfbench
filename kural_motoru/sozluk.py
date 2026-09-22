"""Zemberek sözlüğünü oku — bize lazım olan tek şey DÜZENSİZLİK BAYRAKLARI.

Zemberek'in çözümleyicisini kullanmıyoruz (doğruluğu ölçümümüze yetmez); yalnız
sözlüğünü kullanıyoruz. Sözlükteki bayraklar insan tarafından işaretlenmiş
sözlüksel bilgidir — hangi gövdenin kural dışı davrandığı. Kuralla tahmin
edilemez, bir yerden gelmesi şart, ve açık lisanslı tek kaynak bu.

Lisans: Apache-2.0 (zemberek-nlp). Türetilmiş külliyatta atıf verilecek.

SATIR BİÇİMİ
    kitap [P:Noun; A:Voicing]
    ağız [A:LastVowelDrop]
    hak [A:Doubling; Index:1]
    buzdolabı [A:CompoundP3sg; Roots:buz-dolap]
    gitmek [A:Voicing, Aorist_A]
    TCDD [Pr:tecedede; P:Abbrv]

BİZE LAZIM OLAN BAYRAKLAR
    Voicing        ünlüyle başlayan ek önünde p/ç/t/k yumuşar  (kitap -> kitabı)
    NoVoicing      yumuşamaz — çok heceli olsa bile            (devlet -> devleti)
    LastVowelDrop  son hecenin ünlüsü düşer                    (burun -> burnu)
    Doubling       son ünsüz ikizlenir                         (hak -> hakkı)
    InverseHarmony uyum kırıcı alıntı, ince ek alır            (kalp -> kalbi)
    CompoundP3sg   3. tekil iyelikli birleşik isim             (buzdolabı -> buzdolabına)
    Aorist_A       geniş zaman -ar/-er alır                    (gitmek -> gider DEĞİL, bkz. not)
    Aorist_I       geniş zaman -ır/-ir alır
    Pr             okunuş — kısaltmalarda ek buna göre seçilir (TCDD -> TCDD'yi)

NOT — YUMUŞAMA VARSAYILANI
  Zemberek'te çok heceli ve p/ç/t/k ile biten gövdeler VARSAYILAN olarak yumuşar;
  yumuşamayanlar A:NoVoicing ile işaretlenir (1.693 madde). Tek heceliler ise
  varsayılan olarak yumuşamaz; yumuşayanlar A:Voicing ile işaretlenir (211 madde).
  Bu asimetri sözlüğün kendi sözleşmesi ve bire bir uyulmalı — tersine çevrilirse
  'devleti' yerine 'devledi', 'kabı' yerine 'kapı' üretilir.
"""
import os
import re

KOK = os.path.dirname(os.path.abspath(__file__))

DOSYALAR = {
    "master": "z_master-dictionary.dict",
    "non_tdk": "z_non-tdk.dict",
    "eskimis": "z_tdk-obsolete.dict",
    "ozel": "z_proper.dict",
    "ozel_kulliyat": "z_proper-from-corpus.dict",
    "yer": "z_locations-tr.dict",
    "kisi": "z_person-names.dict",
    "kisaltma": "z_abbreviations.dict",
    "gayriresmi": "z_informal.dict",
}

# Madde satırından ilgilendiğimiz alanlar
_BAYRAK = re.compile(r"A:([^;\]]+)")
_TUR = re.compile(r"P:([^;\],]+)")
_OKUNUS = re.compile(r"Pr:([^;\]]+)")
_KOKLER = re.compile(r"Roots:([^;\]]+)")
_INDEKS = re.compile(r"Index:(\d+)")


class Madde:
    __slots__ = ("govde", "tur", "bayrak", "okunus", "kokler", "indeks", "kaynak")

    def __init__(self, govde, tur, bayrak, okunus, kokler, indeks, kaynak):
        self.govde = govde
        self.tur = tur
        self.bayrak = bayrak
        self.okunus = okunus
        self.kokler = kokler
        self.indeks = indeks
        self.kaynak = kaynak

    def __repr__(self):
        return "Madde(%r, %s, %s)" % (self.govde, self.tur, sorted(self.bayrak))


def _satir_coz(satir, kaynak):
    satir = satir.strip()
    if not satir or satir.startswith("#"):
        return None
    # Gövde ilk köşeli paranteze kadar. Gövdede boşluk olabilir ("acele etmek").
    i = satir.find("[")
    govde = (satir[:i] if i >= 0 else satir).strip()
    kuyruk = satir[i:] if i >= 0 else ""
    if not govde:
        return None

    bayrak = set()
    for m in _BAYRAK.finditer(kuyruk):
        for t in m.group(1).split(","):
            t = t.strip()
            if t:
                bayrak.add(t)

    tm = _TUR.search(kuyruk)
    tur = tm.group(1).strip() if tm else None
    if tur is None:
        # Zemberek sözleşmesi: tür yazılmamışsa -mak/-mek ile biten FİİL,
        # geri kalanı İSİM. Bu varsayılan sözlükte 28.881 maddenin çoğunu
        # kapsıyor; elle her satıra P: yazılmamış.
        tur = "Verb" if re.search(r"(mak|mek)$", govde) else "Noun"

    om = _OKUNUS.search(kuyruk)
    km = _KOKLER.search(kuyruk)
    im = _INDEKS.search(kuyruk)
    return Madde(govde, tur, bayrak,
                 om.group(1).strip() if om else None,
                 km.group(1).strip().split("-") if km else None,
                 int(im.group(1)) if im else 0,
                 kaynak)


def yukle(hangi=("master",), kok=None):
    """Seçilen sözlük dosyalarını okur. Varsayılan: yalnız ana sözlük."""
    kok = kok or KOK
    cik = []
    for ad in hangi:
        yol = os.path.join(kok, DOSYALAR[ad])
        if not os.path.exists(yol):
            raise FileNotFoundError(yol)
        with open(yol, encoding="utf8") as f:
            for satir in f:
                m = _satir_coz(satir, ad)
                if m is not None:
                    cik.append(m)
    return cik


# Çekimi etkileyen bayraklar. Eş yazılışlı maddeler bunlarda ayrışıyorsa
# gövde BELİRSİZDİR ve kıyasa madde olarak konulamaz (altın cevap tek olmaz).
SES_BAYRAK = frozenset(["Voicing", "NoVoicing", "LastVowelDrop", "Doubling",
                        "InverseHarmony", "CompoundP3sg", "Aorist_A", "Aorist_I"])


def indeksle(maddeler, tur=None):
    """Gövde -> BİRİNCİL madde. Zemberek sözleşmesi: Index yazılmayan (0) anlam
    birincildir, Index:1, Index:2 sonraki anlamlardır.

    Bu şart: sözlükte 'hak' üç kez geçiyor — [A:Doubling] (hak, hukuk anlamı),
    [P:Adj] ve [P:Noun; A:Doubling, InverseHarmony; Index:1]. Sözlüğü düz bir
    sözlüğe indirip son satırı almak ikinci anlamı birincil sanmaya yol açıyor
    ve 'hakkı' yerine 'hakki' üretiliyordu."""
    cik = {}
    for m in maddeler:
        if tur and m.tur != tur:
            continue
        v = cik.get(m.govde)
        if v is None or m.indeks < v.indeks:
            cik[m.govde] = m
    return cik


def belirsizler(maddeler, tur=None):
    """Eş yazılışlı maddeleri çekim davranışına göre ayrıştırır.

    Döndürür: gövde -> farklı ses bayrağı kümeleri. Boş değilse o gövdenin
    doğru çekimi bağlama bağlıdır; kaynak külliyata girer ama KIYASA GİRMEZ."""
    gruplar = {}
    for m in maddeler:
        if tur and m.tur != tur:
            continue
        gruplar.setdefault(m.govde, set()).add(frozenset(m.bayrak & SES_BAYRAK))
    return {g: k for g, k in gruplar.items() if len(k) > 1}


def ozet(maddeler):
    import collections
    t = collections.Counter(m.tur for m in maddeler)
    b = collections.Counter()
    for m in maddeler:
        for x in m.bayrak:
            b[x] += 1
    return t, b


if __name__ == "__main__":
    m = yukle(("master", "non_tdk"))
    t, b = ozet(m)
    print("madde: %d" % len(m))
    print("--- sözcük türü ---")
    for k, v in t.most_common(10):
        print("  %-12s %6d" % (k, v))
    print("--- düzensizlik bayrakları ---")
    for k, v in b.most_common(15):
        print("  %-16s %6d" % (k, v))
