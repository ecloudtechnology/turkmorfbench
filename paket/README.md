# TurkMorfBench

**Turkish morphology benchmark for language models** — 466,517 items, 14 buckets,
nonce-stem controls, per-bucket diagnosis, tokenizer analysis.
**Dil modelleri için Türkçe morfoloji kıyası** — 466.517 madde, 14 kova,
uydurma gövde kontrolü, kova bazında teşhis, tokenizer çözümlemesi.

[eCloud Tech.](https://www.e-cloud.web.tr) · code Apache-2.0 · data CC BY 4.0 ·
[data](https://huggingface.co/datasets/ecloudtech/TurkMorfBench) ·
[code](https://github.com/ecloudtechnology/turkmorfbench) · frozen release **3.8.0**

```bash
pip install turkmorfbench

turkmorfbench olc --model ecloudtech/Erk-32B                          # local weights
turkmorfbench olc --uc http://localhost:8000/v1 --model my-model     # OpenAI-compatible endpoint
turkmorfbench bilgi
```

A run does not return a score; it returns a diagnosis — which rule fails, on which
stem-final sound, on real versus nonce stems, and whether the tokenizer kept the
stem intact:

```
ZORUNLU SEÇİM   161 / 260   %61.9
GÖVDE TÜRÜ      gerçek 124/179 %69.3 · uydurma 37/81 %45.7
KOVA            istisna_uyum_kirici 0/12 · ek_zinciri 4/15 · cati 5/11 · ad_cekimi 33/48 · fiil_cekimi 10/10
SON SES         t 6/18 %33.3 · ç 4/10 %40.0 · p 6/12 %50.0 · ünlü 28/37 %75.7
HANGİ KURAL     uyum 28 · iyelik_unlu 22 · zamir_n 10
```

---

## Türkçe

### Ne ölçüyor

Türkçede ek seçimi katı kurallara bağlıdır: büyük ve küçük ünlü uyumu, ünsüz
benzeşmesi, yumuşama, kaynaştırma. Üstüne sözlüksel istisnalar (`burun → burnu`,
`kalp → kalbi`, `ret → reddi`) ve okunuşa bağlı ekler (`TCDD'yi`, `2026'da`) biner.
TurkMorfBench her birini ayrı ayrı ölçer ve **hangisinde düştüğünü söyler.**

| Kova | Anahtar | Madde | Ne sınıyor |
|---|---|---|---|
| ad paradigma yuvaları | `ad_yuva` | 283.360 | çokluk + iyelik + hâl yığını, zamir n'si |
| ad çekimi | `ad_cekimi` | 166.424 | 7 hâl, ünlü uyumu, benzeşme, yumuşama, kaynaştırma |
| ek zinciri | `ek_zinciri` | 9.544 | 1'den 8'e derinlik, ek sırası |
| fiil çekimi | `fiil_cekimi` | 1.792 | 7 zaman/kip, olumsuzluk, geniş zaman istisnaları |
| yapım eki | `yapim_eki` | 1.477 | -lIk, -CI, -lI, -sIz, -sAl, -lAş, -lA |
| özel ad | `istisna_ozel_ad` | 1.200 | kesme işareti, yumuşamama (Sinop'a) |
| birleşik isim | `istisna_birlesik_isim` | 896 | buzdolabına |
| çatı | `cati` | 728 | edilgen, dönüşlü, işteş, ettirgen |
| sayı | `istisna_sayi` | 507 | okunuşa göre ek (2026'da) |
| kısaltma | `istisna_kisaltma` | 304 | okunuşa göre ek (TCDD'yi) |
| ünlü düşmesi | `istisna_unlu_dusmesi` | 177 | burnu, aklı, nakdi · TDK doğrulamalı |
| uyum kırıcı alıntı | `istisna_uyum_kirici` | 71 | kalbi, rolü, kıraati · TDK doğrulamalı |
| ünsüz ikizleşmesi | `istisna_ikizlesme` | 35 | reddi, tıbbı, zıddı · TDK doğrulamalı |
| kaynaştırma istisnası | `istisna_kaynastirma_istisna` | 2 | suyu, neyi |
| **toplam** | | **466.517** | 14 kova |

İki katman: `cekirdek` (1.836 madde, kova dengeli, dakikalar içinde koşar, teşhis
için) ve `tam` (466.517 madde, tasarlanan kapsamın tamamı). Çekirdek bilerek
kova dengelidir; tam kümenin yansız tahmini değildir, ikisi karşılaştırılmaz.

### Tasarım

**Uydurma (wug) gövdeler.** Gerçek kelimede doğru eki üretmek ezberle mümkündür;
*zakak*, *vısep* gibi gövdeler hiçbir külliyatta geçmez, doğru ek ancak kuralla
üretilir. Kıyas her ses ortamında gerçek ve uydurma gövdeyi yan yana koyar.

**Tasarlanmış kapsam.** Ek seçimini belirleyen eksenler önce çaprazlanır — son
ünlü (8) × son ses sınıfı (8) × hece sayısı (3) × iç uyum (2) = **320 hücre** —
gövdeler sonra bu hücreleri doldurmak için üretilir. 33 hücrede Türkçede gerçek
kelime yoktur; kıyas oraları da sınar.

**Altın veri.** Kural motorundan gelir, hiçbir aşamada bir dil modelinden gelmez.
Sözlüksel düzensizlik bayrakları [Zemberek](https://github.com/ahmetaa/zemberek-nlp)
sözlüğünden alınır (Apache-2.0); çözümleyicisi kullanılmaz. Motorun 282 elle
yazılmış altın iddiası vardır ve hepsi geçer. Üç istisna kovasının (ünlü düşmesi,
uyum kırıcı, ikizleşme) **283 maddesinin tamamının** altını [TDK Güncel Türkçe Sözlük](https://sozluk.gov.tr)
ile birebir doğrulanmıştır; TDK'nın biçim vermediği ya da birden fazla biçim
verdiği gövdeler (`hak` → *hakkı* / *hakki*) kıyasa alınmaz.

**Bağımsız dış sınav.** Motor, Universal Dependencies Türkçe ağaç bankalarına
(BOUN, IMST, Penn) karşı koşulur: üçünün aynı etiketlediği 25.681 (gövde, yuva)
çiftinde yüzey biçimini birebir **%91,5**, yazım normalleştirilince **%93,9**
oranında yeniden üretir. Aradaki fark UD'nin kesme işareti ve düzeltme imi
kullanımından gelir; iki sayı ayrı raporlanır.

### Protokol

**Zorunlu seçim** birincil kiptir: altın biçim ile aynı derinlikte kural ihlali
çeldiricileri arasından log-olasılıkla seçtirilir, çıktı ayrıştırılmaz. Şıklar
madde kimliğinden türetilen bir sırayla karıştırılmıştır (`altin_sira`). Serbest
üretim ikincil kiptir ve "okunamadı" ile "yanlış" ayrı sayılır.

**Puanlama.** Aday, `log P(aday | istem)` toplamının adayın **karakter sayısına**
bölünmesiyle puanlanır (`harf`). Karakter sayısı tokenizer'dan bağımsızdır; jeton
sayısına bölmek, kelimeyi kaç parçaya böldüğüne göre modelleri farklı cezalandırır.
Kural, uzunluk yanlılığına göre seçilmiştir: adayların uzunluğu farklı olan
maddelerde altın %29,9 oranında en kısadır, `harf` %39–43 oranında en kısayı
seçer; kalan yanlılık raporlanır, gizlenmez. Yerel ve uzak arka uç aynı jeton
sınırı kuralını uygular; uzak uç `/v1/completions` yanıtında `text_offset`
döndürmek zorundadır, yoksa ölçüm durur.

**Kurala duyarlılık.** `turkmorfbench.duyarlilik` modeli bir kez koşturur ve altı
kuralı aynı ham büyüklüklerden türetir: `ham`, `jeton`, `harf`, `pmi`, `pmi_harf`
ve beş kuralın Copeland uzlaşısı `esli`. İki sistem karşılaştırılırken farkın
yönünün kuraldan kurala değişip değişmediği raporlanır.

**Güven aralığı.** 466.517 madde 466.517 bağımsız gözlem değildir: bir gövde
onlarca madde doğurur, bir fonolojik hücre yüzlerce gövdeyi aynı kurala bağlar.
`turkmorfbench.istatistik` yeniden örnekleme birimini maddeden **kümeye** taşır
(gövde: 32.140 küme · fonolojik hücre: 441 küme) ve her koşumda tasarım etkisini
ölçüp bildirir. İki model, ayrı aralıkların çakışmasına bakılarak değil, eşli
farkın kümeli önyüklemesiyle karşılaştırılır (`esli_fark`).

```python
from turkmorfbench.istatistik import kume_bootstrap, esli_fark, tasarim_etkisi
from turkmorfbench.duyarlilik import bilesen_topla, karsilastir, rapor
s = kume_bootstrap(maddeler, dogru, anahtar="hucre")
f = esli_fark(maddeler, a_dogru, b_dogru, anahtar="hucre")
print(rapor(karsilastir(bilesen_topla(arka_a, maddeler), bilesen_topla(arka_b, maddeler), maddeler, "A", "B"), "A", "B"))
```

### Bulgular

**Gerçek ile uydurma gövde arasında 22–32 puan.** Modeller ekleri büyük ölçüde
kuraldan değil sözlüksel komşuluktan üretiyor. Gerçek kelimenin bulunmadığı 33
hücrede fark, ses bileşimi eşleştirildikten sonra bile 22–23 puandır.

**Liderlik tablosu.** 3.6 çekirdeği (1.836 madde), `harf` kuralı, hücre kümeli %95 güven aralığı, tek sabit betik, bf16, şık sırası
dondurulmuş. TurkishMMLU: aynı sabit betikle 652 temiz soru (beş şık, şans %20). Erk modelleri bu kıyasın teşhis
çıktısıyla iyileştirildi; diğer modeller yayımlandıkları hâliyle ölçüldü.

| # | model | geliştiren | boyut | TurkMorfBench | %95 GA | TurkishMMLU |
|---|---|---|---|---|---|---|
| 1 | Erk-14B *(v2)* | eCloud Tech. | 14B | **80,0** | 75,8–88,3 | 66,9 |
| 2 | turkish-gpt2-large | YTÜ COSMOS | 0,8B | **79,1** | 76,9–81,8 | 18,4 |
| 3 | kanarya-2b | Asafaya | 2B | **78,4** | 76,4–83,3 | 22,9 |
| 4 | Erk-32B *(v2)* | eCloud Tech. | 32B | **76,5** | 71,0–87,3 | 71,5 |
| 5 | Kumru-2B-Base | VNGRS | 2B | **76,2** | 72,6–77,8 | 17,0 |
| 6 | Kumru-2B | VNGRS | 2B | **76,2** | 74,0–78,7 | 19,6 |
| 7 | Turkcell-LLM-7b-v1 | Turkcell | 7B | **76,0** | 74,2–80,5 | 26,4 |
| 8 | Erk-14B *(v1)* | eCloud Tech. | 14B | **75,4** | 70,0–86,0 | 67,2 |
| 9 | Qwen3.8-27B (taban) | Alibaba | 27B | **75,4** | 71,3–83,9 | 70,2 |
| 10 | Turkish-Gemma-9b-v0.1 | YTÜ COSMOS | 9B | **75,2** | 69,8–85,7 | 60,3 |
| 11 | Erk-32B *(v1)* | eCloud Tech. | 32B | **74,9** | 69,2–86,1 | 71,0 |
| 12 | wiroai-turkish-llm-9b | WiroAI | 9B | **74,6** | 70,4–83,1 | 45,7 |
| 13 | Trendyol-LLM-7B-chat-v4.1.0 | Trendyol | 7B | **73,5** | 71,0–79,2 | 50,0 |
| 14 | Qwen3-32B (taban) | Alibaba | 32B | **73,4** | 67,8–84,3 | 67,6 |
| 15 | Turkish-Llama-8b-v0.1 | YTÜ COSMOS | 8B | **72,0** | 68,8–79,0 | 35,0 |
| 16 | Turkish-Llama-8b-Instruct-v0.1 | YTÜ COSMOS | 8B | **70,2** | 65,4–79,9 | 42,2 |
| 17 | Trendyol-LLM-7b-chat-v1.0 | Trendyol | 7B | **67,6** | 65,3–73,3 | 29,9 |

İlk sıralar istatistiksel olarak beraberlik bandındadır; iki modeli karşılaştırırken aralıkların çakışmasına
değil, eşli farkın kümeli önyüklemesine bakılır (`esli_fark`). Morfoloji parametre sayısıyla ölçeklenmez:
TurkishMMLU'da şans düzeyindeki 0,8–2B modeller morfolojide 32B modellerle aynı banttadır.

**Sonuç kurala bağlı değil.** 15 modelde `harf`, `ham` ve `jeton` aynı uçları
verir (ilk iki ve son üç sıra aynı); `ham` 1–4, `jeton` 2–16 puan aşağıda kalır.
`pmi` ve `pmi_harf` 21–51 aralığına çöker: koşulsuz olasılıkla normalleştirmek,
ortak gövdeyi paylaşan adaylar arasındaki ayrımı yok eder; bu iki kural görev için
uygun değildir ve pakette okuyucunun görmesi için durur. Tasarım etkisi modelden
modele 1,2× ile 4,1× arasındadır.

**İnsan tavanı: %78,2 [%70,4 – %83,2].** Aynı maddeler ana dili Türkçe olan
kişilere [morf.e-cloud.web.tr](https://morf.e-cloud.web.tr) üzerinden sorulur;
6 geçerli değerlendirici, 560 yargı, hücre kümeli aralık; toplama sürüyor.
Katılımcı taraması önceden yazılı üç ölçütle yapılır ve sonuca bakılarak
değiştirilmez: en az 10 cevap, soru başına medyan süre ≥ 3 s, kendi şans
düzeyini tek yönlü binom testiyle (α = 0,001) geçme. 12 katılımcının 6'sı bu
ölçütlerle elenmiştir. Model ile insan aynı maddelerde: eCloud Tech.'in AIGENCY V4
modeli aynı arayüzden 515 maddenin tamamına cevap verdi; **AIGENCY V4 %69,9,
geçerli insanlar %79,1**. Bütün sayılar `insan_ozet.py` ile üretilir.

**Tokenizer etkisi.** Yerel ağırlıklarla koşulduğunda rapor, doğruluğu sözlüğün
gövdeyi bütün tutup tutmadığına göre ayırır ve parçalanmanın puan maliyetini
verir. Türkçede jeton başına bölen bir ölçüde tam sözcük jetonlu küçük modeller
en çok kaybeder; `harf` bu yüzden birincil kuraldır.

### Bilinen sınırlar

- `ek_zinciri` kovası 3.6 çekirdeğinde 15 modelin 13'ünde ≥%96: ayırt etmiyor.
  Kova hariç sıralama aynıdır; bir sonraki veri sürümünde çeldiriciler bağlamla
  uyuşmayan dilbilgisel zincirler olacak.
- `istisna_kaynastirma_istisna` iki maddedir (suyu, neyi); tek başına yorumlanmaz.
- İnsan tavanı ön okumadır; uydurma gövdede insan performansı için henüz iddia yok.
- Puanlama kuralının kalan uzunluk yanlılığı (%39–43, hedef %29,9) raporlanır.

### Sürümler

3.8.0 dondurulmuş yayın sürümüdür (veri 3.6.0, puanlama 3.7.0). Veri ya da puanlama kodunu değiştiren her
sürüm `CHANGELOG.md`'de gerekçesiyle kayıtlıdır; farklı veri sürümlerinin
sayıları birbiriyle karşılaştırılmaz. Paket `tutarlilik.py` ile belge, veri ve
yayımlanan paket arasında tutarlılık denetiminden geçer.

---

## English

### What it measures

Turkish suffix selection follows strict rules — two-way and four-way vowel
harmony, consonant assimilation, lenition, buffer consonants — with lexical
exceptions (`burun → burnu`, `kalp → kalbi`, `ret → reddi`) and
pronunciation-driven suffixes (`TCDD'yi`, `2026'da`) on top. TurkMorfBench
measures each separately and reports **which one fails** (bucket table above).

Two tiers: `cekirdek` (1,836 items, bucket-balanced, runs in minutes, for
diagnosis) and `tam` (466,517 items, the full designed coverage). The core tier
is deliberately balanced, not an unbiased sample of the full set; do not compare
the two.

### Design

**Nonce (wug) stems.** A real word can be inflected from memory; *zakak* or
*vısep* appear in no corpus and can only be inflected from the rule. Every
phonological environment carries both real and nonce stems.

**Designed coverage.** The axes that determine suffix selection are crossed
first — final vowel (8) × final-sound class (8) × syllable count (3) × internal
harmony (2) = **320 cells** — and stems are generated to fill them. 33 cells
contain no real Turkish word; the benchmark tests them anyway.

**Gold data.** Generated by the rule engine, never by a language model. Lexical
irregularity flags come from the [Zemberek](https://github.com/ahmetaa/zemberek-nlp)
dictionary (Apache-2.0); its analyser is not used. The engine carries 282
hand-written gold assertions, all passing. All 283 items of the three
exception buckets (vowel drop, inverse harmony, consonant doubling) are verified
character-for-character against the [TDK dictionary](https://sozluk.gov.tr);
stems for which TDK gives no form or more than one are excluded.

**Independent external check.** The engine is run against the Universal
Dependencies Turkish treebanks (BOUN, IMST, Penn): on the 25,681 (lemma, slot)
pairs all three annotate identically it reproduces the attested surface form
**91.5%** verbatim and **93.9%** after spelling normalisation (apostrophes and
circumflex usage differ between treebanks); both figures are reported.

### Protocol

**Forced choice** is the primary mode: the gold form against same-depth
rule-violation distractors, scored by log-likelihood, no output parsing. Options
are shuffled by an item-derived permutation (`altin_sira`). Free generation is
secondary and reports "unreadable" separately from "wrong".

**Scoring.** A candidate is scored by the sum of `log P(candidate | prompt)`
divided by its **character count** (`harf`). Characters are tokenizer-independent;
dividing by tokens penalises models by how many pieces they cut a word into. The
rule was chosen for length bias: the gold is the shortest candidate in 29.9% of
items with unequal lengths, and `harf` picks the shortest 39–43% of the time; the
residual bias is reported, not hidden. Local and remote backends apply the same
token-boundary rule; a remote `/v1/completions` endpoint must return
`text_offset`, otherwise measurement stops.

**Rule sensitivity.** `turkmorfbench.duyarlilik` runs the model once and derives
six rules from the same raw quantities: `ham`, `jeton`, `harf`, `pmi`, `pmi_harf`
and `esli`, a Copeland consensus of the five. When two systems are compared it
reports whether the sign of the difference changes from rule to rule.

**Confidence intervals.** 466,517 items are not 466,517 independent observations:
a stem yields dozens of items and a phonological cell binds hundreds of stems to
one rule. `turkmorfbench.istatistik` moves the resampling unit to the **cluster**
(stem: 32,140 clusters · phonological cell: 441) and measures the design effect
on every run. Two models are compared by a cluster bootstrap of the paired
difference (`esli_fark`), not by overlap of separate intervals.

### Findings

**22–32 points between real and nonce stems.** Models inflect largely from
lexical neighbourhood, not from the rule. In the 33 cells with no real word the
gap is 22–23 points even after matching phonological composition.

**Leaderboard.** 3.6 core (1,836 items), `harf` rule, cell-clustered 95% CI, one pinned script, bf16, option order frozen.
TurkishMMLU: the same pinned script on 652 clean questions (five-way, chance 20%). Erk models were improved
using this benchmark's diagnostic output; the other models were measured as published.

| # | model | developer | size | TurkMorfBench | %95 CI | TurkishMMLU |
|---|---|---|---|---|---|---|
| 1 | Erk-14B *(v2)* | eCloud Tech. | 14B | **80.0** | 75.8–88.3 | 66.9 |
| 2 | turkish-gpt2-large | YTÜ COSMOS | 0,8B | **79.1** | 76.9–81.8 | 18.4 |
| 3 | kanarya-2b | Asafaya | 2B | **78.4** | 76.4–83.3 | 22.9 |
| 4 | Erk-32B *(v2)* | eCloud Tech. | 32B | **76.5** | 71.0–87.3 | 71.5 |
| 5 | Kumru-2B-Base | VNGRS | 2B | **76.2** | 72.6–77.8 | 17.0 |
| 6 | Kumru-2B | VNGRS | 2B | **76.2** | 74.0–78.7 | 19.6 |
| 7 | Turkcell-LLM-7b-v1 | Turkcell | 7B | **76.0** | 74.2–80.5 | 26.4 |
| 8 | Erk-14B *(v1)* | eCloud Tech. | 14B | **75.4** | 70.0–86.0 | 67.2 |
| 9 | Qwen3.8-27B (taban) | Alibaba | 27B | **75.4** | 71.3–83.9 | 70.2 |
| 10 | Turkish-Gemma-9b-v0.1 | YTÜ COSMOS | 9B | **75.2** | 69.8–85.7 | 60.3 |
| 11 | Erk-32B *(v1)* | eCloud Tech. | 32B | **74.9** | 69.2–86.1 | 71.0 |
| 12 | wiroai-turkish-llm-9b | WiroAI | 9B | **74.6** | 70.4–83.1 | 45.7 |
| 13 | Trendyol-LLM-7B-chat-v4.1.0 | Trendyol | 7B | **73.5** | 71.0–79.2 | 50.0 |
| 14 | Qwen3-32B (taban) | Alibaba | 32B | **73.4** | 67.8–84.3 | 67.6 |
| 15 | Turkish-Llama-8b-v0.1 | YTÜ COSMOS | 8B | **72.0** | 68.8–79.0 | 35.0 |
| 16 | Turkish-Llama-8b-Instruct-v0.1 | YTÜ COSMOS | 8B | **70.2** | 65.4–79.9 | 42.2 |
| 17 | Trendyol-LLM-7b-chat-v1.0 | Trendyol | 7B | **67.6** | 65.3–73.3 | 29.9 |

The top ranks are a statistical tie; compare two models by the cluster bootstrap of the paired difference
(`esli_fark`), not by interval overlap. Morphology does not scale with parameter count: 0.8–2B models at chance
on TurkishMMLU sit in the same band as 32B models on morphology.

**The result does not depend on the rule.** Across 15 models `harf`, `ham` and
`jeton` give the same ends of the ranking (top two, bottom three); `ham` sits 1–4
and `jeton` 2–16 points lower. `pmi` and `pmi_harf` collapse to 21–51: normalising
by the unconditional probability erases the distinction between candidates that
share a stem; they are unsuitable for this task and stay in the package so
readers can see it. The design effect ranges from 1.2× to 4.1× across models.

**Human ceiling: 78.2% [70.4 – 83.2].** The same items are put to native speakers
at [morf.e-cloud.web.tr](https://morf.e-cloud.web.tr); 6 valid raters, 560
judgments, cell-clustered interval, collection ongoing. Raters are screened by
three criteria fixed in advance and never adjusted after seeing the result: at
least 10 answers, median time per question ≥ 3 s, and accuracy above the rater's
own chance level on a one-sided binomial test (α = 0.001). 6 of 12 raters were
removed by these criteria. Model and humans on the same items: eCloud Tech.'s
AIGENCY V4 model answered all 515 items through the same interface; **AIGENCY V4
69.9%, valid humans 79.1%**. Every figure is produced by `insan_ozet.py`.

**Tokenizer effect.** With local weights the report splits accuracy by whether
the vocabulary kept the stem intact and states the cost of fragmentation in
points. Under a per-token score, small whole-word-token models lose the most;
this is why `harf` is the primary rule.

### Known limits

- `ek_zinciri` scores ≥96% for 13 of 15 models on the 3.6 core and does not
  discriminate; the ranking without it is identical. The next data release will
  use grammatical chains that disagree with the context as distractors.
- `istisna_kaynastirma_istisna` has two items (suyu, neyi); not interpreted alone.
- The human ceiling is a preliminary reading; no claim yet on nonce stems.
- The residual length bias of the scoring rule (39–43% vs 29.9%) is reported.

### Versions

3.8.0 is the frozen release (data 3.6.0, scoring 3.7.0). Every change to data or scoring code is recorded
with its rationale in `CHANGELOG.md`; figures from different data versions are not
comparable. `tutarlilik.py` checks documentation, data and the published package
against each other.

---

## Citation

```bibtex
@software{turkmorfbench2026,
  title     = {TurkMorfBench: A Diagnostic Morphology Benchmark for Turkish Language Models},
  author    = {{eCloud Tech.}},
  year      = {2026},
  version   = {3.8.0},
  url       = {https://github.com/ecloudtechnology/turkmorfbench},
  note      = {Data: https://huggingface.co/datasets/ecloudtech/TurkMorfBench. A paper citation will replace this entry when published.}
}
```

**Data:** [huggingface.co/datasets/ecloudtech/TurkMorfBench](https://huggingface.co/datasets/ecloudtech/TurkMorfBench) ·
**Code:** [github.com/ecloudtechnology/turkmorfbench](https://github.com/ecloudtechnology/turkmorfbench)

Keywords: Turkish NLP, Türkçe doğal dil işleme, morphology benchmark, morfoloji
kıyası, vowel harmony, ünlü uyumu, wug test, agglutinative languages, LLM
evaluation, dil modeli değerlendirme, tokenizer analysis, subword segmentation.
