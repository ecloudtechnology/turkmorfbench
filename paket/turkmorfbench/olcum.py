"""Ölçüm — iki kip, iki arka uç.

İKİ KİP
  zorunlu seçim (birincil)  altın ile kural-ihlali çeldiricileri arasından
                            log-olasılıkla seçtirilir; AYRIŞTIRMA YOKTUR
  serbest üretim (ikincil)  model biçimi kendisi yazar; cevabı okumak ayrı
                            bir iş ve `oku` modülü onu yapar

  Neden birincisi birincil: serbest üretimde modelin cevabını okumak kırılgan.
  Bir ölçümde model doğru cevabı veriyor ama önüne "??" yazdığı için elli
  puan kaybetmişti. Zorunlu seçimde bu hata sınıfı yoktur.

İKİ ARKA UÇ
  yerel   transformers ile ağırlıklar (tam logit erişimi)
  uzak    OpenAI uyumlu /v1/completions ucu (echo + logprobs)

PUANLAMA KURALI — 3.3.0'da DEĞİŞTİ
  Aday, log P(aday | istem) toplamının ADAYIN KARAKTER SAYISINA bölünmesiyle
  puanlanır. Ortak istem öneki puana GİRMEZ.

  Önceki sürümler tüm dizginin (istem + aday) ortalama log-olasılığını
  alıyordu. Önek her adayda aynı ama jeton sayıları farklı; ortalama
  alınınca o sabit önek adaylar arasında farklı ağırlıklarla dağılıyor ve
  adaylar arasındaki gerçek fark eziliyordu. Ölçtük: bir maddede aday
  toplamları −17,2 ile −25,6 arasında ayrışırken eski kural hepsini −5,1
  ile −5,4 arasına sıkıştırıp yanlış adayı 0,08 farkla seçiyordu.

  Beş kural dört modelde karşılaştırıldı. Ölçüt "en yüksek doğruluk" DEĞİL
  — kuralı doğruluğa göre seçmek, ölçeği ölçülen şeye göre ayarlamaktır.
  Ölçüt uzunluk yanlılığıydı: çeldiricilerin bir kısmı altından kısa (eksik
  ek), bir kısmı uzun. Adayların uzunluğu farklı olan maddelerde altın
  %29,9 oranında en kısadır; yansız bir kural da o civarda en kısayı
  seçmeli. Ölçülen (cosmos-llama8b-it / kumru-2b):

      tam_ort      %47,2 / %47,7      (eski kural)
      aday_top     %51,0 / %57,0      ham toplam: kısayı kayırıyor
      aday_jeton   %47,5 / %48,7      jetona bölme
      aday_harf    %39,4 / %43,2      KARAKTERE bölme  <- seçilen
      pmi          %39,2 / %45,0      koşulsuzla normalleştirme

  Karaktere bölmenin ikinci ve bağımsız gerekçesi: JETONLAYICIDAN BAĞIMSIZ
  olması. Farklı sözlüklü modeller karşılaştırılırken jeton sayısına bölen
  bir ölçü, kelimeyi kaç parçaya böldüklerine göre modelleri farklı
  cezalandırır; karakter sayısı böyle bir yanlılık taşımaz.

  Kalan yanlılık gizlenmiyor: %39-43, hedef %29,9. Uzunluk etkisi azaldı
  ama sıfırlanmadı.
"""
import json
import math
import urllib.error
import urllib.request

ISTEM = "Kelime: %s\nÇekimli biçim: %s"


# --------------------------------------------------------------- yerel ----

class Yerel:
    """transformers ile yerel ağırlıklar."""

    onerilen_isci = 1      # tek GPU: paralellik hız kazandırmaz

    def __init__(self, model_yolu, dtype="bfloat16"):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.torch = torch
        self.tok = AutoTokenizer.from_pretrained(model_yolu)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_yolu, torch_dtype=getattr(torch, dtype), device_map="auto").eval()

    def jetonla(self, s):
        return self.tok.tokenize(s)

    def olasilik(self, istem, aday):
        """log P(aday | istem) — yalnız aday jetonları, karaktere bölünmüş."""
        t = self.torch
        with t.no_grad():
            onek_ids = self.tok(istem, add_special_tokens=True).input_ids
            ids = self.tok(istem + aday, return_tensors="pt").input_ids.to(self.model.device)
            if ids.shape[1] < 2:
                return -1e9
            # SINIR: istem tek başına ve istem+aday ayrı ayrı jetonlanır; BPE birleşimi
            # sınırda jetonu DEĞİŞTİREBİLİR (istem ": " ile biter, "Ġ" + "kal" → "Ġkal").
            # Aday jetonları, iki dizinin ORTAK ÖNEKİ bittiği yerden başlar: sınırı
            # aşan jeton adaya SAYILIR (3.7.0; önce dışarıda kalıyordu — bkz. CHANGELOG).
            ortak = self._ortak_onek(onek_ids, ids[0].tolist())
            lp = self.model(ids).logits[0, :-1].log_softmax(-1)
            tek = lp.gather(-1, ids[0, 1:].unsqueeze(-1)).squeeze(-1)
            bas = max(0, ortak - 1)
            aday_jeton = tek[bas:] if tek[bas:].numel() else tek[-1:]
            return float(aday_jeton.sum()) / max(1, len(aday))

    @staticmethod
    def _ortak_onek(a, b):
        n = 0
        while n < min(len(a), len(b)) and a[n] == b[n]:
            n += 1
        return n

    def uret(self, istem, en_fazla=20):
        t = self.torch
        with t.no_grad():
            ids = self.tok(istem, return_tensors="pt").input_ids.to(self.model.device)
            u = self.model.generate(ids, max_new_tokens=en_fazla, do_sample=False,
                                    pad_token_id=self.tok.eos_token_id)
            return self.tok.decode(u[0][ids.shape[1]:], skip_special_tokens=True)


# ---------------------------------------------------------------- uzak ----

class Uzak:
    """OpenAI uyumlu /v1/completions ucu.

    `echo=True` + `logprobs` ile istemin her jetonunun log-olasılığı okunur;
    bu, yerel logit karşılaştırmasının aynısıdır. Uç `echo` desteklemiyorsa
    ölçüm YAPILMAZ — sessizce üretim kipine düşmek, iki farklı şeyi aynı
    sayı diye raporlamak olur.
    """

    onerilen_isci = 8      # uzak uç ağ bağımlı: paralellik doğrudan hız

    def __init__(self, uc, model, anahtar=None):
        self.uc = uc.rstrip("/") + "/completions" if not uc.endswith("completions") else uc
        self.model = model
        self.anahtar = anahtar
        self._echo_var = None

    def _cagir(self, govde, deneme=4):
        for d in range(deneme):
            try:
                b = {"Content-Type": "application/json"}
                if self.anahtar:
                    b["Authorization"] = "Bearer " + self.anahtar
                r = urllib.request.Request(self.uc, json.dumps(govde).encode(), b)
                with urllib.request.urlopen(r, timeout=90) as y:
                    return json.load(y)["choices"][0]
            except urllib.error.HTTPError as e:
                if e.code in (429, 503) and d < deneme - 1:
                    import time
                    time.sleep(2 ** d)
                    continue
                raise
            except Exception:
                if d == deneme - 1:
                    raise
                import time
                time.sleep(1 + d)

    def echo_destegi(self):
        if self._echo_var is None:
            try:
                c = self._cagir({"model": self.model, "prompt": "deneme",
                                 "max_tokens": 0, "echo": True, "logprobs": 0,
                                 "temperature": 0})
                g = c.get("logprobs") or {}
                lp = g.get("token_logprobs")
                if lp and not g.get("text_offset"):
                    # text_offset yoksa aday jetonları ayrılamaz; sessizce
                    # farklı bir şey ölçmektense ölçmemek doğrusu.
                    raise RuntimeError("uç `text_offset` döndürmüyor; "
                                       "zorunlu seçim bu uçla ölçülemez")
                self._echo_var = bool(lp)
            except Exception:
                self._echo_var = False
        return self._echo_var

    def olasilik(self, istem, aday):
        """log P(aday | istem), karaktere bölünmüş.

        `text_offset` her jetonun istem metnindeki başlangıcını verir. Aday
        jetonları, metin sınırını (len(istem)) AŞAN ilk jetondan başlar: sınırın
        üstüne oturan jeton (istem ": " ile biter, jeton "Ġkal" boşluğu da alır)
        adaya SAYILIR — yerel arka uçla aynı kural (3.7.0). Bu alan olmadan aday
        jetonları ayrılamaz ve ölçüm yerel arka uçla aynı şeyi ölçmez."""
        c = self._cagir({"model": self.model, "prompt": istem + aday, "max_tokens": 0,
                         "echo": True, "logprobs": 0, "temperature": 0})
        g = c.get("logprobs") or {}
        lp = g.get("token_logprobs") or []
        off = g.get("text_offset") or []
        if not lp:
            return -1e9
        if off and len(off) == len(lp):
            son = list(off[1:]) + [len(istem) + len(aday)]      # her jetonun bitişi
            secili = [x for x, b in zip(lp, son) if x is not None and b > len(istem)]
        else:
            secili = [x for x in lp if x is not None]
        if not secili:
            secili = [x for x in lp if x is not None][-1:]
        return sum(secili) / max(1, len(aday))

    def uret(self, istem, en_fazla=20):
        c = self._cagir({"model": self.model, "prompt": istem,
                         "max_tokens": en_fazla, "temperature": 0})
        return c.get("text") or ""


# -------------------------------------------------------------- ölçüm -----

def _tek_madde(arka, m):
    adaylar = [("altin", m["altin"])] + list(m["celdirici"].items())
    onek = ISTEM % (m["govde"], "")
    puan = [(ad, arka.olasilik(onek, b)) for ad, b in adaylar]
    sec = max(puan, key=lambda x: x[1])[0]
    return m["kimlik"], (sec == "altin", None if sec == "altin" else sec)


def secim_olc(arka, maddeler, ilerleme=None, isci=None):
    """Zorunlu seçim. Döndürür: {kimlik: (dogru_mu, secilen_celdirici)}

    Uzak uçta PARALEL koşar. Sıralı koşumda 2.000 maddelik çekirdek katman
    madde başına dört çağrıyla saatler sürüyordu; kimse beklemez ve kıyas
    kullanılmaz. Yerel modelde paralellik anlamsız (tek GPU sırayla çalışır),
    orada tek iş parçacığı kalır.
    """
    if isci is None:
        isci = getattr(arka, "onerilen_isci", 1)
    if isci <= 1:
        cik = {}
        for i, m in enumerate(maddeler):
            k, v = _tek_madde(arka, m)
            cik[k] = v
            if ilerleme and (i + 1) % 100 == 0:
                ilerleme(i + 1, len(maddeler))
        return cik

    from concurrent.futures import ThreadPoolExecutor
    cik, bitti = {}, [0]
    with ThreadPoolExecutor(max_workers=isci) as havuz:
        for k, v in havuz.map(lambda m: _tek_madde(arka, m), maddeler):
            cik[k] = v
            bitti[0] += 1
            if ilerleme and bitti[0] % 100 == 0:
                ilerleme(bitti[0], len(maddeler))
    return cik


URETIM_ORNEK = (
    "Aşağıdaki kelimelerin istenen çekimli biçimini yaz. Yalnız biçimi yaz.\n\n"
    "Kelime: kapı\nÇekimli biçim: kapıyı\n\n"
    "Kelime: ev\nÇekimli biçim: evi\n\n"
    "Kelime: kitap\nÇekimli biçim: kitabı\n\n"
    "Kelime: kuş\nÇekimli biçim: kuşu\n\n")


def uretim_olc(arka, maddeler, oku_modul, ilerleme=None, isci=None):
    """Serbest üretim. Döndürür: {kimlik: (okundu_mu, dogru_mu)}"""
    if isci is None:
        isci = getattr(arka, "onerilen_isci", 1)

    def tek(m):
        ham = arka.uret(URETIM_ORNEK + "Kelime: %s\nÇekimli biçim:" % m["govde"])
        return m["kimlik"], oku_modul.dogru_mu(ham, m["govde"], m["altin"])

    if isci <= 1:
        cik = {}
        for i, m in enumerate(maddeler):
            k, v = tek(m)
            cik[k] = v
            if ilerleme and (i + 1) % 100 == 0:
                ilerleme(i + 1, len(maddeler))
        return cik

    from concurrent.futures import ThreadPoolExecutor
    cik, bitti = {}, [0]
    with ThreadPoolExecutor(max_workers=isci) as havuz:
        for k, v in havuz.map(tek, maddeler):
            cik[k] = v
            bitti[0] += 1
            if ilerleme and bitti[0] % 100 == 0:
                ilerleme(bitti[0], len(maddeler))
    return cik
