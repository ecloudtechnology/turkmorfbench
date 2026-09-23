# TurkMorfBench

**Turkish morphology benchmark for language models** — 465,241 items, diagnostic
reports, wug-test controls, tokenizer analysis.
**Dil modellerinin Türkçe morfoloji yetkinliğini ölçen kıyas** — 465.241 madde,
teşhis raporu, uydurma gövde kontrolü, tokenizer çözümlemesi.

Built by [eCloud Tech.](https://www.e-cloud.web.tr) · code Apache-2.0 · data CC BY 4.0

```bash
pip install turkmorfbench

turkmorfbench olc --model ecloudtech/Erk-32B
turkmorfbench olc --uc http://localhost:8000/v1 --model my-model --isci 16
```

---

## What it tells you / Ne söylüyor

Not a score. A diagnosis. / Puan değil, teşhis.

Real output from a 260-item run (forced choice, one open model served over an
OpenAI-compatible endpoint):

```
ZORUNLU SEÇİM   161 / 260   %61.9

GÖVDE TÜRÜ
  gerçek gövde (real stems)          124/179   %69.3
  uydurma gövde (nonce/wug stems)     37/81    %45.7

KOVA (bucket)
  istisna_uyum_kirici                  0/12    %0.0     harmony-breaking loans
  ek_zinciri                           4/15    %26.7    suffix chains
  cati                                 5/11    %45.5    voice
  ad_cekimi                           33/48    %68.8    nominal case
  fiil_cekimi                         10/10    %100.0   verb inflection

SON SES (stem-final sound)
  t    6/18   %33.3                                     the lenition consonants
  ç    4/10   %40.0
  p    6/12   %50.0
  ünlü (vowel)  28/37  %75.7

HANGİ KURAL BİLİNMİYOR (which rule was violated)
  uyum (vowel harmony)          28   %28.3
  iyelik_unlu (buffer vowel)    22   %22.2
  zamir_n (pronominal n)        10   %10.1
```

When run against local weights, the report adds a **tokenizer breakdown**:
accuracy split by whether the vocabulary kept the stem intact or fragmented it,
and the measured cost of fragmentation in points. That block answers the question
model developers actually ask — *does my vocabulary break Turkish morphology?* —
and no other Turkish benchmark reports accuracy conditioned on tokenization.

---

## Türkçe

### Ne ölçüyor

Türkçe sondan eklemeli bir dildir ve ek seçimi katı kurallara bağlıdır: büyük ve
küçük ünlü uyumu, ünsüz benzeşmesi, ünsüz yumuşaması, kaynaştırma. Üstüne
sözlüksel istisnalar biner: `burun → burnu`, `ret → reddi`, `kalp → kalbi`,
`buzdolabı → buzdolabına`. Bir de okunuşa bağlı ekler: `TCDD'yi`, `2026'da`.

TurkMorfBench bunların hepsini ayrı ayrı ölçer ve **hangisinde düştüğünü söyler.**

| Kova | Madde | Ne sınıyor |
|---|---|---|
| ad çekimi | 159.839 | 7 hâl, ünlü uyumu, benzeşme, yumuşama, kaynaştırma |
| ad paradigma yuvaları | 273.840 | çokluk + iyelik + hâl yığını, **zamir n'si** |
| ek zinciri | 8.344 | 1'den 8'e derinlik, ek sırası |
| fiil çekimi | 1.799 | 7 zaman/kip, olumsuzluk, iki kişi takımı, **geniş zaman istisnaları** |
| yapım eki | 1.442 | -lIk, -CI, -lI, -sIz, -sAl, -lAş, -lA |
| çatı | 669 | edilgen, dönüşlü, işteş, ettirgen |
| özel ad | 1.200 | kesme işareti, **yumuşamama** (Sinop'a, Sinob'a değil) |
| birleşik isim | 897 | buzdolabına |
| sayı | 533 | **okunuşa göre** ek (2026'da) |
| kısaltma | 304 | **okunuşa göre** ek (TCDD'yi) |
| ünlü düşmesi | 181 | burnu, aklı, aczi · **TDK doğrulamalı** |
| uyum kırıcı alıntı | 70 | kalbi, rolü, kıraati · **TDK doğrulamalı** |
| ünsüz ikizleşmesi | 36 | reddi, tıbbı, zıddı · **TDK doğrulamalı** |

### Neden uydurma (wug) gövde

Gerçek kelimede doğru ek üretmek ezberle de mümkündür: model *kitabı* biçimini
külliyatta on binlerce kez görmüştür. Uydurma gövde (*zakak*, *vısep*, *sövot*)
hiçbir külliyatta geçmez; model doğru eki ancak **kuralı** biliyorsa üretir.

Ölçtük: modeller gerçek gövdeyle uydurma gövde arasında 22-32 puan fark veriyor.
Yani büyük ölçüde kuralı değil komşuluğu kullanıyorlar.

### Ses ortamı kapsam dizeyi

Ek seçimini belirleyen eksenler **önce** çaprazlanır, gövdeler sonra o hücreleri
doldurmak için üretilir: son ünlü (8) × son ses sınıfı (8) × hece sayısı (3) ×
iç uyum (2) = **320 hücre**.

Bu kümenin **33 hücresinde Türkçede gerçek kelime yoktur.** Gerçek kelimelerden
kurulan bir kıyas oraları sınayamaz. Ölçtük: modeller tam o hücrelerde, ses
bileşimi eşleştirildikten sonra bile, 22-23 puan daha kötü.

### İki katman

| Katman | Madde | Kimin için |
|---|---|---|
| `cekirdek` | 1.856 | dakikalar içinde koşar, kova dengeli, **teşhis için** |
| `tam` | 465.241 | tasarlanan kapsamın tamamı, **manşet sayı için** |

Çekirdek kova dengelidir, yani tam kümenin yansız tahmini **değildir**; bilerek.
En küçük kovada bile ölçülebilir bir sayı çıksın diye. İkisi karşılaştırılmaz.

### Altın veri nereden gelir

Kural motorundan. **Hiçbir aşamada bir dil modelinden gelmez.**

Açık Türkçe morfolojik çözümleyicilerin doğruluğu %38-72 aralığında ölçülmüştür;
böyle bir aracı altın kaynak yapmak külliyata %28-62 hata enjekte eder. Bu yüzden
keyfi kelimeyi çözümlemiyoruz — altını inşadan belli olan maddeyi üretiyoruz.
Sözlüksel düzensizlikler (hangi gövde yumuşar, hangisinde ünlü düşer)
[Zemberek](https://github.com/ahmetaa/zemberek-nlp) sözlüğünden gelir (Apache-2.0);
çözümleyicisi kullanılmaz.

Kural motorunun 282 elle yazılmış altın iddiası vardır ve hepsi geçer.

### Üç istisna kovası TDK ile doğrulanmıştır

`ünlü düşmesi`, `uyum kırıcı alıntı` ve `ünsüz ikizleşmesi` kovalarının
**317 maddesinin tamamının** altını [TDK Güncel Türkçe Sözlük](https://sozluk.gov.tr)
ile birebir karşılaştırılmıştır. Sözlüğün madde başından sonra verdiği çekim
ipucu (`kıraat, -ti`) altının kendisidir; TDK bir gövde için biçim vermiyorsa ya
da birden fazla veriyorsa (`hak` → *hakkı* / *hakki*) o gövde kıyasa alınmaz.

Bu denetimi yapma sebebimiz, insan tavanı ölçümünde katılımcıların `uyum kırıcı`
kovasında **şans düzeyinin altına** düşmesiydi. Ana dili Türkçe olan insanlar bir
kurala şanstan kötü uyuyorsa, sorun insanda değil altındadır. Üç sistematik hata
çıktı — olmayan yumuşamanın uygulanması (*bidadi*, doğrusu **bidati**),
ince/kalın uyumun kaçırılması (*aczı*, doğrusu **aczi**), ikizleşirken
ötümlüleşmenin atlanması (*retti*, doğrusu **reddi**) — hepsi sözlük
bayraklarının eksikliğinden. Düzeltmeden sonra ölçülen insan doğruluğu
5,6 puan yükseldi.

### İnsan tavanı — ilk ölçüm

**%88,2 [%83,1 – %91,8]** · 3 değerlendirici, 211 yargı · *toplama sürüyor*

Aynı maddeler ana dili Türkçe olan kişilere soruluyor
([morf.e-cloud.web.tr](https://morf.e-cloud.web.tr)). Bu bir **ön okumadır**:
örneklem küçük, aralık geniş ve sayı katılımcı geldikçe güncellenecek.

| kesit | doğruluk |
|---|---|
| gerçek gövde | %90,2 [%84,9 – %93,8] |
| **uydurma gövde** | **%78,4 [%62,8 – %88,6]** |
| ek zinciri (en zor) | %50,0 [%25,4 – %74,6] |

İnsanlar da uydurma gövdede düşüyor — yani kıyasın ölçtüğü zorluk yapaydan
ibaret değil. Ama düşüş 12 puan; modellerde ölçtüğümüz 22-32 puan.

**Katılımcı taraması.** Doğruluk sayısı elenmeden hesaplanmaz. İki ölçüt önceden
yazılır ve sonuca bakılarak değiştirilmez: soru başına medyan süre 3 saniyenin
altındaysa kişi soruyu okumuyordur; doğruluğu kendi şans düzeyini (gördüğü
maddelerin şık sayılarına göre hesaplanır) binom testiyle geçemeyen kişi bilgi
taşımıyordur. İlk turda 6 katılımcının 3'ü elendi.

**Bu ölçüm kıyasın kendi hatasını buldu.** İlk turda katılımcılar
`uyum_kirici` kovasında şans düzeyinin ALTINA düştü. Ana dili Türkçe olan
insanlar bir kurala şanstan kötü uyuyorsa sorun insanda değil altındadır —
TDK denetimi buradan çıktı. Düzeltmeden önce ölçülen insan doğruluğu %73,5'ti.


## Bağımsız dış sınav: UD ağaç bankaları

Kural motorunu kendi testleriyle sınamak döngüseldir — 282 altın iddiayı da biz
yazdık. Motor ayrıca **Universal Dependencies Türkçe ağaç bankalarına** karşı
koşuluyor (BOUN, IMST, Penn): başka ekiplerin elle etiketlediği, hakemli,
bizim hiçbir şekilde etkilemediğimiz veri.

UD her kelimenin yüzey biçimini, sözlük biçimini ve biçimbirim özniteliklerini
verir (`kitabı / kitap / Case=Acc|Number=Sing`); bu, bizim çağrımızın tam
karşılığıdır. Üç bankanın da aynı etiketlediği **25.681 (gövde, yuva)** çifti
karşılaştırıldı:

| ölçü | oran |
|---|---|
| ham uyum (UD metnini birebir tutturma) | **%91,5** |
| çekim uyumu (kesme/düzeltme imi normalleşmiş) | **%93,9** |

Aradaki fark yazımdandır: UD özel adlarda kesme işareti kullanıyor (`bey'in`),
bazı bölümleri Türkçe harfsiz (`baliklarinin`), düzeltme imi bankadan bankaya
değişiyor. İkisi ayrı raporlanır; tek bir sayıya indirmek farkı gizler.

**Bu sınav dört gerçek motor hatası buldu ve hepsi düzeltildi:**

| hata | UD'de | bizde |
|---|---|---|
| çokluk + 3. çoğul iyelik `-lAr`ı iki kez yazıyordu | gözlerini | ~~gözlerlerini~~ |
| vasıta hâli iyelikten sonra zamir n'si alıyordu | hedefiyle | ~~hedefinle~~ |
| `su`/`ne` kaynaştırmada y yerine s alıyordu | suyunu | ~~susunu~~ |
| düzeltme imli ünlüler (â î û) envanterde yoktu | rüzgâra | ~~rüzgâre~~ |

Sonuncusu en genişi: `â` görünmez olduğu için `rüzgâr`ın son ünlüsü `ü`
sanılıyor ve ince ek geliyordu. Düzeltmeden sonra UD uyumu 3,5 puan yükseldi.


### Şıklar karıştırılmıştır

`secenek` listesinde altın rastgele bir konumda durur ve `altin_sira` kaçıncı
olduğunu söyler. Karıştırma madde kimliğinden türetilir: aynı madde her
üretimde aynı sırayı alır, sürümler arası karşılaştırma bozulmaz.

Bu 3.2.1'den önce böyle değildi — altın her maddede birinci şıktı. Zorunlu
seçim kipinde şıklar tek tek puanlandığı için sıra sonucu etkilemiyordu ve
gözden kaçmıştı; ama şıkları A/B/C diye harflendiren bir protokolde hep "A"
demek %100 verirdi. İç tutarlılık denetimiyle yakalandı.

Aynı denetim ikinci bir kusur daha buldu: uydurma gövde üretici yalnız iki
sözlük dosyasına bakıyordu, eskimiş ve gayriresmî sözlüklerdeki yirmi gövde
"uydurma" sayılıp kıyasa girmişti. Wug testinin tek işi gövdenin hiçbir
külliyatta geçmemesini garanti etmek; denetim artık bütün sözlüklere bakıyor.

### Kullanım

```bash
# yerel ağırlıklar
turkmorfbench olc --model ecloudtech/Erk-32B

# OpenAI uyumlu uç (vLLM, llama.cpp server, TGI…)
turkmorfbench olc --uc http://localhost:8000/v1 --model erk --isci 16

# tam katman, yalnız uydurma gövdeler, JSON rapor
turkmorfbench olc --model X --katman tam --govde uydurma --cikti rapor.json

# yalnız istisna kovaları
turkmorfbench olc --model X --kova istisna_unlu_dusmesi istisna_ikizlesme

turkmorfbench bilgi
```

İki kip vardır. **Zorunlu seçim** birincildir: altın biçim ile kural ihlali
çeldiricileri arasından log-olasılıkla seçtirilir, ayrıştırma yoktur. **Serbest
üretim** ikincildir ve "okunamadı" ile "yanlış" ayrı sayılır — bu ayrım olmadan
bir ölçümümüz elli puan yanılmıştı.

---

## English

### What it measures

Turkish is agglutinative and suffix selection follows strict rules: two-way and
four-way vowel harmony, consonant assimilation, consonant lenition, buffer
consonants. On top of these sit lexical exceptions (`burun → burnu`,
`kalp → kalbi`, `ret → reddi`) and pronunciation-driven suffixes
(`TCDD'yi`, `2026'da` — the suffix follows how the number is *read*).

TurkMorfBench measures each of these separately and tells you **which one fails**.

### Why nonce (wug) stems

Producing the right suffix on a real word can be memorisation — a model has seen
*kitabı* tens of thousands of times. A nonce stem (*zakak*, *vısep*) appears in no
corpus; the model can only inflect it from the **rule**. We measure a 22-32 point
gap between real and nonce stems: models are largely using lexical neighbourhood,
not rules.

### Designed coverage, not sampled coverage

The axes that determine suffix selection are crossed **first** — final vowel (8) ×
final-sound class (8) × syllable count (3) × internal harmony (2) = **320 cells** —
and stems are then generated to fill them. **33 of those cells contain no real
Turkish word at all**, so a benchmark built from real words is structurally blind
there. Models score 22-23 points worse in those cells even after matching
phonological composition.

### Gold data never comes from a language model

Published open Turkish morphological analysers measure 38-72% accuracy; using one
as ground truth would inject 28-62% error. Instead of *analysing* arbitrary words
we *generate* items whose gold form follows by construction. Lexical irregularity
flags come from the [Zemberek](https://github.com/ahmetaa/zemberek-nlp) dictionary
(Apache-2.0); its analyser is not used. The rule engine carries 282 hand-written
gold assertions, all passing.

### The exception buckets are verified against TDK

All 317 items in the vowel-drop, inverse-harmony and consonant-doubling buckets
carry a gold form checked character-for-character against the
[TDK Güncel Türkçe Sözlük](https://sozluk.gov.tr). We ran this audit because
native speakers scored **below chance** on the inverse-harmony bucket in the
human-ceiling study — when native speakers do worse than guessing, the gold is
what needs checking, not the speakers. It found three systematic errors inherited
from incomplete lexicon flags (*bidadi* → **bidati**, *aczı* → **aczi**,
*retti* → **reddi**). Measured human accuracy rose 5.6 points after the fix.

### Human ceiling — first measurement

**88.2% [83.1 – 91.8]** · 3 raters, 211 judgments · *collection ongoing*

The same items are put to native speakers at
[morf.e-cloud.web.tr](https://morf.e-cloud.web.tr). This is a **preliminary
reading**: the sample is small, the interval wide, and the figure will be updated
as more raters finish. Humans score 90.2% on real stems and 78.4% on nonce stems
— a 12-point gap, against the 22-32 points we measure on models, so the
real/nonce difficulty is not an artefact.

Raters are screened before the number is computed, on two criteria fixed in
advance: a median of under 3 seconds per question means the question was not
read, and accuracy that fails to beat the rater's own chance level on a binomial
test carries no information. Three of the first six raters were screened out.

**This measurement found the benchmark's own error.** In the first round native
speakers scored *below chance* on the inverse-harmony bucket, which is what
prompted the TDK audit. Before the correction the measured human ceiling was
73.5%.


### Independent external check: UD treebanks

Testing the rule engine against its own assertions is circular — we wrote those
too. The engine is therefore also run against the **Universal Dependencies
Turkish treebanks** (BOUN, IMST, Penn): hand-annotated, peer-reviewed data from
other teams that we had no hand in. On the 25,681 (lemma, slot) pairs all three
treebanks annotate identically, the engine reproduces the attested surface form
for **91.5%** verbatim and **93.9%** once spelling is normalised (UD uses
apostrophes on proper nouns, some sections are ASCII-folded, circumflex usage
differs between treebanks).

The check found four real engine bugs, all fixed: `-lAr` written twice in the
plural + 3rd-person-plural possessive slot (*gözlerlerini* → **gözlerini**), the
pronominal *n* wrongly inserted before the instrumental (*hedefinle* →
**hedefiyle**), the irregular buffer on `su`/`ne` (*susunu* → **suyunu**), and
circumflex vowels (â î û) missing from the vowel inventory, which made the
engine read the wrong vowel as final (*rüzgâre* → **rüzgâra**).

### Two tiers

`cekirdek` (1,856 items, bucket-balanced, runs in minutes, for diagnosis) and
`tam` (465,241 items, for the headline number). The core tier is deliberately
*not* an unbiased sample of the full set — it is balanced so that even the
smallest bucket yields a measurable estimate. Do not compare the two.

### Modes

Forced choice is primary: gold versus rule-violation distractors, scored by
log-likelihood, no output parsing. Free generation is secondary and reports
"unreadable" separately from "wrong" — without that distinction one of our own
measurements was off by fifty points.

---

## Citation

```bibtex
@misc{turkmorfbench2026,
  title  = {TurkMorfBench: A Diagnostic Morphology Benchmark for Turkish Language Models},
  author = {{eCloud Tech.}},
  year   = {2026},
  url    = {https://github.com/ecloudtechnology/turkmorfbench}
}
```

**Data:** [huggingface.co/datasets/ecloudtech/TurkMorfBench](https://huggingface.co/datasets/ecloudtech/TurkMorfBench)
**Code:** [github.com/ecloudtechnology/turkmorfbench](https://github.com/ecloudtechnology/turkmorfbench)

Keywords: Turkish NLP, Türkçe doğal dil işleme, morphology benchmark, morfoloji
kıyası, vowel harmony, ünlü uyumu, wug test, agglutinative languages, LLM
evaluation, dil modeli değerlendirme, tokenizer analysis, subword segmentation.
