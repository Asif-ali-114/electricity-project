"""
ui/sidebar.py

The primary navigation sidebar (spec section 36). Renders the 12 nav
pages, highlights the active page, and flips to the right side of the
window with right-aligned text when Arabic/RTL is active. Also hosts
the language and theme toggles so they're always reachable.
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk

from ui.theme import Theme, font_for, SPACE_MD, SPACE_SM
from ui.components import NavButton
from localization.translations import t, is_rtl

NAV_ITEMS = [
    ("dashboard", "nav_dashboard", "📊"),
    ("data_explorer", "nav_data_explorer", "🔍"),
    ("appliance_analysis", "nav_appliance_analysis", "⚡"),
    ("daily_analysis", "nav_daily_analysis", "📅"),
    ("weekly_analysis", "nav_weekly_analysis", "🗓"),
    ("monthly_analysis", "nav_monthly_analysis", "📆"),
    ("hourly_analysis", "nav_hourly_analysis", "🕐"),
    ("comparisons", "nav_comparisons", "⚖"),
    ("insights", "nav_insights", "💡"),
    ("recommendations", "nav_recommendations", "✅"),
    ("reports", "nav_reports", "📄"),
    ("settings", "nav_settings", "⚙"),
]


class Sidebar(tk.Frame):
    def __init__(self, parent, theme: Theme, language: str, active_page: str,
                 on_navigate, on_toggle_theme, on_toggle_language, **kwargs):
        super().__init__(parent, bg=theme.surface_alt, width=240, **kwargs)
        self.theme = theme
        self.language = language
        self.active_page = active_page
        self.on_navigate = on_navigate
        self.on_toggle_theme = on_toggle_theme
        self.on_toggle_language = on_toggle_language
        self.pack_propagate(False)
        self._build()

    def _build(self):
        theme, language = self.theme, self.language
        anchor = "e" if is_rtl(language) else "w"

        header = tk.Frame(self, bg=theme.surface_alt)
        header.pack(fill="x", padx=SPACE_MD, pady=(SPACE_MD, SPACE_SM))
        tk.Label(
            header, text="⚡ WattWise", bg=theme.surface_alt, fg=theme.text_primary,
            font=font_for(theme, language, 16, "bold"), anchor=anchor,
        ).pack(fill="x")

        nav_frame = tk.Frame(self, bg=theme.surface_alt)
        nav_frame.pack(fill="both", expand=True, padx=SPACE_SM, pady=SPACE_SM)

        for page_key, label_key, icon in NAV_ITEMS:
            label = f"{icon}  {t(label_key, language)}"
            btn = NavButton(
                nav_frame, text=label,
                command=lambda k=page_key: self.on_navigate(k),
                active=(page_key == self.active_page),
            )
            btn.pack(fill="x", pady=2)

        footer = tk.Frame(self, bg=theme.surface_alt)
        footer.pack(fill="x", padx=SPACE_MD, pady=SPACE_MD, side="bottom")

        lang_label = "🇬🇧 English" if language == "ar" else "🇸🇦 العربية"
        ttk.Button(
            footer, text=lang_label, style="Ghost.TButton",
            command=self.on_toggle_language,
        ).pack(fill="x", pady=(0, SPACE_SM))

        theme_label = "☀ Light Mode" if theme.name == "dark" else "🌙 Dark Mode"
        ttk.Button(
            footer, text=theme_label, style="Ghost.TButton",
            command=self.on_toggle_theme,
        ).pack(fill="x")
