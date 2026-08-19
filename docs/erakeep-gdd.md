# ERAKEEP — Game Design Document v1.0

> 2D side-view tower defense + auto-battler + aktif slash savaşı. Tek kaleyi insanlık tarihi boyunca geliştir ve hayatta tut.
> Tarih: 2026-08-16 · Durum: Pre-production · Hedef: Solo-dev, Web/Steam, tek dosya prototip ile başlangıç

---

## 0. Elevator Pitch

**"Build a fortress through the ages while armies fight automatically — then physically carve, shoot and bombard your way through the battlefield yourself."**

Oyuncu sol taraftaki kalesini, kulelerini ve otomatik ordusunu kurar; aynı anda mouse/touch ile savaş alanına doğrudan müdahale eder (slash, ok yağmuru, topçu, hava saldırısı). Her çağ atlamada kale, kuleler, ordu ve oyuncunun aktif silahları birlikte evrimleşir: Taş Devri sopasından orbital saldırıya.

### Hedef kitle örtüşmesi
- Tower defense oyuncusu → build kurma
- Auto-battler oyuncusu → savaş izleme
- Action oyuncusu → aktif müdahale
- Roguelite oyuncusu → broken build avı

---

## 1. Design Pillars

1. **Savaş hiç durmaz.** Ekran ayrı savaş sahnelerine bölünmez; düşman akışı sürekli, büyük saldırılar duyuru ile gelir.
2. **Dört sistem, tek build.** Kale + Tower + Ordu + Aktif yetenek — hiçbiri tek başına run kazanmaz, sinerji kazanır.
3. **Evrim görünür olmalı.** Her era geçişi ekranda dramatik değişim yaratır (kale, birlikler, ability'ler). Steam GIF'i bu andır.
4. **Aktif oyun bir kaynak, refleks yarışı değil.** Slash spam'i Command ekonomisi ve düşman counter'ları ile sınırlanır — ceza sistemleriyle değil.
5. **Era = reskin değil, +1 mekanik.** Her çağ tek bir yeni savaş mekaniği getirir; geri kalanı arketip mirasıdır.

### Güç dengesi hedefi (telemetri ile doğrulanır, §14)
Towers ~%35 · Army ~%30 · Aktif oyuncu ~%25 · Sinerji/ekonomi ~%10

---

## 2. Core Loop

### Saniye ölçeği (moment-to-moment)
Düşman akışı gelir → ordu otomatik çarpışır → tower'lar ateş eder → yüksek öncelikli hedef belirir (siege/medic/elite) → oyuncu Command harcayıp müdahale eder → gold ve Knowledge birikir → oyuncu wave arasında harcar.

### Dakika ölçeği (wave yapısı, era başına)
```
Wave 1 → Wave 2 → [Upgrade seçimi] → Wave 3 → Elite → [Upgrade] → Siege Wave → Boss → ERA EVOLUTION
```
Wave'ler ayrı ekran değildir; "Gothic Horde approaching — 35 sec" duyurusu ile yoğunluk artar. Duyuru arası boş kalmaz, düşük yoğunluklu akış devam eder.

### Run ölçeği
**6 era × 5–7 dk = 30–45 dk run.** (İlk tasarımdaki 45–75 dk bilinçli olarak kısaltıldı: sürekli-aksiyon oyununda 60+ dk yorucu ve geç ölüm kaybı ağır. Uzun oyun isteyen Endless History moduna gider.)

---

## 3. Battlefield & Frontline

```
 [🏰] [T][T][T] ---- ordu ----><---- düşman ---- [spawn]
 |--- Defense Zone ---|------ Frontline bölgesi ------|
```

### Frontline sistemi
Orduların çarpıştığı hat dinamiktir; güç dengesine göre ileri/geri kayar.

**İleri itme ödülleri (cap'li — snowball freni):**
| Frontline konumu | Bonus |
|---|---|
| %25 alan | +%10 gold geliri |
| %50 alan | Supply Point: +1 Knowledge/wave |
| %75 alan | Düşman reinforcement süresi +%20 |
| Gold bonusu toplam cap | **+%20** (ilk taslaktaki +%40 snowball üretiyordu) |

**Geri çekilme rubber-band'i ("Last Stand"):**
Frontline kaleye %25 mesafeye girdiğinde:
- Tüm tower'lar menzil avantajıyla ateş eder (doğal)
- **Command dolum hızı +%50** — kaybeden oyuncuya pasif stat değil, müdahale gücü verilir
- Ekran kenarı kızarır, müzik yoğunlaşır (comeback anı hissi)

Doğal gerilim: ordu ileri savaşmak ister (gold/knowledge), tower'lar düşmanın yaklaşmasını ister (menzil + Last Stand). Bu tek başına build çeşitliliği yaratır.

---

## 4. Aktif Oyuncu Sistemi (Fruit Ninja katmanı)

### 4.1 Command Energy
```
COMMAND ████████░░  72/100
```
- Pasif dolum: 4/sn (base)
- Kill iadesi: bazı upgrade'lerle, **saniyede max 6 Command cap'li** (blade build'in kendini besleyen sonsuz döngüsü bu cap ile kırılır; upgrade'ler cap'i büyütür, kaldırmaz)
- Last Stand bölgesinde dolum +%50

### 4.2 Input modeli — 3 slot, 3 jest
Jest **şekli** değil, jest **tipi** ability'yi belirler (touch uyumu + panik anında güvenilir okuma):

| Input | Slot | Örnek (Medieval) |
|---|---|---|
| **TAP** | Precision | Crossbow Shot — tek hedef, weakpoint |
| **DRAG** | Sweep | Blade Sweep — hat boyunca damage |
| **HOLD** | Area | Trebuchet — AoE hedefle, bırak |

> İlk taslaktaki yatay/dikey/çapraz slash ayrımı kesildi: touch'ta ayrım güvenilmez, yanlış okuma frustrasyon üretir. Aynı derinlik ability *seçimiyle* sağlanır (loadout = build).

### 4.3 Era başına ability evrimi
| Era | TAP | DRAG | HOLD |
|---|---|---|---|
| Ancient | Rock Throw | Club/Sword Swipe | Fire Pot Toss |
| Classical | Javelin | Sword Sweep | Arrow Volley |
| Medieval | Crossbow Shot | Blade Sweep | Trebuchet Strike |
| Gunpowder | Musket Shot (weakpoint crit) | Sabre Charge | Mortar Barrage |
| Industrial | Rifle Shot | **Gatling Sweep** (hold-drag tarama) | Field Artillery |
| Modern | Sniper Shot | Minigun Sweep | **Air Strike** (hat çiz, jet bombalar) |

Era atlarken eski era'nın bir ability'si loadout'ta **tutulabilir** (3 slottan 1'i "legacy slot") — build kimliği korunur.

### 4.4 Spam frenleri (2 sistem, 3 değil)
1. **Command maliyeti** — her kullanım kaynak yer (DRAG ~15, TAP ~8, HOLD ~30)
2. **Düşman counter'ları** — Shield Bearer slash'ı bloklar, Armored TAP ister, swarm HOLD ister

> Exhaustion (ard arda kullanımda verim düşüşü) **kesildi**: oyunun satış noktası olan mekaniğe üçüncü bir ceza katmanı bindirmek onu oynanmaz hissettirir. Command + counter yeterli; playtest aksini gösterirse geri eklenir.
> Perfect Slash (hız/açı timing bonusu) **MVP dışı** — post-launch skill-ceiling maddesi (§16).

---

## 5. Tower Defense

### 5.1 Slot sistemi
- Başlangıç 3 slot → kale upgrade'i ile 4 → 5 → 6
- Slot açma maliyeti üstel (gold sink)
- Tower satma: %60 iade (yeniden build esnekliği, ama bedava değil)

### 5.2 Beş arketip — era boyunca tek entity, evrimleşen hat
| Arketip | Rol | Evrim hattı (örnek) |
|---|---|---|
| **Rapid** | Hızlı/düşük dmg, swarm | Watch Tower → Archer → Crossbow → Musket → MG Nest → Autocannon |
| **Heavy** | Yavaş/yüksek dmg, tank/siege | Rock Thrower → Ballista → Trebuchet → Cannon → Artillery → Missile Battery |
| **Area** | Kalabalık temizler | Fire Pot → Oil Cauldron → Mortar → Howitzer → Rocket Battery |
| **Control** | Slow/debuff | Tar Pit → Caltrops → Barbed Wire → EMP Field |
| **Anti-special** | Hedefe özel | Anti-Cavalry Stakes → Pike Wall → Anti-Air Gun → SAM Battery |

**Uygulama kuralı (scope freni):** Her arketip kod tarafında TEK entity'dir. Era geçişi = stat çarpanı + sprite değişimi + (varsa) o era'nın yeni mekaniği. Yeni davranış kodu yalnızca era mekanikleri için yazılır (§7).

### 5.3 Tower upgrade
Her tower era içinde 3 seviye (gold ile): dmg/rate/range artışı. Era atlayınca otomatik olarak yeni forma evrimleşir (seviye korunur).

---

## 6. Auto-Battle Ordusu

### 6.1 Üretim — mikro yönetim yok
Yapılar otomatik üretir; oyuncu yalnızca **kompozisyon** kurar (hangi yapılar, hangi seviyede):
- Barracks: 8 sn'de 2 Infantry
- Archery Camp: 12 sn'de 2 Ranged
- Stable: 20 sn'de 1 Cavalry
- (era ile açılır) Siege Workshop, Support Tent

Birlik davranışı: spawn → ilerle → hedef seç → savaş → öl. Oyuncudan emir yok; upgrade'ler davranışı dolaylı değiştirir ("Cavalry ranged hedeflere öncelik verir" gibi).

### 6.2 Beş birlik arketipi
| Arketip | Rol | Ancient → Modern |
|---|---|---|
| Infantry | Ucuz frontline eti | Spearman → Swordsman → Musketeer → Rifleman → Modern Infantry |
| Tank | Yüksek HP hattı | Shield Bearer → Knight → Cuirassier → Early Tank → MBT |
| Ranged | Hat arkası dmg | Slinger → Archer → Crossbow → Rifle Line → Sniper |
| Anti-Heavy | Zırh delici | Spear → Pike → AT Rifle → Rocket Launcher |
| Specialist | Buff/heal/utility | Standard Bearer → War Priest → Medic → Combat Drone |

### 6.3 Ordu sustain sınırı
Ordu tek başına frontline'ı süresiz tutamaz: üretim hızı kayıp hızının altında kalacak şekilde dengelenir. Tower desteği veya oyuncu müdahalesi olmadan frontline yavaşça geriler. (Bu, "ordu her şeyi yapar, oyuncu izler" moduna karşı ana fren.)

---

## 7. Era Sistemi

### 7.1 Altı era + her birinin TEK yeni mekaniği
| # | Era | Yeni savaş mekaniği |
|---|---|---|
| 1 | **Ancient** | Baseline — tüm temel sistemler |
| 2 | **Classical** | **Formations**: düşmanlar dizilişle gelir (Shield Wall, Phalanx) — hedef önceliği kararı doğar |
| 3 | **Medieval** | **Siege units**: kalene menzilden vuran düşmanlar — "piyade mi siege mi" kararı |
| 4 | **Gunpowder** | **Weakpoints**: TAP ability'ler crit noktası vurur — precision oyunu |
| 5 | **Industrial** | **Air units**: uçan düşmanlar, Anti-Air zorunluluğu — build'e yeni eksen |
| 6 | **Modern** | **Electronics**: EMP/drone/jamming — tower'ları geçici susturan düşmanlar, oyuncu müdahalesi kritikleşir |

Her era ayrıca: kale görseli, tüm sprite'lar, ability seti, müzik katmanı değişir. Ama **kod olarak** yalnızca o tek mekanik yenidir.

### 7.2 Çağ atlama — oyuncu kararı
```
ADVANCE ERA — Cost: 350 Knowledge
Unlocks: Crossbows, Knights, Trebuchets, Stone Castle
⚠ Enemy technology will also advance.
```

### 7.3 Historical Pressure + Underdog Bonus
- Her wave: Era Pressure +5%. 100'de **düşman era atlar** (sen atlamasan da).
- Sonsuz farm imkânsız; ama geride kalmak sahte seçim de değil:
- **Underdog Bonus:** Düşman senden ileri era'daysa Knowledge kazanımı +%50 ve düşman kill gold'u +%25. Geride kalmak = yüksek risk / hızlı yetişme. Gerçek bir strateji ekseni.

---

## 8. Düşman Tasarımı

### 8.1 Roller (her era'da aynı roller, farklı formlar)
Fodder · Armored · Ranged · Fast (cavalry/bike) · Siege · Support (medic/commander) · Air (Era 5+) · Boss

### 8.2 Era örnek listeleri
- **Ancient:** Raider, Spearman, Archer, Shield Soldier, War Elephant (mini-elite), Battering Ram (siege)
- **Classical:** Legionary, Phalanx (formation), Slinger, Chariot, Siege Colossus parçaları
- **Medieval:** Footman, Knight, Crossbowman, Siege Tower, Catapult, War Priest (support)
- **Gunpowder:** Musketeer, Grenadier, Cavalry, Cannon Crew, Armored Wagon
- **Industrial:** Rifleman, MG Team, Field Artillery, Early Tank, Biplane (air)
- **Modern:** Infantry, Sniper, IFV, Tank, Helicopter, Drone Swarm, Missile Launcher (siege), EW Truck (electronics)

### 8.3 Siege — en önemli düşman
Frontline'da savaşmaz; menzile girince **doğrudan kaleye** vurur. Ordu ona geç ulaşır → oyuncunun aktif müdahalesi burada en değerlidir. Her siege ekranda kırmızı castle ikonu + spawn duyurusu ile işaretlenir.

### 8.4 Elite modifiers (tekrar oynanabilirlik)
Armored (+%100 armor) · Raging (+%50 speed) · Veteran (+dmg) · Commander (çevre +%20 atk) · Shielded (ilk 3 hit blok) · Explosive (ölünce AoE)

### 8.5 Formations (Era 2+)
```
SHIELD WALL          COMBINED ARMS
🛡🛡🛡🛡              Tank
  🏹🏹🏹          Inf Inf Inf + Medic
```
Shield Wall: slash bloklanır → TAP/Heavy tower ister. Medic'li grup: önce Medic'i TAP'le → aktif mekaniğe anlam.

### 8.6 Wave preview
Her büyük wave öncesi: `45% Infantry · 30% Heavy · 15% Ranged · 10% Siege` — oyuncu build'i buna göre ayarlar.

---

## 9. Boss'lar

Era sonu boss'ları — hepsi **bölgesel weakpoint** taşır (aktif mekanik precision aracına dönüşür):

| Era | Boss | Weakpoint mekaniği |
|---|---|---|
| Ancient | War Elephant | Sırtındaki howdah — TAP; bacaklar Control ile yavaşlar |
| Classical | Siege Colossus | Eklem noktaları — sırayla kırılır |
| Medieval | Armored Warlord | Kalkanı DRAG ile düşür → gövde açılır |
| Gunpowder | Grand Bombard | Reload anında namlu — timing penceresi |
| Industrial | Landship | Paletler (mobilite) vs taret (dmg) — hangi sırayla? |
| Modern | Superheavy Tank | Taret weakpoint + drone eskortu (önce hava temizliği) |

Boss süresi hedefi: 60–90 sn. Boss sırasında normal akış durmaz, azalır.

---

## 10. Kale

### 10.1 Görsel evrim (Steam GIF ana malzemesi)
Wood Camp → Wooden Fort → Stone Keep → Medieval Castle → Star Fortress → Bunker → Modern Command Base

### 10.2 Dört stat (build kimliği kaleden okunur)
| Stat | Etkisi |
|---|---|
| **WALL** | Kale HP + pasif repair |
| **GARRISON** | Ordu üretim hızı/kapasitesi |
| **ENGINEERING** | Tower dmg/range/slot |
| **COMMAND** | Max Command + dolum hızı + ability gücü |

Her era geçişinde stat'lara harcanacak puan gelir; run içi gold ile de yükseltilir.

---

## 11. Ekonomi

### 11.1 Üç kaynak — daha fazlası yok
| Kaynak | Gelir | Gider |
|---|---|---|
| **GOLD** | Pasif 5/sn + kill (1–20) + frontline bonusu (max +%20) | Tower build/upgrade, ordu yapıları, **repair**, slot açma |
| **KNOWLEDGE** | Wave temizleme + Supply Point + Underdog Bonus | Era atlama, tech seçimleri |
| **COMMAND** | Pasif 4/sn + kill iadesi (cap'li) + Last Stand | Aktif ability'ler |

### 11.2 Formüller (başlangıç değerleri, tuning'e açık)
```
kill_gold(enemy)   = base_cost(enemy) × 0.4
wave_knowledge(n)  = 20 + 5n            (era içi wave no)
era_cost(e)        = 350 × 1.6^(e-1)    (350, 560, 900, 1430, 2290)
repair_cost        = missing_HP × era_çarpanı × 0.5   (gold sink)
tower_cost(tier)   = 80 × 2.2^tier
slot_cost(n)       = 200 × 3^(n-3)      (4. slot 200, 5. slot 600, 6. slot 1800)
enemy_hp(era,wave) = base × 1.35^era × 1.06^wave
```
Zorluk artışı HP çarpanından çok **karmaşıklık** ekler (§12).

### 11.3 Gold sink dengesi
Late-game gold birikimi kararları anlamsızlaştırmasın diye: repair sürekli sink, slot maliyeti üstel, era içi tower tier'ları pahalı. Hedef: oyuncu her wave arasında "neye harcasam" kararı verir, "her şeye yetiyor" durumuna era sonuna kadar ulaşmaz.

---

## 12. Zorluk Eğrisi — HP değil karmaşıklık

| Aşama | Eklenen baskı |
|---|---|
| Era içi wave 1 | Swarm (sayı) |
| Wave 2–3 | Armored karışımı |
| Elite | Modifier'lı birimler |
| Siege wave | Kale tehdidi + escort |
| Boss | Weakpoint + akış devam |
| Era 2+ | Formations |
| Era 3+ | Çoklu siege |
| Era 5+ | Hava ekseni |
| Era 6 | Electronics (tower susturma) |

---

## 13. Roguelite Katmanı

### 13.1 Upgrade seçimi
Era başına 2 seçim noktası (+ boss sonrası 1 nadir seçim) = run başına ~15–18 upgrade. Her seferinde 3'ten 1 seç.

### 13.2 Upgrade havuzu (~100 hedef; kategori başına örnekler)

**BLADE (aktif-DRAG):** Slash dmg +%25 · Slash genişliği +%30 · Bleed (3 sn DoT) · Kill → +2 Command (cap +2) · Double Slash (ikinci hat %50 dmg) · Slash armor'ın %30'unu deler · Bleeding düşmana +%40 dmg

**PRECISION (aktif-TAP):** TAP dmg +%40 · TAP maliyeti −3 · Weakpoint crit ×2.5 · Mark: TAP'lenen hedef 5 sn işaretli · Chain: kill'de yakına sıçrar

**BARRAGE (aktif-HOLD):** AoE yarıçapı +%30 · Burn alanı bırakır · Maliyet −8 · Çift atış (gecikmeli ikinci vuruş)

**FORTRESS (tower):** Tower dmg +%20 · Range +%15 · Rapid attack speed +%25 · Heavy pierce (2 hedef deler) · Chain Shot · Area burn süresi +%50 · Control slow +%20 · Tower kill → +1 gold

**ARMY:** Üretim hızı +%25 · Birlik HP +%30 · Lifesteal %10 · Officer aura (+%15 dmg) · Ölen birlik %20 ihtimalle yeniden doğar · Cavalry charge dmg +%50 · Specialist etkisi ×1.5

**CASTLE/ECONOMY:** Kale HP +%40 · Pasif repair · Gold geliri +%20 · Knowledge +%25 · Wave sonu faiz (%5, cap'li) · Slot indirim %30

**SYNERGY (nadir, build tanımlayıcı):**
- **Oil + Fire:** Oil tower kaplar, herhangi bir fire kaynağı Ignite → büyük AoE
- **Mark + Artillery:** İşaretli hedeflere tower'lar öncelik verir + %30 dmg
- **Bleed + Cavalry:** Kanayan düşmana cavalry charge +%40
- **Last Stand mastery:** Last Stand bölgesinde tower attack speed +%50
- **Commander:** DRAG ile vurulan düşman MARKED → ordu +%50 dmg vurur

### 13.3 Örnek build'ler (tasarım hedefi: hepsi kazanabilmeli, hiçbiri tek başına yetmemeli)
- **Blade:** dmg→genişlik→bleed→command iadesi→double slash — oyuncu sürekli biçer, ama Shielded/Armored düşmanlar tower desteği zorlar
- **Fortress:** tower odaklı — kale katliam yapar ama siege ve electronics oyuncu müdahalesi ister
- **Army:** 30v40 dev savaşlar — sustain sınırı tower desteği ister
- **Commander (hibrit):** aktif oyun orduyu bufflar — en yüksek tavan, en çok dikkat ister

### 13.4 Meta progression — güç değil, seçenek
Run'lar arası **Legacy Points** → yeni içerik unlock: yeni tower hatları, birimler, ability'ler, synergy kartları. Asla "+%X başlangıç gücü" verilmez (power creep freni). İlk run havuzu bilinçli dar (öğrenme), 5 run'da havuz 2 katına çıkar.

---

## 14. Denge Kapıları (test edilebilir kurallar)

%35/30/25/10 hedefi doğrudan ölçülemez; yerine bu kapılar telemetri ile doğrulanır:

1. **AFK testi:** Oyuncu 60 sn input vermezse ilgili wave kaybedilmeli (Elite+ wave'lerde 30 sn).
2. **Solo-slash testi:** Yalnızca aktif ability ile (tower/ordu yatırımı olmadan) Elite wave geçilememeli.
3. **Comeback oranı:** Frontline %25'e gerileyen run'ların en az %35'i toparlanabilmeli (Last Stand çalışıyor mu?).
4. **Build çeşitliliği:** Kazanan run'larda hiçbir arketip build %40'tan fazla paya sahip olmamalı.
5. **Underdog kullanımı:** Run'ların %15–30'unda oyuncu bilinçli era geciktirmeli (daha azsa bonus zayıf, daha çoksa bozuk).
6. **Command idle:** Oyuncu ortalama Command'ın %80+ dolulukta bekletiyorsa maliyetler yüksek demektir.

---

## 15. UX / Okunabilirlik

- **0.3 sn kuralı:** her düşman tipi anında okunur — Armored: gri HP bar · Fast: ⚡ ikon · Siege: kırmızı 🏰 ikon · Air: kanat · Elite: altın çerçeve · Support: yeşil artı
- **Hit feedback:** damage number, kısa hit-stop (30–60 ms), screen shake (siege/boss vuruşları), slash izi VFX
- **Duyurular:** "HORDE APPROACHING — 35s", "SIEGE WEAPON SPOTTED", "BOSS WAVE IN 20 SEC" — banner + ses
- **Wave preview paneli** (kompozisyon yüzdeleri) büyük wave'lerden önce
- **Ölüm ekranı:** hangi sistemin yetersiz kaldığını gösterir ("Kale hasarının %70'i siege'den geldi") — öğrenme döngüsü

### Görsel stil
Kingdom Rush × hand-drawn battlefield: büyük kafalı karakterler, belirgin siluet, abartılı silahlar, az frame + bol hit reaction + güçlü VFX. Birlik başına 5 animasyon yeterli: Idle, Walk, Attack, Hit, Death.

### Performans
Normal 20–50 unit, swarm 80–150. Collision **frontline band** üzerinden basitleştirilir (birlikler banda snap olur, birebir fizik yok); görsel kalabalık ≠ hesap kalabalığı.

---

## 16. Modlar ve Fazlama

| Faz | İçerik |
|---|---|
| **MVP (prototip)** | 1 era (Medieval), §17 kapsamı |
| **v1.0 (Early Access)** | 6 era, ~100 upgrade, 6 boss, Doctrine sistemi (Legion/Architects/Warlords/Engineers/Merchants), unlock meta |
| **Post-launch** | Endless History (leaderboard), Mutators (Long Winter, Endless Horde), Challenges (One Man Army, Great Wall, Pacifist Commander, Swarm), Civilizations (fictional: Empire/Nomads/Eastern Kingdom/Northern Tribes), Perfect Slash |

> Meta katmanları bilinçli fazlandı: Doctrine + Civ + Mutator + Challenge aynı anda launch'ta scope ve tuning yükü olarak taşınamaz.

---

## 17. MVP Kapsamı (prototip — eğlence kanıtı)

**Tek era: Medieval. 10–15 dk run. Soru: "bir wave daha oynar mıyım?"**

- **3 tower:** Archer (Rapid), Ballista (Heavy), Fire Pot (Area)
- **3 birlik:** Swordsman, Spearman, Archer
- **5 düşman:** Raider, Shieldman, Archer, Knight, Catapult (siege)
- **1 boss:** War Elephant (howdah weakpoint)
- **2 aktif ability:** Sword Slash (DRAG), Arrow Rain (HOLD) — TAP MVP'de yok
- **Frontline sistemi** (bonuslar dahil, Last Stand dahil)
- **15 upgrade** (Blade 4, Fortress 4, Army 4, Synergy 3)
- Command energy, wave preview, hit feedback tam sette

**MVP'de bilinçli YOK:** era geçişi, Knowledge, meta progression, formations, doctrine. Bunlar core loop eğlenceli çıkarsa gelir.

**MVP başarı kriteri:** funscore ≥ 70 + §14 kapı 1–3 yeşil.

---

## 18. Risk Kaydı

| Risk | Fren |
|---|---|
| Slash her şeyi öldürür → TD anlamsız | Command maliyeti + Shielded/Armored counter + kill-iade cap |
| Tower'lar çok güçlü → oyuncu izler | Siege + Support + Electronics: yüksek öncelikli hedefler oyuncu ister |
| Ordu çok güçlü | Sustain sınırı (üretim < kayıp) |
| Era = reskin sıkıcılığı | Era başına zorunlu 1 yeni mekanik (§7.1) |
| Scope patlaması | Arketip mirası: 5 tower + 5 birlik + 8 düşman rolü TEK'er entity |
| Snowball (frontline gold) | +%20 cap + Last Stand rubber-band |
| Run çok uzun | 30–45 dk hedefi; Endless ayrı mod |
| Meta katman enflasyonu | Faz planı (§16) |

---

## 19. Açık Sorular (prototip cevaplar)

1. Last Stand +%50 Command yeterli comeback aracı mı, yoksa geçici tower buff'ı da gerekli mi?
2. DRAG slash'ın max uzunluğu sabit mi, upgrade ile mi büyür? (MVP: sabit, upgrade ile büyür)
3. Boss sırasında normal akış ne kadar azalmalı? (MVP: %50)
4. Kill-gold ile pasif gold oranı 50/50 mi 30/70 mi? (MVP: ~40/60, telemetri ile ayarla)
5. Era Pressure %5/wave doğru tempo mu? (Underdog Bonus kullanım oranıyla ölç, §14.5)
