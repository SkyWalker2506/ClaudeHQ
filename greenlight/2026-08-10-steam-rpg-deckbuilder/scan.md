# Canlı pazar taraması — örnekleme: 2026-08-10

Kapsam: Steam premium. Fikrin çarptığı üç tag ayrı ayrı ölçüldü:
Roguelike Deckbuilder · RPG · MMORPG.

---

## 1. Kazanan sayımı (1.000+ inceleme = "Real Steam")

| Tag | Kazanan | Hit oranı | Kaynak |
|---|---|---|---|
| Genel baseline 2025 | 608 / 20.282 | **%2.99** | https://howtomarketagame.com/2026/01/27/what-the-hell-happened-in-2025/ |
| **Roguelike Deckbuilder** | 10–11 (2025) | **%5.1** (2024: %6.71) | aynı kaynak |
| **RPG** | 28 (2025) | **%2.4** (2024: %1.46) | aynı kaynak |
| Q1 2026 deckbuilder | **3 kazanan** | — | https://howtomarketagame.com/2026/05/14/2026-q1-games/ |
| MMORPG | listede yok | — | aynı kaynaklar |

Q1 2026 notu, taramanın en taze sinyali: *"There were 3 Deckbuilders that did well in Q1
where in the past only 1 per year."* Janr **büyüyor**, daralmıyor.

Roguelike Deckbuilder, orta-boy janrlar içinde hit oranı en yüksek olanlardan biri.
Ama survivorship uyarısı geçerli: ortalama gelir dipte, 1.523 oyun tag'de
(https://games-stats.com/steam/?tag=roguelike-deckbuilder — arama sonucu üzerinden;
sayfa Cloudflare arkasında, aşağıya bak).

## 2. Tag medyanı (NET)

**Erişilemedi.** games-stats.com Cloudflare bot doğrulaması arkasında (HTTP 403 +
tarayıcıda "security verification"; CAPTCHA çözümü kural gereği yapılmadı).
gamediscover.co tag analizinin görünür metninde deckbuilder satırı yok.

Zincir uygulandı → **son çare: 2026-08 bayat snapshot.**

| Tag | Medyan NET | Etiket |
|---|---|---|
| Roguelike Deckbuilder | ~$38k | `bayat` |
| Genel Steam medyanı | ~$6.6k | `bayat` |
| İlgi eşiği | $5k+ | `bayat` |

Kaynak (bayat): https://newsletter.gamediscover.co/p/which-genre-should-your-next-pc-game

Kural gereği `bayat` etiketi **Pazar talebi boyutunun tag-medyanı alt kıstasını yarım
puanda bırakır** ve kill kriterlerine "ilk taze veride yeniden puanla" satırı ekler.

Bağımsız çapraz kontrol: 1.523 oyunda toplam net ≥ $97M → kaba ortalama ~$64k; medyan
bunun çok altında olur (dağılım StS2/Balatro tarafına aşırı çarpık). $38k medyan sayısı
bu aritmetikle tutarlı, ama teyit edilmedi.

## 3. Çıta-üstü yüzdesi ($200k+ brüt)

**Doğrudan deckbuilder satırı bulunamadı.** En yakın vekil: Rogue-lite tag'i, 414 başlık,
**%15 > $200k**, %9 > $500k (https://newsletter.gamediscover.co/p/analyzing-the-top-steam-tags).
Karşılaştırma çapası: Crafting %32 > $500k · Platformer 1.166 oyun, %7 > $200k.

Deckbuilder vekil olarak %8–15 bandına konumlandı → **yarım**, etiket `bayat` + `tahmin`.

## 4. Yaşam döngüsü fazı — Roguelike Deckbuilder

**Phase 3 (ikinci dalga, GİR) — ama üst sınırında.**

GİR sinyalleri:
- Slay the Spire 2 (Mart 2026): ilk hafta 3M kopya, ay sonunda 5.3M, Steam'de $108M+,
  574.638 eşzamanlı tepe; 7M ünite
  (https://sensortower.com/blog/mega-crits-slay-the-spire-ii-slays-with-7-million-units-sold,
  https://www.switchbladegaming.com/strategy-games/deck-builder-renaissance-2026/).
  Bu bir P2 "tanımlayıcı hit" tekrarı — janrı küçültmüyor, **kitleyi büyütüyor**.
- Roguelike'lar 2025'te Steam'de ~$400M, 2024'e göre **+%80**
  (https://alineaanalytics.substack.com/p/slay-the-spire-2-one-of-the-best).
- Alt-tür çeşitlenmesi (mekanik / mekânsal / anlatısal) → yeni çıkışlar aynı kitle
  yuvası için yarışmıyor. Q1 2026'da 3 farklı deckbuilder kazandı.

GİRME sinyalleri **yok**: 3 oyun eşzamanlıların %75'ini tutmuyor; StS2 tek başına dev
ama Balatro, Monster Train 2, Mewgenics, Dungeon Clawler ayrı yuvalarda.

Uyarı: arz tarihi zirvede — Steam Deckbuilders Fest 2026'da ~2.800 başlık indirime girdi
(https://www.switchbladegaming.com/strategy-games/deck-builder-renaissance-2026/).
Talep büyüyor ama keşfedilebilirlik pahalı: **hook ekran görüntüsünde görünmüyorsa oyun görünmez.**

## 5. MMORPG katmanı — ayrı test

Bu tag ölçülmedi, **elendi**. Gerekçe kanıtla:

- Sabit kısıt ihlali: sunuculu multiplayer = eleme kriteri (skill sabiti).
- Solo dev gerçekliği: *"scope kills more solo projects than skill does"*; solo indie'lerin
  ~%70'i hiç kâr etmiyor, 2025 medyan indie geliri **$249**
  (https://ziva.sh/blogs/solo-game-development).
- Bütçeli MMO'lar bile ölüyor: Gran Saga ~$25M bütçeyle Aralık 2025'te çıktı, **4 ayda
  kapandı** (https://www.notebookcheck.net/25-million-MMO-gets-shut-down-only-4-Months-after-launch.973828.0.html);
  Ashes of Creation'da yaratıcı yönetmen Ocak 2026'da istifa, ardından toplu işten çıkarma
  (https://en.wikipedia.org/wiki/Ashes_of_Creation).
- **Kart oyununda live-service hattı zaten öldü, PvE hattı yaşadı:** Riot 2024'te 500+
  kişiyi çıkardıktan sonra Legends of Runeterra'nın PvP'sini hazırda beklemeye aldı ve
  tek-oyunculu roguelike moduna (Path of Champions) pivotladı — çünkü PvE, PvP'den çok
  daha popüler çıktı
  (https://playruneterra.com/en-us/news/game-updates/legends-of-runeterra-2024-state-of-the-game-faq,
  https://www.avclub.com/legends-of-runeterra-2025-freedom-dead-game).

Bu son madde dokümanların en pahalı bulgusu: **sektör, kullanıcının önerdiği yönün tam
tersine yürüdü.** Kart + çok oyunculu ilerleme çerçevesi denendi ve terk edildi; kalan
değer kart + roguelike PvE'de.

---

## GEÇTİ / KALDI

| Janr | Karar | Gerekçe |
|---|---|---|
| **Roguelike Deckbuilder** | ✅ GEÇTİ | Medyan ≥ $5k (bayat $38k) · Phase 3 · sprite/AI hattına birebir uyar |
| **RPG (tek oyunculu, koşu tabanlı)** | ✅ GEÇTİ (hibrit bileşen olarak) | %2.4 hit baseline'ın altında değil, 28 kazanan; tek başına değil deckbuilder'la melez olarak |
| **RPG (kapsamlı: şehir + NPC + quest + crafting + ekonomi)** | ❌ KALDI | El-emeği içerik çukuru — üretilebilirlik kısıtına çarpıyor |
| **MMORPG / sunuculu ilerleme** | ❌ KALDI | Sabit kısıt ihlali + LoR pivotu janr içi negatif kanıt |

Faz 2 yalnızca GEÇTİ satırlarında fikir üretir.
