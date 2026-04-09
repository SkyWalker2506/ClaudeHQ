# Cursor Mega-Prompt: Agent Knowledge Migration + Overhaul

> Bu prompt'u Cursor'da `~/Projects/claude-config` reposu acikken yapistir.
> 132 eski formattaki agent'i Knowledge-First formatina gecirip tam overhaul yapar.

---

## PROMPT BASLANGICI — Asagidaki her seyi Cursor'a yapistir

---

Sen bir agent migration uzmanisisin. Bu repo'da (`claude-config`) 15 kategori altinda ~144 agent tanimi var. 12'si zaten Knowledge-First formatinda (dizin yapisi), 132'si hala eski tek-dosya formatinda. Gorev: Eski formattaki TUM agentlari yeni formata gecir VE iceriklerini zenginlestir (overhaul).

## ADIM 0: FORMATLARI OGREN

Calismaya baslamadan once:

1. **Yeni format ornegi oku** — `agents/` altinda dizin olarak tanimli 2-3 agent bul (AGENT.md + knowledge/ + memory/ iceren dizinler). Bunlarin AGENT.md dosyalarini oku ve formati ogren.

2. **Eski format ornegi oku** — `agents/` altinda tek `.md` dosyasi olarak tanimli 2-3 agent bul. Bunlari oku ve eski formati anla.

3. Farki anla:
   - **Eski**: `agents/{kategori}/{isim}.md` — tek dosya, 3 section (Amac, Kapsam, Escalation)
   - **Yeni**: `agents/{kategori}/{isim}/AGENT.md` + `knowledge/_index.md` + `memory/sessions.md` + `memory/learnings.md`

**ONEMLI:** Zaten dizin formatinda olan agentlara DOKUNMA. Sadece tek `.md` dosyasi olan agentlari isle.

## ADIM 1: KESFET

```bash
# Kategorileri listele
ls -d agents/*/

# Her kategoride eski formattaki agentlari bul (tek .md dosyalari, README haric)
find agents/ -mindepth 2 -maxdepth 2 -name "*.md" ! -name "README.md" -type f

# Zaten migrated olanlari bul (dizin yapisi)
find agents/ -mindepth 2 -maxdepth 2 -name "AGENT.md" -type f
```

Toplam eski format agent sayisini not et. Her kategoriyi sirayla isliyeceksin.

## ADIM 2: KATEGORI KATEGORI ISLE

Her kategori icin asagidaki islemi uygula. Bir kategoriyi bitirince commit at, sonra digerine gec.

### Her eski agent icin:

#### 2a. Eski dosyayi oku

`agents/{kategori}/{isim}.md` dosyasini oku. Icerigini anla:
- Amac (Purpose) → Identity'ye donusecek
- Kapsam (Scope) → Scope'a donusecek
- Escalation → Boundaries'e donusecek
- YAML/metadata (tier, capabilities, model) → Korunacak

#### 2b. Dizin olustur

```
agents/{kategori}/{isim}/
├── AGENT.md
├── knowledge/
│   └── _index.md
└── memory/
    ├── sessions.md
    └── learnings.md
```

#### 2c. AGENT.md OLUSTUR (OVERHAUL)

Eski icerigi **aynen kopyalama**. Agent'in domain'ini ve amacini anlayarak zengin bir AGENT.md olustur. Asagidaki sablonu kullan:

```markdown
# {Agent Display Name}

> {Tek satirlik tanim — bu agent'i ozel kilan ne?}

## Identity

**Role:** {Spesifik rol unvani}
**Tier:** {junior|mid|senior} ({haiku|sonnet|opus})
**Category:** {kategori adi}

{2-3 paragraf:
- Bu agent KIM? Hangi domain uzmani?
- Temel yaklasimi/felsefesi ne?
- Benzer agentlardan farki ne?
- Ne tur gorevlerde cagrilmali?

Eski "Amac" section'indan BILGI al ama AYNEN KOPYALAMA.
Agent'in domainine ozgu, zengin bir kimlik olustur.}

## Scope

### In-Scope
- {Bu agent'in sorumlu oldugu somut gorev 1}
- {Bu agent'in sorumlu oldugu somut gorev 2}
- {Bu agent'in sorumlu oldugu somut gorev 3}
- {Eski "Kapsam" section'indan turetilir + zenginlestirilir}

### Out-of-Scope
- {Bu agent'in YAPMADIĞI sey 1}
- {Bu agent'in YAPMADIĞI sey 2}
- {Acikca sinir ciz — baska agentlarin alani}

## Workflow

{Agent'in tipik is akisi — domain'e ozgu adimlar:}

1. **Intake** — {Gorevi nasil alir/anlar}
2. **Analysis** — {Domain-spesifik analiz yaklasimi}
3. **Execution** — {Cekirdek calisma sureci}
4. **Verification** — {Kalite kontrolleri}
5. **Delivery** — {Ciktiyi nasil paketler/sunar}

{Her adimi agent'in gercek domain'ine gore yaz.
Ornek: Bir "code-reviewer" agent icin:
1. Intake: PR/diff'i oku, context'i anla
2. Analysis: OWASP, performance, readability kontrolleri
3. Execution: Satir satir review + oneriler
4. Verification: Onerilerin tutarliligini kontrol et
5. Delivery: Review raporu formatinda sun}

## Decision Tree

| Durum | Aksiyon |
|-------|---------|
| {domain'e ozgu senaryo 1} | {karar/aksiyon} |
| {domain'e ozgu senaryo 2} | {karar/aksiyon} |
| {domain'e ozgu senaryo 3} | {karar/aksiyon} |
| Gorev scope disinda | Escalate → {uygun agent} |
| Yaklasim konusunda belirsizlik | Kullanicidan aciklama iste |
| Kritik/riskli degisiklik | Insan onayi iste |

{En az 4-5 satir olsun. Agent'in gercek karsilasacagi durumlari dusun.}

## Boundaries

### Escalation Kurallari
- {Ne zaman → Kime escalate edilir}
- {Hangi durumda insan mudahalesi istenir}

### Red Flags
- {Bu domain'de dikkat edilmesi gereken uyari isareti 1}
- {Bu domain'de dikkat edilmesi gereken uyari isareti 2}

### Direnmesi Gereken Rasyonelleştirmeler
- "{Gunah cikartma 1}" → {Neden direnmeli}
- "{Gunah cikartma 2}" → {Neden direnmeli}

{Eski "Escalation" section'indan BILGI al ama zenginlestir.
Agent'in domain'ine ozgu gercekci red flags ve rasyonellestirmeler ekle.}

## Tools & Skills
- {arac/skill 1}: {ne zaman kullanilir}
- {arac/skill 2}: {ne zaman kullanilir}

{Agent'in capability tag'lerinden ve domain'inden turet.
Somut tool/skill isimleri kullan (varsa).}

## Output Template

{Bu agent'in tipik ciktisi nasil gorunmeli?
Format, basliklar, icerik yapisi.
Domain'e gore degisir — bir reviewer icin "review raporu",
bir architect icin "design doc", bir tester icin "test plani" vs.}
```

#### 2d. knowledge/_index.md OLUSTUR

```markdown
# {Agent Name} — Knowledge Index

> Domain: {agent'in uzmanlık alanı}
> Last updated: {bugunun tarihi}

## Topics

| Topic | File | Status |
|-------|------|--------|
| {domain konusu 1} | — | planned |
| {domain konusu 2} | — | planned |
| {domain konusu 3} | — | planned |

{3-5 domain-relevant konu basligi ekle.
Henuz icerik dosyasi olusturma — sadece _index.md'de "planned" olarak listele.
Gercek knowledge dosyalari /agent-refine ile olusturulacak.}
```

#### 2e. memory/ DOSYALARI OLUSTUR

**memory/sessions.md:**
```markdown
# Session Log
<!-- Otomatik guncellenir — elle duzenleme -->
```

**memory/learnings.md:**
```markdown
# Learnings
<!-- Agent calistikca biriken ogrenimler -->
```

#### 2f. Eski dosyayi sil

```bash
rm agents/{kategori}/{isim}.md
```

### Kategori commit'i

Bir kategorideki TUM agentlari isledikten sonra:

```bash
git add agents/{kategori}/
git commit -m "migrate(agents/{kategori}): {N} agents → Knowledge-First + overhaul"
```

## ADIM 3: DOGRULAMA

Tum kategoriler islendikten sonra:

```bash
# Toplam AGENT.md sayisi (eski + yeni hepsi)
find agents/ -mindepth 2 -maxdepth 2 -name "AGENT.md" | wc -l
# Beklenen: ~144 (132 migrated + 12 zaten vardi)

# Kalan eski format (0 olmali)
find agents/ -mindepth 2 -maxdepth 2 -name "*.md" ! -name "README.md" -type f | wc -l
# Beklenen: 0

# Her agent dizininde gerekli dosyalar var mi?
for d in agents/*/*/; do
  [[ -f "$d/AGENT.md" ]] || echo "MISSING AGENT.md: $d"
  [[ -f "$d/knowledge/_index.md" ]] || echo "MISSING knowledge/_index.md: $d"
  [[ -f "$d/memory/sessions.md" ]] || echo "MISSING memory/sessions.md: $d"
  [[ -f "$d/memory/learnings.md" ]] || echo "MISSING memory/learnings.md: $d"
done
```

## ADIM 4: FINAL COMMIT

```bash
git add -A
git commit -m "migrate(agents): tum 132 agent Knowledge-First + overhaul tamamlandi"
```

## ONEMLI KURALLAR

1. **Zaten dizin formatinda olan agentlara DOKUNMA** — Sadece tek `.md` dosyalari isle
2. **Eski icerigi AYNEN KOPYALAMA** — Zenginlestir, overhaul yap, ama eski bilgiyi kaybet
3. **Her agent OZGUN olmali** — Ayni template'i kopyala-yapistir yapma. Her agent'in domain'ini dusun ve ona gore yaz
4. **Tier/model bilgisini KORU** — Eski dosyadaki tier (junior/mid/senior) yeni AGENT.md'ye tasınmalı
5. **Turkce yaz** — Agent tanimlari Turkce olmali (eski formatla tutarli)
6. **Kategori bazinda commit** — Her kategoriyi bitirince commit at
7. **README.md dosyalarina DOKUNMA** — Kategori README'leri ayni kalmali

## DEVAM ETME (RESUME)

Eger islem yarim kaldiysa, kullanici sana su mesaji gonderecek:

> "{kategori} kategorisinden devam et"

Bu durumda:
1. O kategoriye git
2. Hangi agentlar zaten dizin formatinda (islenmis), hangisi hala .md (islenmemis) kontrol et
3. Sadece islenmemis olanlari isle
4. Kaldığın yerden devam et

---

## PROMPT SONU
