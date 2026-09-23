"""
ui/dashboard.py

The main Dashboard page: stat cards, quick actions, two headline charts
(appliance consumption + time-of-day split), a live insights feed, and
an efficiency/anomaly summary strip. This is the page the user sees
immediately after loading data (spec sections 10, 37, 50).
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk

from ui.theme import Theme, font_for, SPACE_MD, SPACE_SM, SPACE_LG
from ui.components import StatCard, Card, Badge, ScrollableFrame, section_title
from ui import charts
from localization.translations import t, is_rtl, chart_label
from utils.currency import format_currency, format_energy


class DashboardPage(tk.Frame):
    def __init__(self, parent, theme: Theme, language: str, analyzer,
                 on_quick_action=None, **kwargs):
        super().__init__(parent, bg=theme.bg, **kwargs)
        self.theme = theme
        self.language = language
        self.analyzer = analyzer
        self.on_quick_action = on_quick_action or (lambda action: None)
        self._chart_canvases = []
        self._build()

    def _clear_chart_canvases(self):
        for canvas in self._chart_canvases:
            try:
                canvas.get_tk_widget().destroy()
            except Exception:
                pass
        self._chart_canvases = []

    def _build(self):
        theme, language = self.theme, self.language

        scroll = ScrollableFrame(self, theme)
        scroll.pack(fill="both", expand=True)
        body = scroll.body

        if not self.analyzer.is_loaded():
            self._build_empty_state(body)
            return

        summary = self.analyzer.dashboard_summary()

        self._build_quick_actions(body)
        self._build_stat_cards(body, summary)
        self._build_alerts(body)
        self._build_charts_row(body)
        self._build_insights(body)

    # ------------------------------------------------------------------ #
    def _build_empty_state(self, parent):
        theme, language = self.theme, self.language
        wrapper = tk.Frame(parent, bg=theme.bg)
        wrapper.pack(fill="both", expand=True, pady=SPACE_LG * 3)
        tk.Label(
            wrapper, text="⚡", bg=theme.bg, fg=theme.text_secondary,
            font=font_for(theme, language, 48),
        ).pack()
        tk.Label(
            wrapper, text=t("action_load_csv", language), bg=theme.bg, fg=theme.text_primary,
            font=font_for(theme, language, 14, "bold"),
        ).pack(pady=(SPACE_SM, SPACE_MD))
        ttk.Button(
            wrapper, text=t("action_load_csv", language), style="Accent.TButton",
            command=lambda: self.on_quick_action("load_csv"),
        ).pack()

    def _build_quick_actions(self, parent):
        theme, language = self.theme, self.language
        actions = [
            ("load_csv", "action_load_csv"),
            ("generate_report", "action_generate_report"),
            ("trends", "action_trends"),
            ("recommendations", "action_recommendations"),
        ]
        row = tk.Frame(parent, bg=theme.bg)
        row.pack(fill="x", padx=SPACE_LG, pady=(SPACE_LG, 0))
        for action_key, label_key in actions:
            ttk.Button(
                row, text=t(label_key, language), style="Ghost.TButton",
                command=lambda a=action_key: self.on_quick_action(a),
            ).pack(side="right" if is_rtl(language) else "left", padx=(0, SPACE_SM))

    def _build_stat_cards(self, parent, summary: dict):
        theme, language = self.theme, self.language
        section_title(parent, theme, language, t("nav_dashboard", language)).pack_configure(padx=SPACE_LG)

        grid = tk.Frame(parent, bg=theme.bg)
        grid.pack(fill="x", padx=SPACE_LG)
        for i in range(4):
            grid.columnconfigure(i, weight=1, uniform="stat")

        cards = [
            (t("card_total_energy", language), format_energy(summary["total_energy_kwh"]), ""),
            (t("card_estimated_cost", language), format_currency(summary["total_cost"], language), ""),
            (t("card_avg_daily_usage", language), f'{format_energy(summary["avg_daily_kwh"])}/day', ""),
            (t("card_peak_usage", language), chart_label(f"tod_{summary.get('peak_window', 'N/A')}", language), ""),
            (t("card_highest_appliance", language), summary.get("highest_appliance", "N/A"), ""),
            (t("card_lowest_appliance", language), summary.get("lowest_appliance", "N/A"), ""),
        ]

        eff = self.analyzer.efficiency_score()
        cards.append((t("card_efficiency_score", language), f"{eff['score']} / 100", ""))

        recs = self.analyzer.recommendations(as_text=False)
        total_savings = sum(r.get("estimated_monthly_savings", 0) for r in recs)
        cards.append((t("card_potential_savings", language), format_currency(total_savings, language), ""))

        for idx, (label, value, caption) in enumerate(cards):
            row, col = divmod(idx, 4)
            card = StatCard(grid, theme, language, label, value, caption)
            card.grid(row=row, column=col, sticky="nsew", padx=SPACE_SM, pady=SPACE_SM)

    def _build_alerts(self, parent):
        theme, language = self.theme, self.language
        anomalies = self.analyzer.anomalies()
        if not anomalies:
            return
        row = tk.Frame(parent, bg=theme.bg)
        row.pack(fill="x", padx=SPACE_LG, pady=(SPACE_SM, 0))
        text = (
            f"⚠ {len(anomalies)} unusual consumption day(s) detected"
            if language != "ar" else f"⚠ تم رصد {len(anomalies)} يوم استهلاك غير معتاد"
        )
        Badge(row, theme, language, text, level="warning").pack(
            side="right" if is_rtl(language) else "left"
        )

    def _build_charts_row(self, parent):
        theme, language = self.theme, self.language
        row = tk.Frame(parent, bg=theme.bg)
        row.pack(fill="both", expand=True, padx=SPACE_LG, pady=SPACE_MD)
        row.columnconfigure(0, weight=1)
        row.columnconfigure(1, weight=1)

        appliance_df = self.analyzer.appliance_analysis()
        tod_df = self.analyzer.time_of_day_analysis()

        left_card = Card(row, theme)
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, SPACE_SM))
        fig1 = charts.appliance_consumption_bar(appliance_df, theme, language)
        canvas1 = charts.embed_figure(left_card.inner, fig1)
        canvas1.get_tk_widget().pack(fill="both", expand=True)
        self._chart_canvases.append(canvas1)

        right_card = Card(row, theme)
        right_card.grid(row=0, column=1, sticky="nsew", padx=(SPACE_SM, 0))
        fig2 = charts.time_of_day_donut(tod_df, theme, language)
        canvas2 = charts.embed_figure(right_card.inner, fig2)
        canvas2.get_tk_widget().pack(fill="both", expand=True)
        self._chart_canvases.append(canvas2)

    def _build_insights(self, parent):
        theme, language = self.theme, self.language
        section_title(parent, theme, language, t("nav_insights", language)).pack_configure(padx=SPACE_LG)

        card = Card(parent, theme)
        card.pack(fill="x", padx=SPACE_LG, pady=(0, SPACE_LG))
        anchor = "e" if is_rtl(language) else "w"

        for insight in self.analyzer.insights():
            tk.Label(
                card.inner, text=f"• {insight}", bg=theme.surface, fg=theme.text_primary,
                font=font_for(theme, language, 10), anchor=anchor, justify="right" if is_rtl(language) else "left",
                wraplength=900,
            ).pack(fill="x", pady=3, anchor=anchor)
