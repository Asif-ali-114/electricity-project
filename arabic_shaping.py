"""
localization/arabic_shaping.py

Matplotlib (via FreeType) does NOT apply Arabic contextual letter-joining
or right-to-left reordering on its own -- it draws whatever codepoints it
is given, left-to-right, with each letter in isolated form. Left
unhandled, Arabic chart labels render as disconnected, reversed-looking
glyphs instead of proper joined script.

This module reshapes + bidi-reorders Arabic text before it's handed to
matplotlib, using the same class of tooling (arabic-reshaper + python-
bidi) used for the Pillow/raqm-based PDF work on other projects. If
these optional libraries aren't installed, text is returned unchanged
rather than raising, so the app still runs (labels just won't be
properly joined) -- `requirements.txt` includes both packages so a
normal `pip install -r requirements.txt` covers this automatically.
"""

from __future__ import annotations

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    _SHAPING_AVAILABLE = True
except ImportError:
    _SHAPING_AVAILABLE = False


def shape_for_display(text: str, language: str = "en") -> str:
    """Reshape + reorder Arabic text for correct matplotlib rendering.
    No-op for English or when shaping libraries are unavailable."""
    if language != "ar" or not text:
        return text
    if not _SHAPING_AVAILABLE:
        return text
    try:
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except Exception:
        return text


def shaping_available() -> bool:
    return _SHAPING_AVAILABLE
