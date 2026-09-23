"""
main.py

WattWise application entry point. Wires together the sidebar, theming,
language/RTL switching, CSV loading (month selector + file picker), and
page routing. The Dashboard page is fully built in this stage; the
remaining eleven nav pages render a lightweight placeholder until
Stage 5 fills them in with their own dedicated views (they already have
full data/analysis support from Stages 2-3 -- only their UI is pending).
"""

from __future__ import annotations
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

from ui.theme import get_theme, font_for, SPACE_LG, SPACE_MD, SPACE_SM
from ui.components import apply_ttk_style, section_title, Card
from ui.sidebar import Sidebar
from ui.dashboard import DashboardPage
from localization.translations import t, is_rtl
from analysis.analyzer import Analyzer
from data_processing.loader import LoadError

BASE_DIR = Path(__file__).resolve().parent
SETTINGS_PATH = BASE_DIR / "config" / "settings.json"
DATA_DIR = BASE_DIR / "data"

MONTH_FILES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

PLACEHOLDER_PAGES = {
    "data_explorer": "nav_data_explorer",
    "appliance_analysis": "nav_appliance_analysis",
    "daily_analysis": "nav_daily_analysis",
    "weekly_analysis": "nav_weekly_analysis",
    "monthly_analysis": "nav_monthly_analysis",
    "hourly_analysis": "nav_hourly_analysis",
    "comparisons": "nav_comparisons",
    "insights": "nav_insights",
    "recommendations": "nav_recommendations",
    "reports": "nav_reports",
    "settings": "nav_settings",
}


class WattWiseApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.settings = self._load_settings()
        self.language = self.settings.get("language", "en")
        self.theme_mode = self.settings.get("theme", "light")
        self.active_page = "dashboard"
        self.analyzer = Analyzer(language=self.language)

        self._configure_window()
        self.style = apply_ttk_style(self, get_theme(self.theme_mode))

        self._build_layout()
        self._load_initial_data()
        self._render()

    # ------------------------------------------------------------------ #
    # Setup
    # ------------------------------------------------------------------ #
    def _load_settings(self) -> dict:
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"language": "en", "theme": "light"}

    def _save_settings(self) -> None:
        self.settings["language"] = self.language
        self.settings["theme"] = self.theme_mode
        try:
            with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception:
            pass  # non-fatal: app still works without persisting settings

    def _configure_window(self):
        self.title(t("app_title", self.language))
        win = self.settings.get("window", {"width": 1400, "height": 860})
        self.geometry(f'{win.get("width", 1400)}x{win.get("height", 860)}')
        self.minsize(1000, 640)

    def _load_initial_data(self):
        """Demo Mode (spec section 50): auto-load a sample month on first launch."""
        last_month = self.settings.get("last_loaded_month")
        candidate = last_month if last_month in MONTH_FILES else "January"
        path = DATA_DIR / f"{candidate}.csv"
        if path.exists():
            try:
                self.analyzer.load(str(path))
                self.current_month = candidate
            except LoadError:
                self.current_month = None
        else:
            self.current_month = None

    # ------------------------------------------------------------------ #
    # Layout
    # ------------------------------------------------------------------ #
    def _build_layout(self):
        theme = get_theme(self.theme_mode)
        self.configure(bg=theme.bg)

        self.root_frame = tk.Frame(self, bg=theme.bg)
        self.root_frame.pack(fill="both", expand=True)

        # RTL: sidebar moves to the right, content to the left.
        self.sidebar_side = "right" if is_rtl(self.language) else "left"

        self.content_container = tk.Frame(self.root_frame, bg=theme.bg)
        self._build_topbar()
        self.page_container = tk.Frame(self.content_container, bg=theme.bg)
        self.page_container.pack(fill="both", expand=True)

    def _build_topbar(self):
        theme, language = get_theme(self.theme_mode), self.language
        topbar = tk.Frame(self.content_container, bg=theme.bg)
        topbar.pack(fill="x", padx=SPACE_LG, pady=(SPACE_MD, 0))

        anchor_side = "left" if is_rtl(language) else "right"

        month_var = tk.StringVar(value=getattr(self, "current_month", "") or "")
        month_names_localized = [t(f"month_{i+1}", language) for i in range(12)]
        month_combo = ttk.Combobox(
            topbar, values=month_names_localized, textvariable=month_var,
            state="readonly", width=14,
        )
        if getattr(self, "current_month", None):
            idx = MONTH_FILES.index(self.current_month)
            month_combo.current(idx)
        month_combo.bind("<<ComboboxSelected>>", lambda e: self._on_month_selected(month_combo.current()))
        month_combo.pack(side=anchor_side, padx=(SPACE_SM, 0))

        ttk.Button(
            topbar, text=t("action_load_csv", language), style="Accent.TButton",
            command=self._load_csv_dialog,
        ).pack(side=anchor_side, padx=(SPACE_SM, 0))

    # ------------------------------------------------------------------ #
    # Data actions
    # ------------------------------------------------------------------ #
    def _on_month_selected(self, index: int):
        if index < 0:
            return
        month = MONTH_FILES[index]
        path = DATA_DIR / f"{month}.csv"
        if not path.exists():
            messagebox.showwarning(
                t("app_title", self.language),
                f"No sample data found for {month}.",
            )
            return
        try:
            self.analyzer.load(str(path))
            self.current_month = month
            self.settings["last_loaded_month"] = month
            self._save_settings()
            self._render()
        except LoadError as exc:
            messagebox.showerror(t("app_title", self.language), str(exc))

    def _load_csv_dialog(self):
        path = filedialog.askopenfilename(
            title=t("action_load_csv", self.language),
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not path:
            return  # user cancelled -- no error shown
        try:
            self.analyzer.load(path)
            self.current_month = None
            recent = self.settings.setdefault("recent_files", [])
            if path not in recent:
                recent.insert(0, path)
                self.settings["recent_files"] = recent[:10]
            self._save_settings()
            self._render()
        except LoadError as exc:
            messagebox.showerror(t("app_title", self.language), str(exc))
        except Exception as exc:  # noqa: BLE001 - always show a friendly message, never a raw traceback
            messagebox.showerror(
                t("app_title", self.language),
                f"Could not load this file. Please check its format.\n\n({exc})",
            )

    def _handle_quick_action(self, action: str):
        if action == "load_csv":
            self._load_csv_dialog()
        elif action == "trends":
            self._navigate("hourly_analysis")
        elif action == "recommendations":
            self._navigate("recommendations")
        elif action == "generate_report":
            self._navigate("reports")

    # ------------------------------------------------------------------ #
    # Navigation / theming
    # ------------------------------------------------------------------ #
    def _navigate(self, page_key: str):
        self.active_page = page_key
        self._render()

    def _toggle_theme(self):
        self.theme_mode = "dark" if self.theme_mode == "light" else "light"
        self._save_settings()
        self.style = apply_ttk_style(self, get_theme(self.theme_mode))
        self._render(full_rebuild=True)

    def _toggle_language(self):
        self.language = "ar" if self.language == "en" else "en"
        self.analyzer.set_language(self.language)
        self._save_settings()
        self.title(t("app_title", self.language))
        self._render(full_rebuild=True)

    # ------------------------------------------------------------------ #
    # Rendering
    # ------------------------------------------------------------------ #
    def _render(self, full_rebuild: bool = False):
        theme = get_theme(self.theme_mode)

        if full_rebuild:
            for widget in self.root_frame.winfo_children():
                widget.destroy()
            self.configure(bg=theme.bg)
            self.root_frame.configure(bg=theme.bg)
            self.sidebar_side = "right" if is_rtl(self.language) else "left"
            self.content_container = tk.Frame(self.root_frame, bg=theme.bg)
            self._build_topbar()
            self.page_container = tk.Frame(self.content_container, bg=theme.bg)
            self.page_container.pack(fill="both", expand=True)
        else:
            for widget in self.root_frame.winfo_children():
                widget.destroy()

        sidebar = Sidebar(
            self.root_frame, theme, self.language, self.active_page,
            on_navigate=self._navigate,
            on_toggle_theme=self._toggle_theme,
            on_toggle_language=self._toggle_language,
        )
        sidebar.pack(side=self.sidebar_side, fill="y")

        self.content_container = tk.Frame(self.root_frame, bg=theme.bg)
        self.content_container.pack(side="left", fill="both", expand=True)
        self._build_topbar()

        self.page_container = tk.Frame(self.content_container, bg=theme.bg)
        self.page_container.pack(fill="both", expand=True)

        self._render_page(theme)

    def _render_page(self, theme):
        for widget in self.page_container.winfo_children():
            widget.destroy()

        if self.active_page == "dashboard":
            page = DashboardPage(
                self.page_container, theme, self.language, self.analyzer,
                on_quick_action=self._handle_quick_action,
            )
            page.pack(fill="both", expand=True)
        else:
            self._render_placeholder(theme)

    def _render_placeholder(self, theme):
        label_key = PLACEHOLDER_PAGES.get(self.active_page, "nav_dashboard")
        wrapper = tk.Frame(self.page_container, bg=theme.bg)
        wrapper.pack(fill="both", expand=True, padx=SPACE_LG, pady=SPACE_LG)
        section_title(wrapper, theme, self.language, t(label_key, self.language))

        card = Card(wrapper, theme)
        card.pack(fill="x")
        msg = (
            "This page's data and analysis are already implemented -- its dedicated "
            "view is coming in the next build stage."
            if self.language != "ar" else
            "بيانات وتحليلات هذه الصفحة جاهزة بالفعل -- واجهتها الخاصة قادمة في المرحلة القادمة من البناء."
        )
        tk.Label(
            card.inner, text=msg, bg=theme.surface, fg=theme.text_secondary,
            font=font_for(theme, self.language, 10), wraplength=700, justify="left",
        ).pack(anchor="w")


def main():
    app = WattWiseApp()
    app.mainloop()


if __name__ == "__main__":
    main()
