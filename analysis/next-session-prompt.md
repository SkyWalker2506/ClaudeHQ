# Sonraki Session Prompt

Bu prompt'u yeni bir Claude Code session'ında yapıştır. Hem yeni sistemi test eder hem eksikleri tamamlar.

---

## Prompt:

```
Bu session'da 2 görev var: test + tamamla.

## GÖREV 1: Yeni Harness Sistemi Test

Bugün harness engineering overhaul yapıldı. Aşağıdakileri kontrol et ve sonuçları raporla:

### Test 1: Hibrit kural aktif mi
- ~/.claude/CLAUDE.md oku — hibrit dispatch tablosu var mı (Trivial/Kucuk-Orta/Buyuk)?
- "ASLA KENDİN İŞ YAPMAZSIN" yerine hibrit tablo olmalı

### Test 2: Lazy-load çalışıyor mu
- global/charter.md ve global/harness.md dosyalarında INDEX bölümü var mı?
- Bu dosyaları TÜM okuma — sadece INDEX'i oku ve raporla

### Test 3: CLAUDE.md trim edildi mi
- ~/Projects/claude-config/CLAUDE.md kaç satır? (197 olmalı, 714 değil)
- charter.md kaç satır? (~235)
- harness.md kaç satır? (~325)

### Test 4: Knowledge injection hazır mı
- config/agent-dispatch.md'de KNOWLEDGE bloğu var mı?
- global/skills/dispatch/SKILL.md'de "knowledge_index" geçiyor mu?

### Test 5: Telemetry sidecar
- scripts/log_dispatch.py'da "sidecar" geçiyor mu?
- dispatch SKILL.md'de "current_dispatch.json" var mı?

### Test 6: N6 aktif mi
- config/agent-registry.json'da N6 status "active" mi, model "gpt-5.4" mı?

### Test 7: Default model Sonnet mi
- settings.json'da model "claude-sonnet-4-6" mi?

Her test için ✅ veya ❌ raporla.

---

## GÖREV 2: Eksik Agent/Skill Güncellemeleri

Aşağıdaki 4 dosyayı güncelle. Her biri küçük değişiklik — Codex CLI ile yap:
cd ~/Projects/claude-config && cat /tmp/harness-fixes.md | codex exec --model gpt-5.4 --full-auto -

### Fix 1: A2 Task Router AGENT.md
Dosya: agents/orchestrator/task-router/AGENT.md
Identity bölümünden hemen SONRA ekle:

## Hibrit Dispatch Kurali

Jarvis görev büyüklüğüne göre sana iletir:
- Trivial (1-10 satır) → Jarvis kendisi yapar, sana gelmez
- Küçük-Orta (10-300 satır) → SEN karar verirsin: hangi agent, hangi model, hangi backend
- Büyük/Stratejik (300+ satır) → A1 (Opus) danışılır, sen dispatch edersin

Senin işin: görev analizi → agent seçimi → model/backend ataması → dispatch. Jarvis'in constraint'lerini (örn: "GPT kullan", "parçala") dikkate al.

### Fix 2: A1 Lead Orchestrator AGENT.md
Dosya: agents/orchestrator/lead-orchestrator/AGENT.md
Boundaries/Always bölümüne ekle:

- Buyuk/stratejik gorevlerde Jarvis sana danisir — sen mimari karar ver, A2'ye dispatch talimatı ver
- Jarvis trivial/kucuk isleri sana getirmez — sadece 300+ satir, multi-repo, mimari kararlar

### Fix 3: Dispatch SKILL.md hibrit routing
Dosya: global/skills/dispatch/SKILL.md
Dispatch akışının başına ekle:

### Hibrit Routing (Phase 0)
Dispatch başlamadan önce görev büyüklüğünü kontrol et:
1. Trivial (1-10 satır, tek dosya) → Dispatch YAPMA, Jarvis'e "kendin yap" de
2. Küçük-Orta (10-300 satır) → Normal dispatch akışına devam et
3. Büyük/Stratejik (300+ satır) → Önce A1'e danış, sonra dispatch et

### Fix 4: Tüm agent AGENT.md'lere KNOWLEDGE farkındalığı
Dosya: agents/orchestrator/jarvis/knowledge/agent-dispatch-rules.md
Sonuna ekle:

### KNOWLEDGE Bloğu Farkındalığı (Nisan 2026)
Dispatch sırasında her sub-agent'ın prompt'una KNOWLEDGE bloğu eklenir:
- identity: AGENT.md'den Identity + Boundaries
- knowledge_index: knowledge/_index.md tam içeriği
- knowledge_path: ilgili knowledge dosyalarının yolu

Agent'lar bu bilgiyle başlar — boş model gibi davranmazlar. İlk iş olarak knowledge_path'teki ilgili dosyaları okumalılar.

---

## Son adımlar
1. Değişiklikleri commit et: "feat: align agents with hybrid dispatch + knowledge injection system"
2. install.sh --auto --skip-login --stacks general çalıştır
3. Push et
4. Sonuçları raporla — test sonuçları + yapılan değişiklikler
```
