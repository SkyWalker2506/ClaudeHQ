# Swap — tek sayfa GDD

**Tür:** Roguelike deckbuilder · **Referans:** Slay the Spire 2 (yapı) + Backpack Hero
(hook okunabilirliği) · **Platform:** Steam premium, $9.99–14.99 · **Zarf:** 6–9 ay,
tek kişi, 2D sprite + AI sanat hattı

---

## Çekirdek döngü

```
Elini oku  →  düşmanın niyetini gör  →  ELLE YA DA SİLAHLA cevap ver
   ↓                                              ↓
kart oyna                              silah değiştir: el yeniden yazılır
   ↓                                              ↓
   └──────────────  hasar / block / durum  ───────┘
                          ↓
                   düşman turu
                          ↓
              savaş biter → üç ödülden biri:
              [yeni silah]  [kart]  [kalıcı mod]
                          ↓
              harita düğümü seç → tekrar
```

**Bir koşu:** ~25 dk, 3 bölüm, her bölüm sonunda boss. Sessionability testi geçer:
tam bir koşu tek oturumda biter, meta ilerleme koşular arası taşınır.

## Oyuncunun ana eylemi

Kart oynamak **değil** — *hangi silahla oynadığına karar vermek*. Kart oynamak
uygulama, silah seçmek karardır.

## Fun mechanic — Katman 1 (tam)

Üç silah slotun var, biri aktif. **Aktif silah elini yazar:** aynı deste, farklı
silahla farklı kartlar üretir.

```
Deste (sabit, 15-20 "form" kartı)
        ×
Aktif silah (kartın somut haline çevirir)
        =
El (5 kart, silahı değiştirdiğin anda yeniden yazılır)
```

Örnek — elindeki `Kesme` formu:

| Aktif silah | Kart ne oluyor |
|---|---|
| Iron Sword | Slash — 1 enerji, 10 hasar |
| Blood Sword | Bleeding Slash — 1 enerji, 8 hasar, Bleed 3 |
| Greatsword | Cleave — 2 enerji, 22 hasar, tüm hedefler |
| Frost Blade | Rime Cut — 1 enerji, 7 hasar, Freeze 1 |

**Bedava değil — risk & reward buradan doğar.** Silah değiştirmek 1 enerji yakar ve
o tur "kuşanma" durumundasın: aldığın hasar +%50. Yani doğru silaha geçmek her zaman
doğru hamle değil; düşmanın niyetine bakıp *bu turu kaybetmeye değer mi* diye
soruyorsun. Sonuçların çoğu görünür (intent + hangi kartın neye dönüşeceğini gösteren
önizleme), hepsi değil (çekilecek kartlar) — anlamlı seçim koşulu sağlanır.

## Game feel

Silah değişimi tek ekran anıdır: 5 kart aynı anda çevrilir, yeni yüzler yerine oturur,
kılıç sesi + kart kayması. Hasar sayıları büyük, ekran sarsıntısı kısa, Bleed/Burn
ikonları düşman portresinin üstünde birikir. Hedef: **10 saniyelik GIF, sıfır açıklama.**

## Hedef merdiveni

- **Kısa (bir tur):** enerjiyi böl — kart mı oyna, silah mı değiştir
- **Orta (bir savaş):** düşmanın direncini kır (Skeleton Bleed'e dirençli → Fire'a geç)
- **Uzun (bir koşu):** üç silahını birbirini tamamlayacak şekilde topla
- **Meta (koşular arası):** yeni form kartları ve silah ailelerini kalıcı aç

## Kazanma / kaybetme

Kazanma: 3. bölüm boss'u (The Ashen Warlord, 3 fazlı — dokümandan devralındı; her faz
farklı bir silaha zorlar, tek silahla geçilemez). Kaybetme: HP 0 → koşu biter,
meta para kalır.

## System design — skeç

- **Progression:** koşu içi güç = silah kalitesi + form kartı sayısı. Level/XP yok.
- **Economy:** tek para birimi (Ash). Savaş sonu ödül seçimi = ana ekonomi.
- **Difficulty:** 3 bölüm × artan düşman direnç profili; Ascension benzeri 10 kademe.
- **Meta:** form kartı kütüphanesi + silah ailesi kilidi (Sword / Heavy / Blood / Frost / Flame).
- **Silah aileleri:** 5 aile × 3 kademe = 15 silah. Her aile bir build arketipi
  (dokümandan devralındı: Balanced / Bleed / Fire / Heavy / Shield).
- **Counter kuralı korunuyor:** Bleed build yüksek HP boss'ta güçlü, Skeleton'da zayıf.

## Content design — art stili KİLİTLİ

**Ton:** ağır, kavrulmuş, sessiz — kutlama yok. **Kamera:** sabit, cepheden, tek ekran
savaş (Slay the Spire düzeni).

Art stili `/showrunner` G1'e bırakılmadı — **kullanıcı kararıyla stil kütüphanesinden
seçildi: `black-reliquary`** (kaynak: `~/Projects/art-style-library/styles/black-reliquary/`,
origin: necrobeat, 16 örnek / 304 havuz).

### STYLE — harfi harfine kopyalanır, tek kelime değişmez

```
STYLE: Hyper-detailed rendered gothic relic illustration, blackened iron and tarnished brass filigree with cathedral tracery, isolated on pure black, one saturated arcane hue per object: violet, ember, ice or rose.
```

```
LIGHT: Self-luminous object light with tight golden rim highlights on every edge, a single coloured glow core, and a soft aura ring or glowing floor spill beneath the piece.
```

Stil etiketleri: `fits:card`, `fits:prop`, `fits:ui`, `mood:dark/dramatic/gothic`,
`palette:black-brass-violet`, **`repro:medium`**, `silhouette:strong`,
`technique:rendered/3d-look/decorative`.

### Neden bu oyuna oturuyor

- **Silah ailesi renk kodlaması stilin kendi kuralından geliyor.** "One saturated
  arcane hue per object: violet, ember, ice or rose" → Frost Blade = ice,
  Flame Sword = ember, Blood Sword = rose, Iron Sword = violet/nötr. Beş silah
  ailesi zaten stilin dört renk yuvasına oturuyor; renk sistemi ayrıca tasarlanmıyor.
- **Alfa kanalı yokluğu burada kusur değil, uyum.** Kayıtlı uyarı: bu stil saf siyah
  zeminde üretilir, alfa taşımaz, screen/additive blend ister. Swap'ın savaş ekranı
  zaten siyah — varlıklar keylemeden doğrudan oturur.
- `silhouette:strong` + `fits:card` — kart yüzü ve ikon okunabilirliği kanıtlanmış
  (45 ikonda tutmuş).

### Risk — prototipte ölçülecek

Kütüphanedeki 16 örneğin **hepsi nesne** (amfi, piyano, fener, sandık, çan). Stil
karakter/yaratık üzerinde kanıtlanmamış; Swap'ın 12 düşman + 3 boss portresi bu
boşluğa düşüyor.

**Çözüm — stil değil, tasarım uyarlanır** (kütüphane kuralı: bir stil asla değişmez,
gerekirse `black-reliquary-v2` açılır):
düşmanlar canlı yaratık değil **emanet formu** olarak tasarlanır — boş zırh kabuğu,
yanan kafatası mahfazası, buz kaplı miğfer, kül dolu tören çanı. Bu hem stilin nesne
gücünü kullanır, hem dokümanın kendi lore'uyla örtüşür (Combat Arts = somutlaşmış
teknikler), hem karakter animasyonu ihtiyacını sıfırda tutar.

İkinci risk: `repro:medium` etiketi ~40 varlık için ölçülmüş; Swap'ın toplam yükü ~93.
İlk 40'tan sonra stil tutarlılığı yeniden ölçülür.

## Sanat yükü (AI hattı bütçesi)

| Varlık | Adet | Tür | Stil uyumu |
|---|---:|---|---|
| Kart yüzü (form × silah ailesi) | ~40 | ikon-benzeri illüstrasyon | ✅ `fits:card` kanıtlı |
| Silah ikonu | 15 | ikon | ✅ `fits:prop` — stilin en güçlü olduğu yer |
| Düşman "emanet formu" | 12 | nesne-portre | ⚠️ uyarlanmış tasarımla; prototipte ölç |
| Boss (3 faz) | 3 | nesne-portre | ⚠️ aynı |
| Durum/UI ikonu | ~20 | ikon | ✅ `fits:ui` |
| Arka plan | 3 | tek kare | ✅ saf siyah zaten stilin tabanı |

Yürüyüş animasyonu yok, NPC yok, şehir yok, tile set yok. Hareket ihtiyacı shader +
parallax'a devredilir (`/juice`, `/sprite-parallax`) — stilin taban parlaması ve rim
ışığı bu katmana doğal zemin veriyor.

## Para modeli

Steam premium tek satın alma, $9.99–14.99, DLC yok, premium para yok.
Geri-hesap: $150k brüt ≈ 60-70k wishlist; Silver bandı alt eşiği 8k (kill kriteri #5).

## Comparable listesi

| Oyun | Rol | Ne öğretiyor |
|---|---|---|
| Slay the Spire 2 | kazanan | Janr kitlesi büyüyor; 7M ünite, $108M+ Steam |
| Backpack Hero | kazanan | Hook tek ekranda okunursa 500k-1M sahibe ulaşır |
| Chrono Ark | kazanan | RPG + deckbuilder melezi $14.16M — ama 4+ yıl early access |
| Tainted Grail: Conquest | kazanan | "Ekipman deste değiştirir" zaten var, 4.286 inceleme |
| Roguebook | kaybeden | İyi mekanik + ünlü isim, zayıf ekran hook'u = iz bırakmaz |
| Dimension Reign | kaybeden | Doğru tag, görünmez hook: ~$71.960 |
| Legends of Runeterra | kaybeden | Kart + çok oyunculu ilerleme hattı terk edildi |

## Sonraki adım

`/prototype greenlight/2026-08-10-steam-rpg-deckbuilder/gdd.md` — tek savaş, üç silah,
altı form kartı, bir düşman. Ölçülecek tek şey: silah değiştirme anı eğlenceli mi.

Art stili kilitli olduğu için `/showrunner` G1'in 10 stil denemesi turu **atlanır**;
onun yerine ilk sanat partisi doğrudan yukarıdaki STYLE satırıyla üretilir ve
"düşman = emanet formu" uyarlaması ilk 3 görselde doğrulanır.
