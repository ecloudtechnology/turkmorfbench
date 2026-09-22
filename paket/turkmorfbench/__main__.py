# -*- coding: utf-8 -*-
"""turkmorfbench — komut satırı.

    turkmorfbench olc --model ecloudtech/Erk-32B
    turkmorfbench olc --uc http://localhost:8000/v1 --model erk --katman tam
    turkmorfbench bilgi
"""
import argparse
import json
import sys

from . import __version__
from . import veri, olcum, rapor, oku


def _ilerleme(i, n):
    print("  %d/%d" % (i, n), file=sys.stderr, flush=True)


def komut_olc(a):
    maddeler = veri.yukle(a.katman)
    maddeler = veri.suz(maddeler, kova=a.kova, gorev=a.gorev,
                        gercek=None if a.govde == "hepsi" else (a.govde == "gercek"),
                        en_fazla=a.en_fazla)
    print("madde: %d  (katman: %s)" % (len(maddeler), a.katman), file=sys.stderr)
    if not maddeler:
        sys.exit("süzgeçten madde geçmedi")

    if a.uc:
        arka = olcum.Uzak(a.uc, a.model, a.anahtar)
        if not arka.echo_destegi():
            sys.exit("Bu uç `echo` desteklemiyor; zorunlu seçim ölçülemez.\n"
                     "Sessizce üretim kipine düşmüyoruz: iki farklı şey aynı\n"
                     "sayı diye raporlanamaz. --kip uretim ile üretim ölçülebilir.")
        jetonla = None
    else:
        arka = olcum.Yerel(a.model, a.dtype)
        jetonla = arka.jetonla

    secim = uretim = None
    if a.kip in ("secim", "ikisi"):
        secim = olcum.secim_olc(arka, maddeler, _ilerleme, a.isci)
    if a.kip in ("uretim", "ikisi"):
        uretim = olcum.uretim_olc(arka, maddeler, oku, _ilerleme, a.isci)

    if secim is None:
        secim = {m["kimlik"]: (d, None) for m, (o, d) in
                 zip(maddeler, uretim.values())}
    r = rapor.kesitler(maddeler, secim, uretim, jetonla if not a.tokenizer_kapat else None)
    rapor.yazdir(r, a.ad or a.model)

    if a.cikti:
        json.dump({"model": a.model, "katman": a.katman, "kip": a.kip, "rapor": r},
                  open(a.cikti, "w"), ensure_ascii=False, indent=2)
        print("\nyazıldı: %s" % a.cikti, file=sys.stderr)


def komut_bilgi(a):
    m = veri.yukle("cekirdek")
    import collections
    k = collections.Counter(x["kova"] for x in m)
    g = collections.Counter(x["gercek"] for x in m)
    print("TurkMorfBench %s — eCloud Tech." % __version__)
    print("\nçekirdek katman: %d madde  (gerçek %d · uydurma %d)"
          % (len(m), g[True], g[False]))
    print("tam katman:      ~449.000 madde (ilk kullanımda indirilir)")
    print("\nkovalar:")
    for a_, n in k.most_common():
        print("  %-28s %6d" % (a_, n))


def main(argv=None):
    p = argparse.ArgumentParser(prog="turkmorfbench",
                                description="Türkçe morfoloji kıyası — eCloud Tech.")
    p.add_argument("--surum", action="version", version=__version__)
    alt = p.add_subparsers(dest="komut", required=True)

    o = alt.add_parser("olc", help="bir modeli ölç")
    o.add_argument("--model", required=True, help="HF yolu ya da uç nokta model adı")
    o.add_argument("--uc", help="OpenAI uyumlu uç (verilmezse yerel ağırlık)")
    o.add_argument("--anahtar", help="uç için API anahtarı")
    o.add_argument("--katman", default="cekirdek", choices=["cekirdek", "tam"])
    o.add_argument("--kip", default="ikisi", choices=["secim", "uretim", "ikisi"])
    o.add_argument("--kova", nargs="*", help="yalnız bu kovalar")
    o.add_argument("--gorev", nargs="*", help="yalnız bu görevler")
    o.add_argument("--govde", default="hepsi", choices=["hepsi", "gercek", "uydurma"])
    o.add_argument("--en-fazla", type=int, dest="en_fazla")
    o.add_argument("--dtype", default="bfloat16")
    o.add_argument("--ad", help="raporda görünecek ad")
    o.add_argument("--cikti", help="JSON rapor dosyası")
    o.add_argument("--tokenizer-kapat", action="store_true", dest="tokenizer_kapat")
    o.add_argument("--isci", type=int, help="uzak uçta paralel istek sayısı (varsayılan 8)")
    o.set_defaults(fn=komut_olc)

    b = alt.add_parser("bilgi", help="kıyas hakkında")
    b.set_defaults(fn=komut_bilgi)

    a = p.parse_args(argv)
    return a.fn(a) or 0


if __name__ == "__main__":
    sys.exit(main())
