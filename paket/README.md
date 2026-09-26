# TurkMorfBench

**Turkish morphology benchmark for language models** — 466,517 items, diagnostic
reports, wug-test controls, tokenizer analysis.
**Dil modellerinin Türkçe morfoloji yetkinliğini ölçen kıyas** — 466.517 madde,
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

| Kova | Anahtar | Madde | Ne sınıyor |
|---|---|---|---|
| ad paradigma yuvaları | `ad_yuva` | 283.360 | çokluk + iyelik + hâl yığını, **zamir n'si** |
| ad çekimi | `ad_cekimi` | 166.424 | 7 hâl, ünlü uyumu, benzeşme, yumuşama, kaynaştırma |
| ek zinciri | `ek_zinciri` | 9.544 | 1'den 8'e derinlik, ek sırası |
| fiil çekimi | `fiil_cekimi` | 1.792 | 7 zaman/kip, olumsuzluk, **geniş zaman istisnaları** |
| yapım eki | `yapim_eki` | 1.477 | -lIk, -CI, -lI, -sIz, -sAl, -lAş, -lA |
| özel ad | `istisna_ozel_ad` | 1.200 | kesme işareti, **yumuşamama** (Sinop'a, Sinob'a değil) |
| birleşik isim | `istisna_birlesik_isim` | 896 | buzdolabına |
| çatı | `cati` | 728 | edilgen, dönüşlü, işteş, ettirgen |
| sayı | `istisna_sayi` | 507 | **okunuşa göre** ek (2026'da) |
| kısaltma | `istisna_kisaltma` | 304 | **okunuşa göre** ek (TCDD'yi) |
| ünlü düşmesi | `istisna_unlu_dusmesi` | 177 | burnu, aklı, nakdi · **TDK doğrulamalı** |
| uyum kırıcı alıntı | `istisna_uyum_kirici` | 71 | kalbi, rolü, kıraati · **TDK doğrulamalı** |
| ünsüz ikizleşmesi | `istisna_ikizlesme` | 35 | reddi, tıbbı, zıddı · **TDK doğrulamalı** |
| kaynaştırma istisnası | `istisna_kaynastirma_istisna` | 2 | suyu, neyi |
| **toplam** | | **466.517** | 14 kova |

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
| `cekirdek` | 1.836 | dakikalar içinde koşar, kova dengeli, **teşhis için** |
| `tam` | 466.517 | tasarlanan kapsamın tamamı, **manşet sayı için** |

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
**283 maddesinin tamamının** altını [TDK Güncel Türkçe Sözlük](https://sozluk.gov.tr)
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

### 3.6.0: ünlü düşmesinde uyum — kıyasın bir hatası daha

Kural kovaları için eğitim verisi üreteci yazılırken motorun bir hatası
ortaya çıktı: ünlü düşmesinde (*aciz → aczi*) ünlüyle başlayan ekin uyumu
**düşen ünlüden** değil, kalan tabanın son ünlüsünden alınıyordu (*acz* → *a* →
*aczı*). TDK denetimi bunu belirtme hâli için `InverseHarmony` bayrağı ekleyerek
"çözmüştü"; bayrak ise ünsüzle başlayan `-lAr`'a sızıyordu: *acizlarında*,
*ahitlarında* — yanlış Türkçe, doğrusu *acizlerinde*. Etkilenen: **34 gövde,
`ad_yuva`'da 136 yanlış altın**. Aynı 34 gövde bu sızan bayrak yüzünden
`istisna_uyum_kirici` kovasına da yanlış sınıflanmıştı; onlar ünlü-düşmesi
kelimeleridir.

Motor düzeltildi (uyum düşen ünlüyü izler; bayrağa gerek kalmadı), bayrak
araması yeniden koşuldu (501 TDK altınının 501'i yeniden üretildi, hiçbiri
kaybolmadı), kıyas yeniden üretildi: `ad_cekimi` +117, `istisna_uyum_kirici`
105 → 71, toplam 466.517, çekirdek 1.836. Diğer 12 kova değişmedi. 3.5.x ile
`ad_yuva`, `ad_cekimi` ve `istisna_uyum_kirici` sayıları karşılaştırılamaz.

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
3.6 çekirdeğinde 15 modelin 13'ü bu kovada ≥%96 (Qwen3.8-27B tabanı %85,7 ve
Trendyol v1.0 %87,6 dışında): kova tabandan **tavana** geçti ve hâlâ ayırt etmiyor. Kural ihlali içeren
çeldiriciler dil modeline fazla kolay geliyor; 3.7'de çeldiriciler dilbilgisel ama
bağlamla uyuşmayan zincirler (kişi/sayı/durum uyuşmazlığı) olacak. 105 madde
1.836'lık çekirdeğin %5,7'sidir; kova hariç sıralama aynı kalır (kartta verilir).

### Morfoloji ≠ yetenek: aynı modeller iki ölçekte

Bu kıyasta bir 2B model 32B'yi yakalayabilir. Bunun ne anlama geldiğini
söylemek için aynı modelleri **aynı sabit betikle** TurkishMMLU'nun 652 temiz
sorusunda da ölçtük (şık sırası dondurulmuş, kirli 113 soru dışarıda):

| model | boyut | TurkMorfBench 3.6 çekirdek (3.7.0 puanlama) | TurkishMMLU (652) |
|---|---|---|---|
| turkish-gpt2-large | 0,8B | 79,1 | **18,4** |
| kanarya-2b | 2B | 78,4 | **22,9** |
| Kumru-2B | 2B | 76,2 | **19,6** |
| Erk-32B | 32B | 75,0 | **71,0** |
| Qwen3-32B (taban) | 32B | 73,4 | 67,6 |

TurkishMMLU beş şıklıdır; şans %20. Sıfırdan Türkçe külliyatla eğitilen küçük
modeller morfolojide 32B ile **istatistiksel olarak beraber**, genel yetenekte
ise **şans düzeyinde**. Bu, kıyasın ölçtüğü şeyin tanımıdır: TurkMorfBench
akıl yürütmeyi değil, **Türkçe biçim bilgisini** ölçer — ve biçim bilgisi
parametre sayısıyla değil, görülen Türkçe jeton sayısıyla ölçeklenir. Bu
yüzden kıyas tek başına "hangi model iyi" sorusuna cevap vermez; genel yetenek
ölçüsüyle **birlikte** okunmalıdır. Sıralamayı yayımlarken bu sütunu yanına
koyuyoruz.

### Altı kural, aynı sıralama — ve iki kuralın çöktüğü yer

3.7.0 puanlama koduyla 15 model yeniden koşuldu. `harf` (birincil), `ham` ve
`jeton` aynı tabloyu verir: ilk iki ve son üç sıra üç kuralda aynı, ortadaki
beraberlik bandında yer değişimleri var. `ham` 1–4, `jeton` 2–16 puan aşağıda
kalır; jeton başına bölme en çok tam sözcük jetonlu küçük modelleri cezalandırır.
`pmi` ve `pmi_harf` 21–51 aralığına çöker: koşulsuz olasılıkla normalleştirmek,
ortak gövdeyi paylaşan adaylar arasındaki ayrımı yok eder. Bu iki kural bu görev
için uygun değildir; pakette kalıyorlar ki okuyucu bunu kendisi görebilsin.
`esli` 3.7.0'dan itibaren beş tekil kuralın uzlaşısıdır (Copeland). 3.6.x'te
`harf` puanı üzerinde ikili turnuvaydı; tek sayıl puanda turnuva en büyüğü
seçmekle aynıdır, `harf` ile birebir çıkması bir sağlamlık kanıtı değildi.
Uzlaşı, çökmüş iki kuralın oyunu da taşıdığı için `harf`ın 2–12 puan altındadır.
Sonuç: kural seçimi mutlak düzeyi değiştirir, sıralamanın uçlarını değiştirmez;
birincil kural ve her karşılaştırmanın tabanı `harf`tır ve tabloda adıyla verilir.

Tasarım etkisi (hücre kümeli / madde düzeyi aralık genişliği) modelden modele
1,2× ile 4,1× arasında değişiyor. En yükseği Erk modelleri ve Qwen3-32B tabanında
(4,0–4,1×): hücreler arası varyans yüksek, bazı kural hücrelerinde güçlü,
bazılarında zayıf. Kumru-2B'de 1,2× — düz bir profil. Aynı ortalama, farklı biçim.

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

**Model ile insan, aynı maddelerde.** 25 Eylül 2026'da eCloud Tech.'in AIGENCY V4
modeli, insan çalışmasının aynı arayüzü üzerinden 50 oturumda 515 maddenin tamamına
cevap verecek şekilde koşuldu (kendi değerlendirme koşumumuz). Hız ölçütü bu oturumları
insan verisinden ayırdı; veritabanında model oturumu olarak işaretlidir ve insan tavanı
hesabına girmez. Aynı 515 maddede **AIGENCY V4 %69,9, geçerli insanlar %79,1**. Tarama
kuralının, model ve insan cevapları aynı arayüzden geldiğinde bile ikisini ayırabildiğini
gösteren yararlı bir kontrol.

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


### Puanlama kuralı (3.3.0'da değişti)

Aday, `log P(aday | istem)` toplamının **adayın karakter sayısına** bölünmesiyle
puanlanır. Ortak istem öneki puana girmez.

Önceki sürümler istem ve adayın birlikte oluşturduğu dizginin ortalama
log-olasılığını alıyordu. Önek her adayda aynı ama jeton sayıları farklı;
ortalama alınınca o sabit önek adaylar arasında farklı ağırlıklarla dağılıyor
ve gerçek fark eziliyordu. Bir maddede aday toplamları −17,2 ile −25,6 arasında
ayrışırken eski kural hepsini −5,1 ile −5,4 arasına sıkıştırıp yanlış adayı
0,08 farkla seçiyordu.

Kural beş aday arasından **doğruluğa göre değil yanlılığa göre** seçildi:
ölçeği ölçülen şeye göre ayarlamamak için. Çeldiricilerin bir kısmı altından
kısadır (eksik ek). Adayların uzunluğu farklı olan maddelerde altın %29,9
oranında en kısadır; yansız bir kural da o civarda en kısayı seçmeli:

| kural | en kısayı seçme (hedef %29,9) |
|---|---|
| tüm dizgi ortalaması *(eski)* | %47,2 · %47,7 |
| aday toplamı | %51,0 · %57,0 |
| jetona bölünmüş | %47,5 · %48,7 |
| **karaktere bölünmüş** | **%39,4 · %43,2** |
| koşulsuzla normalleştirilmiş | %39,2 · %45,0 |

İkinci ve bağımsız gerekçe: karakter sayısı **jetonlayıcıdan bağımsızdır.**
Farklı sözlüklü modeller karşılaştırılırken jeton sayısına bölen bir ölçü,
kelimeyi kaç parçaya böldüklerine göre modelleri farklı cezalandırır.

Kalan yanlılık gizlenmiyor: %39-43, hedef %29,9. Uzunluk etkisi azaldı ama
sıfırlanmadı.

**Uzak uç kullananlar için:** `/v1/completions` yanıtında `text_offset`
zorunludur; onsuz aday jetonları ayrılamaz. Uç bu alanı döndürmüyorsa ölçüm
sessizce farklı bir şey hesaplamak yerine durur.

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

All 283 items in the vowel-drop, inverse-harmony and consonant-doubling buckets
carry a gold form checked character-for-character against the
[TDK Güncel Türkçe Sözlük](https://sozluk.gov.tr). We ran this audit because
native speakers scored **below chance** on the inverse-harmony bucket in the
human-ceiling study — when native speakers do worse than guessing, the gold is
what needs checking, not the speakers. It found three systematic errors inherited
from incomplete lexicon flags (*bidadi* → **bidati**, *aczı* → **aczi**,
*retti* → **reddi**). Measured human accuracy rose 5.6 points after the fix.

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
On the 3.6 core, 13 of 15 models score ≥96% on this bucket (all but the
Qwen3.8-27B base at 85.7% and Trendyol v1.0 at 87.6%): the bucket moved from floor to **ceiling** and still does
not discriminate. Rule-violating distractors are too easy for a language model; in
3.7 the distractors will be grammatical chains that disagree with the context
(person/number/case mismatch). The 105 items are 5.7% of the 1,836-item core; the
ranking without the bucket is identical (reported on the card).

### Morphology ≠ capability: the same models on two scales

On this benchmark a 2B model can match a 32B one. To say what that means, we
measured the same models with the **same pinned script** on the 652 clean
TurkishMMLU questions (option order frozen, 113 contaminated items removed):

| model | size | TurkMorfBench 3.6 core (3.7.0 scoring) | TurkishMMLU (652) |
|---|---|---|---|
| turkish-gpt2-large | 0.8B | 79.1 | **18.4** |
| kanarya-2b | 2B | 78.4 | **22.9** |
| Kumru-2B | 2B | 76.2 | **19.6** |
| Erk-32B | 32B | 75.0 | **71.0** |
| Qwen3-32B (base) | 32B | 73.4 | 67.6 |

TurkishMMLU is five-way; chance is 20%. Small models trained from scratch on
Turkish are **statistically tied** with a 32B model on morphology and **at
chance** on general capability. That is the definition of what this benchmark
measures: not reasoning but **Turkish form knowledge**, which scales with the
number of Turkish tokens seen, not with parameter count. The benchmark alone
therefore does not answer "which model is better"; it must be read **alongside**
a capability measure, and we publish that column next to the ranking.

### Six rules, one ranking — and where two rules collapse

Fifteen models were re-run with the 3.7.0 scoring code. `harf` (primary), `ham`
and `jeton` give the same table: the top two and bottom three are identical under
all three, with swaps inside the tied middle band. `ham` sits 1–4 and `jeton`
2–16 points lower; dividing by token count penalises small whole-word-token
models most. `pmi` and `pmi_harf` collapse to 21–51: normalising by the
unconditional probability erases the distinction between candidates that share
a stem. Those two rules are unsuitable for this task; they stay in the package so
readers can see it for themselves. Since 3.7.0 `esli` is a consensus of the five
individual rules (Copeland). In 3.6.x it was a pairwise tournament over the
`harf` scalar alone, which is identical to taking its maximum, so its agreement
with `harf` was no evidence of robustness. Because the consensus also carries the
votes of the two collapsed rules it sits 2–12 points below `harf`. The rule
changes the absolute level, not the ends of the ranking; `harf` is the primary
rule and the baseline of every comparison, and every table names it.

The design effect (cell-clustered vs item-level interval width) ranges from 1.2×
to 4.1× across models. It is highest for the Erk models and the Qwen3-32B base
(4.0–4.1×) — high between-cell variance, strong in some rule cells and weak in
others. Kumru-2B sits at 1.2×, a flat profile. Same mean, different shape.

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

**Model and humans on the same items.** On 25 September 2026 eCloud Tech.'s AIGENCY V4
model was run through the same interface as the human study, answering all 515 items
across 50 sessions (our own evaluation run). The speed criterion separated those sessions
from the human data; they are flagged as model sessions in the database and do not enter
the human-ceiling figure. On the same 515 items, **AIGENCY V4 scores 69.9%, the valid humans
79.1%**. A useful check that the screening rule tells model and human answers apart even
when they arrive through the same interface.

Every published figure is produced by `insan_ozet.py`; the thresholds are written
into the script.

### Confidence intervals: 466,517 items are NOT 466,517 independent observations

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
| item | ±0.12 pt | 466,517 |
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
(per character — the 3.3.0 choice), `pmi`, `pmi_harf` and `esli` (consensus of
the five rules, Copeland). The model is not run six times.

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

### Two tiers

`cekirdek` (1,836 items, bucket-balanced, runs in minutes, for diagnosis) and
`tam` (466,517 items, for the headline number). The core tier is deliberately
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
@software{turkmorfbench2026,
  title     = {TurkMorfBench: A Diagnostic Morphology Benchmark for Turkish Language Models},
  author    = {{eCloud Tech.}},
  year      = {2026},
  version   = {3.7.0},
  url       = {https://github.com/ecloudtechnology/turkmorfbench},
  note      = {Data: https://huggingface.co/datasets/ecloudtech/TurkMorfBench. A paper citation will replace this entry when published.}
}
```

**Data:** [huggingface.co/datasets/ecloudtech/TurkMorfBench](https://huggingface.co/datasets/ecloudtech/TurkMorfBench)
**Code:** [github.com/ecloudtechnology/turkmorfbench](https://github.com/ecloudtechnology/turkmorfbench)

Keywords: Turkish NLP, Türkçe doğal dil işleme, morphology benchmark, morfoloji
kıyası, vowel harmony, ünlü uyumu, wug test, agglutinative languages, LLM
evaluation, dil modeli değerlendirme, tokenizer analysis, subword segmentation.

### Güven aralığı: 466.517 madde, 466.517 bağımsız gözlem DEĞİLDİR

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
| madde | ±0,12 puan | 466.517 |
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
`pmi_harf` ve `esli` (beş kuralın uzlaşısı, Copeland). Model altı kez koşmaz.

```python
from turkmorfbench.duyarlilik import bilesen_topla, karsilastir, rapor
ka = bilesen_topla(arka_a, maddeler)
kb = bilesen_topla(arka_b, maddeler)
print(rapor(karsilastir(ka, kb, maddeler, "A", "B", anahtar="hucre"), "A", "B"))
```

Çıktı, iki sistemin farkının **yönünün altı kuralın hepsinde aynı olup olmadığını**
söyler. Aynıysa kalan uzunluk yanlılığı bulguyu taşımıyor demektir; değilse hangi
bulgunun kurala bağlı olduğunu okuyucudan önce biz bilmiş oluruz.
