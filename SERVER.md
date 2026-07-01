# DevNotes MCP Server — DS 6042 Lab 07 · Part 3

## What the server does

**DevNotes** is a note-reading MCP server with two tools:

| Tool | Description | Sensitivity |
|---|---|---|
| `list_notes` | Lists every `.txt` file in `notes/` | Low — directory listing only |
| `read_note(name)` | Reads a note file from `notes/` by name | **High** — resolves user-supplied path against the filesystem |

`list_notes` is intentionally benign (a catalog needs ≥ 2 tools). `read_note` is the sensitive one: it joins a caller-controlled string onto a filesystem path, which is the exact scenario where path-traversal vulnerabilities appear in real file-serving tools.

---

## MCP Inspector screenshot

> **To reproduce:**
> ```
> npx @modelcontextprotocol/inspector python my_server.py
> ```
> Connect in Inspector → Tools tab → call `read_note` with `name = "welcome.txt"`.
> *(Paste screenshot here before submitting.)*

---

## Vulnerability planted

**Class:** Path traversal (Attack 2 / D2 in the lab taxonomy)

**Location:** `read_note` in `my_server.py`, this single line:

```python
path = NOTES_DIR / name          # VULNERABLE
```

`Path.__truediv__` (the `/` operator) concatenates path segments without any canonicalisation. If `name = "../secret.txt"`, the result is:

```
/path/to/assignment-build/notes/../secret.txt
```

Python's `Path.exists()` and `read_text()` follow `..` normally, so the file at `../secret.txt` — one level *above* the intended sandbox — is read and returned to the caller.

**Why this is a realistic developer mistake:**

Joining a user-supplied filename onto a base directory is the obvious way to implement "read from this folder." The `Path` API makes it look completely safe — there's no string concatenation, no `os.path.join` — yet it still follows `..` segments. The sandbox illusion only breaks once you know to call `.resolve()` and compare prefixes. Many developers who know about path traversal in raw string manipulation don't think to check for it when using `pathlib`.

---

## MCP Inspector proof of tool call

*(screenshot placeholder — see above)*

---

## Root cause and fix

**Root cause (one line):**
`NOTES_DIR / name` produces an unresolved path that silently honours `..` segments, letting a caller escape the `notes/` directory with `name = "../secret.txt"`.

**Fix (two lines — mirrors D2 in `secure_server.py`):**

```python
# my_server.py (vulnerable)
path = NOTES_DIR / name

# my_server_secure.py (fixed)
real = (NOTES_DIR / name).resolve()
if not str(real).startswith(str(NOTES_DIR.resolve()) + "/"):
    return "error: path escapes the notes/ sandbox"
```

`.resolve()` collapses every `..` and symlink before the prefix check runs. The trailing `"/"` in the guard is essential — without it, a sibling directory named `notes_evil` would pass `startswith("/path/to/notes")`.

This removes the dangerous capability entirely rather than blocking one specific payload. Any input that escapes `notes/` after resolution is rejected, regardless of how many `..` segments, URL encodings, or symlinks it uses.

---

## Attack output

```
$ python attack_my_server.py
tools: ['list_notes', 'read_note']

[benign] read_note('welcome.txt'):
Welcome to DevNotes — MegaCorpAI Sprint Tool
...

[attack] read_note('../secret.txt'):
flag{path_traversal_escaped_notes_sandbox}
# MegaCorpAI DevNotes — Internal Admin Credentials (DO NOT COMMIT)
ADMIN_API_KEY=sk-admin-megacorpai-internal-Abc123Xyz
POSTGRES_PASSWORD=hunter2_devnotes_prod

✓ ATTACK SUCCEEDED — read a file outside notes/.

$ python attack_my_server.py my_server_secure.py
tools: ['list_notes', 'read_note']

[benign] read_note('welcome.txt'):
Welcome to DevNotes — MegaCorpAI Sprint Tool
...

[attack] read_note('../secret.txt'):
error: path escapes the notes/ sandbox

✗ attack did not land (or you're running the secure server).
```

---

## Group members

- [Name — UVA computing ID]
- [Name — UVA computing ID]
- [Name — UVA computing ID]
