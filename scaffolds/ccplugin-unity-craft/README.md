# ccplugin-unity-craft

Claude Code plugin for [CRAFT](https://github.com/SkyWalker2506/craft-unity) — safe Unity scene manipulation via MCP tools.

## What it does

Teaches Claude Code how to use CRAFT's MCP tools for safe, transaction-based Unity scene manipulation:

- **Craft_Execute** — Run operations as undoable transactions
- **Craft_Validate** — Pre-check operations before execution
- **Craft_Rollback** — Revert any transaction
- **Craft_Query** — Find scene objects by name, component, tag
- **Craft_Status** — Engine status and diagnostics

## Requirements

- [CRAFT Unity package](https://github.com/SkyWalker2506/craft-unity) installed in your Unity project
- Unity MCP bridge active (`com.unity.ai.assistant` >= 2.0.0)
- Unity MCP server configured in Claude Code

## Installation

```bash
git clone https://github.com/SkyWalker2506/ccplugin-unity-craft.git
cd ccplugin-unity-craft && ./install.sh
```

Or via claude-marketplace:
```bash
ccplugin install unity-craft
```

## License

MIT
