"""Tokenizer kırılımı — model geliştiricinin asıl sorusuna cevap veren eksen.

NEDEN BU EKSEN VAR
  Bir kıyasın model geliştiriciye söyleyebileceği en yararlı şey "%43 aldın"
  değil, "sözlüğün Türkçe morfolojiyi bozuyor ve tam orada düşüyorsun".
  2026'da Türkçe alt-kelime stratejisi üzerine en az iki çalışma çıktı
  (arXiv 2602.06942, 2606.18717); alanın sorduğu soru bu. Başarıyı gövdenin
  nasıl parçalandığına göre koşullu raporlayan başka kıyas yok.

ÖLÇÜLEN DÖRT ŞEY
  govde_jeton    çıplak gövde kaç jetona bölünüyor
  bicim_jeton    çekimli biçim kaç jetona bölünüyor
  sinir_korundu  gövde/ek sınırında bir jeton sınırı VAR mı
                 kitap|ı  -> korundu     ·  kit|abı -> korunmadı
  govde_bozuldu  çekimli biçimde gövdenin kendi parçalanışı korunuyor mu
                 "kitap" tek jetonken "kitabı" -> "kit|abı" ise gövde BOZULDU

  Sonuncusu en ayırt edicisi. Türkçede ek, gövdenin son sesini değiştirir
  (yumuşama, ünlü düşmesi); BPE sözlüğü bunu görmediği için çekimli biçim
  bambaşka parçalanabiliyor. O zaman model gövdeyi "aynı kelime" olarak
  tanıyamaz ve kuralı uygulayacağı nesne kaybolur.

KULLANIM
  Herhangi bir jetonlayıcı ile çalışır; tek gereken, metni jeton dizgelerine
  çeviren bir işlev:
      from transformers import AutoTokenizer
      tok = AutoTokenizer.from_pretrained(...)
      jetonla = lambda s: tok.tokenize(s)
  HF, tiktoken, sentencepiece — hepsi bu arayüze uyar.
"""
import collections
import unicodedata


def _sade(j):
    """Jeton dizgesini karşılaştırılabilir hâle getirir.

    Farklı jetonlayıcılar söz başı boşluğu farklı işaretliyor: GPT-2 tarzı
    'Ġ', SentencePiece '▁'. İkisi de atılır; aksi hâlde aynı parçalanış
    farklı jetonlayıcılarda farklı görünür ve kıyaslanamaz.
    """
    return j.replace("Ġ", "").replace("▁", "").replace("##", "")


def _birlesik(jetonlar):
    return "".join(_sade(j) for j in jetonlar)


def sinir_var_mi(jetonlar, uzunluk):
    """`uzunluk` karakterinde bir jeton sınırı var mı?"""
    n = 0
    for j in jetonlar:
        n += len(_sade(j))
        if n == uzunluk:
            return True
        if n > uzunluk:
            return False
    return False


def coz(jetonla, govde, bicim):
    """Tek bir madde için tokenizer öznitelikleri."""
    gj = jetonla(govde)
    bj = jetonla(bicim)

    # gövde/ek sınırı: çekimli biçimde gövdenin (belki değişmiş) kısmı nerede
    # bitiyor? Ortak öneki bul — yumuşama son harfi değiştirdiği için gövdenin
    # tamamı korunmayabilir.
    ortak = 0
    for a, b in zip(govde, bicim):
        if a != b:
            break
        ortak += 1

    return {
        "govde_jeton": len(gj),
        "bicim_jeton": len(bj),
        "jeton_artisi": len(bj) - len(gj),
        "sinir_korundu": sinir_var_mi(bj, ortak) if ortak else False,
        "govde_bozuldu": not _birlesik(bj).startswith(_birlesik(gj)),
        "ortak_onek": ortak,
        "govde_jetonlari": [_sade(j) for j in gj],
        "bicim_jetonlari": [_sade(j) for j in bj],
    }


def rapor(maddeler, jetonla, dogru_mu):
    """Tokenizer kırılımlı teşhis raporu.

    `dogru_mu` madde kimliğinden bool'a bir eşleme (ölçüm sonucu).
    Döndürür: her kesit için (doğru, toplam, oran).
    """
    kesit = collections.defaultdict(lambda: [0, 0])

    def ekle(ad, d):
        kesit[ad][1] += 1
        kesit[ad][0] += int(d)

    for m in maddeler:
        k = m.get("kimlik")
        if k not in dogru_mu:
            continue
        d = dogru_mu[k]
        o = coz(jetonla, m["govde"], m["altin"])

        ekle("gövde %d jeton" % min(o["govde_jeton"], 5), d)
        ekle("biçim %d jeton" % min(o["bicim_jeton"], 6), d)
        ekle("sınır korundu" if o["sinir_korundu"] else "sınır KORUNMADI", d)
        ekle("gövde bozulmadı" if not o["govde_bozuldu"] else "gövde BOZULDU", d)
        ekle("toplam", d)

    return {ad: (d, t, d / t if t else 0.0) for ad, (d, t) in kesit.items()}


def yazdir(r):
    sira = ["toplam", "sınır korundu", "sınır KORUNMADI",
            "gövde bozulmadı", "gövde BOZULDU"]
    sira += sorted(k for k in r if k.startswith("gövde ") and "jeton" in k)
    sira += sorted(k for k in r if k.startswith("biçim "))
    print("%-22s %8s %8s %8s" % ("kesit", "doğru", "toplam", "oran"))
    for k in sira:
        if k not in r:
            continue
        d, t, o = r[k]
        print("%-22s %8d %8d   %%%.1f" % (k, d, t, 100 * o))
