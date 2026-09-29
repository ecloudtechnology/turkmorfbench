"""Modelin serbest üretimdeki cevabını okumak — kıyasın yarısı budur.

NEDEN AYRI MODÜL
  Ölçümde dört kez yanlış sayı ürettik ve dördünde de hata modelde değil
  okumadaydı. Sonuncusu en öğreticisi: Qwen3-32B çoğul ekinde %4 aldı; oysa
  ham çıktısı şuydu —

      " ??\\nKelime: zakak\\nSonuc: zakaklar\\n\\nAçıklama: ..."

  Model DOĞRU cevabı veriyor. Ayrıştırıcı körü körüne ilk satırı aldığı için
  "??" okudu. Aynı koşumda doğrudan cevap veren Erk-32B etkilenmedi ve arada
  elli puanlık hayali bir fark oluştu.

  Bu yüzden okuma, kıyasın bir parçası olarak ayrı yazılıyor ve sınanıyor.
  Kıyası kullanan kimse kendi ayrıştırıcısını yazmak zorunda kalmasın.

KURAL
  İlk satır alınmaz. Çıktıdaki kelimeler taranır ve GÖVDEYLE UYUMLU ilk kelime
  seçilir. Gövdeyle uyumlu olmak, gövdenin ilk harfleriyle başlamak demektir —
  yumuşama son ünsüzü değiştirebilir ama baş tarafı değişmez (kitap -> kitabı,
  ilk üç harf sabit). Bu ölçüt dolgu metni, açıklamayı ve soru tekrarını eler.
"""
import re

# Model çıktısında sık görülen dolgu ve etiketler
GURULTU = re.compile(r"^(sonuç|sonuc|cevap|answer|kelime|word|\?+|-+|\.+|:+)$", re.I)


def _kelimeler(metin):
    """Noktalama ve etiketlerden arındırılmış kelime akışı."""
    for h in re.split(r"[\s\n]+", metin or ""):
        h = h.strip().strip('.,;:!?"\'()[]{}«»“”‘’')
        if h:
            yield h


def _on_ek(govde, n=3):
    """Gövdenin değişmeyen baş parçası. Yumuşama son ünsüzü değiştirir, baş
    tarafı değil. Çok kısa gövdelerde gövdenin tamamı eksi son harf alınır."""
    if len(govde) <= 2:
        return govde[:1]
    return govde[:max(1, min(n, len(govde) - 1))]


def cevap_bul(ham, govde, ek_bekleniyor=True):
    """Ham üretimden gövdeye ait ilk biçimi çıkarır. Bulamazsa None.

    `ek_bekleniyor` doğruysa ÇIPLAK GÖVDENİN KENDİSİ cevap sayılmaz. Gerekçesi
    ölçümden geldi: model soruyu tekrarlıyor —

        " ??\nKelime: zakak\nSonuc: zakaklar"

    ve "zakak" da gövde önekiyle başladığı için ilk eşleşme o oluyordu. Oysa ek
    isteyen bir görevde gövdenin kendisi bir cevap değil, sorunun yankısıdır.
    Yalın hâl gibi ek almayan görevlerde bayrak kapatılır.

    None dönmesi 'model yanlış cevap verdi' demek DEĞİLDİR; 'cevap okunamadı'
    demektir ve ölçümde ayrı sayılmalıdır. İkisini karıştırmak, okunamayan
    cevapları yanlış saymak ve modeli olduğundan kötü göstermek olur.
    """
    if not ham:
        return None
    on = _on_ek(govde).lower()
    g = govde.lower()
    yedek = None
    for h in _kelimeler(ham):
        if GURULTU.match(h):
            continue
        if not h.lower().startswith(on):
            continue
        if ek_bekleniyor and h.lower() == g:
            yedek = yedek or h          # başka aday çıkmazsa diye tutulur
            continue
        return h
    return yedek if not ek_bekleniyor else None


def dogru_mu(ham, govde, altin):
    """(okundu_mu, dogru_mu) döndürür — iki ayrı bilgi, tek sayıya ezilmez."""
    c = cevap_bul(ham, govde)
    if c is None:
        return False, False
    return True, c.lower() == altin.lower()
