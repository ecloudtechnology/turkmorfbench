# 3.7.0 sinir kurali: eski (ilk aday jetonu disarida) vs yeni (ortak onekten itibaren) — GPU'da hizli sinama
import json, torch
from turkmorfbench import olcum, __version__
print("kurulu surum:", __version__)
m = json.load(open("/ari/users/ytanis/turkmorfbench_v3_cekirdek_3.6.json")); m = m["maddeler"] if isinstance(m, dict) else m
for ad, yol in (("Erk-14B", "/ari/users/ytanis/erk14b-gguf-kaynak"), ("kanarya-2b", "/ari/users/ytanis/tablo/kanarya-2b")):
    arka = olcum.Yerel(yol)
    def eski(istem, aday):
        with torch.no_grad():
            n_onek = len(arka.tok(istem, add_special_tokens=True).input_ids)
            ids = arka.tok(istem + aday, return_tensors="pt").input_ids.to(arka.model.device)
            lp = arka.model(ids).logits[0, :-1].log_softmax(-1); tek = lp.gather(-1, ids[0, 1:].unsqueeze(-1)).squeeze(-1)
            bas = max(0, n_onek - 1); aj = tek[bas:] if tek[bas:].numel() else tek[-1:]
            return float(aj.sum()) / max(1, len(aday)), int(aj.numel())
    farkli = de = dy = 0; N = 300
    for x in m[:N]:
        onek = olcum.ISTEM % (x["govde"], "")
        e = {a: eski(onek, a) for a in x["secenek"]}; y = {a: arka.olasilik(onek, a) for a in x["secenek"]}
        se = max(e, key=lambda a: e[a][0]); sy = max(y, key=y.get)
        farkli += se != sy; de += se == x["altin"]; dy += sy == x["altin"]
        if x is m[0]: print("  ornek", x["govde"], {a: (round(e[a][0], 3), e[a][1], round(y[a], 3)) for a in x["secenek"]})
    print("%s: %d maddede secim degisen %d · dogru eski %d / yeni %d" % (ad, N, farkli, de, dy), flush=True)
    del arka; torch.cuda.empty_cache()
