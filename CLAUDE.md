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

Once projeleri kesfet veya yeni proje olustur, ardindan sprint baslat ve task'lari tanimla. Dispatch ile Claude session'larini calistir, monitor ile izle, takilan varsa mudahale et. Tum komutlar yukaridaki "Komutlar" bolumunde listelenmistir.

## Ecosystem Sync (genel kural)

Agent, plugin veya skill eklendiginde/silindiginde/degistiginde **tum downstream sayfalari guncelle**. Bu kural her zaman gecerlidir — hangi projede calisirsan calis.

### Downstream haritasi

| Degisiklik | Guncellenen sayfalar |
|------------|---------------------|
| Agent eklendi/silindi (`claude-config/agents/`) | `claude-config/README.md`, `claude-agent-catalog/README.md`, `ClaudeHQ/README.md` |
| Plugin eklendi/silindi (`ccplugin-*`) | `claude-config/README.md`, `claude-marketplace/README.md`, `marketplace.json`, `ClaudeHQ/README.md` |
| Plugin marketplace.json'a eklendi | `claude-marketplace/README.md` (tablo), `marketplace.json` (description) |
| Skill eklendi/silindi (`claude-config/global/skills/`) | (sayilar henuz README'lerde yok, eklenirse guncelle) |
| Proje eklendi/silindi | `ClaudeHQ/README.md` (projects tablosu), `projects.json` (`hq scan`) |

### Nasil calistirilir

```bash
# Sayilari say, tum README'leri guncelle
./scripts/hq sync

# Nelerin degisecegini goster (dosya degistirmez)
./scripts/hq sync --dry-run
```

### Kural

1. Agent/plugin/skill degisikligi yapildiginda `hq sync` calistir
2. Guncellenen dosyalari ilgili repo'larinda commit et
3. README'lerdeki sayilari asla elle yazma — her zaman `hq sync` kullan

## Yeni proje kurma

1. `mkdir ~/Projects/<proje-adi>`
2. `cd ~/Projects/claude-config && ./install.sh`
3. (Opsiyonel) Jira projesi olustur
4. `projects.json`'a ekle:
   ```json
   {"name": "<adi>", "path": "~/Projects/<adi>", "jira": "<KEY>", "git": "SkyWalker2506/<repo>"}
   ```
5. Git repo olustur ve push et
