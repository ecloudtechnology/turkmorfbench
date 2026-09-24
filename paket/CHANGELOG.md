# Değişiklik kaydı · Changelog

## 3.3.1 — 2026-09-24

Yalnızca belge ve çıktı düzeltmesi; **veri ve ölçüm mantığı değişmedi**,
3.3.0 ile alınan sonuçlar geçerliliğini korur.

- Kova tablosu, üretilen veriyle birebir tutacak şekilde düzeltildi. 3.3.0'ın
  README'sinde manşet sayı (465.241) güncel, kova tablosu ise önceki dökümde
  (~449.000) kalmıştı ve bir kova (`istisna_kaynastirma_istisna`) hiç yoktu.
- Kova tablosuna anahtar sütunu ve toplam satırı eklendi; artık tablodaki ad
  ile veride süzülecek anahtar aynı belgede görünüyor.
- `turkmorfbench --bilgi` çıktısı ve `veri.py` belge dizgisi "~449.000 madde"
  diyordu; 465.241 olarak düzeltildi.
- Yayın öncesi koşulan `tutarlilik.py` eklendi: üretilen veriyi tek doğru
  kaynak sayar ve tüm belgelerdeki sayıları ona karşı denetler.

Only documentation and CLI output changed; **the data and scoring logic are
untouched**, so numbers produced with 3.3.0 remain valid.

- Bucket table corrected against the generated data. In 3.3.0 the headline
  (465,241) was current but the bucket table still showed the previous release
  (~449,000) and omitted one bucket (`istisna_kaynastirma_istisna`).
- Bucket table now carries the bucket key and a total row.
- `turkmorfbench --bilgi` and the `veri.py` docstring said "~449,000 items";
  corrected to 465,241.
- Added `tutarlilik.py`, a pre-release check that validates every documented
  figure against the generated data.

## 3.3.0

- 465.241 madde, 14 kova; TDK doğrulamalı istisna kovaları.
