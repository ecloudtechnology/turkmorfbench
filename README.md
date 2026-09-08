---
license: cc-by-4.0
language:
  - tr
pretty_name: TurkMorfBench — Türkçe Morfoloji Kıyası
tags:
  - turkish
  - türkçe
  - morphology
  - morfoloji
  - vowel-harmony
  - wug-test
  - llm-benchmark
  - evaluation
task_categories:
  - text-generation
  - multiple-choice
size_categories:
  - n<1K
---

# TurkMorfBench — Türkçe morfoloji kıyası: gerçek ve uydurma gövdelerde ek üretimi

TurkMorfBench, bir dil modelinin Türkçe **ek sistemini** ne kadar bildiğini ölçer:
ünlü uyumu, ünsüz benzeşmesi, ünsüz yumuşaması ve kaynaştırma. 512 madde,
8 ek görevi, 64 gövde — **40 gerçek**, **24 uydurma** (wug). İki ölçüm kipi vardır:
serbest üretim ve sesbilimsel çeldiricili zorunlu seçim.

*English summary at the end.*

## Neden uydurma gövde

Gerçek kelimelerde doğru ek üretmek ezberle de mümkündür: model *kitabı* biçimini
külliyatta on binlerce kez görmüştür. Uydurma gövde (*çölgap*, *zelbik*, *pürsat*)
külliyatta hiç geçmez; model doğru eki ancak **kuralı** biliyorsa üretir. İkisi
arasındaki fark, modelin kuralı mı yoksa biçimleri mi öğrendiğini gösterir.
Bu, dil ediniminde 1958'den beri kullanılan *wug testi*nin Türkçe eklere uyarlamasıdır.

## Kapsam

| Görev | Ek | Örnek (gerçek) | Örnek (wug) |
|---|---|---|---|
| `cogul` | -ler/-lar | kapı → kapılar | kuntaş → kuntaşlar |
| `hal_yonelme` | -e/-a (+y) | çocuk → çocuğa | brelak → brelağa |
| `hal_bulunma` | -de/-da/-te/-ta | çölgap → çölgapta | yontuç → yontuçta |
| `hal_ayrilma` | -den/-dan/-ten/-tan | kuş → kuştan | krint → krintten |
| `hal_belirtme` | -i/-ı/-u/-ü (+y) | ağaç → ağacı | dratok → dratoğu |
| `iyelik_1sg` | -im/-ım/-um/-üm (+m) | masa → masam | çölgap → çölgabım |
| `iyelik_1pl` | -imiz/… (+miz) | ev → evimiz | glodek → glodeğimiz |
| `iyelik_3sg` | -i/… (+si) | araba → arabası | fönük → fönüğü |

Her görev 64 gövdenin hepsine uygulanır: 8 × 64 = 512 madde, 320 gerçek + 192 uydurma.

Sınanan kurallar:

- **Büyük ünlü uyumu** (-ler/-lar) ve **küçük ünlü uyumu** (-i/-ı/-u/-ü)
- **Ünsüz benzeşmesi**: sert ünsüzden sonra -de → -te, -den → -ten
- **Ünsüz yumuşaması**: ünlüyle başlayan ek önünde p/ç/t/k → b/c/d/ğ
- **Kaynaştırma**: ünlüyle biten gövdede -y-, -s-, -m-

## Altın cevap kuralı — okuyun

Yumuşama Türkçede **sözlükseldir**: *kitap → kitabı* ama *süt → sütü*, *renk → rengi*
(nk → ng). Bu yüzden:

- **Gerçek gövdeler** yalnızca yumuşama davranışı tartışmasız olan gövdelerden
  seçildi: çok heceli ve düzenli yumuşayanlar (*çocuk, kitap, ağaç, bardak…*) ile
  hiç yumuşamayan ünsüzle bitenler (*kuş, taş, ev, yol…*). Tek heceli t/k gövdeleri
  (*süt, kat*) ve nk→ng gibi özel durumlar **kapsam dışıdır**.
- **Uydurma gövdeler** için tek bir kural uygulanır ve belgelenir: çok heceli
  uydurma gövde p/ç/t/k ile bitiyorsa ünlüyle başlayan ek önünde yumuşatılır
  (*çölgap → çölgabı*, *brelak → brelağa*). Bu, Türkçe konuşurların yeni sözcüklere
  uyguladığı üretken varsayımdır; kıyas bunu **ölçmez, varsayar** ve her uydurma
  madde bu varsayımla tutarlıdır.

Altın cevaplar üç bağımsız yoldan doğrulanmıştır:

1. **Üretici motor** (`morfbench_v2.py`): ünlü uyumu, ünsüz benzeşmesi,
   yumuşama ve kaynaştırmayı uygulayan sesbilimsel motor; gövde havuzu ünlü
   düşmesi ve istisna kelimelerden arındırılmış, uydurma gövdeler ünlü düşmesi
   tetiklemeyecek desende seçilmiş (tohum 1337, yeniden üretilebilir).
2. **Bağımsız kural tablosu** (`kural_denetimi.py`): motordan ayrı yazılmış
   ikinci bir üretici; her cevabı yeniden türetip karşılaştırır — **512/512**.
3. **Morfolojik çözümleyici** (`crosscheck.py`): gerçek kelime cevapları
   *zeyrek* Türkçe morfolojik çözümleyicisiyle çözümlenir; beklenen ek
   etiketi (Dat, Loc, P3sg…) çözümde yoksa madde şüpheli sayılır.

**Sürüm notu (v1 → v2).** İlk sürüm (329 madde, 7 görev) yayımlanmadı; içinde
gerçek gövdelerde 18 yanlış altın cevap (*çocuka*, *südü*, *renği* gibi — yönelme
ekinde yumuşama uygulanmamış, iyelikte her gövdeye uygulanmıştı) ve uydurma
gövdelerde tutarsız bir kural vardı. v2 bu hataları düzeltir, `hal_belirtme`
görevini ekler ve gövde sayısını 47'den 64'e çıkarır. Burada raporlanan tüm
sayılar v2 ile ölçülmüştür.

## Ölçüm kipleri

**1. Üretim.** Model soruyu görür ("'çocuk' kelimesine -e/-a yönelme eki ekle.
Sadece kelimeyi yaz."), cevabı serbest üretir; noktalama ve büyük/küçük harf
temizlenip altınla tam eşleşme aranır. Bilgiyle birlikte **biçime uyma**yı da
ölçer — talimat almamış taban modeller burada düşük kalır.

**2. Zorunlu seçim.** Altın cevap ve sesbilimsel çeldiriciler (aynı ekin yanlış
ünlü uyumlu / yanlış benzeşmeli varyantları: *çocuğa* / *çocuğe* / *çocuka*…)
arasından log-olasılığı en yüksek olan seçilir. Biçim uyumunu devreden çıkarır,
yalnızca **bilgiyi** ölçer. Çeldirici üretilemeyen maddeler (ekin ünlüsü yoksa)
atlanır.

İki kip arasındaki fark bilgilendiricidir: ölçtüğümüz bir devam-eğitimi modeli
üretim kipinde tabanını +36 puan geçiyordu, zorunlu seçimde +3,7. Farkın büyük
kısmı bilgi değil biçim uyumuydu. **Tek başına üretim puanı raporlamayın.**

## Sonuçlar (v2)

Her fark 10.000 yeniden örneklemeli **eşli bootstrap** %95 güven aralığıyla
verilir; aralığı sıfırı içeren fark "gösterilemedi" olarak yazılır.

**Zorunlu seçim** (502 madde; 10 maddeye çeldirici üretilemedi):

| Model | Toplam | Gerçek (312) | Uydurma (190) |
|---|---|---|---|
| Qwen3-32B | %89,44 | %94,55 | %81,05 |
| Erk-32B (LoRA 0,40) | %89,84 · +0,40 [−1,20, +2,19] | %95,19 · +0,64 [−0,64, +1,92] | %81,05 · 0,00 |
| **Erk-32B (LoRA 0,75, yayınlanan)** | %91,43 · +1,99 [−0,20, +4,18] | %96,47 · +1,92 [−0,32, +4,17] | %83,16 · +2,11 [−2,11, +6,32] |
| Erk-32B (LoRA 0,80) | %91,83 · +2,39 [+0,20, +4,78] | %97,12 · +2,56 [+0,64, +4,81] | %83,16 · +2,11 [−2,63, +6,84] |

**Üretim** (512 madde, tam eşleşme, Qwen3 düşünme modu açık):

| Model | Toplam |
|---|---|
| Qwen3-32B | %31,64 |
| Erk-32B (LoRA 0,40) | %55,86 · +24,22 [+18,95, +29,49] |
| Erk-32B (LoRA 0,75) | %61,52 · +29,88 [+24,61, +35,16] |
| **Erk-32B (LoRA 0,75 + kimlik sistem istemi, yayınlanan yapılandırma)** | %59,38 · +27,73 [+22,46, +33,01] |
| Erk-32B (LoRA 0,40 + kimlik sistem istemi) | %49,02 · +17,38 [+11,91, +22,85] |

İki kip arasındaki ~28 puanlık fark biçim uyumudur: taban model düşünme
bloğunda kalıp kelimeyi yazmıyor; zorunlu seçimde aynı model %89 biliyor.
Sistem isteminin üretim puanına etkisi ölçeğe bağlıdır (0,75'te −2,15,
gösterilemedi; 0,40'ta −6,84, anlamlı) — dağıtılan yapılandırmayla ölçün.

Gerçek–uydurma uçurumu (taban: %94,55 → %81,05) kıyasın ölçmek istediği şey:
model biçimleri kuraldan çok daha iyi biliyor. Bir devam-eğitimi modelinde
(Erk-32B) uydurma gövde puanı hiçbir ölçekte tabandan ayrılmadı — Türkçe
devam-eğitimi ek sistemini ölçülebilir biçimde değiştirmedi.

## Kullanım

```bash
pip install torch transformers
python turkmorfbench_olc.py --model Qwen/Qwen3-32B --kip zorunlu
python turkmorfbench_olc.py --model Qwen/Qwen3-32B --kip uretim
```

Çıktı: toplam / gerçek / uydurma doğruluk ve madde bazlı tahmin vektörü (JSON).
İki modeli aynı maddelerde karşılaştırmak için `bootstrap.py` eşli güven aralığı
verir.

Veri biçimi (`turkmorfbench.json`):

```json
{"kok": "çocuk", "gorev": "hal_yonelme", "cevap": "çocuğa", "tip": "gercek",
 "soru": "'çocuk' kelimesine -e/-a yönelme eki ekle. Sadece kelimeyi yaz.",
 "kural": "yönelme + ünlü uyumu + yumuşama"}
```

`kural` alanı, o maddede sınanan sesbilimsel kuralları listeler; alt küme
analizinde (yalnız uyum / yumuşama içerenler / kaynaştırma içerenler) kullanılır.

## Sınırlar

1. Kapsam **kurallı gövdelerle** sınırlıdır; sözlüksel istisnalar (ünlü düşmesi
   *burun → burnu*, tek heceli yumuşamayanlar, nk→ng) bilinçli olarak dışarıdadır.
   Bir modelin istisnaları bilip bilmediğini bu kıyas ölçmez.
2. Uydurma gövde kuralı bir **varsayımdır**; konuşurlar arasında yumuşama
   üretkenliği değişebilir. Uydurma alt küme puanı bu varsayıma görecelidir.
3. 24 uydurma gövde ile uydurma alt kümesi küçüktür (192 madde, ±5 puan);
   küçük farklar için "gösterilemedi" beklenmelidir.
4. Türkçe isim çekimiyle sınırlıdır; fiil çekimi, türetme ve söz dizimi yoktur.

## Atıf

```
eCloud Tech. (2026). TurkMorfBench: Gerçek ve uydurma gövdelerde Türkçe ek
üretimi kıyası (v2). https://github.com/ecloudtechnology/turkmorfbench
```

Lisans: veri ve betikler **CC BY 4.0**. İletişim: info@e-cloud.web.tr

---

## English summary — TurkMorfBench

A benchmark of Turkish nominal morphology for language models: 512 items over
8 suffix tasks (plural, dative, locative, ablative, accusative, 1sg/1pl/3sg
possessive) and 64 stems — **40 real words and 24 nonce (wug) stems**. Nonce stems
never occur in any corpus, so a correct suffix there reflects **rule knowledge**
(vowel harmony, consonant assimilation, consonant softening, buffer consonants)
rather than memorised forms.

Two evaluation modes: free **generation** (exact match; measures knowledge *and*
format compliance) and **forced choice** among phonological distractors (measures
knowledge only). Report both — in our measurements a continued-pretraining model
beat its base by +36 points in generation but only +3.7 in forced choice.

Gold answers follow a documented rule table; real stems are restricted to ones
with uncontroversial softening behaviour, and nonce stems apply a single stated
convention (multi-syllabic p/ç/t/k stems soften before vowel-initial suffixes).
v1 (unpublished) had 18 wrong gold answers; all reported numbers use v2. License
CC BY 4.0.
