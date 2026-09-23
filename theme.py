"""
ui/theme.py

Centralized light/dark theme definitions for WattWise. Every color,
font, and spacing value used across the UI comes from here so switching
themes never requires touching individual widget code.
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    name: str
    bg: str                # main window background
    surface: str            # card / panel background
    surface_alt: str        # secondary panel background (sidebar)
    text_primary: str
    text_secondary: str
    text_on_accent: str
    accent: str              # primary brand accent
    accent_hover: str
    success: str
    warning: str
    danger: str
    border: str
    chart_bg: str
    chart_grid: str
    chart_palette: tuple[str, ...]
    font_family: str
    font_family_ar: str


LIGHT = Theme(
    name="light",
    bg="#F4F6FB",
    surface="#FFFFFF",
    surface_alt="#FFFFFF",
    text_primary="#1B1F2A",
    text_secondary="#6B7280",
    text_on_accent="#FFFFFF",
    accent="#4F6EF7",
    accent_hover="#3F58D8",
    success="#22A55A",
    warning="#F5A623",
    danger="#E5484D",
    border="#E4E8F0",
    chart_bg="#FFFFFF",
    chart_grid="#E9ECF3",
    chart_palette=("#4F6EF7", "#22A55A", "#F5A623", "#E5484D", "#8B5CF6", "#06B6D4", "#EC4899", "#84CC16"),
    font_family="Segoe UI",
    font_family_ar="Dubai",
)

DARK = Theme(
    name="dark",
    bg="#12141C",
    surface="#1B1E29",
    surface_alt="#171922",
    text_primary="#F1F3F9",
    text_secondary="#9CA3AF",
    text_on_accent="#FFFFFF",
    accent="#6E8CFF",
    accent_hover="#8AA1FF",
    success="#34D07E",
    warning="#FFB84D",
    danger="#FF6B6E",
    border="#2A2E3C",
    chart_bg="#1B1E29",
    chart_grid="#2A2E3C",
    chart_palette=("#6E8CFF", "#34D07E", "#FFB84D", "#FF6B6E", "#A78BFA", "#22D3EE", "#F472B6", "#A3E635"),
    font_family="Segoe UI",
    font_family_ar="Dubai",
)

THEMES = {"light": LIGHT, "dark": DARK}

# Spacing scale (px) reused across every page for visual consistency.
SPACE_XS = 4
SPACE_SM = 8
SPACE_MD = 16
SPACE_LG = 24
SPACE_XL = 32

CARD_RADIUS_HINT = 12  # Tkinter has no native rounded corners; components.py
                        # simulates this via padding + border color, noted
                        # here so it's a single source of truth for the value.


def get_theme(mode: str) -> Theme:
    return THEMES.get(mode, LIGHT)


def font_for(theme: Theme, language: str, size: int = 10, weight: str = "normal") -> tuple:
    family = theme.font_family_ar if language == "ar" else theme.font_family
    return (family, size, weight)
