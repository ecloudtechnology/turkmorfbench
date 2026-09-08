"""TurkMorfBench değerlendirme betiği — herhangi bir Hugging Face nedensel dil modeli.

İki kip:
  zorunlu  : altın cevap + sesbilimsel çeldiriciler arasından log-olasılığı en yüksek
             olan seçilir (öğretmen zorlamalı, uzunluğa bölünmüş). Biçim uyumundan
             bağımsız, yalnızca bilgi.
  uretim   : model soruya serbest cevap üretir, normalize edilmiş tam eşleşme.
             Bilgi + biçime uyma. (Sohbet şablonu varsa kullanılır; yoksa düz istem.)

Kullanım:
  python turkmorfbench_olc.py --model Qwen/Qwen3-32B --kip zorunlu
  python turkmorfbench_olc.py --model Qwen/Qwen3-32B --kip uretim --dusunme-kapali

Çıktı JSON'da madde bazlı 0/1 vektörü bulunur; iki modeli aynı maddelerde
karşılaştırmak için bootstrap.py kullanın.
"""
import argparse, itertools, json, re, sys, time
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

IKILI, DORTLU = "ae", "ıiuü"
# Az-örnekli gövdeler KIYASIN DIŞINDAN seçilmiştir (kıyas gövdeleriyle çakışmaz).
ORNEK = [("'tahta' kelimesinin çoğulu nedir?", "tahtalar"),
         ("'sepet' kelimesine -de/-da bulunma eki ekle.", "sepette"),
         ("'sandalye' kelimesini 'onun (3. tekil) ...' iyelik ekiyle çek.", "sandalyesi"),
         ("'kabak' kelimesini 'benim (1. tekil) ...' iyelik ekiyle çek.", "kabağım")]
ONEK = "".join("Soru: %s\nCevap: %s\n\n" % (s, c) for s, c in ORNEK)


def celdiriciler(kok, altin, en_cok=7):
    """Altın cevabın ek kısmını bulup ünlü uyumu / ünsüz benzeşmesi / yumuşama varyantları üret."""
    i = 0
    while i < min(len(kok), len(altin)) and kok[i] == altin[i]:
        i += 1
    govde, ek = altin[:i], altin[i:]
    if not ek:
        return []
    yerler = [(j, ch) for j, ch in enumerate(ek) if ch in IKILI + DORTLU]
    if not yerler:
        return []
    secenekler = [list(IKILI if ch in IKILI else DORTLU) for _, ch in yerler]
    adaylar = set()
    for kombo in itertools.product(*secenekler):
        y = list(ek)
        for (j, _), v in zip(yerler, kombo):
            y[j] = v
        adaylar.add(govde + "".join(y))
    for a in list(adaylar):                          # benzeşme: d <-> t
        e = a[len(govde):]
        if e and e[0] in "dt":
            adaylar.add(govde + ("t" if e[0] == "d" else "d") + e[1:])
    if i < len(kok) and i < len(altin) and kok[i] != altin[i]:   # yumuşamamış hâl
        adaylar.add(kok[:i + 1] + altin[i + 1:])
    adaylar.discard(altin)
    return sorted(adaylar)[:en_cok]


def temizle(s):
    return re.sub(r"[.,!?;:\"'()\[\]*`]", "", s.strip().lower())


def zorunlu(model, tok, data):
    items = []
    for x in data:
        cel = celdiriciler(x["kok"], x["cevap"])
        if cel:
            items.append((x, [x["cevap"]] + cel))
    print("zorunlu seçim uygulanabilen madde: %d / %d" % (len(items), len(data)), flush=True)
    vec, tipler = [], []
    with torch.no_grad():
        for x, adaylar in items:
            soru = x["soru"].replace(" Sadece kelimeyi yaz.", "")
            p_ids = tok(ONEK + "Soru: %s\nCevap:" % soru, return_tensors="pt").input_ids.to(model.device)
            en_iyi, en_skor = None, -1e9
            for a in adaylar:
                a_ids = tok(" " + a, add_special_tokens=False, return_tensors="pt").input_ids.to(model.device)
                ids = torch.cat([p_ids, a_ids], dim=1)
                lp = torch.log_softmax(model(ids).logits[0, :-1].float(), dim=-1)
                n = a_ids.shape[1]
                s = float(lp[-n:].gather(1, ids[0, 1:][-n:].unsqueeze(1)).sum()) / n
                if s > en_skor:
                    en_skor, en_iyi = s, a
            vec.append(int(en_iyi == x["cevap"])); tipler.append(x["tip"])
    return vec, tipler


def uretim(model, tok, data, yigin, maks_yeni, dusunme_kapali):
    tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    istemler = []
    for x in data:
        soru = x["soru"] + (" /no_think" if dusunme_kapali else "")
        if getattr(tok, "chat_template", None):
            istemler.append(tok.apply_chat_template([{"role": "user", "content": soru}],
                                                    tokenize=False, add_generation_prompt=True))
        else:
            istemler.append(ONEK + "Soru: %s\nCevap:" % x["soru"])
    vec, tipler, kesik = [], [], 0
    with torch.no_grad():
        for b in range(0, len(data), yigin):
            enc = tok(istemler[b:b + yigin], return_tensors="pt", padding=True,
                      add_special_tokens=False).to(model.device)
            out = model.generate(**enc, max_new_tokens=maks_yeni, do_sample=False,
                                 pad_token_id=tok.pad_token_id)
            for j, x in enumerate(data[b:b + yigin]):
                r = tok.decode(out[j][enc.input_ids.shape[1]:], skip_special_tokens=True)
                if "</think>" in r:
                    r = r.split("</think>", 1)[1]
                elif "<think>" in r:
                    kesik += 1; r = ""                      # düşünme bloğu bitmedi
                ilk = temizle(r).split("\n")[0].strip()
                vec.append(int(ilk == temizle(x["cevap"]) or temizle(r) == temizle(x["cevap"])))
                tipler.append(x["tip"])
            print("  %d / %d" % (min(b + yigin, len(data)), len(data)), flush=True)
    print("kesik (cevapsız) üretim: %d" % kesik, flush=True)
    return vec, tipler


def ozet(vec, tipler):
    def oran(t):
        v = [a for a, b in zip(vec, tipler) if t is None or b == t]
        return 100.0 * sum(v) / max(len(v), 1), len(v)
    return {"toplam": oran(None), "gercek": oran("gercek"), "wug": oran("wug")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--kip", choices=["zorunlu", "uretim"], default="zorunlu")
    ap.add_argument("--bench", default="turkmorfbench.json")
    ap.add_argument("--out", default=None)
    ap.add_argument("--yigin", type=int, default=16)
    ap.add_argument("--maks-yeni", type=int, default=64)
    ap.add_argument("--dusunme-kapali", action="store_true",
                    help="Qwen3 gibi hibrit düşünen modellerde /no_think ekle")
    ap.add_argument("--dtype", default="bfloat16")
    a = ap.parse_args()
    data = json.load(open(a.bench, encoding="utf-8"))
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, torch_dtype=getattr(torch, a.dtype),
                                                 device_map="auto").eval()
    if a.kip == "zorunlu":
        vec, tipler = zorunlu(model, tok, data)
    else:
        vec, tipler = uretim(model, tok, data, a.yigin, a.maks_yeni, a.dusunme_kapali)
    oz = ozet(vec, tipler)
    print("\n%s | %s" % (a.model, a.kip))
    for k in ("toplam", "gercek", "wug"):
        print("  %-7s %%%.2f  (n=%d)" % (k, oz[k][0], oz[k][1]))
    out = a.out or "sonuc_%s_%s.json" % (re.sub(r"[^A-Za-z0-9]+", "_", a.model), a.kip)
    json.dump({"model": a.model, "kip": a.kip, "bench": a.bench, "ozet": oz,
               "vec": vec, "tip": tipler, "sure_sn": round(time.time() - t0)},
              open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("-> %s" % out)


if __name__ == "__main__":
    main()
