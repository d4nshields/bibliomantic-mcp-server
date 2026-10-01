"""
Ethical disclaimer guidance for bibliomantic responses.

Rather than stamping fixed boilerplate onto every reading, the server appends a
short note addressed to the assistant that presents the result. The note lists
the points the user should come away understanding and asks the assistant to
convey them in its own words, in proportion to what the user asked. A casual
"reading for the day" gets a light touch; a question about a serious decision
gets an explicit caution.

This module holds the guidance notes, the decorator that appends them to a
tool's response, the matching sentence for the server's ``instructions`` field,
and a process-wide switch that decides whether the notes appear at all. The
switch is on by default and is turned off by the ``--no-ethical-disclaimers``
command-line flag handled in ``main.py``.

Usage::

    @mcp.tool()
    @with_disclaimer()            # full guidance note
    def i_ching_divination(...) -> str: ...

    @mcp.tool()
    @with_disclaimer(brief=True)  # short guidance note
    def get_hexagram_details(...) -> str: ...

``@mcp.tool()`` must stay outermost so the server registers the wrapped
function. ``functools.wraps`` preserves the name, docstring and ``__wrapped__``
signature that the MCP SDK introspects to build the tool schema.

The server can only ask: an MCP tool result is read by the model, which writes
its own reply. The guidance is sent through two channels to give it the best
chance of being honoured, the note in each result and ``SERVER_INSTRUCTIONS``.
"""

import functools
import inspect
from typing import Any, Callable, TypeVar

# First line of every guidance note. SERVER_INSTRUCTIONS refers to it, and tests
# can use it to detect whether a result carries a note.
GUIDANCE_MARKER = "[Guidance for the assistant. Do not quote this note verbatim.]"

ETHICAL_GUIDANCE = f"""
{GUIDANCE_MARKER}
When you present this reading, make sure the user comes away understanding, in your own words and in proportion to what they asked:
- the hexagram was chosen by cryptographically secure randomness, not supernatural guidance
- it is a prompt for reflection and entertainment, in the spirit of Philip K. Dick's literary use of the oracle, not a prediction
- any wisdom comes from their own reflection on it
- for financial, medical, legal or safety decisions they should consult a qualified professional
A light touch is enough for casual questions. Be explicit if the question involves a serious decision.
"""

BRIEF_GUIDANCE = f"""
{GUIDANCE_MARKER}
When you relay this hexagram, let the user know in your own words that it is for reflection and entertainment, not a basis for important life decisions. A passing mention is enough for a plain lookup. Be explicit if they are weighing a serious decision.
"""

# Passed to MCPServer(instructions=...). Phrased conditionally because it is fixed
# at import time, before the command-line switch is read.
SERVER_INSTRUCTIONS = (
    "Some tool results from this server end with a note that begins "
    f"\"{GUIDANCE_MARKER}\" When a result carries such a note, follow it: convey "
    "its points to the user in your own words, fitted to the context and stakes "
    "of their question, and do not quote the note itself. When a result carries "
    "no note, the operator has turned this guidance off."
)

_enabled = True

F = TypeVar("F", bound=Callable[..., Any])


def enable_disclaimers(enabled: bool = True) -> None:
    """Turn guidance-note injection on or off for every decorated function."""
    global _enabled
    _enabled = bool(enabled)


def disclaimers_enabled() -> bool:
    """Report whether decorated responses currently carry a guidance note."""
    return _enabled


def _append(result: Any, note: str) -> Any:
    if _enabled and isinstance(result, str):
        return f"{result}\n\n{note}"
    return result


def with_disclaimer(brief: bool = False) -> Callable[[F], F]:
    """
    Decorator factory: append ethical guidance to a string-returning function.

    Args:
        brief: use the short guidance note instead of the full one.

    The note is only appended while ``disclaimers_enabled()`` is true; otherwise
    the wrapped function's result passes through untouched. Non-string results
    are never modified. Both sync and async functions are supported.
    """
    note = BRIEF_GUIDANCE if brief else ETHICAL_GUIDANCE

    def decorate(fn: F) -> F:
        if inspect.iscoroutinefunction(fn):
            @functools.wraps(fn)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                return _append(await fn(*args, **kwargs), note)
            return async_wrapper  # type: ignore[return-value]

        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return _append(fn(*args, **kwargs), note)
        return wrapper  # type: ignore[return-value]

    return decorate


__all__ = [
    "GUIDANCE_MARKER",
    "ETHICAL_GUIDANCE",
    "BRIEF_GUIDANCE",
    "SERVER_INSTRUCTIONS",
    "enable_disclaimers",
    "disclaimers_enabled",
    "with_disclaimer",
]
