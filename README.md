# DS 6042 · Lab 07 Part 3 — DevNotes MCP Server

Build → Break → Secure on a self-authored MCP server.

## Group members
- [Name — computing ID]
- [Name — computing ID]
- [Name — computing ID]

## Files
- `my_server.py` — MCP server with a planted path-traversal vulnerability in `read_note`
- `attack_my_server.py` — MCP client that exploits it over the protocol
- `my_server_secure.py` — the fixed server (traversal blocked, legitimate reads still work)
- `SERVER.md` — writeup + Inspector screenshot

See `SERVER.md` for the vulnerability details, root cause, and fix.

## Running it

```bash
pip install mcp

# load in MCP Inspector
npx @modelcontextprotocol/inspector python my_server.py

# exploit the vulnerable server
python attack_my_server.py

# same attack against the fixed server — now blocked
python attack_my_server.py my_server_secure.py
```

> To reproduce the attack locally, `read_note` expects a `notes/welcome.txt` (a benign note) and a `secret.txt` one level above `notes/` (the file the traversal reaches). The values in `secret.txt` are placeholders.
