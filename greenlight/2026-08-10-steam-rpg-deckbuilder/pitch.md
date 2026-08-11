# Pitch — 2026-08-10

## Karar

**Dokümanların çekirdeği doğru, kabuğu yanlış. Kabuğu at, çekirdeği keskinleştir.**

Öneri: **V1 — "Swap"** (82/100, A bandı). Savaş ortasında silah değiştirdiğinde
elindeki kartların canlı yeniden yazıldığı, koşu tabanlı, tek oyunculu roguelike
deckbuilder. Steam premium, 6–9 ay, tek kişi + AI sprite hattı.

Doküman hali (V0) 50/100 aldı ve **iki ayrı sert eleme kuralına** takıldı:
üretilebilirlik 10/20 (< 12 eşiği) ve geri-hesap kapısı. Elenme sebebi fikrin kötü
olması değil — çekirdeği taramanın en iyi janrında duruyor — etrafına sarılan MMORPG
kabuğunun hem takvimi hem hook'u yemesi.

## Neden bu — kanıtla

**1. Janr doğru, tarama bunu üç ayrı ölçümde onaylıyor.**
Roguelike Deckbuilder 2025'te %5.1 hit oranı (baseline %2.99), 10-11 kazanan
(https://howtomarketagame.com/2026/01/27/what-the-hell-happened-in-2025/); Q1 2026'da
tek bir çeyrekte 3 kazanan — *"in the past only 1 per year"*
(https://howtomarketagame.com/2026/05/14/2026-q1-games/). Roguelike geliri 2025'te
~$400M, +%80 YoY (https://alineaanalytics.substack.com/p/slay-the-spire-2-one-of-the-best).
Yaşam döngüsü **Phase 3** — Slay the Spire 2 (7M ünite, $108M+, 574k eşzamanlı tepe)
kitleyi kapatmadı, büyüttü
(https://sensortower.com/blog/mega-crits-slay-the-spire-ii-slays-with-7-million-units-sold).

**2. MMORPG kabuğu iki bağımsız gerekçeyle düşüyor.**
- *Üretim:* şehir + 6 semt + 5 NPC + diyalog + 5-8 quest + crafting + ekonomi + 3 bölge
  = el-emeği içerik çukuru. Tek kişi + 6-9 ayda bitmez; *"scope kills more solo projects
  than skill does"*, solo indie'lerin ~%70'i hiç kâr etmiyor, 2025 medyan indie geliri
  $249 (https://ziva.sh/blogs/solo-game-development). Bütçeli MMO'lar bile ölüyor:
  Gran Saga ~$25M ile çıktı, 4 ayda kapandı
  (https://www.notebookcheck.net/25-million-MMO-gets-shut-down-only-4-Months-after-launch.973828.0.html).
- *Janr içi kanıt:* Riot, Legends of Runeterra'nın PvP'sini 2024'te hazırda beklemeye
  aldı ve tek-oyunculu roguelike moduna (Path of Champions) pivotladı — çünkü gelir PvP
  tarafında sönmüştü ve PvE çok daha popülerdi
  (https://playruneterra.com/en-us/news/game-updates/legends-of-runeterra-2024-state-of-the-game-faq).
  Kart + çok oyunculu ilerleme çerçevesi **denendi ve terk edildi.** Dokümanların
  önerdiği yön, sektörün geri çekildiği yön.

**3. Dokümanların hook olarak sunduğu şey hook değil — janr standardı.**
"Ekipman desteye kart ekler" Tainted Grail: Conquest'te, Chrono Ark'ta, Dawncaster'da
zaten var. Ekran testinde de kalıyor: envanteri değiştirip *ayrı* bir deste ekranında
sonucu görmek tek karede anlaşılmaz. V1 bu ilişkiyi **savaşın içine** taşıyor: elindeki
5 kart tek animasyonda yeniden yazılıyor. Tek GIF, sıfır açıklama. 1.523 oyunluk bir
tag'de ve 2.800 başlıklı bir Deckbuilders Fest'te
(https://www.switchbladegaming.com/strategy-games/deck-builder-renaissance-2026/)
görünmenin tek yolu bu.

**4. Geri-hesap.** Hedef $150k brüt ≈ 60-70k wishlist; Silver bandı 8k-60k.
Comparable proxy (Boxleiter, inceleme ×30, etiket `tahmin`): Tainted Grail: Conquest
4.286 inceleme ≈ 128k satış — banda ulaşıyor, ama o bir stüdyo ürünü (3D, IP'li).
Chrono Ark 300k satış / ~$14.16M — ama 4+ yıl early access
(https://store.steampowered.com/news/app/1188930/view/4187861970972855102).
Tek kişi + 6-9 ay için doğru okuma: **janr banda ulaşabiliyor, kapsam küçültülmüş
haliyle.** V0 kapsamıyla ulaşmıyor. Bu yüzden kapsam küçültüldü, janr değil.

## Yedekler

**V2 — "Forge" (77, B).** Kart çekmiyorsun, kart döversin: cevher + eşya örste
birleşip destenin kartlarını üretiyor. Crafting tag'inin çıta-üstü oranı Steam'in en
iyilerinden (686 başlığın %32'si > $500k). *Neden birinci değil:* merge/craft
deckbuilder yuvası Backpack Hero ve Dungeon Clawler tarafından tutulmuş; V1'in
"el canlı yeniden yazılıyor" anına doğrudan emsal yok, GIF'i daha ayırt edici.

**V3 — V1'in web portal kesimi (75, B).** Aynı çekirdek, ≤6 dk koşu, <20 MB.
*Neden birinci değil:* aynı fikir, üç kat düşük gelir tavanı ($200-2.000/ay/oyun
portföy bandı). **Ama alternatif değil, sigorta:** CrazyGames Basic Launch 7 gün +
500 oynanışta objektif sonuç verir
(https://docs.crazygames.com/resources/basic-launch-metrics/) — Steam'e aylar
harcamadan hook'un çalışıp çalışmadığını ölçmenin en ucuz yolu.

## Kill kriterleri — peşinen, sayıyla

Bunlardan biri gerçekleşirse fikir ölür, tarama yenilenir, cila yapılmaz:

1. **`bayat` metrik düzeltmesi.** Tag medyanı ve çıta-üstü oranı bu koşuda
   games-stats.com Cloudflare duvarı yüzünden alınamadı, 2026-08 snapshot'ından
   `bayat` etiketiyle kullanıldı. **İlk taze veride yeniden puanla.** Roguelike
   Deckbuilder tag medyanı NET < $5k çıkarsa → fikir ölür.
2. **Çıta-üstü oranı < %8** ölçülürse → fikir ölür.
3. **Faz kayması.** 3 oyun eşzamanlı oyuncuların %75+'ini tutmaya başlarsa (Phase 4) →
   pivotsuz girilmez.
4. **Hook testi.** Prototipin 10 saniyelik GIF'i, oyunu bilmeyen 5 kişiye açıklamasız
   gösterildiğinde 3'ü "silah değişince kartlar değişiyor" diyemezse → hook yok, fikir
   ölür (V2'ye geç).
5. **Wishlist kapısı.** Next Fest sonunda wishlist < 8.000 (Silver alt bandı) →
   Steam yolu bırakılır, V3 web kesimine dönülür.
6. **Portal sigortası.** V3 denenirse ve CrazyGames Basic Launch barı tutmazsa
   (ort. oturum < 10 dk, D1 < %10, 1-dk dönüşüm < %80) → çekirdek loop eğlenceli değil,
   Steam'e para harcanmaz.
7. **Takvim.** 4. ayın sonunda oynanabilir tam koşu (savaş + ödül + meta) ayakta
   değilse → kapsam yeniden yarıya iner ya da proje durur.

## Dokümanlardan ne KALIYOR, ne GİDİYOR

| Kalıyor | Gidiyor |
|---|---|
| Ekipman = karakter kimliği (Principle 1) | Ironhaven şehri, 6 semt, 5 NPC, diyalog |
| Deste = savaş stratejisi (Principle 2) | Quest sistemi, ekonomi, crafting, materyaller |
| Loot = yeni olasılık (Principle 3) | Level/XP ilerlemesi (koşu içi güç eğrisi yerine geçiyor) |
| "Daha fazla kart ≠ daha iyi" (Principle 4) | 8 sınıf yol haritası, 4 bölge genişlemesi |
| Her build'in bir counter'ı var (Principle 6) | MMORPG çerçevesi, sunucu, PvP/guild/raid |
| Tag sistemi (Sword/Fire/Bleed/Heavy) — sinerjinin omurgası | Master data'nın 8 tablosu → 3 tabloya iner |
| Effect tabanlı kart sistemi (GDD §43) | Element yelpazesi 7 → 3 (Physical/Fire/Bleed) — zaten demo önerisi |
| Enemy intent (GDD §25) | — |
| The Ashen Warlord 3 fazlı boss | 3 bölge / Kingdoms-Wilds-Ashen Lands coğrafyası |
| Dark fantasy tonu, Warrior kimliği | — |

Dokümanların **kalitesi sorun değil**: 3-katman çerçevesinin System Design ve Content
Design katmanları zaten iyi yazılmış. Eksik olan Katman 1: *fun mechanic* net değil.
"Ekipman kart verir" bir veri ilişkisi, oyuncunun zevk aldığı bir eylem değil. V1 o
boşluğu dolduruyor — geri kalan her şey dokümanlardan devralınabilir.

## Sonraki adım

```
/prototype greenlight/2026-08-10-steam-rpg-deckbuilder/gdd.md
```

Önce prototip: core loop'un his kanıtı alınmadan sanata bütçe harcanmaz (3-katman
tezinin ana kuralı). Kill kriteri #4 (GIF testi) bu prototiple ölçülür. Eğlence kanıtı
gelince aynı GDD ile `/showrunner`.
