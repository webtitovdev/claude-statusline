# Claude Code Statusline

Статус-лайн для Claude Code CLI в пять строк. Основан на Awesome Statusline (режим FULL).

```
🤖 Модель | 🎨 стиль | ✅ git (↑ahead ↓behind) | 🐍 окружение
📂 полный путь 🌿(ветка) | 💰 стоимость | ⏰ длительность
🧠 контекст, полоса на 40 блоков
🚀 лимит 5 часов + когда сбросится
🌟 лимит 7 дней + когда сбросится
```

Лимиты берутся из поля `rate_limits`, которое Claude Code передаёт на вход скрипту (есть у подписок Pro и Max). В API скрипт сам не ходит.

## Что нужно

- bash (на Windows подойдёт Git Bash)
- jq. Если jq нет в PATH, положите `jq`/`jq.exe` рядом со скриптом: скрипт добавляет свою папку в PATH.
- терминал с truecolor и эмодзи

## Установка

```bash
cp statusline.sh ~/.claude/statusline.sh
```

В `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "bash ~/.claude/statusline.sh"
  }
}
```

Перезапустите Claude Code.
