# CRAFT — Claude's Reliable AI Framework for Transactions

## Context

CRAFT, Unity Editor icinde AI kaynakli islemleri guvenli, geri alinabilir sekilde calistiran bir execution engine. Amac: Claude Code Unity sahnesini manipule ederken transaction safety, validation ve rollback garantisi saglamak.

---

## Stratejik Analiz: MCP Yaklasimi Secimi

### Mevcut Piyasa

| | Unity Official MCP | 3rd Party (Standalone) | Sifirdan |
|---|---|---|---|
| **Paket** | `com.unity.ai.assistant@2.4-pre.1` | IvanMurzak (55 tool), AnkleBreaker (288 tool) | — |
| **Bridge** | Built-in (SSE) | Kendi Node.js server | Yazilacak |
| **Tool kayit** | `[McpTool]` attribute, auto-scan | Kendi attribute sistemi | Yazilacak |
| **Stability** | Pre-release (hala -pre) | Mature (production'da) | — |
| **Fiyat** | Unity Points (kredi sistemi, ucretli) | Free & open source | Free |
| **Unity versiyon** | 6000.0+ (Unity 6) | Cesitli (eski surumleri de destekler) | Esnek |
| **Extension ornegi** | Meta Quest (tek bilinen) | Genis community | — |
| **Undo desteği** | Yok | AnkleBreaker: temel | — |
| **Transaction safety** | Yok | Yok | — |

### Secenek 1: Unity Official MCP Uzerine Insa

**ARTILARI:**
1. Bridge/transport hazir — `[McpTool]` ile tool kaydetmek 5 satir kod
2. Unity'nin resmi cozumu — long-term support beklentisi
3. Meta Quest da bu yaklasimi kullaniyor — validate edilmis pattern
4. `McpToolRegistry` otomatik assembly scan yapiyor — zero-config
5. Unity ekosistemiyle native entegrasyon (AI Gateway, Assistant panel)

**EKSILERI:**
1. **Pre-release risk** — 2.0 → 2.4 arasi API degisiklikleri olmus, daha da degisebilir
2. **Unity Points kredi sistemi** — MCP bridge'in kendisi de ucretli olabilir (net degil)
3. **Unity 6+ zorunlu** — Unity 2022 LTS kullanan devasa kullanici bazini disarida birakir
4. **Tek extension ornegi** — Sadece Meta Quest yapmis, community adoption dusuk
5. **Kara kutu** — Bridge/transport koduna erisim yok, debug zor
6. **Unity AI Beta ile bagli** — Paketin gelecegi Unity'nin AI stratejisine bagimli

### Secenek 2: 3rd Party MCP Uzerine Insa (orn. IvanMurzak)

**ARTILARI:**
1. **Mature & stable** — IvanMurzak v0.51+, production'da kullaniliyor
2. **Acik kaynak** — Bridge kodu gorunur, debug edilebilir, fork edilebilir
3. **Ucretsiz** — Unity Points yok, community-driven
4. **Genis Unity versiyon desteği** — Eski surumlerde de calisir
5. **Zengin tool seti hazir** — 55-288 tool zaten var, CRAFT bunlari complement eder
6. **Roslyn C# execution** (IvanMurzak) — dynamic code execution hazir

**EKSILERI:**
1. **Community-maintained** — Maintainer birakabilir, PR merge yavasalabilir
2. **Ekstra dependency** — Node.js MCP server kurulumu gerekli
3. **API uyumsuzluk riski** — Major version'da breaking change olabilir
4. **Standart yok** — Her 3rd party farkli API, farkli attribute sistemi
5. **CRAFT'in positioning'i karisir** — "Bu ne, Unity MCP plugin mu, IvanMurzak plugin mu?"

### Secenek 3: Sifirdan Yazma

**ARTILARI:**
1. **Tam kontrol** — Bridge, transport, tool registry hepsi senin
2. **Bagimlilik yok** — Ne Unity AI Assistant'a ne 3rd party'ye bagimli
3. **Esnek** — Istedigin Unity versiyonunu, istedigin transport'u sec
4. **Differentiator** — Rakiplerden tamamen farkli bir mimari

**EKSILERI:**
1. **Devasa is yuku** — MCP server + bridge + transport + tool registry = aylar
2. **Tekerleği yeniden icad** — Zaten cozulmus problemleri cozuyorsun
3. **Maintenance yuku** — MCP spec degisince sen guncelle
4. **Community adoption** — "Neden bunu kullanayim, X zaten var" problemi

### Secenek 4: Adapter Pattern (ONERILEN)

**CRAFT core'u hicbir MCP bridge'e bagimli olmaz.** Sadece ince bir adapter katmani ile istenen bridge'e baglanir.

```
craft-unity/
├── Core/           ← Saf C#, MCP yok, Undo/Transaction/Validation
├── Operations/     ← Unity API kullanan op'lar
├── WorldQuery/     ← Scene query engine
├── Adapters/
│   ├── Official/   ← com.unity.ai.assistant icin [McpTool] adapter
│   └── (future)    ← IvanMurzak, standalone, vs.
```

**ARTILARI:**
1. **Core bagimsizsiz** — TransactionManager, CraftEngine, Operations hicbir MCP'ye bagimli degil
2. **Adapter swap** — Official MCP pre-release'den cikarsa onu kullan, cikamazsa 3rd party'ye gec
3. **Risk minimize** — Unity Points sorunu ciksa bile core etkilenmez
4. **Test edilebilir** — Core'u MCP olmadan unit test et
5. **Phase 1'de Official MCP ile basla** — En az is yuku, en hizli MVP
6. **Gelecekte genisle** — IvanMurzak adapter'i, standalone adapter'i ekle

**EKSILERI:**
1. **Adapter katmani ekstra abstraction** — Ama cok ince (sadece McpTools/ klasoru)
2. **Ilk basta tek adapter** — Gercekte Phase 1'de sadece Official MCP destekli

Bu aslinda mevcut plan'dan cok farkli degil — tek fark **bilinçli olarak Core'u MCP-agnostic tutmak** ve McpTools/ klasorunu "adapter" olarak gormek.

### KARAR

**Secenek 4 (Adapter Pattern) + Phase 1'de Official MCP adapter'i ile basla.**

Neden:
- Core (TransactionManager, CraftEngine, Operations, Validation) saf C# — MCP attribute'u import etmez
- McpTools/ klasoru ince adapter — `[McpTool]` attribute ile `CraftEngine` method'larini expose eder
- Official MCP sorun cikarirsa, sadece McpTools/ klasorunu degistirirsin, core ayni kalir
- Meta Quest'in yaklasimi zaten bu — extension package olarak official uzerine insa

```
┌─────────────────────────────────────────────────────────┐
│ Claude Code / Cursor / Any MCP Client                   │
└───────────────────────┬─────────────────────────────────┘
                        │ MCP Protocol (SSE)
┌───────────────────────▼─────────────────────────────────┐
│ MCP Bridge (Official or 3rd party)                      │
│ com.unity.ai.assistant OR IvanMurzak OR standalone       │
└───────────────────────┬─────────────────────────────────┘
                        │ Tool discovery
┌───────────────────────▼─────────────────────────────────┐
│ com.skywalker.craft                                     │
│                                                         │
│  Adapters/McpTools/     │  Core/ (MCP-AGNOSTIC)         │
│  ┌──────────────┐       │  ┌──────────────────────────┐ │
│  │ Craft_Execute │──────▶│  │ CraftEngine              │ │
│  │ Craft_Validate│       │  │  ├─ StaticValidator       │ │
│  │ Craft_Rollback│       │  │  ├─ TransactionManager    │ │
│  │ Craft_Query   │       │  │  │   ├─ Unity Undo Groups │ │
│  │ Craft_Status  │       │  │  │   └─ CommandLog        │ │
│  └──────────────┘       │  │  └─ TraceRecorder         │ │
│  [McpTool] attribute    │  └──────────────────────────┘ │
│  (Official MCP adapter) │                               │
│                         │  Operations/  WorldQuery/      │
│                         │  ┌──────────┐ ┌────────────┐  │
│                         │  │ CreateGO  │ │ WorldQuery │  │
│                         │  │ ModifyCmp │ │ Engine     │  │
│                         │  │ DeleteGO  │ └────────────┘  │
│                         │  └──────────┘                  │
└─────────────────────────────────────────────────────────┘
                           │ Direct Unity API calls
                           ▼
                    Unity Editor API
              (GameObject, Undo, AssetDatabase...)
```

**Key insight:** Core/ ve Operations/ klasorleri **hicbir MCP namespace import etmez**. Sadece McpTools/ adapter katmani `[McpTool]` attribute kullanir. Bu sayede bridge degisirse sadece adapter degisir.

CRAFT, Unity'nin built-in tool'lariyla yanyana calisir. Claude Code basit isler icin `Unity_ManageGameObject` (raw, fast), guvenli isler icin `Craft_Execute` (transaction-safe, validated) kullanir. SKILL.md yonlendirir.

---

## Repo 1: craft-unity

### Yapi

```
craft-unity/
├── package.json                    # com.skywalker.craft
├── CHANGELOG.md
├── LICENSE
├── README.md
├── Runtime/
│   ├── SkyWalker.Craft.Runtime.asmdef
│   └── PersistentId.cs             # MonoBehaviour — stable scene object identity
├── Editor/
│   ├── SkyWalker.Craft.Editor.asmdef
│   ├── Core/
│   │   ├── ICraftOperation.cs      # Execute(op) + Validate(op)
│   │   ├── CraftEngine.cs          # Singleton orchestrator
│   │   ├── TransactionManager.cs   # Undo group mapping + CommandLog
│   │   ├── CommandLog.cs           # Asset-level event sourcing
│   │   └── TraceRecorder.cs        # Execution trace for debugging
│   ├── Models/
│   │   ├── CraftOperation.cs       # { type, target, parameters }
│   │   ├── CraftResult.cs          # { success, transactionId, results[], trace }
│   │   ├── CraftTrace.cs           # { steps[], duration, warnings }
│   │   ├── ValidationResult.cs     # { valid, errors[], warnings[] }
│   │   ├── WorldQueryRequest.cs
│   │   └── WorldQueryResult.cs
│   ├── Validation/
│   │   ├── StaticValidator.cs      # Tier 1: schema check, ref existence, type compat
│   │   └── SandboxValidator.cs     # Tier 2: PreviewScene dry-run (Phase 2)
│   ├── Operations/
│   │   ├── CreateGameObjectOp.cs   # Undo.RegisterCreatedObjectUndo
│   │   ├── ModifyComponentOp.cs    # Undo.RecordObject + reflection set
│   │   ├── DeleteGameObjectOp.cs   # Undo.DestroyObjectImmediate
│   │   ├── SetParentOp.cs          # Undo.SetTransformParent
│   │   └── InstantiatePrefabOp.cs  # PrefabUtility.InstantiatePrefab + Undo
│   ├── WorldQuery/
│   │   └── WorldQueryEngine.cs     # Name + component + tag filter
│   └── McpTools/
│       ├── CraftExecuteTool.cs     # [McpTool("Craft_Execute")]
│       ├── CraftValidateTool.cs    # [McpTool("Craft_Validate")]
│       ├── CraftRollbackTool.cs    # [McpTool("Craft_Rollback")]
│       ├── CraftQueryTool.cs       # [McpTool("Craft_Query")]
│       └── CraftStatusTool.cs      # [McpTool("Craft_Status")]
└── Tests/Editor/
    ├── SkyWalker.Craft.Tests.Editor.asmdef
    ├── TransactionManagerTests.cs
    ├── OperationTests.cs
    └── WorldQueryTests.cs
```

### package.json

```json
{
  "name": "com.skywalker.craft",
  "version": "0.1.0",
  "displayName": "CRAFT - Claude's Reliable AI Framework for Transactions",
  "description": "Safe AI execution layer with transaction safety, rollback, and validation for Unity MCP",
  "unity": "6000.0",
  "dependencies": {
    "com.unity.ai.assistant": "2.0.0"
  }
}
```

### Assembly Definitions

**SkyWalker.Craft.Runtime.asmdef** — pure Runtime (PersistentId MonoBehaviour)

**SkyWalker.Craft.Editor.asmdef:**
- Refs: `SkyWalker.Craft.Runtime`, `Unity.AI.Assistant.Editor`
- Editor-only platform

### Core Contracts

```csharp
// ICraftOperation.cs
public interface ICraftOperation
{
    string Type { get; }
    ValidationResult Validate(CraftOperation op);
    CraftResult Execute(CraftOperation op);
}
```

```csharp
// CraftOperation.cs (JSON'dan deserialize)
[Serializable]
public class CraftOperation
{
    public string type;           // "CreateGameObject", "ModifyComponent", etc.
    public string target;         // GameObject path or asset path
    public Dictionary<string, object> parameters;
}
```

### Transaction = Unity Undo Group

```csharp
// TransactionManager.cs — key logic
public string Begin(string name)
{
    var id = Guid.NewGuid().ToString();
    Undo.IncrementCurrentGroup();
    int groupIndex = Undo.GetCurrentGroup();
    Undo.SetCurrentGroupName($"CRAFT: {name}");
    _activeTransactions[id] = groupIndex;
    return id;
}

public void Commit(string transactionId)
{
    Undo.CollapseUndoOperations(_activeTransactions[transactionId]);
    _committedTransactions[transactionId] = _activeTransactions[transactionId];
    _activeTransactions.Remove(transactionId);
}

public bool Rollback(string transactionId)
{
    if (_committedTransactions.TryGetValue(transactionId, out int group))
    {
        Undo.RevertAllDownToGroup(group);
        _commandLog.RevertTo(transactionId); // asset ops outside Undo
        _committedTransactions.Remove(transactionId);
        return true;
    }
    return false;
}
```

### MCP Tool Definitions

| Tool | Params | Returns |
|------|--------|---------|
| `Craft_Execute` | `operations[], transactionName, validate=true, dryRun=false` | `{ success, transactionId, results[], trace }` |
| `Craft_Validate` | `operations[], tier="static"` | `{ valid, errors[], warnings[] }` |
| `Craft_Rollback` | `transactionId?, steps=1` | `{ success, rolledBack[] }` |
| `Craft_Query` | `query, filters{name,components,tags,parent}, maxResults` | `{ results[{path,name,components,transform}] }` |
| `Craft_Status` | `include[]` | `{ engine, recentTransactions, lastTrace }` |

### Execution Flow

```
Craft_Execute(operations, transactionName)
  │
  ├─ 1. Parse & deserialize operations
  ├─ 2. StaticValidator.Validate(each op)
  │     └─ fail? → return errors, no mutation
  ├─ 3. TransactionManager.Begin(transactionName)
  │     └─ Undo.IncrementCurrentGroup + SetCurrentGroupName
  ├─ 4. foreach op:
  │     ├─ Resolve ICraftOperation by op.type
  │     ├─ op.Execute() — calls Unity API with Undo.RecordObject
  │     └─ TraceRecorder.Record(step)
  ├─ 5. Any failure? → TransactionManager.Rollback(id)
  ├─ 6. TransactionManager.Commit(id)
  └─ 7. return CraftResult { success, transactionId, results, trace }
```

---

## Repo 2: ccplugin-unity-craft

### Yapi

```
ccplugin-unity-craft/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── unity-craft/
│       └── SKILL.md
├── CLAUDE.md
├── README.md
├── LICENSE
└── install.sh
```

### plugin.json

```json
{
  "name": "unity-craft",
  "description": "Safe Unity scene manipulation via CRAFT MCP tools",
  "version": "0.1.0",
  "author": { "name": "Musab Kara", "url": "https://github.com/SkyWalker2506" },
  "category": "development",
  "keywords": ["unity", "gamedev", "mcp", "craft", "transactions"],
  "requires": { "mcpServers": ["unity"] }
}
```

### SKILL.md Outline

- **Trigger:** "unity scene", "create gameobject", "add component", "rollback", "scene query"
- **Golden Rules:**
  1. Always use `Craft_Execute` for scene mutations (not raw Unity MCP tools)
  2. Name transactions descriptively (e.g., "Add player spawn point with collider")
  3. `Craft_Query` before modify — find target first
  4. validate=true is default — trust it
  5. Always report transactionId to user for rollback capability
- **Tool usage patterns** with JSON examples for Create, Modify, Delete, Query
- **Error handling:** auto-rollback on failure, validation error reporting

---

## Phase 1 Implementation Steps

### Step 1: Repo Scaffolding
- [ ] Create `craft-unity` repo with package.json, asmdefs, README, LICENSE, CLAUDE.md
- [ ] Create `ccplugin-unity-craft` repo with plugin.json, SKILL.md skeleton

### Step 2: Models & Contracts
- [ ] `CraftOperation.cs` — operation definition
- [ ] `CraftResult.cs` — result envelope
- [ ] `CraftTrace.cs` — execution trace
- [ ] `ValidationResult.cs` — validation output
- [ ] `ICraftOperation.cs` — Execute + Validate contract

### Step 3: Core Engine
- [ ] `TransactionManager.cs` — Undo group lifecycle + CommandLog
- [ ] `CommandLog.cs` — asset-level event log
- [ ] `CraftEngine.cs` — orchestrator (validate -> begin -> execute -> commit/rollback)
- [ ] `TraceRecorder.cs` — step-by-step recording

### Step 4: Operations (3 core)
- [ ] `CreateGameObjectOp.cs` — empty + primitive + with components
- [ ] `ModifyComponentOp.cs` — reflection-based field/property set with Undo
- [ ] `DeleteGameObjectOp.cs` — Undo.DestroyObjectImmediate

### Step 5: Validation
- [ ] `StaticValidator.cs` — type existence, target resolution, parameter check

### Step 6: MCP Tools
- [ ] `CraftExecuteTool.cs` — [McpTool("Craft_Execute")]
- [ ] `CraftRollbackTool.cs` — [McpTool("Craft_Rollback")]
- [ ] `CraftStatusTool.cs` — [McpTool("Craft_Status")]

### Step 7: World Query
- [ ] `WorldQueryEngine.cs` — name + component + tag filter
- [ ] `CraftQueryTool.cs` — [McpTool("Craft_Query")]

### Step 8: Validate Tool + Plugin Finalize
- [ ] `CraftValidateTool.cs` — [McpTool("Craft_Validate")]
- [ ] Finalize SKILL.md with full examples
- [ ] install.sh for ccplugin

### Phase 2 (Later)
- SetParentOp, InstantiatePrefabOp, CreateAssetOp
- SandboxValidator (PreviewScene dry-run)
- RiskAssessor (risk scoring)
- SceneDoctor (MissingReferenceRule, BrokenPrefabRule)
- PersistentId (stable cross-session identity)
- Spatial query (SpatialIndex, proximity scorer)
- DAG execution for parallel operations

---

## Verification

1. Unity 6 projede `com.skywalker.craft` package'i import et
2. `com.unity.ai.assistant@2.0` kurulu ve MCP bridge aktif
3. Claude Code'dan `Craft_Execute` ile GameObject olustur — transactionId donmeli
4. `Craft_Status` ile engine durumu — son transaction gorunmeli
5. `Craft_Rollback` ile geri al — sahne orijinal durumda
6. `Craft_Query` ile sahne sorgula
7. `Craft_Validate` ile gecersiz operation — hata donmeli
8. ccplugin install, skill trigger'lar calissin

## Ecosystem Guncelleme

1. `projects.json`'a `craft-unity` ve `ccplugin-unity-craft` ekle
2. `hq sync` calistir
3. `claude-marketplace`'e plugin ekle
