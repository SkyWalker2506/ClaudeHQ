# Kalıcı bilgi tabanı — mevcut durum ve tartışılacaklar

> **Bu doküman GPT ile tartışmak için hazırlandı.** Amaç: ajanların iş yaparken güvenilir
> biçimde eriştiği, yeni bulgularla güncellenen, kotayı boşa harcamayan bir bilgi katmanı
> tasarlamak. Aşağıdaki her sayı **ölçülmüştür**, tahmin değil; ölçülemeyenler öyle işaretli.

**Tarih:** 2026-07-29 · **Ortam:** Claude Code, ~67 proje deposu, macOS

---

## 0. Soru

Bilgi katmanının **dördü birden** olması gerekiyor ve bugün hiçbiri tam değil:

1. **Garanti** — her çalışmada okunduğundan emin olmak
2. **Güncel** — yeni bulgu paketi güncellesin
3. **Ucuz** — her oturumda her şeyi yüklemesin; sadece gerekeni, gerektiğinde
4. **Göz ardı edilmesin** — "ucuz" olsun diye hiç bakılmayan bir şeye dönüşmesin

3 ile 4 birbirine karşıt ve asıl tasarım problemi bu gerilimde.

---

## 1. Ne var — sayılarla

| Katman | Adet | Fiilen kullanılan |
|---|---|---|
| Agent tanımı (`AGENT.md`) | **212** | **1** (`web-game-editor-craftsman`, o da proje-local dosyadan) |
| Agent registry kaydı | 210 (43 "aktif") | 0 registry dispatch'i, son 30 gün |
| Agent-local knowledge dosyası | 1.124 (ort. 5,3/agent) | tamamı 2026-04'te donmuş |
| Agent `memory/learnings.md` | 205 | **183'ü bayt bayt aynı boilerplate** |
| Skill | 72 kaynak / 84 mirror | progressive disclosure **çalışıyor** (L1 24 KB / L2 324 KB) |
| Plugin | 22 repo / 21 marketplace | **8 kurulu** |
| ADR-002 knowledge paketi | 6 repo, **70 madde** | doğrulayıcı **3** repoda |
| Auto-memory dosyası (ClaudeHQ) | **3.171** (13 MB) | indekste **233** |
| Auto-memory (tüm ekosistem) | 47 dizin, **7.750 dosya** | — |
| Graph cache | 67 projenin **1'inde** | 101 gün bayat, tüm kenarlar `contains` |

**Subagent çağrısı, tüm 3.795 transcript boyunca:** 524. Bunun **301'i (%57,4)** `general-purpose`
— ki `harness.md:266` bunu "KESİN YASAK, tek istisna yok" diye yazıyor. İhlallerin yazılacağı
log dosyası hiç oluşturulmamış.

**Hive (ajanlar arası paylaşılan öğrenme):** tüm ömründe **1 kayıt** (2026-06-09).
**Dispatch telemetrisi:** 2026-04-12'den beri boş.

---

## 2. Ölçülen dört başarısızlık kalıbı

### 2.1 Bilgi var, erişilemiyor — %93

ClaudeHQ memory dizini: **3.171 dosya, 3,2 MB, ~839.000 token** birikmiş bilgi.
`MEMORY.md` indeksi **233 tanesini** linkliyor. Kalan **2.938 dosya** hiçbir mekanizma
tarafından yüzeye çıkarılamıyor.

Alternatif erişim yolu **yok**: veritabanı yok, embedding yok, vektör indeksi yok. Düz `.md`
dosyaları ve elle yazılmış bir indeks. Her oturumda yalnız indeks yükleniyor (~4.600 token);
tekil dosya ancak model karar verip `Read` çağırınca açılıyor — ve indekste görünmeyen dosyayı
açmayı düşünmesinin bir yolu yok.

Bugünkü "compaction" (261 KB → 18,6 KB) tam olarak bunu üretti: girdiler indeksten çıkarıldı,
dosyalar diskte bırakıldı.

Ek: tekil dosyalarda **915 wiki-link, 329'u kırık (%36)**; 105'i başka projenin memory'sine
işaret ediyor ve izolasyon nedeniyle **asla** açılamaz.

### 2.2 "Zorunlu okuma" hiçbir yerde zorunlu değil

`ADR-002` bir okuma sırası tarif ediyor: `STATE.md → knowledge/_index.md → maddeler → iş →
receipt'e citedTopics`. 202/211 `AGENT.md` bunu "zorunlu" diye yazıyor.

**Zorlayan hiçbir şey yok.** Ve bunu en net söyleyen, ADR'nin kendi reposu:

> *"Ajanı knowledge okumaya zorlayan bir runtime yazılmadı. ADR-002 §4'ün sırası bir brief
> kuralıdır… **Kapı değil, kayıt.**"* — `bm-contracts/docs/AI/STATE.md`

`citedTopics` alanı **hiçbir gerçek receipt'te** yazılmamış; tüm JSON/YAML taramasında yalnız
şemanın kendisinde geçiyor. Alıntılamayı *seçen* ajan tutarlı olmak zorunda (şema zinciri
mutasyonla sınanıyor); **hiç alıntılamayana hiçbir şey olmuyor**.

Doğrulayıcı olan tek repoda ihlal **sıfır** (15/15). Doğrulayıcı olmayan repolarda 70 maddenin
10'unda ADR'nin zorunlu tuttuğu "Sınırlar" bölümü **yok**. Kapının olduğu yerde kural tutuyor,
olmadığı yerde tutmuyor — kanıt tam olarak bu dağılımda.

### 2.3 Aynı kısıtı elle taşıma — tek oturumda 29 bin token

Bu oturumun transcript'inden:

```
açılan agent                 : 32
brief'lerin toplam boyutu    : 115.566 karakter  (~28.900 token)
  MDP yasağını tekrar yazdım : 25 kez
  git yasağını tekrar yazdım : 13 kez
  durma şartını yazdım       : 14 kez
```

Ajanların paylaşması gereken kalıcı kısıtlar her brief'e **elle kopyalanıyor**. Ve
kopyalanmadığında uygulanmıyor: bu oturumda bir ajan, canlı başka bir ajanın yarım dosyalarını
kendi commit'ine süpürdü — çünkü o kısıt o brief'te yoktu.

Ayrıca iki ajan **aynı hatayı bağımsız olarak keşfetti** (`team.lineHeight`/`team.width`'in
yanlış birimde puanlanması). Birincinin bulgusunun ikinciye ulaşan bir kanalı olsaydı, ikinci
onu okuyup geçerdi.

### 2.4 Yazma hattı çalışıyor ama boşa akıyor

`auto-memory-review.sh` (Stop hook) 2026-04-23'ten beri **8.681 dispatch** yapmış — ama
`MEMORY_DIR` tek bir dizine **hardcoded**, yani hangi projede çalışırsan çalış oraya yazıyor,
ve **469 permission hatası** var. Haftalık konsolidasyon script'i (`auto-dream.sh`) yazılmış
ama **hiç kurulmamış** — LaunchAgent yok, log hiç oluşmamış.

Ve bakım aracı yapısal olarak yetersiz: `/memory-prune` skill'i "max 15 tool call" limitiyle
3.171 dosyayı tarayamaz.

---

## 3. Bugün gerçekten çalışan üç şey

Tasarımın bunları **korumas**ı lazım:

1. **Progressive disclosure (skill'ler).** L1 frontmatter 24 KB, L2 gövde 324 KB — 13:1.
   Model açıklamayı görüyor, gövdeyi ancak çağırınca yüklüyor. Aradığınız "sadece gerektiğinde"
   davranışının çalışan hâli **bu**.
2. **"Hangi görevde ne okunur" tablosu.** 6/6 knowledge paketinde var. 15 maddelik bir paketten
   ilgili 1-2 maddeye yönlendiriyor. İlkel ama işe yarıyor.
3. **İndeks ile karar dosyasının ayrılması.** Bir pakette `_index.md` bir tur boyunca "iki madde
   aynı sonuca vardı" diye yazdı; **varmamışlardı**. Çözüm: indeks bir *maddeler tablosudur*,
   karar mercii değil. Çelişkiler numaralı ayrı bir dosyada (Ç-1…Ç-12), her biri gerekçesiyle.
   **Madde ile karar farklı türler**: madde birikir, karar çelişkiyi kapatır.

---

## 4. En öğretici tek olay — bugün, bana oldu

Bir ADR'ye "bu alan hesaplanamaz, kanoniklik tanımsız, bu ADR'nin açık borcu" diye not
düştüm. **Yanlıştı.** Kural zaten vardı ve notu yazdığım commit'ten **bir önceki** commit'te
eklenmişti: tam bir şema, 12 golden vektörle, satır sonu/BOM/NFC/sıralama/algoritma kimliği
dahil.

İddiayı, o ADR'nin kendi şemalar klasörünü açmadan yazdım.

Bunun tasarıma girdisi doğrudan: **bilgiyi kaydetmek problemin kolay yarısı.** Zor yarısı,
ona danışması gereken şeyin gerçekten danıştığından emin olmak. Ben — bilgi katmanını kuran
taraf — kendi kayıtlı bilgimi okumadan onun hakkında iddiada bulundum. 212 ajanın bunu
yapmayacağını varsaymak için sebep yok.

Aynı örüntü kapılarda **beş kez** çıktı bu oturumda: bir kontrol yeşil döndü çünkü **iki
taraflı bir gerçeğin bir tarafına** bakıyordu. Kaynak bildiriminin üç biçiminden birini tanıyan
kontrol; dalları erişilemez olduğu için hiç başarısız olamayan kapı; "spec'te manipulator varsa
metne ulaşmış mı" diye sorup "elemanın eylemi var mı" diye sormayan kapı (68 buton eylemsiz
geçti); şablonu olmayan liste (8 liste boş kutu çizdi); ve kapsam raporunun kendisi — 79
odaklanabilir eleman sayıp sağlıklı göründü, oysa 68'i hiçbir şey yapmıyordu.

**Bir kuralın uygulanabileceği şeyi saymak, uygulandığı şeyi saymak değil.** Hepsi mutasyon
testiyle yakalandı; hiçbiri kapıyı okuyarak yakalanmadı.

---

## 5. Tartışmak istediğim sorular

**A. Erişim.** 839 bin token'lık bir gövdeden ihtiyaç anında doğru 2 KB'ı getirmenin yolu ne?
Embedding/RAG mı, elle küratörlü hiyerarşik indeks mi, ikisi birden mi? Memory palace benzeri
mekânsal/ilişkisel indeksleme bu problemde gerçek bir kazanç sağlıyor mu, yoksa metafor mu?

**B. Garanti.** "Ajan okudu" nasıl **kanıtlanır**? Bugünkü cevap `citedTopics[]` ve hiç
yazılmıyor. Alternatifler: okumayı zorunlu kılan bir tool-gate; brief'e enjekte edilen özet;
çıktıyı bilgiye karşı doğrulayan bir kontrol. Hangisi kotayı en az harcar?

**C. Ucuzluk ile göz ardı etme arasındaki gerilim.** Progressive disclosure çalışıyor ama
"görünmeyeni açmayı düşünmeme" riskini de üretiyor — 2.938 dosya tam olarak bu. Bir şeyin
**var olduğunu** ucuza bildirip **içeriğini** pahalıya açmanın doğru granülaritesi ne?

**D. Güncelleme.** Bir ajan bir bulgu ürettiğinde bu nereye yazılmalı, kim onaylamalı, ve
diğer ajanlara nasıl ulaşmalı? Bugün: agent→global terfi mekanizması **yok**, hive ölü,
otomatik yazma tek dizine hardcoded.

**E. Çelişki.** Kaynak sınıfı hiyerarşisi `measured > docs > talk` iki `docs` çeliştiğinde
sessiz kalıyor — bu oturumda iki kez oldu. Hakem kim/ne olmalı?

**F. Bayatlama.** 1.124 agent knowledge dosyası 2026-04'te donmuş, 183 `learnings.md` birbirinin
aynısı. Kullanılmayan bilgi ile yanlış bilgi arasındaki farkı ne ölçer?

**G. Ölçek kararı.** 212 agent'ın 211'i hiç kullanılmadı. Bilgi tabanını **212 ajan için** mi
tasarlamalı, yoksa önce ajan sayısını gerçek kullanıma indirmeli mi?

---

## 6. Kısıtlar

- Claude Code oturumları; `MEMORY.md` otomatik yükleniyor, tekil dosyalar model kararıyla
- Memory **proje bazlı izole**; cross-project erişim bugün yok (329 kırık wiki-link'in 105'i bu yüzden)
- Kota gerçek bir kısıt — her oturumda 800 bin token yüklenemez
- Ajanlar paralel çalışıyor (bu oturumda aynı anda 8'e kadar) ve birbirinin çıktısını görmüyor
- Çözüm **ölçülebilir** olmalı: bu ekosistemin tekrar tekrar öğrendiği ders, ölçmeyen bir
  kapının er geç yeşil yalan söylediği
