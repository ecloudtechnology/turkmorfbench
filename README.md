# TurkMorfBench v3

**465.241 madde · 14 kova · uydurma gövde kontrollü · teşhis raporlu**
**465,241 items · 14 buckets · wug-controlled · diagnostic reporting**

[eCloud Tech.](https://www.e-cloud.web.tr) · kod Apache-2.0 · veri CC BY 4.0

```bash
pip install turkmorfbench
turkmorfbench olc --model YOUR/MODEL
```

```python
from datasets import load_dataset
d = load_dataset("ecloudtech/TurkMorfBench", "cekirdek")   # 1.856 madde
d = load_dataset("ecloudtech/TurkMorfBench", "tam")        # 465.241 madde
```

---

## Ne ölçüyor

Türkçe sondan eklemelidir ve ek seçimi katı kurallara bağlıdır: büyük ve küçük
ünlü uyumu, ünsüz benzeşmesi, ünsüz yumuşaması, kaynaştırma. Üstüne sözlüksel
istisnalar biner (`burun → burnu`, `kalp → kalbi`, `ret → reddi`) ve okunuşa
bağlı ekler gelir (`TCDD'yi`, `2026'da`).

Bu kıyas hepsini **ayrı ayrı** ölçer ve hangisinde düşüldüğünü söyler.

| Kova | Madde | Ne sınıyor |
|---|---|---|
| `ad_yuva` | 283.360 | çokluk + iyelik + hâl yığını, **zamir n'si** |
| `ad_cekimi` | 166.307 | 7 hâl, uyum, benzeşme, yumuşama, kaynaştırma |
| `ek_zinciri` | 8.351 | 1'den 8'e derinlik, ek sırası |
| `fiil_cekimi` | 1.792 | 7 zaman/kip, olumsuzluk, **geniş zaman istisnaları** |
| `yapim_eki` | 1.477 | -lIk, -CI, -lI, -sIz, -sAl, -lAş, -lA |
| `istisna_ozel_ad` | 1.200 | kesme işareti, **yumuşamama** (Sinop'a) |
| `istisna_birlesik_isim` | 896 | buzdolabına |
| `cati` | 728 | edilgen, dönüşlü, işteş, ettirgen |
| `istisna_sayi` | 507 | **okunuşa göre** ek (2026'da) |
| `istisna_kisaltma` | 304 | **okunuşa göre** ek (TCDD'yi) |
| `istisna_unlu_dusmesi` | 177 | burnu, aklı, nakdi · **TDK doğrulamalı** |
| `istisna_uyum_kirici` | 105 | kalbi, rolü, kıraati · **TDK doğrulamalı** |
| `istisna_ikizlesme` | 35 | reddi, tıbbı, zıddı · **TDK doğrulamalı** |
| `istisna_kaynastirma` | 2 | suyu, neyi |

## Madde biçimi

```json
{
  "kimlik": "6c4f2594d126",
  "kova": "ad_yuva",
  "gorev": "cog-3t-bulunma",
  "govde": "içtimaiyat",
  "altin": "içtimaiyatlarında",
  "celdirici_tur":   ["zamir_n", "uyum"],
  "celdirici_bicim": ["içtimaiyatlarıda", "içtimaiyatlarınde"],
  "secenek": ["içtimaiyatlarıda", "içtimaiyatlarında", "içtimaiyatlarınde"],
  "altin_sira": 1,
  "gercek": true,
  "hucre": ["a", "t", 3, "kirik"],
  "bayrak": []
}
```

**Çeldiriciler rastgele değil.** Her biri tek bir kuralı bozar, adı da o kuraldır.
Model `içtimaiyatlarıda` seçtiyse zamir n'sini bilmiyor; `içtimaiyatlarınde`
seçtiyse ünlü uyumunu. Tek bir doğruluk sayısı bunu söylemez.

`hucre` alanı ses ortamını taşır: (son ünlü, son ses sınıfı, hece sayısı,
iç uyum). `bayrak` sözlüksel düzensizlikleri (`LastVowelDrop`, `Doubling`,
`InverseHarmony`, `CompoundP3sg`).

## Uydurma (wug) gövde

Gerçek kelimede doğru ek üretmek ezberle de mümkündür. Uydurma gövde
(*zakak*, *vısep*, *sövot*) hiçbir külliyatta geçmez; model doğru eki ancak
**kuralı** biliyorsa üretir.

Ölçtük: modeller gerçek ile uydurma gövde arasında **22-32 puan** fark veriyor.

## Ses ortamı kapsam dizeyi

Ek seçimini belirleyen eksenler önce çaprazlanır, gövdeler sonra üretilir:
son ünlü (8) × son ses sınıfı (8) × hece sayısı (3) × iç uyum (2) = **320 hücre**.

**33 hücrede Türkçede gerçek kelime yoktur.** Gerçek kelimelerden kurulan bir
kıyas oraları sınayamaz. Ölçtük: modeller o hücrelerde, ses bileşimi
eşleştirildikten sonra bile **22-23 puan** daha kötü.

## İki katman

| Katman | Madde | Kimin için |
|---|---|---|
| `cekirdek` | 1.856 | dakikalar içinde koşar, **kova dengeli**, teşhis için |
| `tam` | 465.241 | tasarlanan kapsamın tamamı, manşet sayı için |

Çekirdek kova dengelidir; tam kümenin yansız tahmini **değildir** ve öyle
olması amaçlanmamıştır. En küçük kovada bile ölçülebilir bir sayı çıksın diye.
**İkisi karşılaştırılmaz.**

## Altın veri nereden gelir

Kural motorundan. **Hiçbir aşamada bir dil modelinden gelmez.**

Açık Türkçe morfolojik çözümleyicilerin doğruluğu %38-72 ölçülmüştür; böyle bir
aracı altın kaynak yapmak külliyata %28-62 hata enjekte eder. Bu yüzden keyfi
kelimeyi çözümlemiyoruz, altını inşadan belli olan maddeyi üretiyoruz.
Sözlüksel düzensizlikler [Zemberek](https://github.com/ahmetaa/zemberek-nlp)
sözlüğünden gelir (Apache-2.0); çözümleyicisi kullanılmaz.

Kural motorunun **282 elle yazılmış altın iddiası** vardır ve hepsi geçer.

### Üç istisna kovası TDK ile doğrulanmıştır

`istisna_unlu_dusmesi`, `istisna_uyum_kirici` ve `istisna_ikizlesme` kovalarının
**317 maddesinin tamamının** altını [TDK Güncel Türkçe
Sözlük](https://sozluk.gov.tr) ile birebir karşılaştırılmıştır; sözlüğün madde
başından sonra verdiği çekim ipucu (`kıraat, -ti`) altının kendisidir. TDK bir
gövde için ek biçimi vermiyorsa ya da birden fazla biçim veriyorsa
(`hak` → *hakkı* / *hakki*) o gövde kıyasa **alınmaz**.

Bu doğrulamayı yapma sebebimiz, insan tavanı ölçümünde katılımcıların
`uyum_kirici` kovasında **şans düzeyinin altına** düşmesiydi. Ana dili Türkçe
olan insanlar bir kurala şanstan kötü uyuyorsa, sorun insanda değil altındadır.
Denetim üç sistematik hata çıkardı — olmayan yumuşamanın uygulanması
(*bidadi*, doğrusu **bidati**), ince/kalın uyumun kaçırılması (*aczı*, doğrusu
**aczi**), ikizleşirken ötümlüleşmenin atlanması (*retti*, doğrusu **reddi**).
Hepsi Zemberek'in bayraklarının TDK'ye göre eksik olmasından kaynaklanıyordu.
Düzeltmeden sonra ölçülen insan doğruluğu 5,6 puan yükseldi.

### TDK düzeltmesi bütün kovalara uygulanır

Doğru biçim yalnız istisna kovalarına yazılsaydı aynı gövdenin iki altını
olurdu — `kıraat` istisna kovasında `kıraati`, ad çekimi kovasında `kıraadi`.
Bunun yerine TDK'nin verdiği biçimden **sözlük bayrağı geri çıkarılır**
(`kıraat` → `InverseHarmony, NoVoicing`) ve motor her kovada, her hâlde, her ek
yığınında doğru biçimi üretir. 147 sözlük maddesi bu yolla düzeltildi.

Denetim kural motorunda da bir boşluk açığa çıkardı: ünlü düşmesi, yumuşama ve
ikizleşme birbirini dışlıyordu, oysa birlikte olabiliyorlar —
`nakit → nakdi` (ünlü düşer **ve** yumuşar), `ret → reddi` (yumuşar **ve**
ikizleşir). 24 gövde hiçbir bayrak kümesiyle üretilemiyordu ve hepsi bu iki
birleşimdendi.

TDK'nin verdiği biçim hiçbir bayrak kümesiyle üretilemiyorsa gövde kuralla
açıklanamıyor demektir ve kıyasa alınmaz (*raptı*, *veçhi* dahil altı gövde).

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


## Sınırlar — bunları biliyoruz ve yazıyoruz

- **Eş yazılışlı gövdeler kıyasa alınmadı**: çekim davranışları ayrıştığı için
  altın cevap tek olmuyor (genel kovalarda 278 gövde). Üç istisna kovasında
  hakem TDK'dir: sözlük tek bir biçim veriyorsa gövde kalır, vermiyor ya da
  birden fazla veriyorsa çıkar.
- **İstisna gövdelerinin yarısından çoğu TDK'nin güncel sözlüğünde yok**
  (*inhimak*, *meşihat*, *pirüpak* gibi arkaik alıntılar). O gövdeler bu
  sürümde kıyasa alınmadı; istisna kovaları artık yaşayan Türkçeyi ölçüyor.
- **Ettirgende 66 madde elendi**: tek heceli gerçek gövdelerde ek seçimi
  sözlükseldir ve açık istisna listemizde olmayanlar güvenilmez sayıldı.
- İstisna kovaları doğası gereği gerçek gövdelidir — uydurma bir kelimenin
  sözlüksel istisnası olamaz.

## Atıf

```bibtex
@misc{turkmorfbench2026,
  title  = {TurkMorfBench: A Diagnostic Morphology Benchmark for Turkish Language Models},
  author = {{eCloud Tech.}},
  year   = {2026},
  url    = {https://huggingface.co/datasets/ecloudtech/TurkMorfBench}
}
```

---

## English

### What it measures

Turkish is agglutinative and suffix selection follows strict rules: two-way and
four-way vowel harmony, consonant assimilation, consonant lenition and buffer
consonants — plus lexical exceptions (`burun → burnu`, `kalp → kalbi`,
`ret → reddi`) and pronunciation-driven suffixes (`TCDD'yi`, `2026'da`, where
the suffix follows how the abbreviation or number is *read*, not written).

The benchmark measures each separately and reports **which rule failed**.

### Distractors are rule violations, not noise

Every distractor breaks exactly one rule and is named after it. A model that
picks `içtimaiyatlarıda` does not know the pronominal *n*; one that picks
`içtimaiyatlarınde` does not know vowel harmony. A single accuracy number cannot
say this — this is what makes the benchmark diagnostic rather than a scoreboard.

### Nonce (wug) stems

Inflecting a real word can be memorisation. A nonce stem appears in no corpus, so
only the rule can produce the right form. Measured gap between real and nonce
stems: **22-32 points**.

### Designed coverage

The axes that determine suffix selection are crossed first (320 cells), and stems
are generated to fill them. **33 cells contain no real Turkish word at all** — a
real-word benchmark is structurally blind there, and models score 22-23 points
worse in exactly those cells even after matching phonological composition.

### The exception buckets are verified against TDK

All 317 items in `istisna_unlu_dusmesi`, `istisna_uyum_kirici` and
`istisna_ikizlesme` carry a gold form checked character-for-character against the
[TDK Güncel Türkçe Sözlük](https://sozluk.gov.tr), whose entries state the
inflected stem directly (`kıraat, -ti`). We ran this audit because native
speakers scored **below chance** on `uyum_kirici` in the human-ceiling study —
when native speakers do worse than guessing, the gold is what needs checking, not
the speakers. It found three systematic errors inherited from incomplete lexicon
flags: applying lenition where the dictionary forbids it (*bidadi*, correct
**bidati**), missing inverse harmony (*aczı*, correct **aczi**), and failing to
voice a doubled stop (*retti*, correct **reddi**). Measured human accuracy rose
5.6 points after the correction.

### Gold never comes from a language model

Published open Turkish morphological analysers measure 38-72% accuracy; using one
as ground truth would inject 28-62% error. Items are *generated* so that the gold
form follows by construction. Lexical irregularity flags come from the Zemberek
dictionary (Apache-2.0); its analyser is not used. The rule engine carries 282
hand-written gold assertions, all passing.

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


### Options are shuffled

The gold form sits at a random position in `secenek`, and `altin_sira` gives
its index. The shuffle is derived from the item id, so an item keeps its
ordering across regenerations.

Before 3.2.1 the gold was always the first option. Forced-choice scoring makes
the order irrelevant, which is why it went unnoticed — but any protocol that
letters the options A/B/C would have scored 100% by always answering A. An
internal consistency audit caught it, along with twenty stems marked as nonce
that were in fact present in the obsolete and informal dictionaries.

### Known limits

Homograph stems are excluded (their inflection is
context-dependent, so no single gold form exists) — 278 in the general buckets;
in the three exception buckets TDK arbitrates, and a stem is kept only when the
dictionary gives exactly one suffixed form. Over half of the flagged exception
stems are archaic loans absent from TDK's current dictionary and were dropped. 66 causative items were
excluded as lexically unreliable. Exception buckets are real-stem only by nature.

**Code:** [github.com/ecloudtechnology/turkmorfbench](https://github.com/ecloudtechnology/turkmorfbench) ·
**Package:** [pypi.org/project/turkmorfbench](https://pypi.org/project/turkmorfbench/)
