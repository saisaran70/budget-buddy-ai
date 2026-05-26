"""
Claude Code Stop hook — auto-updates obsidian/progress.md and obsidian/decisions.md.

Reads the session transcript JSON from stdin (provided by Claude Code),
calls OpenRouter to summarise what happened, then appends to the vault files.
"""

import json
import os
import re
import sys
from datetime import datetime, date
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
VAULT = Path(__file__).parent.parent / "obsidian"
PROGRESS_FILE = VAULT / "progress.md"
DECISIONS_FILE = VAULT / "decisions.md"


def _load_env():
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())


def _call_openrouter(prompt: str) -> str:
    import urllib.request

    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    model = os.environ.get("OPENROUTER_MODEL", "openai/gpt-oss-20b:free")

    if not api_key or api_key == "your-openrouter-api-key-here":
        return ""

    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 900,
        "temperature": 0.3,
    }).encode()

    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://budget-buddy-ai.local",
            "X-Title": "Budget Buddy AI",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"[update_obsidian] OpenRouter call failed: {e}", file=sys.stderr)
        return ""


def _extract_transcript_messages(transcript_path: str) -> list[dict]:
    try:
        data = json.loads(Path(transcript_path).read_text(encoding="utf-8"))
        messages = data if isinstance(data, list) else data.get("messages", [])
        return messages
    except Exception:
        return []


def _build_session_text(messages: list[dict]) -> str:
    parts = []
    for m in messages:
        role = m.get("role", "")
        if role not in ("user", "assistant"):
            continue
        content = m.get("content", "")
        if isinstance(content, list):
            content = " ".join(
                c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text"
            )
        if content.strip():
            parts.append(f"{role.upper()}: {content.strip()[:600]}")
    return "\n\n".join(parts[-40:])  # last 40 turns to stay within token budget


def _get_next_decision_number() -> int:
    try:
        text = DECISIONS_FILE.read_text(encoding="utf-8")
        nums = re.findall(r"## DEC-(\d+)", text)
        return max(int(n) for n in nums) + 1 if nums else 1
    except Exception:
        return 1


def _get_session_number() -> int:
    try:
        text = PROGRESS_FILE.read_text(encoding="utf-8")
        nums = re.findall(r"## Session (\d+)", text)
        return max(int(n) for n in nums) + 1 if nums else 2
    except Exception:
        return 2


def _update_last_updated(file: Path, today: str):
    text = file.read_text(encoding="utf-8")
    text = re.sub(r"updated: \d{4}-\d{2}-\d{2}", f"updated: {today}", text)
    text = re.sub(r"Last updated: \d{4}-\d{2}-\d{2}", f"Last updated: {today}", text)
    file.write_text(text, encoding="utf-8")


def main():
    _load_env()

    # Read hook input from stdin
    raw = sys.stdin.read().strip()
    try:
        hook_data = json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        hook_data = {}

    transcript_path = hook_data.get("transcript_path", "")
    today = date.today().isoformat()
    now = datetime.now().strftime("%H:%M")
    session_num = _get_session_number()
    next_dec = _get_next_decision_number()

    # Build prompt from transcript
    messages = _extract_transcript_messages(transcript_path) if transcript_path else []
    session_text = _build_session_text(messages)

    if not session_text:
        print("[update_obsidian] No transcript content found — skipping AI summary.", file=sys.stderr)
        return

    # ── Ask AI to extract progress + decisions ────────────────────────────────
    ai_prompt = f"""You are a technical documentation assistant. Analyse this Claude Code session transcript and extract structured notes.

SESSION TRANSCRIPT (excerpt):
{session_text}

Return ONLY valid JSON in this exact structure — no markdown fences, no extra text:
{{
  "session_summary": "2-3 sentence paragraph describing what was built or fixed this session.",
  "completed_tasks": ["task 1", "task 2"],
  "files_changed": ["path/to/file.py", "another/file.html"],
  "next_priorities": ["next thing to build", "another priority"],
  "new_decisions": [
    {{
      "title": "Short decision title",
      "decision": "What was decided",
      "reason": "Why this choice was made",
      "impact": "What this affects in the codebase"
    }}
  ]
}}

Only include new_decisions for choices that are genuinely architectural or technical (stack choice, library choice, pattern choice, security approach). Skip trivial implementation details.
Return empty array [] for new_decisions if nothing significant was decided.
"""

    ai_response = _call_openrouter(ai_prompt)

    # Parse AI response
    try:
        if ai_response.startswith("```"):
            ai_response = ai_response.split("```")[1]
            if ai_response.startswith("json"):
                ai_response = ai_response[4:]
        extracted = json.loads(ai_response.strip())
    except (json.JSONDecodeError, Exception):
        # Fallback: write minimal entry without AI summary
        extracted = {
            "session_summary": "Session completed — AI summary unavailable.",
            "completed_tasks": [],
            "files_changed": [],
            "next_priorities": [],
            "new_decisions": [],
        }

    # ── Append to progress.md ─────────────────────────────────────────────────
    tasks_md = "\n".join(f"- {t}" for t in extracted.get("completed_tasks", [])) or "- (no tasks extracted)"
    files_md = "\n".join(f"- `{f}`" for f in extracted.get("files_changed", [])) or "- (none)"
    next_md  = "\n".join(f"- [ ] {t}" for t in extracted.get("next_priorities", [])) or "- [ ] (none logged)"

    progress_entry = f"""
---

## Session {session_num} — {today} {now}

**Status:** 🔄 Auto-logged by Stop hook

### Summary
{extracted.get("session_summary", "")}

### Completed tasks
{tasks_md}

### Files changed
{files_md}

### Next priorities
{next_md}

"""

    # Insert before the "Upcoming" section if it exists, else append
    progress_text = PROGRESS_FILE.read_text(encoding="utf-8")
    upcoming_marker = "## Upcoming"
    if upcoming_marker in progress_text:
        progress_text = progress_text.replace(upcoming_marker, progress_entry + upcoming_marker)
    else:
        progress_text += progress_entry

    # Update session count in footer
    progress_text = re.sub(
        r"Sessions logged: \d+",
        f"Sessions logged: {session_num}",
        progress_text,
    )
    progress_text = re.sub(r"Last updated: \d{4}-\d{2}-\d{2}", f"Last updated: {today}", progress_text)
    progress_text = re.sub(r"updated: \d{4}-\d{2}-\d{2}", f"updated: {today}", progress_text)
    PROGRESS_FILE.write_text(progress_text, encoding="utf-8")
    print(f"[update_obsidian] progress.md updated (Session {session_num})")

    # ── Append new decisions to decisions.md ──────────────────────────────────
    new_decisions = extracted.get("new_decisions", [])
    if new_decisions:
        decisions_text = DECISIONS_FILE.read_text(encoding="utf-8")
        footer_marker = "\n---\n\n*Last updated:"

        entries = []
        for i, dec in enumerate(new_decisions):
            dec_num = next_dec + i
            entries.append(f"""
## DEC-{dec_num:03d} · {dec.get("title", "Untitled")}
**Date:** {today}
**Decision:** {dec.get("decision", "")}
**Reason:** {dec.get("reason", "")}
**Impact:** {dec.get("impact", "")}
""")

        new_block = "\n".join(entries)

        # Update total count
        dec_count = next_dec + len(new_decisions) - 1
        decisions_text = re.sub(
            r"Total decisions logged: \d+",
            f"Total decisions logged: {dec_count}",
            decisions_text,
        )
        decisions_text = re.sub(r"Last updated: \d{4}-\d{2}-\d{2}", f"Last updated: {today}", decisions_text)
        decisions_text = re.sub(r"updated: \d{4}-\d{2}-\d{2}", f"updated: {today}", decisions_text)

        if footer_marker in decisions_text:
            decisions_text = decisions_text.replace(footer_marker, new_block + footer_marker)
        else:
            decisions_text += new_block

        DECISIONS_FILE.write_text(decisions_text, encoding="utf-8")
        print(f"[update_obsidian] decisions.md updated ({len(new_decisions)} new decision(s))")
    else:
        _update_last_updated(DECISIONS_FILE, today)
        print("[update_obsidian] decisions.md — no new decisions this session")


if __name__ == "__main__":
    main()
