# Fikirler ve puanlama — 2026-08-10

Mod değerlendirme olduğu için Faz 2'nin "10 yeni fikir" kuralı yerine **girdi fikri
puanlanır**, sert eleme uygulanır, sonra Faz 3 geliştirme turu kaldıraçlarıyla
**hedeflenmiş kurtarma varyantları** üretilir (skill'in "az-fikir yolu" prosedürü).

---

## V0 — Doküman olduğu gibi: "MMORPG + Deck Builder"

```
HOOK: "Yeni bir kılıç bulmak yeni bir oyun tarzı keşfetmek demektir" —
      ekipman desteye kart ekler.
      Görsel öge: envanterde silah değişince deste listesinin değişmesi.
LOOP: Explore → Encounter → Combat → Loot → Equipment değiştir → Deck düzenle → Explore
HOOK-STACK: deckbuilder + MMORPG progression çerçevesi
KAZANAN COMP: Tainted Grail: Conquest — RPG + deckbuilder roguelike, ekipman/karakter
      deste değiştiriyor; 4.286 inceleme, %89 olumlu (≈128k satış, Boxleiter ×30, `tahmin`)
      https://store.steampowered.com/app/1199030/Tainted_Grail_Conquest/
      Chrono Ark — RPG parti + deckbuilder, 300k satış, ~$14.16M brüt
      https://store.steampowered.com/news/app/1188930/view/4187861970972855102
KAYBEDEN COMP: Legends of Runeterra — kart + kalıcı ilerleme + çok oyunculu çerçeve.
      Riot 2024'te PvP'yi hazırda beklemeye aldı, tek-oyunculu roguelike moduna pivotladı;
      gelir PvP tarafında sönmüştü, değer PvE'deydi.
      https://playruneterra.com/en-us/news/game-updates/legends-of-runeterra-2024-state-of-the-game-faq
      Dimension Reign — roguelike deckbuilder, ~$71.960 brüt: janrın medyan altı gerçeği
      https://steam-revenue-calculator.com/app/1162480/dimension-reign-roguelike-deckbuilder
SPRITE-FIT: kart + ikon + portre çekirdeği AI hattına birebir uyar;
      ama şehir (Ironhaven), 6 semt, 5 NPC, harita, quest sahneleri bunu bozar
PARA: Steam premium, $150k brüt hedefi ≈ 60-70k wishlist
```

### Skor kırılımı

| Boyut | Alt kıstas | Puan | Çapa |
|---|---|---:|---|
| Pazar talebi (30) | Kazanan sayımı | **10** | RL Deckbuilder 2025'te 10-11 kazanan ≥ 10 → tam |
| | Tag medyanı | **5** | ~$38k ≥ $20k = tam, ama `bayat` → yarımda kilitli |
| | Çıta-üstü % | **5** | Rogue-lite vekili %15, `bayat`+`tahmin` → yarımda kilitli |
| Yaşam döngüsü (15) | Faz tespiti | **15** | Phase 3, StS2 janrı büyütüyor |
| Hook gücü (20) | Ekran testi (yargı) | **5** | Hook iki ekran arası ilişkide: envanteri değiştir → *ayrı* deste ekranında sonucu gör. Tek karede görünmüyor, açıklama cümlesi gerekiyor → yarım |
| | Hook-stack | **0** | "Ekipman kart verir" Tainted Grail, Chrono Ark, Dawncaster'da zaten var. MMORPG progression bir hook değil, bir çerçeve → "X ama daha büyük" |
| Üretilebilirlik (20) | Showrunner zarfı | **0** | Şehir + 5 NPC + diyalog + 5-8 quest + crafting + ekonomi + 3 bölge = el-emeği içerik çukuru |
| | Sprite-fit | **10** | Kart/ikon/portre ağırlıklı çekirdek |
| Para uyumu (15) | Geri-hesap | **0** | 60-70k wishlist'i kapsam değil hook toplar; bu kapsam 6-9 ayda **bitmez**. Comparable'lar (Tainted Grail = stüdyo+IP+3D, Chrono Ark = 4 yıl early access) tek kişi zarfını temsil etmiyor |

**TOPLAM: 50/100** → C bandı
**SERT ELEME:** Üretilebilirlik 10/20 < 12 **ve** geri-hesap kapısı geçilemedi → **F / ELE**

### Neden eleniyor — tek cümle

Fikrin *deckbuilder çekirdeği* taramanın en iyi janrında duruyor, ama etrafına sarılan
*MMORPG kabuğu* hem üretilebilirliği hem geri-hesabı tek başına öldürüyor — ve hook
olarak sunulan "ekipman kart verir" iddiası janrda zaten standart.

---

## Faz 3 — Geliştirme turu (tek tur)

Düşük çıkan üç boyuta somut kaldıraç uygulandı:

| Düşük boyut | Uygulanan kaldıraç |
|---|---|
| Üretilebilirlik 10/20 | El-emeği içeriği sistemle değiştir: şehir/NPC/quest → koşu haritası düğümleri + meta-progression; diyalog → kartın kendisi |
| Hook 5/20 | İkinci **bağımsız** hook ekle ve hook'u tek kareye indir: statik "ekipman deste verir" ilişkisini **savaş içinde canlı** hale getir |
| Para 0/15 | Kapsamı Silver bandına küçült (6-9 ay, koşu tabanlı, şehirsiz) |

Kaldıraçlar hook'u ve janrı değiştirdiği için comparable'lar yeniden bulundu.

---

## V1 — "Swap": savaş ortasında silah değiştir, elin dönüşsün  ⭐

```
HOOK: Savaşın ortasında kılıcı değiştirirsin ve ELİNDEKİ KARTLAR gözünün önünde
      başka kartlara dönüşür.
      Görsel öge: 5 kartlık el, tek animasyonda yeniden yazılıyor — tek GIF'te anlaşılır.
LOOP: Kart oyna → düşman niyeti değişir → doğru silaha geç (bedava değil: 1 enerji /
      1 tur "kuşanma" penceresi) → el yeniden yazılır → combo → koşu ödülü yeni silah
HOOK-STACK: (1) roguelike deckbuilder  (2) gerçek zamanlı loadout swap: deste sabit
      değil, aktif ekipmana göre canlı yeniden yazılan bir el
      → iki bağımsız hook, "X ama Y" değil
KAZANAN COMP: Slay the Spire 2 — janrın kitlesini büyüttü, talep kanıtı
      https://sensortower.com/blog/mega-crits-slay-the-spire-ii-slays-with-7-million-units-sold
      Backpack Hero — "envanter yerleşimi = güç" hook'u tek ekranda okunur; 500k-1M sahip
      https://steamspy.com/app/1970580
KAYBEDEN COMP: Dimension Reign (~$71.960) — janr etiketi doğru, hook ekran görüntüsünde
      yok; Roguebook — Richard Garfield ismi + yüksek mekanik derinlik, ama hook'u
      "iki kahraman + harita boyama": kritik iyi, kültürel iz bırakmadı
      https://opencritic.com/game/11538/roguebook/reviews
SPRITE-FIT: kart yüzü, silah ikonu, düşman portresi, durum ikonu. Şehir yok, NPC yok,
      yürüyüş animasyonu yok → AI sprite hattının tam ortası
PARA: Steam premium $9.99-14.99; Silver bandı 8k-60k wishlist hedefi
```

| Boyut | Puan | Çapa |
|---|---:|---|
| Pazar talebi | **20**/30 | V0 ile aynı (10 + 5 `bayat` + 5 `bayat`) |
| Yaşam döngüsü | **15**/15 | Phase 3 |
| Hook gücü | **20**/20 | Ekran testi tam: elin dönüşmesi tek karede görünür. Hook-stack tam: 2 bağımsız |
| Üretilebilirlik | **20**/20 | Zarf tam: koşu tabanlı, prosedürel harita, el-emeği içerik yok. Sprite-fit tam |
| Para uyumu | **7**/15 | Sınırda: janr talebi kanıtlı ve GIF'lenebilir hook wishlist toplar; ama 1.523 oyunluk arzda keşfedilebilirlik pahalı, tek kişi pazarlama bandında |

**TOPLAM: 82/100** → **A bandı — güçlü aday**
**GELİŞTİR:** V0 50 → V1 82 (+32; Hook +15, Üretilebilirlik +10, Para +7)

---

## V2 — "Forge": kartları döversin  (yedek)

```
HOOK: Kart çekmezsin — kart DÖVERSİN. Koşu boyunca topladığın cevher + eşyayı örste
      birleştirip destenin kartlarını fiziksel olarak üretirsin.
      Görsel öge: örs ekranı, iki kart girer bir kart çıkar.
LOOP: Savaş → hammadde düşer → örste birleştir (kayıp riski var) → yeni kart → daha zor savaş
HOOK-STACK: (1) deckbuilder  (2) crafting/merge ekonomisi — Crafting tag'i çıta-üstü
      oranında Steam'in en iyilerinden: 686 başlığın %32'si > $500k
      https://newsletter.gamediscover.co/p/analyzing-the-top-steam-tags
KAZANAN COMP: Dungeon Clawler (pençe makinesi + deckbuilder — mekanik hook'u tek GIF'te);
      Backpack Hero (envanter = deste)
KAYBEDEN COMP: Deck of Ashes — "kart üret/craft" fikrini denedi, karanlık fantezi
      teması, iz bırakmadı: crafting katmanı grind'e dönüştü
SPRITE-FIT: kart + malzeme ikonu + örs ekranı → çok uygun
PARA: Steam premium $9.99-12.99
```

| Boyut | Puan |
|---|---:|
| Pazar talebi | **20**/30 |
| Yaşam döngüsü | **15**/15 |
| Hook gücü | **15**/20 (ekran testi 10 tam; hook-stack 5 — merge/craft deckbuilder'ı Backpack Hero/Dungeon Clawler yuvasında zaten dolu) |
| Üretilebilirlik | **20**/20 |
| Para uyumu | **7**/15 |

**TOPLAM: 77/100** → B bandı. Tek geliştirme turu hakkı V0→V1'de kullanıldı; yedek listesine.
**Neden birinci değil:** hook'u komşu iki oyunla aynı yuvada; V1'in "el canlı yeniden
yazılıyor" anı için doğrudan bir emsal yok, bu yüzden GIF'i daha ayırt edici.

---

## V3 — V1'in web portal kesimi  (yedek)

Aynı çekirdek, CrazyGames/Poki/Playgama için: tek koşu ≤ 6 dk, build < 20 MB, yükleme < 10 sn.

| Boyut | Puan |
|---|---:|
| Pazar talebi | **15**/30 (portal KPI'ları ulaşılabilir ama deckbuilder portalda kanıtlı bir kova değil — idle/merge/2P kadar talep yok) |
| Yaşam döngüsü | **15**/15 |
| Hook gücü | **20**/20 |
| Üretilebilirlik | **20**/20 |
| Para uyumu | **5**/15 (portföy geliri $200-2.000/ay/oyun; tek oyunla $150k çıtası tutmaz) |

**TOPLAM: 75/100** → B bandı.
**Neden birinci değil:** aynı fikir, üç kat düşük tavan. **Ama** en hızlı talep testi:
CrazyGames Basic Launch 7 gün + 500 oynanışta objektif sonuç veriyor
(https://docs.crazygames.com/resources/basic-launch-metrics/). V1'in Steam yolunda
**risk sigortası** olarak kullanılmalı, alternatif olarak değil.

---

## Sıralama

| # | Fikir | Puan | Bant |
|---|---|---:|---|
| 1 | **V1 — Swap** | 82 | A |
| 2 | V2 — Forge | 77 | B |
| 3 | V3 — Web kesimi | 75 | B |
| — | V0 — doküman hali | 50 | F (sert eleme) |
