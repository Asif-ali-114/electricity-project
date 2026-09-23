"""
ui/components.py

Reusable, theme-aware Tkinter widgets shared across every page: stat
cards, nav buttons, primary/secondary buttons, a scrollable frame, and
alert/badge widgets. Tkinter has no native rounded corners or shadows,
so "card" styling is simulated via flat borders + background contrast,
which reads as clean and modern without fighting the toolkit.

All widgets take a `theme` (ui.theme.Theme) and `language` so RTL text
anchoring and font selection stay consistent everywhere.
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk

from ui.theme import Theme, font_for, SPACE_MD, SPACE_SM


def apply_ttk_style(root: tk.Tk, theme: Theme) -> ttk.Style:
    """Configure a single ttk.Style instance to match the active theme.
    Uses 'clam' as the base theme since it's the most re-themeable
    built-in ttk theme (default/native themes ignore background colors)."""
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure("TFrame", background=theme.bg)
    style.configure("Surface.TFrame", background=theme.surface)
    style.configure("Sidebar.TFrame", background=theme.surface_alt)

    style.configure(
        "TLabel", background=theme.bg, foreground=theme.text_primary
    )
    style.configure(
        "Surface.TLabel", background=theme.surface, foreground=theme.text_primary
    )
    style.configure(
        "Secondary.TLabel", background=theme.surface, foreground=theme.text_secondary
    )
    style.configure(
        "Sidebar.TLabel", background=theme.surface_alt, foreground=theme.text_primary
    )

    style.configure(
        "Accent.TButton",
        background=theme.accent,
        foreground=theme.text_on_accent,
        borderwidth=0,
        focusthickness=0,
        padding=(14, 8),
    )
    style.map("Accent.TButton", background=[("active", theme.accent_hover)])

    style.configure(
        "Ghost.TButton",
        background=theme.surface,
        foreground=theme.text_primary,
        borderwidth=1,
        relief="solid",
        padding=(12, 6),
    )
    style.map("Ghost.TButton", background=[("active", theme.border)])

    style.configure(
        "Nav.TButton",
        background=theme.surface_alt,
        foreground=theme.text_primary,
        borderwidth=0,
        anchor="w",
        padding=(16, 10),
    )
    style.map("Nav.TButton", background=[("active", theme.border)])

    style.configure(
        "NavActive.TButton",
        background=theme.accent,
        foreground=theme.text_on_accent,
        borderwidth=0,
        anchor="w",
        padding=(16, 10),
    )

    style.configure(
        "Treeview",
        background=theme.surface,
        fieldbackground=theme.surface,
        foreground=theme.text_primary,
        rowheight=28,
        borderwidth=0,
    )
    style.configure(
        "Treeview.Heading",
        background=theme.surface_alt,
        foreground=theme.text_secondary,
        borderwidth=0,
    )
    style.map("Treeview", background=[("selected", theme.accent)], foreground=[("selected", theme.text_on_accent)])

    style.configure(
        "TCombobox",
        fieldbackground=theme.surface,
        background=theme.surface,
        foreground=theme.text_primary,
    )

    return style


class Card(tk.Frame):
    """A flat 'card' panel: surface background, subtle border, padded content."""

    def __init__(self, parent, theme: Theme, padding: int = SPACE_MD, **kwargs):
        super().__init__(
            parent,
            bg=theme.surface,
            highlightbackground=theme.border,
            highlightthickness=1,
            bd=0,
            **kwargs,
        )
        self.theme = theme
        self.inner = tk.Frame(self, bg=theme.surface)
        self.inner.pack(fill="both", expand=True, padx=padding, pady=padding)


class StatCard(Card):
    """Dashboard stat card: label on top, big value, optional sub-caption."""

    def __init__(self, parent, theme: Theme, language: str, label: str, value: str,
                 caption: str = "", accent_color: str | None = None, **kwargs):
        super().__init__(parent, theme, **kwargs)
        anchor = "e" if language == "ar" else "w"
        justify = "right" if language == "ar" else "left"

        tk.Label(
            self.inner, text=label, bg=theme.surface, fg=theme.text_secondary,
            font=font_for(theme, language, 10), anchor=anchor, justify=justify,
        ).pack(fill="x")

        tk.Label(
            self.inner, text=value, bg=theme.surface,
            fg=accent_color or theme.text_primary,
            font=font_for(theme, language, 22, "bold"), anchor=anchor, justify=justify,
        ).pack(fill="x", pady=(SPACE_SM, 0))

        if caption:
            tk.Label(
                self.inner, text=caption, bg=theme.surface, fg=theme.text_secondary,
                font=font_for(theme, language, 9), anchor=anchor, justify=justify,
            ).pack(fill="x", pady=(2, 0))


class NavButton(ttk.Button):
    """A sidebar navigation entry that visually highlights when active."""

    def __init__(self, parent, text: str, command, active: bool = False, **kwargs):
        style = "NavActive.TButton" if active else "Nav.TButton"
        super().__init__(parent, text=text, command=command, style=style, **kwargs)


class Badge(tk.Label):
    """Small colored pill used for alerts/status (e.g. anomaly warnings)."""

    LEVEL_COLORS = {
        "info": ("accent", "text_on_accent"),
        "success": ("success", "text_on_accent"),
        "warning": ("warning", "text_on_accent"),
        "danger": ("danger", "text_on_accent"),
    }

    def __init__(self, parent, theme: Theme, language: str, text: str, level: str = "info", **kwargs):
        bg_attr, fg_attr = self.LEVEL_COLORS.get(level, self.LEVEL_COLORS["info"])
        super().__init__(
            parent, text=text,
            bg=getattr(theme, bg_attr), fg=getattr(theme, fg_attr),
            font=font_for(theme, language, 9, "bold"),
            padx=10, pady=4,
            **kwargs,
        )


class ScrollableFrame(tk.Frame):
    """A vertically scrollable container -- used for any page whose content
    may exceed the visible window height (spec section 52: responsive)."""

    def __init__(self, parent, theme: Theme, **kwargs):
        super().__init__(parent, bg=theme.bg, **kwargs)
        self.theme = theme

        self.canvas = tk.Canvas(self, bg=theme.bg, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.body = tk.Frame(self.canvas, bg=theme.bg)

        self.body.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self._window = self.canvas.create_window((0, 0), window=self.body, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_canvas_resize(self, event):
        self.canvas.itemconfig(self._window, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


def section_title(parent, theme: Theme, language: str, text: str) -> tk.Label:
    anchor = "e" if language == "ar" else "w"
    lbl = tk.Label(
        parent, text=text, bg=theme.bg, fg=theme.text_primary,
        font=font_for(theme, language, 15, "bold"), anchor=anchor,
    )
    lbl.pack(fill="x", pady=(SPACE_MD, SPACE_SM))
    return lbl
