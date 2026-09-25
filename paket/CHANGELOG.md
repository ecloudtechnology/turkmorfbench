# Değişiklik kaydı · Changelog

## 3.6.0 — 2026-09-25

**Veri değişti**: ünlü düşmesi motoru düzeltildi; 34 gövde, `ad_yuva`'da 136 yanlış
altın (*acizlarında* → *acizlerinde*), `istisna_uyum_kirici`'ye yanlış sınıflanan
34 gövde çıkarıldı. `ad_cekimi` 166.307 → 166.424, `istisna_uyum_kirici` 105 → 71,
toplam 466.434 → 466.517, çekirdek 1.856 → 1.836. Diğer 12 kova birebir aynı.
Motor: `ad_cekim._govde_hazirla` — uyum düşen ünlüyü izler; TDK bayrak araması
yeniden koşuldu (501/501). `istisna_verisi_uret.py`: istisna kovaları için
kıyas DIŞI TDK gövdeleriyle sentetik veri.

**Data changed**: vowel-drop harmony fixed in the engine; 34 stems, 136 wrong
`ad_yuva` golds, 34 stems removed from `istisna_uyum_kirici` where the leaked flag
had misfiled them. `ad_cekimi` 166,307 → 166,424, `istisna_uyum_kirici` 105 → 71,
total 466,434 → 466,517, core 1,856 → 1,836. The other 12 buckets are identical.


## 3.5.0 — 2026-09-25

**Veri değişti**: `ek_zinciri` kovası yeniden üretildi, toplam 465.241 → 466.434.
Diğer 13 kova birebir aynı; onların 3.4.x sayıları geçerli. `ek_zinciri` ve
genel doğruluk sayıları 3.4.x ile karşılaştırılamaz.

- **`ek_zinciri` çeldiricileri kural ihlaline çevrildi — kıyasın kendi hatası.**
  Beş farklı model derinlik 2/3/5/7'de tam %0, 6/8'de ~%100 alıyordu; bu model
  özelliği olamaz. Eski çeldiriciler "bir basamak eksik/fazla" idi — ikisi de
  DİLBİLGİSEL biçimler. İstem hedef derinliği söylemediği için model en olası
  geçerli biçimi seçiyor ve yanlış sayılıyordu. Artık aynı derinlikte uyum
  ihlali, sahte kaynaştırma ve sıra bozukluğu. Derinlik-1 maddeleri de kovaya
  girdi (8.351 → 9.544).
- **Çekirdek seçimi özet-kararlı yapıldı.** `rng.shuffle` eklemeye duyarlıydı:
  tam kümeye 1.193 madde girince çekirdek bütün kovalarda kaydı (1.856'nın
  yalnız 1.214'ü ortak kaldı). Sıra artık her maddenin kimliğinden türeyen
  özetle belirlenir; yeni madde ancak özeti üst bölgeye düşerse eskisini iter.
  Bu geçişte 3.4 çekirdeğiyle ortak madde 255'e düştü — **bir kerelik** kopuş;
  bundan sonra kayma eklemeyle orantılı.
- `tutarlilik.py --paket <dosya>`: yayımlanan paketin uzun açıklamasını da
  veriye karşı denetler.
- `kural_verisi_uret.py`: kural kovaları (kısaltma, sayı, çatı) için kıyas
  DIŞI sentetik eğitim verisi; kova bazlı kontaminasyon denetimi.

**Data changed**: the `ek_zinciri` bucket was regenerated, total 465,241 →
466,434. The other 13 buckets are identical; their 3.4.x figures stand.
`ek_zinciri` and overall accuracy are not comparable with 3.4.x.

- **`ek_zinciri` distractors are now rule violations — the benchmark's own
  error.** Five different models scored exactly 0% at depths 2/3/5/7 and ~100%
  at 6/8. The old distractors ("one step fewer/more") were grammatical forms;
  with no target depth in the prompt, a model picks the most probable valid
  form and is marked wrong. Depth-1 items now enter the bucket (8,351 → 9,544).
- **Core selection is now hash-stable.** `rng.shuffle` was insertion-sensitive.
  Membership is now decided per item by a digest of its ID. One-time break with
  the 3.4 core (255 shared); proportional drift from here on.
- `tutarlilik.py --paket`: verifies the published package's long description.
- `kural_verisi_uret.py`: contamination-free synthetic data for the rule
  buckets (abbreviation, number, voice).

## 3.4.0 — 2026-09-25

İki yeni modül; **veri ve puanlama kuralı değişmedi**, 3.3.x ile alınan
doğruluk sayıları geçerliliğini korur. Değişen, o sayıların etrafındaki
belirsizliğin nasıl bildirildiğidir.

- **`turkmorfbench.istatistik` — küme önyüklemesi.** 465.241 madde 465.241
  bağımsız gözlem değildir: tek gövde onlarca maddeyi, tek fonolojik hücre
  yüzlerce gövdeyi aynı kurala bağlar. Madde düzeyinde önyükleme örneklemi
  olduğundan büyük gösterip aralığı daraltıyordu. Yeniden örnekleme birimi
  artık gövde / fonolojik hücre / gövde×görev olabilir. `esli_fark()` iki
  sistemin farkını doğrudan örnekler; `tasarim_etkisi()` madde düzeyine göre
  kaç kat şişirme olduğunu ve etkin örneklem büyüklüğünü bildirir.
- **`turkmorfbench.duyarlilik` — puanlama kuralı duyarlılığı.** Model bir kez
  koşar, altı kural (ham, jeton, harf, pmi, pmi_harf, ikili karşılaştırma) tek
  koşumdan türer. Çıktı, iki sistemin farkının yönünün tüm kurallarda aynı olup
  olmadığını söyler.
- **İnsan tavanı güncellendi ve iki iddia GERİ ÇEKİLDİ.** Yeni ölçüm %73,0
  [64,7–80,6], 5 geçerli değerlendirici / 437 yargı. Önceki %88,2 geri
  çekilmiştir: 3 değerlendiriciye dayanıyordu ve o havuzun 520 maddesinin
  257'si güncel kıyas verisinde yoktu. "İnsan düşüşü 12 puan" iddiası da geri
  çekilmiştir; uydurma gövde tarafında yeterli yargı yok. Yayımlanan sayılar
  artık `insan_ozet.py` tarafından üretilir.

Two new modules; **the data and the scoring rule are unchanged**, so accuracy
figures from 3.3.x remain valid. What changed is how the uncertainty around
those figures is reported.

- **`turkmorfbench.istatistik` — cluster bootstrap.** 465,241 items are not
  465,241 independent observations. The resampling unit can now be the stem, the
  phonological cell, or stem×task. `esli_fark()` resamples the difference between
  two systems directly; `tasarim_etkisi()` reports the design effect and the
  effective sample size against item-level bootstrap.
- **`turkmorfbench.duyarlilik` — scoring-rule sensitivity.** The model runs once;
  six rules are derived from the stored components. The output states whether the
  sign of a difference holds under all six.
- **Human ceiling updated; two claims WITHDRAWN.** New reading 73.0%
  [64.7–80.6], 5 valid raters / 437 judgments. The earlier 88.2% is withdrawn
  (3 raters; 257 of that pool's 520 items did not exist in the current benchmark
  data). The "12-point human drop" claim is withdrawn as well.

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
