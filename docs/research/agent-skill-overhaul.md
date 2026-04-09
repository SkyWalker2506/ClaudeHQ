# Agent & Skill System Overhaul — Research Brief

> **Status:** Research pending
> **Owner:** Overhaul Research Team (N3, N6, N7, N8, K9)
> **Target:** claude-config agent & skill sistemi

---

## Problem

Mevcut agent sistemi 139 agent tanimliyor ama hepsi ayni sablonu kullaniyor:
- Ayni 3-section format (Amac, Kapsam, Escalation)
- Ayni "autonomous" template
- Gercek davranis farki yok — sadece capability tag'leri ve model secimi degisiyor
- Skill'ler de benzer sekilde yapisal derinlik eksik

## Hedef

1. **Agent Overhaul** — Agentlari gercek uzman haline getir (katmanli context, ozel workflow, karar agaci, tool talimatlari, cikti sablonu)
2. **Skill Quality Uplift** — Skill'lere structured process, red flags, verification, common rationalizations ekle
3. **Ikisini birlestir** — Agent, hangi skill'i ne zaman ve nasil kullanacagini bilsin

## Arastirilacak Konular

### R1: Agent Architecture Patterns
- Mevcut en iyi agent framework'leri (CrewAI, AutoGen, LangGraph, OpenAI Swarm, Claude sub-agents)
- Her birinin agent tanim formati, routing mekanizmasi, memory yonetimi
- Hangisi bizim Claude Code ortamina en uygun?
- "Gercek uzmanlik" icin minimum gerekli context nedir?

### R2: Skill Design Best Practices
- addyosmani/agent-skills format analizi (SKILL.md anatomy) — github.com/addyosmani/agent-skills
- GitHub spec-kit SDD methodology analizi — github.com/github/spec-kit (spec-driven.md okunmali)
- Cursor rules, Windsurf rules karsilastirmasi
- Skill'in "ne zaman kullanilmali / kullanilmamali" boundary tanimlari
- Red flags ve common rationalizations pattern'i nasil yazilir?
- Verification steps nasil tasarlanir?

### R3: Persistent Memory Architecture
- MemPalace analizi — mempalace.tech / github.com/milla-jovovich/mempalace
  - Verbatim storage vs AI-curated summary: trade-off'lar
  - Hiyerarsik organizasyon: Wing → Room → Hall → Closet → Drawer
  - AAAK 30x lossless compression formati (LLM-native readable)
  - ChromaDB vector search + SQLite metadata
  - Local-first, zero API cost
- Bizim mevcut memory sistemi (~/.claude/projects/.../memory/) ile karsilastirma
- Agent-specific memory: her agent kendi alaninda ne hatirlayacak?
- Session-arasi bilgi kaybi nasil sifirlanir?
- Mem0, Zep, LangMem gibi alternatif memory layer'lar

### R4: Layered Context Strategy
- L0 (minimal kimlik) vs L1 (workflow) vs L2 (referans bilgi) katman tasarimi
- Token butcesi hesaplama: her katman ne kadar token harcar?
- Lazy-load mekanizmasi: dosyadan mi, MCP'den mi, inline mi?
- Cache stratejisi: ayni agent tekrar cagrildiginda ne yuklenecek?

### R4: Workflow & Decision Tree Design
- Agent'a ozel workflow nasil tanimlanir? (DSL, flowchart, step-list)
- Karar agaci formati: if/then rules mi, scoring mi, LLM-based routing mi?
- Escalation vs delegation vs rejection kararlari
- Gated workflow pattern'i (addyosmani'deki gibi human-in-the-loop gates)

### R5: Output Template & Quality Standards
- Her agent tipi icin cikti formati (design doc, review report, test plan, etc.)
- Structured output vs free-form: ne zaman hangisi?
- Quality scoring: agent ciktisi nasil degerlendirilir?
- 5-axis review modeli bizim sisteme nasil uyarlanir?

### R6: Composition & Orchestration
- Skill composition: bir komut birden fazla skill'i nasil cagirmali?
- Agent-to-agent delegation: A calisirken B'yi nasil tetikler?
- Pipeline tanimi: define → plan → build → verify → review → ship
- Artifact hand-off: bir asamanin ciktisi sonrakinin girdisi

### R7: Competitive Analysis
- Devin, Cursor Agent, Windsurf Cascade, Codex nasil yapilandirmis?
- Replit Agent, Lovable, Bolt — ayni pattern'ler mi?
- Acik kaynakli agent-skill kutuphaneleri (agent-skills, spec-kit, vb.)
- Ne yapiyorlar ki biz yapmiyoruz?

## Cikti Beklentisi

Her arastirma konusu icin:
1. **Findings** — ne buldun (bullet list, kaynakli)
2. **Recommendation** — bizim sisteme nasil uyarlanmali
3. **Implementation sketch** — somut format/sablon onerisi
4. **Token impact** — tahmini token maliyeti degisikligi

## Atama

| Konu | Agent | Neden |
|------|-------|-------|
| R1: Agent Architecture | N6 (AI Systems Architect) | Framework bilgisi + mimari karar |
| R2: Skill Design | N7 (Skill Design Specialist) | Skill anatomy uzmani |
| R3: Persistent Memory | N3 (Prompt Engineer) | Memory mimarisi + token optimizasyonu |
| R4: Layered Context | N3 (Prompt Engineer) | Token optimizasyonu + context tasarimi |
| R5: Workflow Design | N8 (Workflow Engineer) | Proses tasarimi + karar agaclari |
| R6: Output Templates | N7 (Skill Design Specialist) | Format standartlari |
| R7: Composition | N6 (AI Systems Architect) | Orkestrasyon mimarisi |
| R8: Competitive | K9 (AI Tool Evaluator) | Benchmark + karsilastirma |

## Siralama

1. Paralel: R1 + R2 + R3 + R8 (bagimsiz arastirmalar)
2. Paralel: R4 + R5 (R1 + R3 sonuclarina bagli)
3. Seri: R6 → R7 (birbirine bagli)
4. Final: Tum bulgulari birlestir → Overhaul Plan v1
