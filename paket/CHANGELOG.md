# Değişiklik kaydı · Changelog

## 3.7.0 — 2026-09-26

**Puanlama kodu değişti; veri 3.6.0 ile aynı.** Dış inceleme dört noktayı doğru buldu, dördü de düzeltildi.
(1) **Jeton sınırı.** İstem `"…Çekimli biçim: "` boşlukla bitiyordu; istem tek başına ve istem+aday ayrı
jetonlanınca sınırdaki jeton değişiyor (`Ġ`+`kal` → `Ġkal`) ve adayın İLK jetonu puan dışı kalıyordu.
3.6 çekirdeğinde adayların %93–99,7'si etkileniyordu (Erk %95,0 · kanarya %99,7 · Kumru %92,7 · Gemma %95,3).
Yerel arka uç artık iki jeton dizisinin ortak önekinden başlar, uzak arka uç sınırı aşan jetonu sayar;
iki arka uç aynı kuralı uygular. Bütün tablo sayıları bu kodla yeniden ölçüldü.
(2) **`esli` kuralı** yalnız `harf` puanı üzerinde ikili turnuvaydı; tek sayıl puanda turnuva, en büyüğü
seçmekle aynıdır — `harf` ile birebir çıkması sağlamlık kanıtı değildi. Şimdi beş tekil kuralın uzlaşısı
(Copeland: her çift beş kuralda oylanır). (3) **`yon_tutarli`** yalnız anlamlı satırların işaretine
bakıyordu; artık tüm kuralların işaretine bakar, anlamlı olanlar `anlamli_yon_tutarli`. (4) `govde_gorev`
anahtarı "hiyerarşik" diye anılıyordu; çapraz anahtarlı tek aşamalı küme bootstrap'ıdır, öyle yazıldı.
Paket kodundaki eski sayılar (465.241, 1.856) kaldırıldı; `veri.TAM_N/CEKIRDEK_N` sabitleri `tutarlilik.py`
ile veriye bağlandı. Durum: Beta → Production/Stable. `CITATION.cff` eklendi, atıf `@software`.
**Scoring code changed; data identical to 3.6.0.** An external review raised four points; all were correct
and are fixed. (1) **Token boundary.** The prompt ends with a space; tokenising the prompt alone and
prompt+candidate separately changes the boundary token (`Ġ`+`kal` → `Ġkal`) and the candidate's FIRST token
was left out of the score. On the 3.6 core this affected 93–99.7% of candidates. The local backend now
starts at the end of the common token prefix, the remote backend counts the token that crosses the boundary;
both apply the same rule. All table numbers were re-measured with this code. (2) **`esli`** was a pairwise
tournament over the `harf` scalar alone, which is identical to taking its maximum, so its agreement with
`harf` was no evidence of robustness. It is now a consensus over the five individual rules (Copeland).
(3) **`yon_tutarli`** looked only at significant rows; it now checks the sign of every rule, with
`anlamli_yon_tutarli` for the significant ones. (4) `govde_gorev` is a crossed-key single-stage cluster
bootstrap, not a hierarchical one; documented as such. Stale counts removed from package code;
`veri.TAM_N/CEKIRDEK_N` are checked against the data. Status Beta → Production/Stable; `CITATION.cff` added.


## 3.6.3 — 2026-09-25

Yalnızca belge, veri ve kod 3.6.0 ile aynı. (1) TDK-doğrulamalı üç kovanın toplamı
317 → **283** (3.6.0'da `istisna_uyum_kirici` 105 → 71 olunca metin güncellenmemişti).
(2) Morfoloji ≠ yetenek tablosu 3.6 çekirdeğinde (1.836 madde) yeniden ölçüldü;
3.5 çekirdeği sayıları kaldırıldı, boyut sütunu eklendi. (3) Bulgu: yeniden
tasarlanan `ek_zinciri` kovası 3.6 çekirdeğinde 15 modelin 14'ünde ≥%96 — tabandan
tavana geçti, 3.7'de yeniden tasarlanacak. `tutarlilik.py` iki yeni denetim: TDK
toplamı ve karşılaştırma tablosu başlığındaki sürüm.
Documentation only; data and code identical to 3.6.0. (1) The TDK-verified total
317 → **283** (text was not updated when `istisna_uyum_kirici` went 105 → 71 in 3.6.0).
(2) The morphology ≠ capability table re-measured on the 3.6 core (1,836 items);
3.5-core numbers removed, size column added. (3) Finding: the redesigned `ek_zinciri`
bucket sits at ≥96% for 14 of 15 models on the 3.6 core — floor became ceiling; it
will be redesigned in 3.7. `tutarlilik.py` gains two checks: TDK total and the
version in the comparison-table header.


## 3.6.2 — 2026-09-25

Yalnızca belge: insan tavanı bölümünde model oturumlarının anlatımı düzeltildi. Veri ve kod 3.6.0 ile aynı.
Documentation only: the account of the model sessions in the human-ceiling section was corrected. Data and code identical to 3.6.0.


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
