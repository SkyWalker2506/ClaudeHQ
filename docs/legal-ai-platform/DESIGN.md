# Legal AI Platform — Dizayn Dokümanı

**Versiyon:** 1.0 (Baseline)
**Tarih:** 2026-08-11
**Durum:** Teknik mimari donduruldu; ürün hipotezleri doğrulama aşamasında
**Dikey:** İcra-İflas
**İlk ürün:** SEARCH (AI'sız)

---

## 0. Bu doküman nedir, nasıl kullanılır

Bu doküman, avukatlara yönelik hukuk arama + AI platformunun **dondurulmuş tasarım baseline'ıdır**. Üç turluk mimari değerlendirmenin sonucudur ve iki tür karar içerir:

1. **Teknik mimari sabitleri** — yeniden tartışmaya açılmaz; değişiklik ancak saha verisi bir hipotezi düşürürse yapılır.
2. **Ürün hipotezleri** — falsifiable'dır; her biri önceden tanımlı `PASS / REVISE / KILL` kriterine bağlıdır (§3).

Sonraki doküman bu baseline'ı **değil**, doğrulama sonuçlarını konuşur:
`Validation & Execution Plan — Legal AI Platform / İcra-İflas MVP`.

Kural: Mimarinin dördüncü kez gözden geçirilmesi değer üretmez. Bundan sonraki değişiklikler yalnızca **saha verisiyle** gerekçelendirilir.

---

## 1. Ürün özeti

**Problem:** Avukatın hukuki araştırması bugün dağınık kaynaklar (Yargıtay Karar Arama, mevzuat.gov.tr, Resmî Gazete, ticari veri tabanları) arasında bölünmüş, yavaş ve doğrulaması zor.

**Ürün:** Tek arama çubuğundan başlayan, kaynağı doğrulanabilir hukuk platformu. Dört katman, sırayla açılır:

| Katman | Tanım | AI? | Faz |
|---|---|---|---|
| **SEARCH** | Hukuk dikeyinde arama: mevzuat, içtihat, RG, dilekçe örnekleri. Tarihsel versiyon farkındalıklı. | Hayır | Faz 1 (MVP) |
| **ASK** | Hukuki soru → retrieval → kaynaklı cevap + deterministik atıf doğrulama | Evet | Faz 2 |
| **DRAFT** | Şablon + kaynak + AI ile dilekçe üretimi; doğrulanmış/doğrulanamayan atıf raporu | Evet | Faz 3 |
| **DOSYA** | Dosya yükleme + analiz (premium/kurumsal) | Evet | En son |

**Moat tanımı (kesinleştirilmiş):** AI modeli değil; birbirini besleyen dört varlık:
- Güvenilir, sürdürülebilir edinilmiş hukuk corpus'u
- Fıkra/bent granülaritesinde **tarihsel versiyonlama** ("17 Mayıs 2021'de yürürlükteki hüküm neydi?")
- Üstün **Türkçe hukuk retrieval'ı**
- **Deterministik citation doğrulama** (ileride: citation graph + negatif atıf)

Bunlar tek tek kopyalanabilir; kopyalanamayan, birbirini beslemeleridir: tarihsel versiyonlama → temporal citation validation'ı mümkün kılar; citation graph → negatif atıf kontrolünü mümkün kılar; hukukçu doğrulamalı gold set → sağlayıcı değiştirme kabiliyetini mümkün kılar. Gold set bir test dosyası değil, **şirket varlığıdır**.

---

## 2. Dondurulmuş teknik kararlar

Aşağıdakiler tartışmaya kapalıdır:

### Güvenlik / mimari
- **Frontend hiçbir zaman doğrudan AI provider'a bağlanmaz.** Provider anahtarları (OpenAI/Gemini/Claude/service-role) client'ta asla bulunmaz. Tüm AI trafiği kendi Gateway'imizden geçer.
- Zincir: `Frontend → API → Auth → Rate Limit → User Budget → Global Budget → Abuse Detection → Search/RAG → Model Router → Provider`
- Kullanıcı yalnızca kendi Supabase session JWT'sini görür (süreli, RLS'li).
- Tüm kullanıcı tablolarında **RLS** zorunlu. Admin erişimi frontend RLS'i üzerinden değil, kontrollü backend endpoint'lerinden.

### Maliyet modeli
- Kota birimi **sorgu sayısı değil, maliyet** (AI Cost Credit).
- MVP maliyet motoru sade: `pre-check (user + global kota) → reserve → çağrı → reconcile`
  - + **idempotency key** (retry'da çift ücretlendirme yok)
  - + **reservation TTL + süpürücü job** (streaming'de kopan bağlantının kilitli rezervi)
  - + rate limit **Redis'te** (Postgres'te hot-row contention yaratmaz); rezervasyon Postgres'te (para = transaction)
  - + kill switch 2 kademe: throttle @%85, stop @%100
- %60/75/85/90/95/98 çok kademeli degradation, risk skoru, percentile bazlı abuse modeli → **gerçek 500-1.000 kullanıcı verisi görülene kadar yapılmaz.**
- Global cap, kullanıcı kotaları toplamından değil, **beklenen gerçek kullanımın 2-3 katından** türetilir; aşımda önce ağır kullanıcılar throttle edilir.
- Kur politikası: iç birim USD-endeksli credit, kullanıcıya TL gösterimi.

### Organizasyon modeli
- Hedef birim tekil avukat değil, **büro**. Şema baştan: `organizations / organization_members / organization_roles / subscriptions / subscription_seats / usage_accounts / usage_ledger / budget_policies`
- Bütçe hiyerarşisi: `Platform → Organization → User` (Team katmanı: şemada yer var, ilk sürümde tablo kurulmaz).
- Aynı IP'den çok hesap **tek başına abuse sinyali değildir** (büro = NAT arkasında 20 avukat); IP yalnızca diğer sinyallerle birlikte değerlendirilir.

### Gizlilik (Gate 1'de detaylanacak; ilkeler sabit)
- `Client → Privacy Gateway → Search/AI Gateway` katmanı.
- Deterministik alanlar (TCKN, telefon, IBAN, e-posta) regex/checksum; ad-soyad/adres NER ile tespit; gerekmedikçe pseudonymization (`Ahmet Yılmaz → PERSON_1`).
- **Pseudonymization kişisel veri statüsünü kaldırmaz, riski azaltır.** Savunma "veri aktarmıyoruz" değil, "aktarılan veri minimize edilmiş ve alıcı tarafından tek başına ilişkilendirilemez"dir.
- Rehydration map: **session-scope** (çok turlu tutarlılık için), şifreli, TTL'li, oturum sonunda imha; **log / APM / hata izi / prompt arşivine asla yazılmaz.**
- Admin'in ham kullanıcı içeriğine erişimi varsayılan **yok**; gerekirse ayrı privilege + gerekçe + süreli elevation + immutable audit.
- Log ayrımı: **analytics log** (token, maliyet, latency — prompt içermez, uzun saklanır) vs **content log** (kısa retention, örn. 30 gün; kullanıcı bilinçli açarsa saklanır).
- KVKK rolleri baştan sabitlenmez; **faaliyet bazında** veri sorumlusu/işleyen sınıflandırması yapılır. Yurt dışı aktarım: güncel kademeli rejim (yeterlilik kararı → uygun güvenceler → istisnalar); hangi provider/region/alt-işleyenin hangi aktarım mekanizmasına dayanacağı **ürün tasarımı aşamasında** hukukçuyla belirlenir. Standart sözleşme yolunda Kurul'a bildirim yükümlülüğü provider eklemeyi bir uyum işlemi yapar → `provider_transfer_basis` router filtresi olur.
- Avukatlık Kanunu m.36 (sır saklama) KVKK'dan ayrı ve daha sert yükümlülüktür; DOSYA'nın en sona bırakılmasının ana nedeni.
- Provider'larla zero-data-retention / no-training anlaşması: maliyet kalemi değil, **satış argümanı**.

### Model yönetimi (Faz 2+)
- Model isimleri ve fiyatları **hiçbir dokümanda/kodda hard-code edilmez**; `provider_models / provider_price_versions / eval_results` DB'den gelir.
- Router mantığı: `eligible models → minimum quality threshold → privacy/region requirements → latency → cheapest qualifying model`. Yani "en ucuz" değil, **"gerekli kaliteyi geçen en ucuz."**
- Router, eval seti (Gate 3) olmadan devreye alınmaz. İlk sürüm: tek model + tek yedek.

### Citation doğrulama (Faz 2+; tasarım sabit)
Deterministik kontroller (SQL/string/identifier matching — LLM değil):
1. Atıf kimliği corpus'ta var mı? (`İİK m.62`, `2021/1234 E., 2022/5678 K.`)
2. Kullanılan **tarihsel sürüm** doğru mu?
3. Kaynak, generation context'ine gerçekten verilmiş miydi?
4. Tırnak içi alıntı kaynakta **birebir substring** olarak var mı?
Tutmayan atıf: silinir veya `⚠ doğrulanamadı` etiketiyle gösterilir.
Semantik verifier ("kaynak bu iddiayı destekliyor mu") ancak bunun **üstüne** eklenir.
Kullanıcıya görünür çıktı: *"8 atıfın 8'i kaynak veritabanında doğrulandı; 7'si iddiayı güçlü biçimde destekliyor."* Bu, ürünün satılabilir farkıdır.
Negatif atıf ("bu karar sonradan aşılmış mı") MVP dışı; ancak veri modeli `citation_graph` için **şema seviyesinde** yer bırakır.

### Cache (Faz 2+; ilkeler sabit)
- İki katman: **retrieval cache** (genel corpus, güvenli, kazancın çoğu) ve **answer cache** (yalnızca kişisel veri içermeyen genel sorular).
- Cache key: `normalized_query + jurisdiction + corpus_version + effective_date + retrieval_result_hash + answer_policy_version` — kanun değişince eski cache otomatik geçersiz.
- Pseudonymize içerik taşıyan sorgular **hiç cache'lenmez**; cache **asla org sınırını aşmaz**.
- MVP'de answer cache yok; retrieval cache de trafik oluşana kadar ertelenir.

### UX ilkeleri
- Kullanıcıya para sayacı gösterilmez ("₺73,42 / ₺100,00" yok). Dil: "bu ay 163 işlem, planınız rahat yetiyor."
- Kota bitişinde sert kesme yok: soft cap → ucuz modele düşür; ek kredi satın alma (gelir kalemi); hard stop yalnızca açık kötüye kullanımda.
- Global kill switch kullanıcıya yansıtılmaz; son çaredir.
- Kullanıcı model adı seçmez; "Hızlı / Derin Analiz" seçer.

---

## 3. Ürün hipotezleri ve karar kuralları

Hipotezler **kutsal karar değildir**. Eşikler saha verisi gelmeden, Validation & Execution Plan'da gerekçesiyle birlikte kilitlenecek; aşağıda karar çerçevesi sabitlenmiştir:

| # | Hipotez | Test | Önceden belirlenen karar |
|---|---|---|---|
| H1 | Avukatların hukuk araştırmasında ciddi acısı var | 20 görüşme | Yeterli sayıda avukat problemi **kendiliğinden** anlatmazsa SEARCH-first yeniden değerlendirilir |
| H2 | Mevcut araçlardan ölçülebilir fark yaratabiliriz | 50 soruluk rakip benchmark (Lexpera/Kazancı/Jurix + genel AI) | Rakipler kabul edilen kaliteyi zaten sağlıyorsa farklılaşma yeniden konumlandırılır (örn. corpus yarışına girmeyip mevcut DB'lerin üstünde doğrulama/dilekçe katmanı olmak) |
| H3 | Kullanıcı ödeme yapar (~1.000 TL/ay hipotezi) | Görüşme + fiyat testi | Doğrulanmazsa paket/fiyat yeniden tasarlanır |
| H4 | PostgreSQL tabanlı Türkçe search yeterli | FTS fixture (§8) | Belirlenen recall/precision seviyesine ulaşmazsa search backend alternatifleri (Elasticsearch/Typesense) değerlendirilir |
| H5 | Corpus sürdürülebilir biçimde edinilebilir | Corpus Acquisition Matrix (§7) | Kritik kaynak sınıfının yasal/sürdürülebilir edinimi yoksa kapsam değiştirilir |

**Doğrulama disiplini:**
- Eşikler **veri toplanmadan önce** yazılır ve kilitlenir; sonradan verinin geçtiği yere taşınmaz.
- Görüşme metodu: ilk bölümde üründen hiç bahsedilmez; avukatın **son 5 gerçek araştırması** anlattırılır (nereden başladı, kaç dakika, nerede zorlandı, hangi araç). Ürün ancak sonda gösterilir.
- Örneklem bilinçli çeşitlendirilir: tanıdık/teknoloji-meraklısı çevre dışına; farklı yaş, büro ölçeği, dijital yetkinlik.
- Benchmark tekrar koşulabilir kaydedilir: ekran görüntüsü, tam sorgu, tarih, süre, sonuç sırası (§9 şeması).

---

## 4. Gate planı ve paralel track'ler

**Gate = karar noktası, takvim fazı değil.** Kararlar seri, işler paralel.

```text
GATE -2  Problem / ödeme isteği doğrulaması (15-20 avukat görüşmesi)
GATE -1  Rakip benchmark (50 gerçek icra-iflas sorusu)
GATE  0  Corpus feasibility (kaynak + hak + acquisition + temporal model)
GATE  1  Privacy / avukatlık sırrı / KVKK mimarisi
GATE  2  İcra-iflas SEARCH
GATE  3  Gold set + retrieval benchmark
GATE  4  ASK + deterministik citation validation
GATE  5  DRAFT
GATE  6  DOSYA
```

Aynı anda başlayan track'ler:

| Track | İçerik | Bağımlılık |
|---|---|---|
| **A — Market** | Avukat görüşmeleri, rakip testi, fiyat testi | Yok — hemen |
| **B — Corpus** | Kaynak envanteri, İİK temporal prototipi, kaynak hukuku | Yok — hemen |
| **C — Search R&D** | Türkçe normalizasyon, `turkish_stem`, phrase dictionary, kısaltma parser, FTS benchmark | Yok — halka açık mevzuat metniyle hemen |
| **D — Legal/Privacy** | KVKK danışmanlığı, avukatlık sırrı, provider/DPA/transfer yapıları | Yok — uzun teslim süreli, erken başlar; Gate 0'ın bazı satırlarını bu track doldurur |

**Gate 0 çıkış kriteri (daraltılmış):**
> İcra-iflas MVP'sinin ihtiyaç duyduğu her kaynak sınıfı için edinim yöntemi ve hukuki statü belirlenmiş; kullanılamayan kaynak açıkça `BLOCKED`; İİK üzerinde fıkra/bent seviyesinde temporal model **uçtan uca çalışan bir prototiple** doğrulanmış.

Gate 0 kapsam sınırı — **yapılmayacaklar:** tam citation graph, bütün hukuk corpus'u, kusursuz ingestion, yüz binlerce karar, gelişmiş negative-treatment. Citation graph için yalnızca DB'de yer bırakılır.

**Not:** Gate -2'nin çıktısı (avukatların gerçek soruları) Gate 3 gold set'inin ham maddesidir; Gate -1'in 50 sorusu gold set'in çekirdeğidir. Bu işler birbirini besler.

---

## 5. Faz 1 mimarisi ve stack

Faz 1'de **AI yok.** Kapsam: Auth + org modeli, icra-iflas SEARCH, ingestion pipeline, temporal corpus, FTS.

### Stack

| Bileşen | Seçim | Not |
|---|---|---|
| Frontend | **Vite + React + TypeScript SPA** | Vercel'de host; Tauri taşınabilirliği için SSR'sız (§6) |
| Pazarlama sitesi | Next.js (sonra) | SEO ihtiyacı uygulamada değil, tanıtımda |
| Auth + operasyonel DB + FTS | **Supabase** (Free → Pro) | `app` ve `corpus` şemaları baştan ayrı |
| Arama API | Vercel fonksiyonu → **Postgres RPC** | İş mantığı DB fonksiyonlarında (taşınabilir); Vercel'e özgü API'lere yaslanılmaz |
| Ingestion worker | **GitHub Actions cron** | Vercel'de DEĞİL (serverless profili uymaz); büyüyünce Fly/Railway container |
| Ham snapshot arşivi + yedekler | **Cloudflare R2** | 10 GB ücretsiz, sıfır egress, S3-uyumlu API (kilitlenme yok) |
| AI Gateway | — | Faz 2'de **ayrı servis** olarak doğar |

### Akış

```text
GitHub Actions (her gece)
   ├─ RG / mevzuat / AYM kontrol
   ├─ yeni belge → ham kopya (hash'li) → R2
   └─ parse → temporal model → Supabase corpus şeması → FTS index

GitHub Actions (haftalık)
   └─ pg_dump → R2                      (Free tier'da otomatik yedek yok)

Kullanıcı
   └─ SPA (Vercel) → API → Postgres FTS + metadata filtre → sonuç
```

### Ingestion altın kuralı: bir kez çek, çok kez parse et
Her indirilen sayfa/PDF'in ham hali `source_url + fetch_date + snapshot_hash + parser_version` ile R2'ye kaydedilir; parser **ham kopyadan** çalışır, canlı siteden değil. Gerekçe: (a) fıkra/bent parser'ı ilk seferde doğru çıkmaz, yeniden parse bedava olmalı; (b) kaynak kesilirse `rebuild_time` cevabı bu arşivdir; (c) provenance, citation validator'ın zeminidir.

### Faz 1 kaynak kapsamı
Güvenli kaynaklarla başlanır: **mevzuat.gov.tr, Resmî Gazete arşivi, AYM Kararlar Bilgi Bankası.** Yargıtay toplu çekimi Gate 0'ın `BLOCKED/OK` kararına kilitlidir — "script hazır" diye genişletilmez. Hedef tüm mevzuat değil: İİK uçtan uca + FTS testine yetecek icra-iflas alt kümesi.

### Free tier sınırları ve yükseltme eşiği

| Sınır | Etki | Önlem |
|---|---|---|
| Vercel Hobby ticari kullanıma kapalı | Prototip OK; **ilk ödeme alan gün Pro zorunlu** | Planlı eşik: "ilk abone = Vercel Pro + Supabase Pro günü" (~45$/ay) |
| Supabase Free: 1 hafta trafiksiz proje uyur | Demo öncesi sürpriz | Günlük ingestion cron aynı zamanda keep-alive |
| Supabase Free: otomatik yedek yok | Kullanıcı/gold-set verisi kurtarılamaz | Haftalık pg_dump → R2 |
| Supabase Free: 500 MB DB | İİK + icra alt kümesi + FTS sığar | Sığmıyorsa kapsam Faz 1'i aşmış demektir — lehte fren |
| Supabase Free: 1 GB Storage | RG PDF'leri hızla doldurur | Ham arşiv R2'de; yalnızca dikey belgeler; HTML gzip |
| GH Actions: 2.000 dk/ay (private) | Günlük tarama + haftalık yedek çok altında | — |

**Kural:** Free tier sınırları **veri modeli kararlarını değiştirmez.** ("Storage dar, snapshot tutmayalım" / "500 MB az, fıkra granülaritesinden vazgeçelim" yasak.) Sınırlara kapsam daraltarak ve ucuz yan depoyla uyulur, model basitleştirilerek değil.

---

## 6. Taşınabilirlik (Web → Windows/Mac)

**Karar:** Desktop bir "port" değil, "kabuk" olacak — **Tauri**, aynı SPA build'ini sarar (Electron değil: ~10MB vs ~150MB, düşük bellek, v2 ile mobil kapısı). Desktop Faz 1'de **yapılmaz**, yalnızca engellenmez.

Taşınabilirliği belirleyen üç disiplin:
1. **Backend frontend framework'üne gömülmez.** Gateway ayrı API servisidir; web/desktop/mobil aynı API'nin istemcileridir. (Faz 1 istisnası: ince arama endpoint'leri Vercel fonksiyonunda yaşayabilir; mantık Postgres RPC'de kalır.)
2. **Uygulama saf SPA'dır**; SSR gereken her şey ayrı pazarlama sitesindedir.
3. **Platforma dokunan her şey adapter arkasında:** token saklama (cookie/keychain), OAuth callback (redirect/deep-link), dosya kaydetme, güncelleme, pencere/bildirim. Uygulamanın geri kalanı platformu bilmez. Supabase Auth PKCE akışı desktop'ta deep-link ile çalışır (bilinen yol).

### Repo yapısı

```text
repo/
├── apps/
│   ├── web/          → Vite + React SPA (asıl ürün)
│   ├── marketing/    → Next.js (sonra)
│   └── desktop/      → Tauri kabuğu (sonra; web build'ini sarar)
├── packages/
│   ├── api-client/   → Gateway API'sine konuşan typed tek istemci
│   ├── ui/           → paylaşılan bileşenler
│   └── platform/     → storage/auth/download adapter'ları
└── services/
    └── gateway/      → API + AI Gateway + Privacy Gateway (Faz 2'de ayrı servis)
```

Not: Desktop'un gerçek değeri teknik değil, DOSYA/enterprise katmanının satış aracıdır ("verileriniz kurumunuzun makinesinde imzalı uygulamada"); zamanlaması o katmanla örtüşür.

---

## 7. Corpus mimarisi

### 7.1 Corpus Acquisition Matrix (Gate 0'ın ana çıktısı)

Her kaynak için zorunlu alanlar:

```text
source_owner              acquisition_method        legal_basis
update_frequency          retention_right           redistribution_right
derivative_right          attribution_requirement   anonymization_status
failure_mode              rebuild_time
```

- `derivative_right`: snippet göstermek ile LLM'in metni yeniden ifade etmesi **farklı haklardır**.
- `anonymization_status`: karar metninin anonimleştirilme durumu bizim KVKK yükümüzü doğrudan belirler.
- `rebuild_time`: kaynak kesilirse corpus'un snapshot'lardan yeniden kurulma süresi (`failure_mode`'un sayısal karşılığı).
- Kullanılamayan kaynak açıkça `BLOCKED` işaretlenir; ürün buna göre kapsam değiştirir.

İlk mini-matrix kapsamı: **İİK/mevzuat.gov.tr, Resmî Gazete, AYM, Yargıtay** (yalnızca bu dördü; tam matrix Gate 0'da).

### 7.2 Temporal veri modeli

Versiyonlama **madde seviyesinde kalmaz**; en az `Kanun → Madde → Fıkra → Bent` granülaritesinde. (Türk mevzuatında değişiklikler tipik olarak fıkra/bent seviyesinde yapılır; m.62 bütün olarak versiyonlanırsa "m.62/2 2021'de ne diyordu" cevaplanamaz.)

Her birimde üç tarih **ayrı** tutulur:

| Alan | Anlam |
|---|---|
| `publication_date` | Resmî Gazete'de yayım |
| `effective_date` | Yürürlük (çoğu zaman farklı, bazen ileri tarihli) |
| `applicability` | Geçici maddelerle gelen özel uygulama kuralı ("derdest dosyalara uygulanmaz" vb.) |

Üçüncüsü olmadan doğru madde bulunup **yanlış cevap** verilir. **Geçici maddeler corpus'ta birinci sınıf vatandaştır** — ek metin değil, retrieval'ın doğrudan girdisi.

Versiyon zinciri: `valid_from / valid_to / supersedes_version_id / source_snapshot_hash`. Değişiklik/ilga ilişkileri kayıt altında. Bu, "15 Mart 2023'te yürürlükteki mevzuata göre" sorgusunun ve Gate 3'teki `temporal correctness` metriğinin altyapısıdır.

`citation_graph` (karar → karar atıf/aşma ilişkisi): **şema seviyesinde yer bırakılır**, gerçek karar corpus'u görülmeden tasarlanmaz.

### 7.3 Chunking (Gate 2)

512-token kör pencere **kullanılmaz.** Belge tipine özgü parsing:
- Kanun: `Kanun → Madde → Fıkra → Bent` yapısal sınırlarında
- Karar: mümkün oldukça `metadata → olay → hukuki mesele → gerekçe → hüküm`
Her chunk, parent maddesine/kararına ve komşu bölümlerine geri bağlanabilir.

---

## 8. Türkçe arama (FTS) test planı

PostgreSQL'in `turkish` konfigürasyonu ve `turkish_stem` Snowball sözlüğü vardır → Elasticsearch'e gün-bir mecburiyet **yok**; karar benchmark'la verilir (H4). Benchmark "yeterli mi?" diye değil, **beş kırılma ekseni** üzerinden tablo üretir:

1. **Noktalı/noktasız I** — `lower()/upper()` collation'a bağlı; `İSTANBUL` → `i̇stanbul` (combining dot) `istanbul` ile eşleşmez; `tr_TR`'de `I → ı` İngilizce kelimeleri bozar. İndeks ve sorgu tarafında **aynı normalizasyon** şart; karma corpus'ta muhtemelen `unaccent` + özel normalize fonksiyonu.
2. **Over/under-stemming** — Snowball agresif davranabilir; yalnız recall değil **false positive** de ölçülür.
3. **Çok kelimeli hukuk terimleri** — `menfi tespit davası`, `takibin taliki` tek kavramdır; phrase search + elle kurulan **hukuk terim sözlüğü** (eşanlam + kısaltma; editoryal iş, corpus'un parçası).
4. **Kısaltma genişletme** — `İİK, HMK, TBK, CMK, İYUK, 12. HD` query normalization'da açılır; atıf kimlikleri (`2021/1234 E.`) FTS'e değil **ayrı parser'a** gider.
5. **Diakritiksiz giriş** — `sozlesme`, `odeme emri`; `unaccent` + `turkish_stem` TS config **sırası** kritik.

Test fixture'ı kalıcıdır: gerçek İİK metni + gerçek sorgular; chunking/normalizasyon her değiştiğinde aynı set yeniden koşulur (regression).

Retrieval pipeline (Gate 2): `query normalization → lexical → semantic → metadata filters → fusion`.
**Harici reranker MVP'de yok** — iki nedenle: (a) kullanıcı sorgusunu yurt dışı servise gönderir (Gate 1 ihlali riski; hukuk sorgusu tek başına hassas olabilir), (b) self-host GPU maliyeti "sıfıra yakın sabit maliyet" hedefini kırar. Gate 3 ölçümü kazancı kanıtlarsa eklenir.

---

## 9. Evaluation dataset

**Statü: şirket varlığı.** Geçici Excel değil; versiyonlanan, tekrar koşulabilir dataset. Aynı veri sırayla şu işlerde yeniden kullanılır: rakip benchmark → FTS regression → retrieval gold set → ASK evaluation → model değişikliği regression.

### İki ayrı varlık: `case` ve `run`

Soru tanımı (kalıcı) ile koşu gözlemi (tekrarlanan) ayrı tutulur — bir case'in çok run'ı olur:

```text
case (kalıcı, versiyonlu)              run (her koşuda yeni)
──────────────────────────             ─────────────────────────
case_id                                run_id
question                               case_id
legal_domain                           system_under_test   (Lexpera / bizim FTS / ASK v2 ...)
effective_date                         exact_query
expected_sources                       query_date
acceptable_sources                     response_time
unacceptable_results                   returned_sources
gold_set_version                       result_rank
corpus_version_bound                   screenshots
                                       reviewer
                                       verdict
                                       notes
```

### Gold set kuralları
- ~200 hukukçu-doğrulamalı soru; **~50'si held-out** (yalnız sürüm kabul testlerinde açılır — overfit önlemi).
- **Abstention puanlanır:** bilerek cevaplanamaz sorular eklenir; "corpus'ta dayanak yok" demek başarıdır.
- Gold set **corpus sürümüne bağlı versiyonlanır** (mevzuat değişince "doğru cevap" değişebilir).
- Verdict mümkün olduğunca `acceptable/unacceptable` listelerinden **mekanik türetilir**; yorum gereken alt küme ilk 50 soruda **iki bağımsız hakeme** puanlatılır — hakemler arası tutarsızlık, kabul kriterinin belirsizliğini erken gösterir.
- Hukukçu doğrulama saatleri **gerçek bütçe kalemidir** (External Cost).

### Metrikler
`Recall@5/10/20`, `MRR/nDCG`, citation precision, citation recall, unsupported-claim rate, **temporal correctness** (doğru madde + yanlış tarihsel sürüm = başarısız), abstention doğruluğu.

---

## 10. Özellik etiketleme şeması

"Birikmiş istek listesi" riskine karşı: bundan sonraki her spesifikasyon maddesi şu metadata'yı taşır — taşımayan madde MVP kapsamına **giremez**:

```text
Priority:     MUST / SHOULD / LATER
Stage:        MVP / Post-MVP / Enterprise
Owner:        Engineering / Legal / Legal Editor / Product
Dependency:   ...
Acceptance:   ölçülebilir kriter
Effort:       tahmin
External Cost: (örn. hukukçu-saati)
```

Örnek:

```text
Feature:       Deterministic Citation Validator
Priority:      MUST          Stage: ASK MVP (Faz 2)
Owner:         Engineering + Legal Editor
Dependency:    Structured corpus
Acceptance:    Gold sette citation identity precision >= hedef
External Cost: Legal validation hours
```

---

## 11. Bilinçli ertelenenler (MVP dışı)

| Ne | Ne zaman |
|---|---|
| AI (ASK/DRAFT/DOSYA) ve AI Gateway | Faz 2+ — retrieval kanıtlandıktan sonra |
| Model router | Gate 3 eval seti sonrası; ilk sürüm tek model + yedek |
| Semantic answer cache | Trafik sonrası; retrieval cache de ertelenir |
| Harici reranker | Gate 3 kazancı kanıtlarsa |
| Çok kademeli degradation + risk skorlama | Gerçek 500-1.000 kullanıcı verisi sonrası |
| Team katmanı | Gerçek büro isteyince (şemada yer hazır) |
| DRAFT şablon genişliği | İcra dikeyinde 3-5 şablonla başlanır |
| Citation graph / negatif atıf | Karar corpus'u görüldükten sonra; şimdilik şemada yer |
| Desktop (Tauri) build | İlk kurumsal talep; birkaç günlük iş olacak şekilde §6 disiplinleri şimdi |
| Ödeme altyapısı (İyzico/PayTR, e-arşiv/e-fatura, KDV, iade, seat proration) | Ödeme almadan önce; kapsamı küçümseme — muhasebe tarafı gateway'den çok kenar durum üretir |
| Yargıtay toplu ingestion | Gate 0 `OK` kararına kilitli |

**Kesilmeyecekler** (sonradan eklemesi acı, baştan ucuz): idempotency key, reservation TTL, org-seviyesi bütçe şeması, citation validator tasarımı, snapshot/provenance, fıkra/bent granülaritesi, case/run ayrımı.

---

## 12. Bilinen açık riskler

Mimari dışı, proje kaderini belirleyen üç bilinmeyen:

1. **Corpus erişimi** (H5) — tamamen bizim kontrolümüzde değil; Gate 0'ın konusu. Rakiplerin (Lexpera/Kazancı/Jurix) asıl varlığı 20 yıllık tasnifli içtihat + editoryal ekip; onlarla AI'da değil **corpus'ta** yarışıyoruz.
2. **Ölçülmemiş farklılaşma** (H2) — rakipler yeterince iyiyse hiçbir mimari kurtarmaz; Gate -1'in konusu.
3. **Dağıtım** — 1.000 ödeyen avukata ulaşma kanalı (baro, büro satışı, CAC) henüz tanımsız; Track A görüşmelerinden beslenecek.

Ayrıca: ingestion + embedding maliyeti tek seferlik değildir (her chunking revizyonu = yeniden işleme; en az 2-3 kez ödenecek); Gate 0-3 iş yükünün büyük kısmı yazılım değil (kaynak müzakeresi, editoryal sözlük, hukukçu doğrulaması) — tek dikey kararının hayati nedeni.

---

## 13. İlk çalışma paketi

Sıradaki doküman: **`Validation & Execution Plan — Legal AI Platform / İcra-İflas MVP`** — mimari anlatmaz; `hipotez → test → owner → maliyet → süre → kanıt → PASS/REVISE/KILL` formatındadır ve eşik gerekçelerini içerir.

Hemen başlayan dört iş (hiçbiri diğerini beklemez):

1. **İlk 5 avukat görüşmesi** — fikir satmadan, son 5 gerçek araştırmayı anlattırarak (§3 metodu).
2. **Rakip benchmark'ın ilk 10 sorusu** — case/run formatında (§9), ekran görüntülü, tekrar koşulabilir.
3. **Türkçe FTS spike** — gerçek İİK metninde §8'in beş ekseni; kalıcı fixture olarak.
4. **Gate 0 mini-matrix** — yalnızca İİK/mevzuat, RG, AYM, Yargıtay için edinim + kullanım durumu (§7.1 alanlarıyla).

Bu dört çalışmadan çıkacak veri, üç mimari incelemenin toplamından daha fazla şeyi değiştirecek — plan buna göre güncellenir, doküman değil.
