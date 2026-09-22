"""Ad çekim motorunun altın sınaması.

Motor 4,3 milyon biçim üretecek. Tek bir kural hatası milyonlarca biçimi
zehirler ve kimse fark etmez. Bu yüzden her kural için ELLE YAZILMIŞ, doğruluğu
tartışmasız bir biçim listesi var. Motor değişirse önce burası koşulur.

Liste kasten "kolay" değil: her satır belirli bir kuralı sınıyor ve satırın
yanında hangi kuralı sınadığı yazılı. Geçen bir sınama, hangi kuralın
doğrulandığını da söylemeli.
"""
import sys
import sozluk
import ad_cekim

# (gövde, çokluk, iyelik, hâl, beklenen, sınanan kural)
ALTIN = [
    # --- ünsüz yumuşaması: çok heceli p/ç/t/k varsayılan yumuşar
    ("kitap", "tek", "yok", "belirtme", "kitabı",    "yumuşama p->b"),
    ("kitap", "tek", "yok", "yonelme",  "kitaba",    "yumuşama + büyük uyum"),
    ("kitap", "tek", "yok", "tamlayan", "kitabın",   "yumuşama + tamlayan"),
    ("ağaç",  "tek", "yok", "belirtme", "ağacı",     "yumuşama ç->c"),
    ("kanat", "tek", "yok", "belirtme", "kanadı",    "yumuşama t->d"),
    ("ayak",  "tek", "yok", "belirtme", "ayağı",     "yumuşama k->ğ"),
    # --- yumuşama OLMAYAN yerler
    ("kitap", "tek", "yok", "bulunma",  "kitapta",   "ünsüzle başlayan ek: yumuşama yok"),
    ("kitap", "cog", "3t",  "yalin",    "kitapları", "çokluk araya girince yumuşama yok"),
    ("at",    "tek", "yok", "belirtme", "atı",       "tek heceli: varsayılan yumuşamaz"),
    ("devlet","tek", "yok", "belirtme", "devleti",   "NoVoicing bayrağı"),
    # --- n'den sonra k -> g
    ("renk",  "tek", "yok", "belirtme", "rengi",     "k->g (n'den sonra)"),
    ("renk",  "tek", "yok", "bulunma",  "renkte",    "renk + bulunma"),
    # --- ünsüz benzeşmesi D -> t
    ("kuş",   "tek", "yok", "bulunma",  "kuşta",     "benzeşme ş -> t"),
    ("kuş",   "tek", "yok", "ayrilma",  "kuştan",    "benzeşme + ayrılma"),
    ("ev",    "tek", "yok", "bulunma",  "evde",      "ötümlü: d kalır"),
    # --- küçük ünlü uyumu dört yönlü
    ("ev",    "tek", "yok", "belirtme", "evi",       "küçük uyum: e -> i"),
    ("kuş",   "tek", "yok", "belirtme", "kuşu",      "küçük uyum: u -> u"),
    ("göz",   "tek", "yok", "belirtme", "gözü",      "küçük uyum: ö -> ü"),
    ("kız",   "tek", "yok", "belirtme", "kızı",      "küçük uyum: ı -> ı"),
    # --- kaynaştırma
    ("araba", "tek", "yok", "belirtme", "arabayı",   "kaynaştırma y (belirtme)"),
    ("araba", "tek", "yok", "yonelme",  "arabaya",   "kaynaştırma y (yönelme)"),
    ("araba", "tek", "yok", "tamlayan", "arabanın",  "kaynaştırma n (tamlayan)"),
    ("araba", "tek", "3t",  "yalin",    "arabası",   "kaynaştırma s (iyelik 3t)"),
    ("araba", "tek", "1t",  "yalin",    "arabam",    "ünlü sonrası iyelik 1t"),
    ("ev",    "tek", "1t",  "yalin",    "evim",      "ünsüz sonrası iyelik 1t"),
    ("ev",    "tek", "1c",  "yalin",    "evimiz",    "iyelik 1ç"),
    # --- zamir n'si
    ("kitap", "tek", "3t",  "yonelme",  "kitabına",  "zamir n'si (3t + hâl)"),
    ("kitap", "cog", "3t",  "yonelme",  "kitaplarına","zamir n'si (çoğul 3t + hâl)"),
    ("ev",    "tek", "3t",  "bulunma",  "evinde",    "zamir n'si + bulunma"),
    ("ev",    "tek", "1t",  "bulunma",  "evimde",    "1t'de zamir n'si YOK"),
    # --- ünlü düşmesi
    ("burun", "tek", "yok", "belirtme", "burnu",     "LastVowelDrop"),
    ("burun", "tek", "yok", "bulunma",  "burunda",   "ünsüz ek: düşme yok"),
    ("ağız",  "tek", "yok", "belirtme", "ağzı",      "LastVowelDrop"),
    ("akıl",  "tek", "yok", "belirtme", "aklı",      "LastVowelDrop"),
    ("oğul",  "tek", "yok", "belirtme", "oğlu",      "LastVowelDrop"),
    ("şehir", "tek", "yok", "belirtme", "şehri",     "LastVowelDrop"),
    # --- ünsüz ikizleşmesi
    ("hak",   "tek", "yok", "belirtme", "hakkı",     "Doubling"),
    ("hak",   "tek", "yok", "bulunma",  "hakta",     "ünsüz ek: ikizleşme yok"),
    ("sır",   "tek", "yok", "belirtme", "sırrı",     "Doubling"),
    ("af",    "tek", "yok", "belirtme", "affı",      "Doubling"),
    # --- uyum kırıcı alıntılar
    ("kalp",  "tek", "yok", "belirtme", "kalbi",     "InverseHarmony + yumuşama"),
    ("kalp",  "tek", "yok", "yonelme",  "kalbe",     "InverseHarmony yönelme"),
    ("kalp",  "tek", "yok", "bulunma",  "kalpte",    "InverseHarmony + benzeşme"),
    ("saat",  "tek", "yok", "belirtme", "saati",     "InverseHarmony (yumuşamasız)"),
    ("saat",  "tek", "yok", "bulunma",  "saatte",    "InverseHarmony + benzeşme"),
    ("rol",   "tek", "yok", "belirtme", "rolü",      "InverseHarmony yuvarlak"),
    ("gol",   "tek", "yok", "belirtme", "golü",      "InverseHarmony yuvarlak"),
    # --- kaynaştırma istisnası
    ("su",    "tek", "yok", "belirtme", "suyu",      "özel gövde: su"),
    ("su",    "tek", "yok", "tamlayan", "suyun",     "özel gövde: su tamlayan"),
    ("su",    "tek", "yok", "bulunma",  "suda",      "su + ünsüz ek (kural)"),
    # --- birleşik isim
    ("buzdolabı", "tek", "yok", "yonelme",  "buzdolabına",  "CompoundP3sg + zamir n'si"),
    ("buzdolabı", "tek", "yok", "bulunma",  "buzdolabında", "CompoundP3sg + bulunma"),
    ("buzdolabı", "tek", "yok", "belirtme", "buzdolabını",  "CompoundP3sg + belirtme"),
    # --- çokluk ve yığın
    ("ev",    "cog", "yok", "yalin",    "evler",     "çokluk ince"),
    ("kitap", "cog", "yok", "yalin",    "kitaplar",  "çokluk kalın"),
    ("ev",    "cog", "1c",  "bulunma",  "evlerimizde","dört ekli yığın"),
    ("kalp",  "cog", "yok", "bulunma",  "kalplerde", "ters uyum yalnız ilk ekte"),
    # --- vasıta
    ("araba", "tek", "yok", "vasita",   "arabayla",  "vasıta + kaynaştırma"),
    ("ev",    "tek", "yok", "vasita",   "evle",      "vasıta ünsüz sonrası"),

    # --- ÜNSÜZ KÜMESİYLE BİTEN GÖVDELER
    # Bu blok, kapsam dizeyi motoru sınadığında ortaya çıkan bir açığı kapatır:
    # altın sınamada tek bir küme-sonlu madde yoktu ve motor ötümsüz ünsüzden
    # sonra da yumuşatıyordu (caşost -> caşosdu). Milyonlarca biçimi zehirleyecek
    # bir hataydı ve yalnız uydurma gövdede görüldü.
    ("üst",    "tek", "yok", "belirtme", "üstü",     "ötümsüz (s) sonrası yumuşama YOK"),
    ("dost",   "tek", "yok", "belirtme", "dostu",    "ötümsüz (s) sonrası yumuşama YOK"),
    ("çift",   "tek", "yok", "belirtme", "çifti",    "ötümsüz (f) sonrası yumuşama YOK"),
    ("taht",   "tek", "yok", "belirtme", "tahtı",    "ötümsüz (h) sonrası yumuşama YOK"),
    ("alt",    "tek", "yok", "belirtme", "altı",     "tek heceli küme, bayraksız"),
    ("kent",   "tek", "yok", "belirtme", "kenti",    "NoVoicing bayraklı küme"),
    ("kurt",   "tek", "yok", "belirtme", "kurdu",    "ötümlü (r) sonrası Voicing"),
    ("yurt",   "tek", "yok", "belirtme", "yurdu",    "ötümlü (r) sonrası Voicing"),
    ("harp",   "tek", "yok", "belirtme", "harbi",    "küme + Voicing + InverseHarmony"),
    ("sevinç", "tek", "yok", "belirtme", "sevinci",  "çok heceli küme, ç->c"),
    ("üst",    "tek", "yok", "bulunma",  "üstte",    "küme + benzeşme"),
    ("kurt",   "cog", "yok", "yalin",    "kurtlar",  "küme + çokluk, yumuşama yok"),
]


def main():
    ham = sozluk.yukle(("master", "non_tdk"))
    # Eş yazılışlılarda BİRİNCİL anlam (Index en küçük). Ad çekimi sınandığı
    # için fiiller dışarıda; "hak [P:Adj]" gibi başka türden maddeler de
    # birincil seçimini bozmasın diye tür süzgeci var.
    maddeler = sozluk.indeksle([m for m in ham if m.tur in ("Noun", "Adj")])
    gecen = kalan = 0
    eksik = []
    hatalar = []
    for gv, c, i, h, bek, kural in ALTIN:
        m = maddeler.get(gv)
        if m is None:
            eksik.append(gv)
            continue
        cik = ad_cekim.cekim(m, c, i, h)
        if cik == bek:
            gecen += 1
        else:
            kalan += 1
            hatalar.append((gv, c, i, h, bek, cik, kural, sorted(m.bayrak)))

    print("ALTIN SINAMA — ad çekimi")
    print("  geçen %d / %d" % (gecen, gecen + kalan))
    if eksik:
        print("  SÖZLÜKTE YOK: %s" % ", ".join(sorted(set(eksik))))
    if hatalar:
        print("\n  DÜŞENLER:")
        for gv, c, i, h, bek, cik, kural, bayrak in hatalar:
            print("    %-10s %-4s %-4s %-9s  beklenen %-14s üretilen %-14s  [%s] %s"
                  % (gv, c, i, h, bek, cik, kural, bayrak))
    return 1 if (hatalar or eksik) else 0


if __name__ == "__main__":
    sys.exit(main())
