"""Ek zinciri derinliği — 1'den 8'e kadar aynı gövde üzerine yığma.

NEDEN AYRI EKSEN
  Türkçe sondan eklemeli; bir gövdeye arka arkaya sekiz ek gelmesi olağandır.
  Rakip çalışma (arXiv 2410.12656) derinlik arttıkça başarının sıfıra indiğini
  gösteriyor ama ekleri KARIŞTIRARAK veriyor — oysa Türkçede ek sırası katıdır.
  Karıştırılmış bir yığın, modelin sırayı mı bilmediğini yoksa derinlikte mi
  kaybolduğunu ayırmıyor.

  Burada sıra doğal, derinlik kontrollü ve her basamak tek bir ek ekliyor.

MERDİVEN (ev)
  1  ev-ler                              çokluk
  2  ev-ler-imiz                         + iyelik 1. çoğul
  3  ev-ler-imiz-de                      + bulunma
  4  ev-ler-imiz-de-ki                   + ilgi -ki
  5  ev-ler-imiz-de-ki-ler               + çokluk
  6  ev-ler-imiz-de-ki-ler-den           + ayrılma
  7  ev-ler-imiz-de-ki-ler-den-miş        + rivayet
  8  ev-ler-imiz-de-ki-ler-den-miş-siniz  + 2. çoğul kişi

  Sekiz basamağın hepsi gerçek, konuşulan Türkçe. Uydurma bir yığın değil.

İKİ AYRI ÖLÇÜM — ASIL SORU BU
  Sesbilimsel kararların hepsi BİRİNCİ basamakta, gövdeye bitişik ekte verilir
  (yumuşama, ünlü düşmesi, uyum). Sonraki ekler kendinden öncekine uyar.
  Dolayısıyla derinlik iki ayrı şeyi sınayabilir:

    tam  — sekiz ekli biçimin tamamı doğru mu
    kök  — gövdeye bitişik karar hâlâ doğru mu (yani model uzadıkça ilk
           kararını bozuyor mu)

  İkincisi yeni bir soru: "model uzun kelimede gövdeyi unutuyor mu". Tek bir
  doğruluk sayısı bunu göstermez.

NOT — `-ki` DEĞİŞMEZ SANILMASIN
  `-ki` genelde değişmez (evdeki) ama yuvarlak ince ünlüden sonra `-kü` olur
  (dün-kü, bugün-kü). Merdivende hep bulunma ekinden sonra geldiği için `-ki`
  kalır; başka yerde kullanılırsa kural gerekir.
"""
import ses

# (ek şablonu, basamak adı) — sıra katıdır, değiştirilemez
MERDIVEN = [
    ("lAr",    "çokluk"),
    ("(I)mIz", "iyelik_1c"),
    ("DA",     "bulunma"),
    ("ki",     "ilgi"),
    ("lAr",    "çokluk_2"),
    ("DAn",    "ayrilma"),
    ("mIş",    "rivayet"),
    ("sInIz",  "kisi_2c"),
]

EN_DERIN = len(MERDIVEN)


def kur(govde_hazir, derinlik):
    """Hazırlanmış gövdeye merdivenin ilk `derinlik` basamağını uygular.

    `govde_hazir` ad_cekim'in gövde hazırlığından geçmiş olmalı (yumuşama,
    ünlü düşmesi, ikizleşme). Merdivenin ilk eki `-lAr` ünsüzle başladığı için
    aslında gövdeyi bozmaz; ama merdiven başka bir ekle başlatılırsa bu şart olur.
    """
    b = govde_hazir
    for sablon, _ in MERDIVEN[:derinlik]:
        b += ses.coz(sablon, b)
    return b


def basamaklar(govde_hazir):
    """1..8 derinliğinin hepsini döndürür: [(derinlik, ad, biçim), ...]"""
    cik = []
    b = govde_hazir
    for i, (sablon, ad) in enumerate(MERDIVEN, 1):
        b += ses.coz(sablon, b)
        cik.append((i, ad, b))
    return cik


def kok_parcasi(bicim, govde_ham, govde_hazir):
    """Modelin ürettiği biçimde gövdeye bitişik karar doğru mu?

    Yalnız başlangıcına bakılır: gövde hazırlığı (yumuşama vb.) korunmuş mu.
    `kitap` için beklenen başlangıç `kitap` (çokluk ünsüzle başladığı için
    yumuşama yok); `kitab-ım-da-ki` gibi ünlüyle başlayan bir merdivende ise
    `kitab` olurdu. Bu yüzden karşılaştırma HAZIR gövdeyledir, ham gövdeyle değil.
    """
    return bool(bicim) and bicim.lower().startswith(govde_hazir.lower())
