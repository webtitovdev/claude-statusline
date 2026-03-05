#!/usr/bin/env python3
import json, sys, os, subprocess, time, urllib.request, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

input_data = json.load(sys.stdin)

# --- Basic fields ---
cwd = input_data.get('workspace', {}).get('current_dir', '')
dir_name = os.path.basename(cwd) if cwd else '~'
pct = int(input_data.get('context_window', {}).get('used_percentage', 0) or 0)

# --- Git branch (cached) ---
GIT_CACHE = os.path.join(os.environ.get('TEMP', '/tmp'), 'claude-sl-git')
git_branch = ''
try:
    stale = True
    if os.path.exists(GIT_CACHE):
        stale = (time.time() - os.path.getmtime(GIT_CACHE)) > 5
    if stale:
        branch = subprocess.check_output(
            ['git', 'branch', '--show-current'],
            text=True, stderr=subprocess.DEVNULL, cwd=cwd or None
        ).strip()
        with open(GIT_CACHE, 'w') as f:
            f.write(branch)
        git_branch = branch
    else:
        with open(GIT_CACHE) as f:
            git_branch = f.read().strip()
except Exception:
    git_branch = ''

# --- Usage data (cached, 60s TTL) ---
USAGE_CACHE = os.path.join(os.environ.get('TEMP', '/tmp'), 'claude-sl-usage.json')
USAGE_TTL = 60

session_remaining = None
weekly_remaining = None

try:
    cached = None
    stale_data = None
    if os.path.exists(USAGE_CACHE):
        with open(USAGE_CACHE) as f:
            stale_data = json.load(f)
        age = time.time() - os.path.getmtime(USAGE_CACHE)
        if age < USAGE_TTL:
            cached = stale_data

    if cached is None:
        creds_path = os.path.join(os.path.expanduser('~'), '.claude', '.credentials.json')
        with open(creds_path) as f:
            creds = json.load(f)
        token = creds.get('claudeAiOauth', {}).get('accessToken', '')
        if token:
            req = urllib.request.Request(
                'https://api.anthropic.com/api/oauth/usage',
                headers={
                    'Authorization': f'Bearer {token}',
                    'anthropic-beta': 'oauth-2025-04-20',
                    'Accept': 'application/json',
                }
            )
            try:
                with urllib.request.urlopen(req, timeout=5) as resp:
                    cached = json.loads(resp.read())
                with open(USAGE_CACHE, 'w') as f:
                    json.dump(cached, f)
            except Exception:
                cached = stale_data

    if not cached:
        cached = stale_data

    if cached:
        five_h = cached.get('five_hour', {}).get('utilization')
        seven_d = cached.get('seven_day', {}).get('utilization')
        if five_h is not None:
            session_remaining = max(0, round(100 - five_h))
        if seven_d is not None:
            weekly_remaining = max(0, round(100 - seven_d))
except Exception:
    pass

# --- Colors ---
GREEN = '\033[32m'
RED = '\033[31m'
DIM = '\033[2m'
RESET = '\033[0m'
CYAN = '\033[36m'
YELLOW = '\033[33m'

# --- Context bar ---
ctx_color = GREEN if pct < 60 else RED
bar_w = 10
filled = pct * bar_w // 100
bar = '\u2593' * filled + '\u2591' * (bar_w - filled)

# --- Build line ---
sep = f' {DIM}\u2502{RESET} '
parts = []

parts.append(f'\U0001F4C1 {dir_name}')

if git_branch:
    parts.append(f'\U0001F33F {git_branch}')

if session_remaining is not None:
    s_color = GREEN if session_remaining > 40 else (YELLOW if session_remaining > 15 else RED)
    parts.append(f'\u26A1 {s_color}{session_remaining}%{RESET}')
else:
    parts.append(f'\u26A1 {DIM}--{RESET}')

if weekly_remaining is not None:
    w_color = GREEN if weekly_remaining > 40 else (YELLOW if weekly_remaining > 15 else RED)
    parts.append(f'\U0001F4C5 {w_color}{weekly_remaining}%{RESET}')
else:
    parts.append(f'\U0001F4C5 {DIM}--{RESET}')

parts.append(f'{ctx_color}{bar} {pct}%{RESET}')

print(sep.join(parts))
