# TurkMorfBench v3

**466.434 madde · 14 kova · uydurma gövde kontrollü · teşhis raporlu**
**466,434 items · 14 buckets · wug-controlled · diagnostic reporting**

[eCloud Tech.](https://www.e-cloud.web.tr) · kod Apache-2.0 · veri CC BY 4.0

```bash
pip install turkmorfbench
turkmorfbench olc --model YOUR/MODEL
```

```python
from datasets import load_dataset
d = load_dataset("ecloudtech/TurkMorfBench", "cekirdek")   # 1.856 madde
d = load_dataset("ecloudtech/TurkMorfBench", "tam")        # 466.434 madde
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
| `ek_zinciri` | 9.544 | 1'den 8'e derinlik, ek sırası |
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
| `istisna_kaynastirma_istisna` | 2 | suyu, neyi |
| **toplam** | **466.434** | 14 kova |

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
| `tam` | 466.434 | tasarlanan kapsamın tamamı, manşet sayı için |

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

### 3.5.0: `ek_zinciri` kovası düzeltildi — kıyasın kendi hatası

Beş farklı model derinlik 2/3/5/7'de **tam %0**, 6/8'de ~%100 alıyordu. Bu bir
model özelliği olamaz; kova tasarımının artefaktıydı. Önceki çeldiriciler "bir
basamak eksik" ve "bir basamak fazla" biçimlerdi — ikisi de **dilbilgisel**.
İstem hedef derinliği söylemediği için model en olası *geçerli* biçimi seçiyor
ve bu yanlış sayılıyordu. Çeldiriciler artık diğer kovalardaki gibi kural
**ihlali**: aynı derinlikte uyum bozulmuş (*temerrütlerımız*), sahte kaynaştırma
(*temerrütleryimiz*), sıra bozuk. Derinlik-1 maddeleri de bu sayede kovaya
girdi (8.351 → 9.544). Bu düzeltme bütün modelleri eşit etkiler; 3.4.x ile
alınan `ek_zinciri` sayıları karşılaştırılamaz, diğer 13 kova değişmedi.

### Morfoloji ≠ yetenek: aynı modeller iki ölçekte

Bu kıyasta bir 2B model 32B'yi yakalayabilir. Bunun ne anlama geldiğini
söylemek için aynı modelleri **aynı sabit betikle** TurkishMMLU'nun 652 temiz
sorusunda da ölçtük (şık sırası dondurulmuş, kirli 113 soru dışarıda):

| model | TurkMorfBench 3.5 çekirdek | TurkishMMLU (652) |
|---|---|---|
| kanarya-2b | 77,3 | **22,9** |
| turkish-gpt2-large (0,8B) | 76,9 | **18,4** |
| Kumru-2B | 76,8 | **19,6** |
| Erk-32B | 75,2 | **71,0** |
| Qwen3-32B (taban) | 73,3 | 67,6 |

TurkishMMLU beş şıklıdır; şans %20. Sıfırdan Türkçe külliyatla eğitilen küçük
modeller morfolojide 32B ile **istatistiksel olarak beraber**, genel yetenekte
ise **şans düzeyinde**. Bu, kıyasın ölçtüğü şeyin tanımıdır: TurkMorfBench
akıl yürütmeyi değil, **Türkçe biçim bilgisini** ölçer — ve biçim bilgisi
parametre sayısıyla değil, görülen Türkçe jeton sayısıyla ölçeklenir. Bu
yüzden kıyas tek başına "hangi model iyi" sorusuna cevap vermez; genel yetenek
ölçüsüyle **birlikte** okunmalıdır. Sıralamayı yayımlarken bu sütunu yanına
koyuyoruz.

### Altı kural, aynı sıralama — ve iki kuralın çöktüğü yer

3.4.0'daki duyarlılık altyapısı 16 modelde koşuldu. `harf` ile `esli` (ikili
karşılaştırma) her modelde birebir aynı doğruluğu veriyor; `ham` ve `jeton`
aynı sıralamayı 1–3 puan düşük düzeyde koruyor. Yani bulgular puanlama kuralına
bağlı değil. `pmi` ve `pmi_harf` ise 21–51 aralığına çöküyor: koşulsuz olasılıkla
normalleştirmek, ortak gövdeyi paylaşan adaylar arasında ayrımı yok ediyor. Bu
iki kural bu görev için uygun değildir; pakette kalıyorlar ki okuyucu bunu
kendisi görebilsin.

Tasarım etkisi (hücre kümeli / madde düzeyi aralık genişliği) modelden modele
1,2× ile 4,7× arasında değişiyor. En yükseği Erk modellerinde: hücreler arası
varyansı yüksek, yani bazı kural hücrelerinde çok güçlü bazılarında zayıf.
Kumru-2B'de 1,2× — düz bir profil. Aynı ortalama, farklı biçim.

### İnsan tavanı — ikinci ölçüm

**%78.2 [%70.4 – %83.2]** · 6 geçerli değerlendirici, 560 yargı · *toplama sürüyor*

Aynı maddeler ana dili Türkçe olan kişilere soruluyor
([morf.e-cloud.web.tr](https://morf.e-cloud.web.tr)). Bu hâlâ bir **ön
okumadır**: örneklem küçük, aralık geniş ve sayı katılımcı geldikçe
güncellenecek. Aralık **fonolojik hücre** kümeli önyüklemeyle verilmiştir;
madde düzeyinde hesaplansa %74.6–%81.8 çıkardı, çünkü aynı hücreye bağlı
maddeler bağımsız gözlem değildir.

**Önceki sürümde bildirdiğimiz %88,2 [83,1–91,8] geri çekilmiştir.** İki sebebi
var ve ikisi de bizim tarafımızda: (1) o sayı 3 değerlendiriciye dayanıyordu;
altıya çıkınca dağılım genişledi — geçerli kişilerin tek tek doğrulukları %96.7, %85.1, %84.5, %75.0, %68.6, %53.2'dir, yani "tavan" tek bir sayıdan çok bir yelpaze.
(2) o ölçümün yapıldığı madde havuzunun 520 maddesinden 257'si güncel kıyas
verisinde yoktu — havuz bir önceki üretimden alınmıştı. Havuz 24 Eylül 2026'da
güncel veriden yeniden kuruldu; artık her madde kıyasta karşılığı olan bir
maddedir ve gövde/hücre kümelemesi yapılabilmektedir.

| kesit | doğruluk | n |
|---|---|---|
| gerçek gövde | %79.5 [%75.8 – %82.9] | 531 |
| uydurma gövde | %55.2 [%34.5 – %74.1] | 29 |

**Uydurma gövdedeki insan performansı hakkında henüz bir şey söylemiyoruz.**
Önceki sürümde bildirdiğimiz "insan düşüşü 12 puan" iddiası da geri
çekilmiştir: o sayı da, buradaki 24.3 puanlık nokta tahmini de onlarca yargıya
dayanıyor ve aralık her iki yönde de sonuca izin vermiyor. Uydurma gövde
karşılaştırması ancak ikisinin de bulunduğu kovalarda (`ad_cekimi`, `ad_yuva`,
`ek_zinciri`) eşleştirilmiş olarak anlamlıdır; havuz bu amaçla her birinde 20
gerçek + 20 uydurma olacak şekilde dengelendi, ama yeterli yargı henüz
birikmedi.

**Katılımcı taraması — ölçümü koruyan asıl savunma.** Doğruluk sayısı elenmeden
hesaplanmaz. Üç ölçüt önceden yazılır ve sonuca bakılarak değiştirilmez: en az
10 cevap; soru başına medyan süre 3 saniyenin altındaysa kişi soruyu
okumuyordur; doğruluğu kendi şans düzeyini (gördüğü maddelerin şık sayılarına
göre hesaplanır) tek yönlü binom testiyle α = 0,001'de geçemeyen kişi bilgi
taşımıyordur.

Bu tarama boşuna değil: **12 katılımcının 6'sı elendi**, beşi hız ölçütünden.
Bir katılımcı 111 soruyu **36 saniyede** cevaplamıştı — soru başına 0,3 saniye.
Hızdan elenen beş kişinin beşi aynı zamanda şans düzeyindeydi; iki bağımsız
ölçüt aynı kişileri gösteriyor. Süre hesabında sıfır saniyelik aralıklar
atılmaz: zaman damgaları saniye çözünürlüğünde olduğu için hızlı tıklamanın
kanıtı tam da o sıfırlardır.

**Model ile insan, aynı maddelerde.** 25 Eylül 2026'da 13:48–14:09 (UTC)
arasında 50 oturum kaydoldu (bir dakikada 16 kayıt), her biri tam 156 madde
cevapladı ve her oturumun 156 cevabı **aynı saniyede** yazıldı. Sunucu
günlüğündeki istemci kimliği kendini tanıtıyordu: `eCloud koşumu/1.0
eCloud değerlendirme koşumu). Elli oturumun ikili cevap uyumu 1,00 —
tek bir deterministik dil modeli, 50 farklı 156'lık dilimle. Hız ölçütü
ellisini de eledi; oturumlar veritabanında `sentetik_oturum` olarak
işaretlendi ve dışa aktarımda **yapısal olarak** dışlanır. Bu olay olmasaydı
"insan tavanı" bir LLM tavanına dönüşürdü: aynı 515 maddede o modelin puanı
%69,9, geçerli insanların %79,1. Kalabalık-kaynaklı her kıyas için tehdit
modeli budur ve savunması eleme kuralıdır, .

Yayımlanan sayıların tamamı `insan_ozet.py` tarafından üretilir; eşikler
betiğin içinde yazılıdır.

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

### 3.5.0: the `ek_zinciri` bucket was fixed — the benchmark's own error

Five different models scored **exactly 0%** at depths 2/3/5/7 and ~100% at 6/8.
That cannot be a model property; it was an artefact of the bucket design. The
old distractors were "one step fewer" and "one step more" — both **grammatical**
forms. Since the prompt does not state the target depth, a model picks the most
probable *valid* form and is marked wrong. Distractors are now rule
**violations**, as in every other bucket: broken harmony at the same depth
(*temerrütlerımız*), a spurious buffer consonant (*temerrütleryimiz*), wrong
order. Depth-1 items now enter the bucket as well (8,351 → 9,544). The fix
affects every model equally; `ek_zinciri` figures from 3.4.x are not comparable,
the other 13 buckets are unchanged.

### Morphology ≠ capability: the same models on two scales

On this benchmark a 2B model can match a 32B one. To say what that means, we
measured the same models with the **same pinned script** on the 652 clean
TurkishMMLU questions (option order frozen, 113 contaminated items removed):

| model | TurkMorfBench 3.5 core | TurkishMMLU (652) |
|---|---|---|
| kanarya-2b | 77.3 | **22.9** |
| turkish-gpt2-large (0.8B) | 76.9 | **18.4** |
| Kumru-2B | 76.8 | **19.6** |
| Erk-32B | 75.2 | **71.0** |
| Qwen3-32B (base) | 73.3 | 67.6 |

TurkishMMLU is five-way; chance is 20%. Small models trained from scratch on
Turkish are **statistically tied** with a 32B model on morphology and **at
chance** on general capability. That is the definition of what this benchmark
measures: not reasoning but **Turkish form knowledge**, which scales with the
number of Turkish tokens seen, not with parameter count. The benchmark alone
therefore does not answer "which model is better"; it must be read **alongside**
a capability measure, and we publish that column next to the ranking.

### Six rules, one ranking — and where two rules collapse

The 3.4.0 sensitivity machinery was run on 16 models. `harf` and `esli`
(pairwise) give identical accuracy for every model; `ham` and `jeton` preserve
the same order 1–3 points lower. The findings do not depend on the scoring rule.
`pmi` and `pmi_harf` collapse to 21–51: normalising by the unconditional
probability erases the distinction between candidates that share a stem. Those
two rules are unsuitable for this task; they stay in the package so readers can
see it for themselves.

The design effect (cell-clustered vs item-level interval width) ranges from 1.2×
to 4.7× across models. It is highest for the Erk models — high between-cell
variance, strong in some rule cells and weak in others. Kumru-2B sits at 1.2×, a
flat profile. Same mean, different shape.

### Human ceiling — second measurement

**78.2% [70.4 – 83.2]** · 6 valid raters, 560 judgments · *collection ongoing*

The same items are put to native speakers at
[morf.e-cloud.web.tr](https://morf.e-cloud.web.tr). This is still a
**preliminary reading**: the sample is small, the interval wide, and the figure
will be updated as more raters finish. The interval comes from a
**phonological-cell cluster bootstrap**; computed per item it would read
74.6–81.8%, because items sharing a cell are not independent observations.

**The 88.2% [83.1–91.8] reported in an earlier release is withdrawn.** Two
reasons, both on our side: (1) that figure rested on 3 raters; with 6 the spread
widened — the individual accuracies of the valid raters are 96.7%, 85.1%, 84.5%, 75.0%, 68.6%, 53.2%, so the "ceiling" is a spread rather than a point. (2) 257 of
the 520 items in the pool used for that measurement did not exist in the current
benchmark data; the pool had been drawn from an earlier generation. It was
rebuilt from current data on 24 September 2026, so every item now corresponds to
a benchmark item and stem/cell clustering is possible.

| slice | accuracy | n |
|---|---|---|
| real stems | 79.5% [75.8 – 82.9] | 531 |
| nonce stems | 55.2% [34.5 – 74.1] | 29 |

**We make no claim about human performance on nonce stems yet.** The earlier
"12-point human drop" claim is also withdrawn: that figure, and the 24.3-point
point estimate here, both rest on a few dozen judgments and the interval permits
no conclusion in either direction. The real/nonce contrast is only meaningful as
a matched comparison inside the buckets that contain both (`ad_cekimi`,
`ad_yuva`, `ek_zinciri`); the pool was rebalanced to 20 real + 20 nonce in each,
but enough judgments have not yet accumulated.

**Rater screening — the defence that protects the measurement.** The accuracy
figure is not computed before screening. Three criteria are fixed in advance and
never adjusted after seeing the result: at least 10 answers; a median of under
3 seconds per question means the question was not read; and accuracy that fails
to beat the rater's own chance level (computed from the option counts of the
items they saw) on a one-sided binomial test at α = 0.001 carries no
information.

The screening is not decorative: **6 of 12 raters were removed**, five of them on
the speed criterion. One had answered 111 questions in **36 seconds** — 0.3 s per
question. All five speed-removed raters were also at chance level; two
independent criteria point at the same people. Zero-second gaps are not discarded
when computing the median: timestamps have one-second resolution, so those zeros
are precisely the evidence of click-through.

**Model and humans on the same items.** Between 13:48 and 14:09 UTC on
25 September 2026, 50 sessions registered (16 in a single minute), each
answered exactly 156 items, and every session's 156 answers were written in
**the same second**. The client identified itself in the server log:
`eCloud değerlendirme koşumu`. Pairwise answer
agreement across the 50 sessions was 1.00 — one deterministic language model
over 50 different 156-item slices. The speed criterion removed all fifty; the
sessions are flagged as `sentetik_oturum` in the database and excluded
**structurally** at export. Without this, the "human ceiling" would have become
an LLM ceiling: on the same 515 items that model scores 69.9%, the valid humans
79.1%. This is the check for any crowd-sourced benchmark, and the defence
is the screening rule, .

Every published figure is produced by `insan_ozet.py`; the thresholds are written
into the script.

### Confidence intervals: 466,434 items are NOT 466,434 independent observations

Items are not generated independently. One stem (*kitap*) yields dozens of items
across the plural × possessive × case cross; one phonological cell (final vowel,
final-consonant class, depth, harmony) binds hundreds of stems to the same rule.
A model that misses lenition on *kitap* misses it across most items derived from
that stem.

Item-level bootstrap ignores this: it treats each item as a separate observation,
overstates the sample, and returns intervals that are too narrow. That is false
precision, and it is the easiest place to challenge a published figure.

`turkmorfbench.istatistik` moves the resampling unit from the item to the
**cluster**. In the full set:

| unit | clusters | items per cluster |
|---|---|---|
| stem | 32,140 | median 16 |
| **phonological cell** | **441** | median 247, largest 18,594 |

The difference is not cosmetic. Under a pattern where model competence varies at
the rule level — which is exactly what the benchmark sets out to measure — the
design effect we measured is:

| clustering | interval width | effective n |
|---|---|---|
| item | ±0.12 pt | 466,434 |
| stem | 2.0× | 118,274 |
| **phonological cell** | **30.8×** | **491** |

Those figures come from a simulation; the real design effect depends on how
correlated a real model's errors are within a cell. `tasarim_etkisi()` measures
and reports it for every run.

Comparing two models by checking whether two separate intervals overlap is wrong:
it throws away the paired design and can hide a real difference. `esli_fark()`
resamples the difference directly.

### Is the result an artefact of the scoring rule?

The scoring rule changed in 3.3.0 (see `olcum.py`) and the residual length bias
was not hidden: the gold is shortest in 29.9% of items with unequal candidate
lengths, while the chosen rule picks the shortest 39–43% of the time. That is not
the real question. The real question is whether the **result** changes when the
rule changes.

`turkmorfbench.duyarlilik` runs the model **once**, stores the raw sum, token
count, character count and unconditional probability per candidate, and derives
six rules from those three quantities: `ham` (raw), `jeton` (per token), `harf`
(per character — the 3.3.0 choice), `pmi`, `pmi_harf` and `esli` (pairwise
contrastive, Copeland). The model is not run six times.

The output states whether the **sign of the difference between two systems is the
same under all six rules**. If it is, the residual length bias does not carry the
finding; if it is not, we learn which finding depends on the rule before the
reader does.

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

### Güven aralığı: 466.434 madde, 466.434 bağımsız gözlem DEĞİLDİR

Kıyastaki maddeler birbirinden bağımsız üretilmez. Tek bir gövde (*kitap*)
çokluk × iyelik × hâl çaprazından onlarca madde doğurur; tek bir fonolojik hücre
(son ünlü, son ünsüz sınıfı, derinlik, uyum) yüzlerce gövdeyi aynı kurala bağlar.
Bir model *kitap* gövdesinde yumuşamayı kaçırıyorsa, o gövdeden türeyen
maddelerin çoğunda birlikte kaçırır.

Madde düzeyinde klasik önyükleme bunu görmezden gelir: her maddeyi ayrı bir gözlem
sayar, örneklemi olduğundan büyük gösterir ve aralığı gereğinden daraltır. Bu,
sahte kesinliktir ve yayımlanan bir sayının en kolay çürütülen yeridir.

`turkmorfbench.istatistik` yeniden örnekleme birimini maddeden **kümeye** taşır.
Kümeler tam veri kümesinde şöyle dağılır:

| birim | küme sayısı | küme başına madde |
|---|---|---|
| gövde | 32.140 | medyan 16 |
| **fonolojik hücre** | **441** | medyan 247, en büyüğü 18.594 |

Fark önemsiz değil. Model yetkinliğinin kural düzeyinde değiştiği bir örüntüde —
ki kıyasın ölçmeye çalıştığı tam olarak budur — ölçtüğümüz tasarım etkisi şudur:

| kümeleme | aralık genişliği | etkin n |
|---|---|---|
| madde | ±0,12 puan | 466.434 |
| gövde | 2,0 kat | 118.274 |
| **fonolojik hücre** | **30,8 kat** | **491** |

Bu rakamlar bir benzetimden gelir; gerçek tasarım etkisi, gerçek bir modelin
hatalarının hücre içinde ne kadar ilintili olduğuna bağlıdır. `tasarim_etkisi()`
bunu her koşumda ölçer ve bildirir.

```python
from turkmorfbench.istatistik import kume_bootstrap, esli_fark, tasarim_etkisi
s = kume_bootstrap(maddeler, dogru, anahtar="hucre")     # gövde / hücre / gövde_görev
f = esli_fark(maddeler, a_dogru, b_dogru, anahtar="govde")   # iki sistemin FARKI
```

İki modeli karşılaştırırken iki ayrı aralığa bakıp "çakışıyor mu" demek yanlıştır:
eşli tasarımın gücünü atar ve gerçek farkı gizleyebilir. `esli_fark()` farkı
doğrudan örnekler.

### Sonuç puanlama kuralına bağlı mı

3.3.0'da puanlama kuralı değişti (bkz. `olcum.py`) ve kalan uzunluk yanlılığı
gizlenmedi: altın, uzunlukları farklı maddelerde %29,9 oranında en kısadır,
seçilen kural %39–43 oranında en kısayı seçer. Asıl soru bu değil — asıl soru,
kural değişince **sonucun** değişip değişmediğidir.

`turkmorfbench.duyarlilik` modeli **bir kez** koşturur, her aday için ham toplam,
jeton sayısı, karakter sayısı ve koşulsuz olasılığı saklar, ve altı kuralı bu üç
büyüklükten türetir: `ham`, `jeton`, `harf` (3.3.0'da seçilen), `pmi`,
`pmi_harf` ve `esli` (ikili karşılaştırma, Copeland). Model altı kez koşmaz.

```python
from turkmorfbench.duyarlilik import bilesen_topla, karsilastir, rapor
ka = bilesen_topla(arka_a, maddeler)
kb = bilesen_topla(arka_b, maddeler)
print(rapor(karsilastir(ka, kb, maddeler, "A", "B", anahtar="hucre"), "A", "B"))
```

Çıktı, iki sistemin farkının **yönünün altı kuralın hepsinde aynı olup olmadığını**
söyler. Aynıysa kalan uzunluk yanlılığı bulguyu taşımıyor demektir; değilse hangi
bulgunun kurala bağlı olduğunu okuyucudan önce biz bilmiş oluruz.
