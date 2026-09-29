"""TurkMorfBench altın cevap denetimi: her cevap kural tablosundan yeniden üretilir.

  python kural_denetimi.py turkmorfbench.json      ->  "512 / 512 tutuyor" beklenir

Kural tablosu (README'deki "Altın cevap kuralı" bölümünün kodu):
  - büyük ünlü uyumu: -ler/-lar, -de/-da, -den/-dan
  - küçük ünlü uyumu: -i/-ı/-u/-ü (son ünlüye göre)
  - ünsüz benzeşmesi: f s t k ç ş h p sonrası -de -> -te, -den -> -ten
  - kaynaştırma: ünlüyle biten gövdede -y- (yönelme, belirtme), -s- (3sg), -m-/-miz- (1sg/1pl)
  - yumuşama: ünlüyle başlayan ek önünde
      gerçek gövde -> YUMUSAYAN sözlüğünden (sözlüksel; kıyas yalnızca tartışmasız
                      gövdeleri içerir), diğer gerçek gövdeler değişmez
      uydurma gövde -> çok heceli ve p/ç/t/k ile bitiyorsa b/c/d/ğ (belgelenen varsayım)

Bu betik kıyasın kendisini denetler, modeli değil. Kıyasa madde eklenirse
önce bu denetimden geçmelidir.
"""
import json, sys

ARKA, ON = "aıou", "eiöü"
SERT = "fstkçşhp"
# Kıyastaki gerçek gövdelerden ünlü-ilk ek önünde yumuşayanlar (sözlüksel).
YUMUSAYAN = {"çocuk": "çocuğ", "balık": "balığ", "ekmek": "ekmeğ", "yaprak": "yaprağ",
             "kitap": "kitab", "ağaç": "ağac", "çiçek": "çiçeğ", "köpek": "köpeğ",
             "bardak": "bardağ", "toprak": "toprağ", "yatak": "yatağ", "sokak": "sokağ",
             "durak": "durağ"}
YUMUSAK = {"p": "b", "ç": "c", "t": "d", "k": "ğ"}


def son_unlu(k):
    for ch in reversed(k):
        if ch in ARKA + ON:
            return ch
    raise ValueError("ünlüsüz gövde: %s" % k)


def dortlu(k):
    return {"a": "ı", "ı": "ı", "o": "u", "u": "u", "e": "i", "i": "i", "ö": "ü", "ü": "ü"}[son_unlu(k)]


def ikili(k):
    return "a" if son_unlu(k) in ARKA else "e"


def unlu_biter(k):
    return k[-1] in ARKA + ON


def hece(k):
    return sum(ch in ARKA + ON for ch in k)


def unlu_ek_govdesi(k, tip):
    if tip == "gercek":
        return YUMUSAYAN.get(k, k)
    if k[-1] in YUMUSAK and hece(k) >= 2:            # uydurma: belgelenen varsayım
        return k[:-1] + YUMUSAK[k[-1]]
    return k


def uret(k, gorev, tip):
    v, a = dortlu(k), ikili(k)
    g = unlu_ek_govdesi(k, tip)
    d = "t" if k[-1] in SERT else "d"
    if gorev == "cogul":        return k + "l" + a + "r"
    if gorev == "hal_bulunma":  return k + d + a
    if gorev == "hal_ayrilma":  return k + d + a + "n"
    if gorev == "hal_yonelme":  return k + "y" + a if unlu_biter(k) else g + a
    if gorev == "hal_belirtme": return k + "y" + v if unlu_biter(k) else g + v
    if gorev == "iyelik_3sg":   return k + "s" + v if unlu_biter(k) else g + v
    if gorev == "iyelik_1sg":   return k + "m" if unlu_biter(k) else g + v + "m"
    if gorev == "iyelik_1pl":   return k + "m" + v + "z" if unlu_biter(k) else g + v + "m" + v + "z"
    raise ValueError("bilinmeyen görev: %s" % gorev)


def main(yol):
    d = json.load(open(yol, encoding="utf-8"))
    yanlis = []
    for e in d:
        b = uret(e["kok"], e["gorev"], e["tip"])
        if b != e["cevap"]:
            yanlis.append((e["tip"], e["kok"], e["gorev"], e["cevap"], b))
    for y in yanlis:
        print("  UYUŞMUYOR %-6s %-8s %-13s altın=%-14s kural=%s" % y)
    print("%d / %d tutuyor" % (len(d) - len(yanlis), len(d)))
    sys.exit(1 if yanlis else 0)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "turkmorfbench.json")
