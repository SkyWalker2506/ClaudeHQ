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

## Yeni proje kurma

1. `mkdir ~/Projects/<proje-adi>`
2. `cd ~/Projects/claude-config && ./install.sh`
3. (Opsiyonel) Jira projesi olustur
4. `projects.json`'a ekle:
   ```json
   {"name": "<adi>", "path": "~/Projects/<adi>", "jira": "<KEY>", "git": "SkyWalker2506/<repo>"}
   ```
5. Git repo olustur ve push et
