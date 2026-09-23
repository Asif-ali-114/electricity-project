"""
ui/charts.py

Builds theme-aware matplotlib Figures for every chart in the spec
(appliance bar/pie/cost/duration, daily/weekly/monthly/hourly trends,
heatmap, comparison, forecast). Figure-building functions here have NO
Tkinter dependency -- they return a plain `matplotlib.figure.Figure` --
so they can be unit-tested headlessly. Only `embed_figure()` touches
Tkinter, via FigureCanvasTkAgg, and is called by the page code that
already has a live Tk parent widget.

Every chart must render inside the app window per spec section 12/57 --
never open a separate Matplotlib window -- which this module guarantees
by always returning a Figure to be embedded, never calling plt.show().
"""

from __future__ import annotations
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # safe default; embed_figure() re-parents onto Tk canvas regardless of backend
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from ui.theme import Theme
from localization.translations import translate_appliance, chart_label
from localization.arabic_shaping import shape_for_display

plt.rcParams["axes.unicode_minus"] = False


def _new_figure(theme: Theme, figsize=(6, 4)) -> tuple[Figure, plt.Axes]:
    fig = Figure(figsize=figsize, dpi=100)
    ax = fig.add_subplot(111)
    _style_axes(fig, ax, theme)
    return fig, ax


def _style_axes(fig: Figure, ax: plt.Axes, theme: Theme) -> None:
    fig.patch.set_facecolor(theme.chart_bg)
    ax.set_facecolor(theme.chart_bg)
    for spine in ax.spines.values():
        spine.set_color(theme.chart_grid)
    ax.tick_params(colors=theme.text_secondary, labelsize=8)
    ax.xaxis.label.set_color(theme.text_secondary)
    ax.yaxis.label.set_color(theme.text_secondary)
    ax.title.set_color(theme.text_primary)
    ax.grid(True, color=theme.chart_grid, linewidth=0.6, axis="y")
    ax.set_axisbelow(True)


def _translated_labels(names, language: str) -> list[str]:
    return [shape_for_display(translate_appliance(n, language), language) for n in names]


def _title(key: str, language: str, fallback: str) -> str:
    label = chart_label(key, language) if key else fallback
    return shape_for_display(label, language)


def _tod_labels(names, language: str) -> list[str]:
    return [shape_for_display(chart_label(f"tod_{n}", language), language) for n in names]


def _weekday_labels(names, language: str) -> list[str]:
    return [shape_for_display(chart_label(f"weekday_{n}", language), language) for n in names]


# --------------------------------------------------------------------- #
# Appliance charts (spec section 12)
# --------------------------------------------------------------------- #
def appliance_consumption_bar(appliance_df: pd.DataFrame, theme: Theme, language: str,
                               title: str | None = None) -> Figure:
    title = title or _title("chart_appliance_consumption", language, "Appliance Consumption")
    fig, ax = _new_figure(theme, figsize=(7, 4.2))
    data = appliance_df.head(10).iloc[::-1]
    labels = _translated_labels(data["Appliance"], language)
    colors = [theme.chart_palette[i % len(theme.chart_palette)] for i in range(len(data))]
    ax.barh(labels, data["Total_Energy_kWh"], color=colors)
    ax.set_xlabel("kWh")
    ax.set_title(title)
    fig.tight_layout()
    return fig


def appliance_contribution_pie(appliance_df: pd.DataFrame, theme: Theme, language: str,
                                title: str | None = None) -> Figure:
    title = title or _title("chart_appliance_contribution", language, "Appliance Contribution")
    fig, ax = _new_figure(theme, figsize=(5.5, 5))
    data = appliance_df.head(7)
    labels = _translated_labels(data["Appliance"], language)
    colors = [theme.chart_palette[i % len(theme.chart_palette)] for i in range(len(data))]
    wedges, _, autotexts = ax.pie(
        data["Total_Energy_kWh"], labels=None, autopct="%1.0f%%",
        colors=colors, wedgeprops=dict(width=0.42, edgecolor=theme.chart_bg),
        pctdistance=0.78,
    )
    for t in autotexts:
        t.set_color(theme.text_primary)
        t.set_fontsize(8)
    ax.legend(wedges, labels, loc="center left", bbox_to_anchor=(1, 0.5),
              fontsize=8, frameon=False, labelcolor=theme.text_primary)
    ax.set_title(title)
    fig.tight_layout()
    return fig


def appliance_cost_chart(appliance_df: pd.DataFrame, theme: Theme, language: str,
                          title: str | None = None) -> Figure:
    title = title or _title("chart_appliance_cost", language, "Appliance Cost")
    fig, ax = _new_figure(theme, figsize=(7, 4.2))
    data = appliance_df.head(10)
    labels = _translated_labels(data["Appliance"], language)
    ax.bar(labels, data["Estimated_Cost"], color=theme.accent)
    ax.set_ylabel("Cost")
    ax.set_title(title)
    ax.tick_params(axis="x", rotation=40)
    fig.tight_layout()
    return fig


def appliance_duration_chart(appliance_df: pd.DataFrame, theme: Theme, language: str,
                              title: str | None = None) -> Figure:
    title = title or _title("chart_appliance_duration", language, "Appliance Duration")
    fig, ax = _new_figure(theme, figsize=(7, 4.2))
    data = appliance_df.head(10)
    labels = _translated_labels(data["Appliance"], language)
    ax.bar(labels, data["Total_Duration_Hours"], color=theme.success)
    ax.set_ylabel("Hours")
    ax.set_title(title)
    ax.tick_params(axis="x", rotation=40)
    fig.tight_layout()
    return fig


def appliance_comparison_barh(appliance_df: pd.DataFrame, theme: Theme, language: str,
                               title: str | None = None) -> Figure:
    title = title or _title("chart_appliance_comparison", language, "Appliance Comparison")
    fig, ax = _new_figure(theme, figsize=(7, 4.2))
    data = appliance_df.sort_values("Total_Energy_kWh").tail(10)
    labels = _translated_labels(data["Appliance"], language)
    ax.barh(labels, data["Percent_of_Total"], color=theme.chart_palette[4])
    ax.set_xlabel("% of total usage")
    ax.set_title(title)
    fig.tight_layout()
    return fig


# --------------------------------------------------------------------- #
# Time-based charts (spec sections 13-17, 57)
# --------------------------------------------------------------------- #
def daily_consumption_line(daily_df: pd.DataFrame, theme: Theme, language: str,
                            title: str | None = None) -> Figure:
    title = title or _title("chart_daily_consumption", language, "Daily Consumption")
    fig, ax = _new_figure(theme, figsize=(8, 4))
    ax.plot(daily_df["Date"], daily_df["Energy_kWh"], color=theme.accent, linewidth=2)
    ax.fill_between(daily_df["Date"], daily_df["Energy_kWh"], color=theme.accent, alpha=0.12)
    ax.set_ylabel("kWh")
    ax.set_title(title)
    fig.autofmt_xdate(rotation=30)
    fig.tight_layout()
    return fig


def daily_cost_chart(daily_df: pd.DataFrame, theme: Theme, language: str,
                      title: str | None = None) -> Figure:
    title = title or _title("chart_daily_cost", language, "Daily Cost")
    fig, ax = _new_figure(theme, figsize=(8, 4))
    ax.bar(daily_df["Date"], daily_df["Cost"], color=theme.warning)
    ax.set_ylabel("Cost")
    ax.set_title(title)
    fig.autofmt_xdate(rotation=30)
    fig.tight_layout()
    return fig


def weekly_bar_chart(weekly_df: pd.DataFrame, theme: Theme, language: str,
                      title: str | None = None) -> Figure:
    title = title or _title("chart_weekly_consumption", language, "Weekly Consumption")
    fig, ax = _new_figure(theme, figsize=(7, 4))
    ax.bar(weekly_df["Week_Label"], weekly_df["Energy_kWh"], color=theme.chart_palette[2])
    ax.set_ylabel("kWh")
    ax.set_title(title)
    fig.tight_layout()
    return fig


def monthly_bar_chart(monthly_df: pd.DataFrame, theme: Theme, language: str,
                       title: str | None = None) -> Figure:
    title = title or _title("chart_monthly_consumption", language, "Monthly Consumption")
    fig, ax = _new_figure(theme, figsize=(8, 4))
    ax.bar(monthly_df["Month"], monthly_df["Energy_kWh"], color=theme.chart_palette[0])
    ax.set_ylabel("kWh")
    ax.set_title(title)
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    return fig


def hourly_consumption_chart(hourly_df: pd.DataFrame, theme: Theme, language: str,
                              title: str | None = None) -> Figure:
    title = title or _title("chart_hourly_consumption", language, "Hourly Consumption")
    fig, ax = _new_figure(theme, figsize=(8, 4))
    ax.plot(hourly_df["Hour"], hourly_df["Energy_kWh"], color=theme.chart_palette[5],
            marker="o", markersize=3, linewidth=1.8)
    peak_idx = hourly_df["Energy_kWh"].idxmax()
    ax.scatter([hourly_df["Hour"][peak_idx]], [hourly_df["Energy_kWh"][peak_idx]],
               color=theme.danger, zorder=5, s=40)
    ax.set_xlabel("Hour of day")
    ax.set_ylabel("kWh")
    ax.set_xticks(range(0, 24, 2))
    ax.set_title(title)
    fig.tight_layout()
    return fig


def time_of_day_donut(tod_df: pd.DataFrame, theme: Theme, language: str,
                       title: str | None = None) -> Figure:
    title = title or _title("chart_time_of_day", language, "Time-of-Day Usage")
    fig, ax = _new_figure(theme, figsize=(5.5, 5))
    colors = [theme.chart_palette[i % len(theme.chart_palette)] for i in range(len(tod_df))]
    wedges, _, autotexts = ax.pie(
        tod_df["Energy_kWh"], autopct="%1.0f%%", colors=colors,
        wedgeprops=dict(width=0.42, edgecolor=theme.chart_bg), pctdistance=0.78,
    )
    for t in autotexts:
        t.set_color(theme.text_primary)
        t.set_fontsize(8)
    tod_legend_labels = _tod_labels(tod_df["Time_of_Day"], language)
    ax.legend(wedges, tod_legend_labels, loc="center left", bbox_to_anchor=(1, 0.5),
              fontsize=8, frameon=False, labelcolor=theme.text_primary)
    ax.set_title(title)
    fig.tight_layout()
    return fig


# --------------------------------------------------------------------- #
# Heatmap (spec section 18)
# --------------------------------------------------------------------- #
def usage_heatmap(matrix_df: pd.DataFrame, theme: Theme, language: str,
                   title: str | None = None) -> Figure:
    title = title or _title("chart_heatmap", language, "Usage Heatmap (Day x Hour)")
    import seaborn as sns
    fig = Figure(figsize=(9, 4.2), dpi=100)
    ax = fig.add_subplot(111)
    fig.patch.set_facecolor(theme.chart_bg)
    ax.set_facecolor(theme.chart_bg)

    cmap = "rocket" if theme.name == "dark" else "flare"
    display_matrix = matrix_df.copy()
    display_matrix.index = _weekday_labels(display_matrix.index, language)
    sns.heatmap(
        display_matrix, ax=ax, cmap=cmap, cbar=True,
        linewidths=0.4, linecolor=theme.chart_bg,
        xticklabels=2, yticklabels=True,
    )
    ax.tick_params(colors=theme.text_secondary, labelsize=8)
    ax.set_xlabel(shape_for_display("Hour" if language != "ar" else "الساعة", language))
    ax.set_ylabel("")
    ax.title.set_color(theme.text_primary)
    ax.set_title(title)
    fig.tight_layout()
    return fig


# --------------------------------------------------------------------- #
# Comparison & forecast charts (spec sections 30, 26)
# --------------------------------------------------------------------- #
def comparison_bar_chart(labels: list[str], values_a: list[float], values_b: list[float],
                          theme: Theme, language: str, series_labels=("A", "B"),
                          title: str | None = None) -> Figure:
    title = title or _title("chart_comparison", language, "Comparison")
    import numpy as np
    fig, ax = _new_figure(theme, figsize=(7, 4.2))
    x = np.arange(len(labels))
    width = 0.35
    ax.bar(x - width / 2, values_a, width, label=series_labels[0], color=theme.chart_palette[0])
    ax.bar(x + width / 2, values_b, width, label=series_labels[1], color=theme.chart_palette[1])
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=30)
    ax.legend(frameon=False, labelcolor=theme.text_primary)
    ax.set_title(title)
    fig.tight_layout()
    return fig


def forecast_chart(historical_daily: pd.DataFrame, forecast_kwh: float, theme: Theme,
                    language: str, title: str | None = None) -> Figure:
    title = title or _title("chart_forecast", language, "Forecast")
    fig, ax = _new_figure(theme, figsize=(7, 4))
    ax.plot(historical_daily["Date"], historical_daily["Energy_kWh"],
            color=theme.accent, linewidth=2, label=shape_for_display(chart_label("series_historical", language), language))
    if not historical_daily.empty:
        last_date = historical_daily["Date"].iloc[-1]
        next_date = pd.Timestamp(last_date) + pd.Timedelta(days=1)
        ax.plot([last_date, next_date],
                [historical_daily["Energy_kWh"].iloc[-1], forecast_kwh],
                color=theme.warning, linewidth=2, linestyle="--",
                label=shape_for_display(chart_label("series_forecast", language), language))
        ax.scatter([next_date], [forecast_kwh], color=theme.warning, zorder=5)
    ax.legend(frameon=False, labelcolor=theme.text_primary, fontsize=8)
    ax.set_title(title)
    fig.autofmt_xdate(rotation=30)
    fig.tight_layout()
    return fig


# --------------------------------------------------------------------- #
# Tkinter embedding
# --------------------------------------------------------------------- #
def embed_figure(parent, figure: Figure):
    """Embed a matplotlib Figure into a Tk widget. Returns the canvas widget
    so callers can .pack()/.grid() it and later call .draw_idle() on refresh."""
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    canvas = FigureCanvasTkAgg(figure, master=parent)
    canvas.draw()
    return canvas
