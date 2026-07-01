"""my_server.py — YOUR MCP server.  Lab 07 · Part 3 capstone (Build → Break → Secure).

You've attacked three real MCP servers (§9–§11). Now build one. This skeleton
uses the official MCP SDK (`pip install mcp`) over stdio — the same protocol the
real servers speak. Run it and it waits for an MCP client on stdin/stdout:

    python my_server.py

Attack it with the companion client (also a template you finish):

    python attack_my_server.py

Your job (see the Part 3 assignment on the lab page):
  1. BUILD   — make both tools below actually work (≥2 working tools).
  2. BREAK   — plant exactly ONE vulnerability from the lab taxonomy in a tool,
               and finish attack_my_server.py to exploit it OVER MCP.
  3. SECURE  — copy this to my_server_secure.py, fix the one bug (remove the
               dangerous capability, don't just blocklist your one payload), and
               show the same attack now fails.
"""

from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-server")

NOTES_DIR = Path(__file__).parent / "notes"


@mcp.tool()
def list_notes() -> str:
    """List the note files available to read. (A benign tool, so the catalog has
    more than one entry — leave this one safe.)"""
    return "\n".join(sorted(p.name for p in NOTES_DIR.glob("*.txt"))) or "(no notes)"


@mcp.tool()
def read_note(name: str) -> str:
    """Read a note by name from the notes/ directory and return its text.

    A legitimate call looks like:  read_note("welcome.txt")  ->  notes/welcome.txt
    """
    # ========================================================================
    # PLANTED VULNERABILITY · path traversal (Attack 2 / D2 class)
    #
    # The naive join  NOTES_DIR / name  does NOT canonicalise the path.
    # A caller can supply  name="../secret.txt"  and Python's Path will
    # happily read a file one level above notes/ — outside the intended
    # sandbox.  The fix (in my_server_secure.py) is to call .resolve()
    # and check the result starts with NOTES_DIR.resolve() + "/".
    # ========================================================================
    path = NOTES_DIR / name          # VULNERABLE: no resolve() / prefix check
    if not path.exists() or not path.is_file():
        return f"error: note not found: {name!r}"
    return path.read_text(encoding="utf-8", errors="replace")


if __name__ == "__main__":
    mcp.run()  # stdio transport — an MCP client speaks JSON-RPC over stdin/stdout
