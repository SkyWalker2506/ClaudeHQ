# ClaudeHQ — Cross-Project Workspace

> Tum genel kurallar `~/Projects/claude-config/CLAUDE.md` dosyasindadir ve burada da gecerlidir.

## Bu proje nedir

ClaudeHQ, Musab Kara'nin Claude ekosisteminin merkezi calisma alanidir. Buradan tum projelere erisebilir, cross-project gorevler yonetebilirsin.

## Oturum basinda

1. `~/Projects/claude-config/CLAUDE.md` oku ve uygula
2. `projects.json` dosyasini oku — hangi projeler var, nerede, Jira key'i ne
3. Yanit basinda etiket: `(Jarvis)` — Sonnet disindaysa model adini ekle

## Cross-project calisma

- "X projesinde sunu yap" → `projects.json`'dan path'i bul, o dizine git, orada calis
- Birden fazla projeyi etkileyen gorevlerde her projeyi sirayla veya paralel isle
- Her projenin kendi CLAUDE.md kurallari o proje icinde gecerlidir

## Jira

- Bu workspace'in Jira projesi: **CHQ**
- Proje bazli Jira key'leri `projects.json`'da tanimli

## HQ Proje Yonetimi

ClaudeHQ, tum projeleri merkezi olarak yonetir. `~/Projects` altinda CLAUDE.md olan her klasor otomatik proje olarak taninir.

### Komutlar

- `./scripts/hq scan` — ~/Projects tara, projects.json olustur/guncelle
- `./scripts/hq new <isim> [--jira KEY]` — Yeni proje olustur (git, CLAUDE.md, sprint dahil)
- `./scripts/hq dispatch <proje>` — Tek proje icin Claude session baslat
- `./scripts/hq dispatch --all` — Tum aktif projeler icin toplu session baslat
- `./scripts/hq status [proje]` — Durum dashboard'u goster
- `./scripts/hq sprint plan <proje>` — Sprint planlama session'i baslat
- `./scripts/hq sprint list [proje]` — Sprint'leri listele
- `./scripts/hq sprint init <proje>` — Proje icin sprint tracking baslat
- `./scripts/hq monitor [--watch]` — Calisan session'lari izle
- `./scripts/hq stuck` — Takilan projeleri goster
- `./scripts/hq archive <proje>` — Projeyi pasife al
- `./scripts/hq activate <proje>` — Projeyi aktife al
- `./scripts/hq config [proje]` — Proje konfigurasyonunu goster
- `./scripts/hq logs <proje>` — Session loglarini goster

### Dosya Yapisi

- `projects.json` — Otomatik kesfedilen projeler (gitignored, `hq scan` ile olusur)
- `sprints/{proje}/sprint-{N}.json` — Sprint tanimlari ve task'lar
- `progress/{proje}.json` — Otomatik ilerleme takibi (gitignored)
- `templates/` — Sprint ve task prompt sablonlari

### Tipik Workflow

1. `hq scan` — Projeleri kesfet (veya `hq new <isim>` ile yeni proje ac)
2. `hq sprint init <proje>` — Sprint dosyasi olustur, task'lari tanimla
3. `hq dispatch <proje|--all>` — Claude session'larini baslat
4. `hq monitor --watch` — Ilerlemeyi izle
5. `hq stuck` — Takilan projeleri kontrol et
6. `hq logs <proje>` — Detayli log incele

## Yeni proje kurma

1. `mkdir ~/Projects/<proje-adi>`
2. `cd ~/Projects/claude-config && ./install.sh`
3. (Opsiyonel) Jira projesi olustur
4. `projects.json`'a ekle:
   ```json
   {"name": "<adi>", "path": "~/Projects/<adi>", "jira": "<KEY>", "git": "SkyWalker2506/<repo>"}
   ```
5. Git repo olustur ve push et
