"""Sayıları Türkçe okunuşa çevirir — sayı ekleri için zorunlu.

NEDEN GEREKLİ
  Sayıya gelen ek, sayının YAZILIŞINA değil OKUNUŞUNA uyar:
    2026'da   çünkü "iki bin yirmi altı" -> son ünlü ı -> -da
    1'e       çünkü "bir"                -> son ünlü i -> -e
    100'ü     çünkü "yüz"                -> son ünlü ü -> -ü
    6'yı      çünkü "altı"               -> son ünlü ı -> -yı (ünlüyle biter!)
  Yazılışa bakan bir model "2026'de" ya da "6'ı" üretir. Bu, kıyasın en
  ayırt edici kovalarından biri: kural basit ama okunuşu bilmeyi gerektiriyor.

  Son ünlünün yanında son SESİN ünlü mü ünsüz mü olduğu da gerekiyor
  (altı -> 6'yı, kaynaştırma var; yüz -> 100'ü, yok).
"""

BIRLER = ["", "bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz"]
ONLAR = ["", "on", "yirmi", "otuz", "kırk", "elli", "altmış", "yetmiş", "seksen", "doksan"]
BASAMAK = ["", "bin", "milyon", "milyar", "trilyon", "katrilyon"]


def _uc_basamak(n):
    """0-999 arası bir sayının okunuşu."""
    p = []
    y, k = divmod(n, 100)
    if y:
        # "bir yüz" denmez, "yüz" denir
        p.append(BIRLER[y] if y > 1 else "")
        p.append("yüz")
    o, b = divmod(k, 10)
    if o:
        p.append(ONLAR[o])
    if b:
        p.append(BIRLER[b])
    return " ".join(x for x in p if x)


def oku(n):
    """Tam sayının Türkçe okunuşu. 0 -> 'sıfır'."""
    if n == 0:
        return "sıfır"
    if n < 0:
        return "eksi " + oku(-n)
    parcalar, i = [], 0
    while n > 0:
        n, k = divmod(n, 1000)
        if k:
            s = _uc_basamak(k)
            if BASAMAK[i]:
                # "bir bin" denmez, "bin" denir; "iki bin" denir
                s = (s + " " if not (i == 1 and k == 1) else "") + BASAMAK[i]
            parcalar.insert(0, s.strip())
        i += 1
    return " ".join(parcalar)
