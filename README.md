# Claude Code Statusline

Custom status line for [Claude Code CLI](https://claude.ai/code) that displays key session metrics at the bottom of the terminal.

![Python](https://img.shields.io/badge/python-3.10+-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

## What it looks like

```
📁 my-project │ 🌿 main │ ⚡ 94% │ 📅 65% │ ▓▓▓▓░░░░░░ 42%
```

## Segments

| Icon | What it shows | Color logic |
|------|--------------|-------------|
| 📁 | Current working directory | — |
| 🌿 | Git branch | — |
| ⚡ | Session remaining (5h window) | 🟢 >40% · 🟡 15–40% · 🔴 <15% |
| 📅 | Weekly remaining (7d window) | 🟢 >40% · 🟡 15–40% · 🔴 <15% |
| ▓░ | Context window usage | 🟢 <60% · 🔴 ≥60% |

Session and weekly usage are fetched from the Anthropic OAuth API (`/api/oauth/usage`) and reflect how much of your Pro/Max plan quota remains.

## Requirements

- **OS:** Windows (tested on Windows 11, Git Bash)
- **Python:** 3.10+
- **Claude Code CLI** with an active Pro or Max subscription
- OAuth credentials in `~/.claude/.credentials.json` (created automatically when you log into Claude Code)

## Installation

1. **Copy the script** to your Claude config directory:

```bash
cp statusline.py ~/.claude/statusline.py
```

2. **Add to Claude Code settings** (`~/.claude/settings.json`):

```json
{
  "statusLine": {
    "type": "command",
    "command": "C:/Users/YOUR_USERNAME/AppData/Local/Programs/Python/Python312/python.exe C:/Users/YOUR_USERNAME/.claude/statusline.py"
  }
}
```

Replace `YOUR_USERNAME` and adjust the Python path if needed.

3. **Restart Claude Code** or send a message — the status line appears at the bottom after the next assistant response.

## How it works

Claude Code pipes a JSON payload to the script via stdin on every update. The script extracts:

- **Directory & git branch** — from the JSON + `git branch --show-current`
- **Session/weekly usage** — HTTP GET to `https://api.anthropic.com/api/oauth/usage` using the OAuth token from `~/.claude/.credentials.json`
- **Context window %** — from the JSON `context_window.used_percentage` field

### Caching

To keep the status line fast and avoid API spam:

| Data | Cache TTL |
|------|-----------|
| Git branch | 5 seconds |
| Usage API response | 60 seconds |

Cache files are stored in `%TEMP%` (`claude-sl-git`, `claude-sl-usage.json`).

## License

MIT
