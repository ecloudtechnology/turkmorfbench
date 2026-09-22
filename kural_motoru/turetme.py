"""Çatı ve yapım ekleri — kıyasın üçüncü ekseni.

ÇATI (fiilden fiile)
  edilgen  -Il / -In / -n     yaz-ıl · al-ın · oku-n
  dönüşlü  -In               yıka-n · giy-in
  işteş    -Iş               gör-üş · vur-uş
  ettirgen -DIr / -t / …     aşağıya bak, tek düzensiz olan bu

ETTİRGEN NEDEN AYRI ELE ALINIYOR
  Kuralın güvenilir olduğu iki durum var:
    ünlüyle biten ya da -l/-r ile biten çok heceli gövde -> -t
      bekle-t · otur-t · kısal-t
    geri kalan                                           -> -DIr
      yaz-dır · sev-dir · kes-tir
  Ama tek heceli gövdelerin bir bölümü SÖZLÜKSEL olarak başka ek alır ve bu
  sözlükte işaretli değil:
    -Ir  iç-ir · kaç-ır · düş-ür · geç-ir · uç-ur · doy-ur · bit-ir · piş-ir
    -It  ak-ıt · kork-ut · ürk-üt · sark-ıt
    -Ar  çık-ar · kop-ar · gid-er
  Bu liste TDK'dan derlendi ve AÇIK duruyor; gizli bir düzeltme tablosu değil.

  ÖNEMLİ TASARIM NOTU: uydurma (wug) gövdede sözlüksel istisna OLAMAZ — var
  olmayan bir kelimenin sözlükte kaydı olmaz. Yani ettirgen, uydurma gövdelerde
  tamamen kurala bağlıdır ve güvenle üretilebilir. Gerçek gövdelerde ise yalnız
  kuralın tuttuğu yerler ile aşağıdaki açık liste kullanılır; kalanı kıyasa
  ALINMAZ. Bu, üretilemeyen yeri sessizce uydurmak yerine kapsam dışı bırakmak
  demektir.

YAPIM EKLERİ (addan ada / addan fiile)
  -lIk  göz-lük · kitap-lık      -CI   göz-cü · kitap-çı
  -lI   göz-lü                   -sIz  göz-süz
  -sAl  kum-sal · biçim-sel      -lAş  güzel-leş
  -lA   taş-la · su-la
  Hepsi ünsüzle başladığı için gövdeyi bozmazlar; yumuşama, ünlü düşmesi ve
  ikizleşme bu eklerde İŞLEMEZ (kitap-lık, kitab-lık değil).
"""
import ses

# --- çatı ------------------------------------------------------------------
CATI = {
    "edilgen":  None,      # gövdeye göre seçilir
    "donuslu":  "(I)n",
    "istes":    "(I)ş",
    "ettirgen": None,      # gövdeye göre seçilir
}

# Ettirgende kurala uymayan tek heceli gövdeler. TDK'dan derlendi, açık liste.
ETTIRGEN_ISTISNA = {
    "iç": "ir", "kaç": "ır", "düş": "ür", "geç": "ir", "uç": "ur", "doy": "ur",
    "bit": "ir", "piş": "ir", "göç": "ür", "aş": "ır", "taş": "ır", "duy": "ur",
    "yat": "ır", "bat": "ır", "art": "ır", "sap": "ır",
    "ak": "ıt", "kork": "ut", "ürk": "üt", "sark": "ıt", "kalk": "ıt",
    "çık": "ar", "kop": "ar", "git": "er",
}

# --- yapım ekleri ----------------------------------------------------------
YAPIM = {
    "lik":  "lIk",    # göz -> gözlük
    "ci":   "CI",     # göz -> gözcü, kitap -> kitapçı
    "li":   "lI",     # göz -> gözlü
    "siz":  "sIz",    # göz -> gözsüz
    "sal":  "sAl",    # kum -> kumsal
    "les":  "lAş",    # güzel -> güzelleş
    "le":   "lA",     # taş -> taşla
}


def edilgen_ek(gv):
    """Ünlüyle biten gövde -n, -l ile biten -In, kalanı -Il alır.
    oku-n · al-ın · yaz-ıl.  Tek kural yazılırsa 'alıl' ya da 'okuul' çıkar."""
    if not gv:
        return "Il"
    if gv[-1] in ses.UNLULER:
        return "n"
    if gv[-1] == "l":
        return "(I)n"
    return "(I)l"


def ettirgen_ek(gv, uydurma=False):
    """Ettirgen ekini seçer. Döndürür: (şablon, güvenilir_mi).

    İlk sürümde tek heceli ünsüz-sonlu gerçek gövdelerin HEPSİ kapsam dışı
    bırakılmıştı. Yanlıştı: `yaz-dır`, `sev-dir`, `kes-tir` apaçık ve kuralın
    ta kendisi. Açık liste dışındakileri elemek, çoğunluğu atıp azınlığı
    kurtarmak oluyordu.

    Doğrusu: kuralı her zaman uygula, ama tek heceli GERÇEK gövde açık
    istisna listesinde değilse `güvenilir=False` döndür. O maddeler kıyasa
    doğrudan girmez; ayrı bir gözden geçirme kovasına düşer. Sessizce uydurmak
    da sessizce atmak da değil — işaretlemek.

    `uydurma=True` ise istisna hiç aranmaz: var olmayan gövdenin sözlüksel
    istisnası olamaz, kural tek başına geçerlidir ve sonuç her zaman güvenilir."""
    if not uydurma and gv in ETTIRGEN_ISTISNA:
        return ETTIRGEN_ISTISNA[gv], True
    if gv and (gv[-1] in ses.UNLULER or gv[-1] in "lr") and ses.hece_sayisi(gv) > 1:
        return "t", True
    tek_heceli_gercek = (not uydurma and ses.hece_sayisi(gv) <= 1
                         and bool(gv) and gv[-1] not in ses.UNLULER)
    return "DIr", not tek_heceli_gercek


def cati(govde, tur, uydurma=False, gozden_gecirmeye_izin=True):
    """Fiil gövdesine çatı eki ekler.

    `gozden_gecirmeye_izin=False` ile çağrılırsa ettirgende güvenilmeyen
    maddeler None döner — kıyas kurulurken bu kip kullanılır."""
    gv = govde
    if tur == "edilgen":
        sablon = edilgen_ek(gv)
    elif tur == "ettirgen":
        sablon, guvenilir = ettirgen_ek(gv, uydurma)
        if not guvenilir and not gozden_gecirmeye_izin:
            return None
    else:
        sablon = CATI[tur]
    return gv + ses.coz(sablon, gv)


def yapim(govde, tur):
    """Ada yapım eki ekler.

    Bu eklerin hepsi ünsüzle başlar; bu yüzden gövdeye DOKUNMAZLAR.
    kitap -> kitaplık (kitablık DEĞİL), burun -> burunlu (burnlu DEĞİL).
    Ad çekimindeki yumuşama/düşme/ikizleşme mantığı buraya taşınırsa hepsi bozulur."""
    return govde + ses.coz(YAPIM[tur], govde)
