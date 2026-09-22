# -*- coding: utf-8 -*-
"""Madde kümesini yükler. Çekirdek pakette gömülü; tam küme istenirse indirilir."""
import json
import os

KOK = os.path.dirname(os.path.abspath(__file__))
CEKIRDEK = os.path.join(KOK, "veri", "cekirdek.json")
TAM_ADRES = ("https://huggingface.co/datasets/ecloudtech/TurkMorfBench/"
             "resolve/main/turkmorfbench_v3_tam.json")


def yukle(katman="cekirdek", onbellek=None):
    """`cekirdek` (pakette gömülü, ~2.000 madde) ya da `tam` (~449.000, indirilir).

    Tam küme 145 MB; pakete konmaz, ilk kullanımda indirilip önbelleğe alınır.
    """
    if katman == "cekirdek":
        with open(CEKIRDEK, encoding="utf8") as f:
            return json.load(f)["maddeler"]

    onbellek = onbellek or os.path.join(
        os.path.expanduser("~"), ".cache", "turkmorfbench", "tam.json")
    if not os.path.exists(onbellek):
        os.makedirs(os.path.dirname(onbellek), exist_ok=True)
        import urllib.request
        print("tam küme indiriliyor (~145 MB, bir kez)…")
        urllib.request.urlretrieve(TAM_ADRES, onbellek)
    with open(onbellek, encoding="utf8") as f:
        return json.load(f)["maddeler"]


def suz(maddeler, kova=None, gercek=None, gorev=None, en_fazla=None, tohum=1337):
    """Madde süzme. `gercek=False` yalnız uydurma gövdeler demektir."""
    c = maddeler
    if kova:
        k = {kova} if isinstance(kova, str) else set(kova)
        c = [m for m in c if m["kova"] in k]
    if gercek is not None:
        c = [m for m in c if m["gercek"] is gercek]
    if gorev:
        g = {gorev} if isinstance(gorev, str) else set(gorev)
        c = [m for m in c if m["gorev"] in g]
    if en_fazla and len(c) > en_fazla:
        import random
        random.Random(tohum).shuffle(c)
        c = c[:en_fazla]
    return c
