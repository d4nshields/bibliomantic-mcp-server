# ADR-002: Contextual Ethical Guidance via Decorator

**Status:** Implemented  
**Date:** 2026-10-01  
**Decision Makers:** Development Team

## Context

Ethical disclaimers existed in two places. `ethical_server.py` was a complete second MCP server whose tools ended with a fixed disclaimer paragraph; `main.py` imported it only as a fallback if the enhanced server failed to import, so in a working install it never ran. The enhanced server carried its own copy of the same paragraphs, written inline into every return path of every divination tool.

That left three problems:

- The disclaimer text and the decision to show it were duplicated across tool bodies and across two servers.
- An operator had no way to turn the disclaimers off.
- The text was rigid boilerplate. An MCP tool result is read by the model, which then writes its own reply, so the paragraph was never guaranteed to reach the user verbatim anyway, and when it did it read the same for "a reading for the day" as for "should I quit my job".

## Decision

Treat the disclaimer as a cross-cutting concern, applied by a decorator, and phrase it as guidance for the assistant rather than as text for the user.

### Components:

1. **`bibliomantic_server/ethics.py`**: holds the guidance notes, the `@with_disclaimer()` decorator, a process-wide on/off switch and the sentence used for the server's MCP `instructions` field.
2. **`@with_disclaimer(brief=False)`**: wraps a string-returning tool and appends a guidance note to its result. Applied beneath `@mcp.tool()` on `i_ching_divination` and `bibliomantic_consultation` (full note) and `get_hexagram_details` (brief note). `functools.wraps` preserves the name, docstring and signature the MCP SDK introspects, so tool schemas are unchanged.
3. **Guidance note**: begins with a fixed marker line addressed to the assistant, lists the points the user should come away understanding (secure randomness rather than supernatural guidance; reflection and entertainment rather than prediction; consult a professional for financial, medical, legal or safety decisions) and asks the assistant to convey them in its own words, with a light touch for casual questions and an explicit caution for serious ones.
4. **Server instructions**: `MCPServer(instructions=...)` carries a conditional sentence telling the assistant to follow such a note when a result includes one. It is conditional because it is fixed at import time, before the command-line switch is read.
5. **`--no-ethical-disclaimers`**: command-line flag parsed in `main.py`. Guidance is on by default; the flag turns it off for the whole process. `server_statistics` reports the current setting.
6. **`ethical_server.py` removed**: along with the import fallback chain in `main.py`. The enhanced server is now imported directly, so a broken install fails loudly instead of starting a different server.

## Consequences

### Positive:

- Tool bodies contain no disclaimer text; the wording lives in one module.
- Operators can disable the guidance without editing code.
- The caution a user receives scales with the stakes of their question instead of being identical boilerplate.
- One fewer unused server module to keep in step with the real one.

### Negative:

- The server can request this behaviour but not enforce it. The exact wording shown to the user is chosen by the model and is not auditable. A deployment that needs fixed, verifiable wording is not served by this design.
- Hosts treat tool results as untrusted data, so a strict host or model may ignore instructions that arrive inside one. Sending the same request through the `instructions` field mitigates this but does not remove it.
- A tool has one note for all of its return paths, so validation and error messages carry the same note as a successful reading.
- The switch is process-wide state set at startup, not a per-request option.

## Implementation Notes

- `@mcp.tool()` must remain the outermost decorator so that the wrapped function is the one registered.
- The decorator supports sync and async functions and leaves non-string results untouched.
- Changing behaviour requires restarting the server process; MCP hosts read `instructions` and the tool list only when they connect.
- Verified end to end over stdio with the default launch and with `--no-ethical-disclaimers`: note present or absent on every return path of the three tools, instructions delivered at initialize, tool schemas and descriptions intact.
