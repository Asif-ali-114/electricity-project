# ⚡ WattWise — Intelligent Electricity Usage Analyzer

This is a staged build. Given the scope of the full spec (60+ feature
sections: Tkinter GUI, 10+ analysis modules, forecasting, anomaly
detection, EN/AR with full RTL, USD/SAR currency switching, PDF
reporting), it's being built in five stages so each layer is solid
before the next is built on top of it.

## Stage 1 — Foundation (this delivery)
- Project structure (`electricity_analyzer/`)
- `requirements.txt`
- `config/settings.json` — theme, language, per-language electricity
  rate, currency config, recent files, monthly goal
- `utils/currency.py` — centralized `format_currency()` / `calculate_cost()`;
  enforces EN→USD / AR→SAR only, offline fallback rate documented
- `localization/translations.py` — centralized `t(key, lang)` dictionary
  (nav, quick actions, dashboard cards, settings, months, errors)
- `data_processing/generate_sample_data.py` — generates 12 realistic
  monthly CSVs (`data/January.csv` … `December.csv`) with seasonal
  behavior (AC/fan usage peaks in summer, water-heater usage peaks in
  winter, evening/morning appliance spikes, fridge near-constant,
  washing machine as discrete sessions) plus a small number of
  intentional data-quality issues (missing cost, negative energy,
  blank appliance name) for the app's validation/cleaning features to
  demonstrate.

### Verified so far
- January Air Conditioner: 36.6 kWh vs July: 216.8 kWh (~6x, matches
  summer-cooling expectation)
- January Water Heater: 108.0 kWh vs July: 11.7 kWh (~9x, matches
  winter-heating expectation)
- Refrigerator duration correctly capped at ≤24h/day
- ~2,900–5,900 rows/month across appliances, with injected data-quality
  issues confirmed present

## Stage 2 — Data pipeline + core analytics (this delivery)
- `data_processing/loader.py` — intelligent column mapping (accepts
  header variants like "Power (W)", "Appliance Name", etc.), derives
  `Energy_kWh` when missing, supports single or multi-file loads
- `data_processing/validator.py` — `DataQualityReport` (rows, valid,
  invalid, missing values, per-issue-type breakdown)
- `data_processing/cleaner.py` — drops unrecoverable rows, fixes
  negative-energy sign errors, derives missing durations, adds
  `Month`/`Day`/`Weekday`/`Hour` helper columns, returns a human-readable
  cleaning log
- `analysis/statistics.py` — pure functions for totals, appliance
  breakdown (%, avg/day, cost, sessions, peak hour), daily/weekly/
  monthly/hourly/time-of-day breakdowns, day×hour heatmap matrix,
  period comparison
- `analysis/analyzer.py` — `Analyzer` class tying it all together
  (load → validate → clean → analyze) as the single entry point the
  GUI will call in Stage 4, plus the section-32 filter set

### Verified so far (ran against real generated data, Jan+Jul combined)
- 997 rows loaded, 4 negative-energy rows auto-corrected, 0 rows lost
- Dashboard summary: 976.51 kWh total, $136.71 at the USD rate, correct
  highest/lowest appliance, correct peak time-of-day window
- Appliance ranking, weekly/monthly/hourly/time-of-day tables, and the
  7×24 day-of-week heatmap matrix all produced consistent numbers

**Known limitation to refine in Stage 4:** week numbering is currently a
simple day-offset from the dataset's earliest date, so combining
non-contiguous months produces oddly-jumping week numbers. Fine for
single-month views; will reset per-calendar-month before the UI ships.

## Stage 3 — Intelligence layer (this delivery)
- `analysis/anomaly.py` — z-score + IQR + 7-day moving-average deviation,
  merged and attributed to the likely-cause appliance per flagged day
- `analysis/efficiency.py` — explainable 0-100 efficiency score (appliance
  concentration, evening-peak share, avg-daily-usage vs. benchmark,
  day-to-day variability, anomaly frequency), each penalty tied to a
  human-readable reason
- `analysis/prediction.py` — transparent (non-ML) next-day/week/month
  forecasts blending recent average with linear trend, always flagged
  `is_estimate: True`
- `analysis/recommendations.py` — data-driven recommendations with
  estimated monthly savings, rendered through a bilingual template table
- `analysis/simulator.py` — "What If I Reduce Usage?" simulator (current
  vs. new monthly kWh, money saved, yearly savings)
- `analysis/insights.py` — natural-language insights generated from
  live stats (top appliance share, peak window, peak weekday,
  period-over-period change, household profile), bilingual
- `localization/translations.py` — added appliance-name translations
  (`translate_appliance()`) so generated sentences read naturally in
  Arabic instead of mixing in English appliance names
- `Analyzer` extended with `.anomalies()`, `.efficiency_score()`,
  `.forecasts()`, `.recommendations()`, `.insights()`, `.what_if()`

### Verified so far (July data, English then Arabic)
- Efficiency score: 96/100, correctly explained by AC concentration (41%)
  and 2 detected anomaly days
- Anomalies: 2 days flagged (Jul 13, Jul 19), both correctly attributed
  to Air Conditioner, with z-score/IQR agreement on one of them
- Forecasts: next-month estimate (517 kWh) sensibly close to July's
  actual pace
- What-if: AC 4.66h→4h/day projects ~$4.17/month, ~$50/year savings
- Recommendations & insights render correctly in **both languages**,
  including appliance names ("Air Conditioner" → "مكيف الهواء") — caught
  and fixed a bug where Arabic sentences were leaking English appliance
  names before this was wired in

## Stage 4 — Tkinter GUI (this delivery)
- `ui/theme.py` — light/dark palettes (colors, chart palette, fonts),
  single source of truth for every color used in the app
- `ui/components.py` — `apply_ttk_style()` (themes every ttk widget via
  the 'clam' base theme so dark mode actually works), `Card`,
  `StatCard`, `NavButton`, `Badge`, `ScrollableFrame`, `section_title`
- `ui/charts.py` — all 13 chart types from spec sections 12/13-18/57
  (appliance bar/pie/cost/duration/comparison, daily line/cost, weekly/
  monthly bar, hourly line with peak marker, time-of-day donut, day×hour
  heatmap, comparison bars, forecast line) as pure Tk-independent
  `Figure` builders + a thin `embed_figure()` Tkinter wrapper, so charts
  never open a separate window (spec requirement) and are unit-testable
  headlessly
- `localization/arabic_shaping.py` — reshapes/reorders Arabic chart text
  via arabic-reshaper + python-bidi (same approach as the raqm-based PDF
  work on other projects), with a safe no-op fallback if those optional
  libs aren't installed
- Chart titles, time-of-day categories, and weekday names added to
  `localization/translations.py` (`chart_label()`) so every chart is
  fully bilingual, not just the appliance names
- `ui/sidebar.py` — 12-item nav, active-page highlighting, language/
  theme toggles, flips to the right edge with right-aligned text in
  Arabic (RTL)
- `ui/dashboard.py` — the full Dashboard page: quick actions, 8 stat
  cards, anomaly alert badge, two headline charts (appliance bar +
  time-of-day donut), live insights feed, empty-state prompt when no
  data is loaded
- `main.py` — app shell: window setup, ttk theming, CSV loading (month
  dropdown + file picker with friendly error dialogs, never a raw
  traceback), demo-mode auto-load on first launch, settings
  persistence, full theme/language switching (rebuilds the whole UI,
  including sidebar side and text alignment, on toggle)

### Verified so far
- All 13 chart builders run headlessly (no Tk needed) against real July
  data, in **both** light/dark themes and **both** languages, with zero
  errors -- confirmed via saved PNG spot-checks (bar chart, day×hour
  heatmap, dark-mode Arabic cost chart, Arabic heatmap)
- Arabic chart text renders correctly joined even via the shaping
  fallback path in this sandbox; will be even more robust with
  `arabic-reshaper`/`python-bidi` installed per `requirements.txt`
- Every `ui/*.py` and `main.py` file passes `python -m py_compile`

### Known limitation
This sandbox has no network access and can't install `python3-tk`
(confirmed: apt fetch returns 403 via the egress proxy), so the actual
Tkinter widget tree, layout, RTL flip, and click handlers in
`main.py`/`ui/sidebar.py`/`ui/dashboard.py` could **not** be visually
run or screenshot-tested here -- only syntax-checked. The 11 non-
dashboard nav pages currently render a placeholder card; their data/
analysis is fully implemented (Stages 2-3), only their dedicated views
are pending. **Please run `python main.py` locally as the first real
test of the GUI layer** and let me know what you see -- I'll fix
anything that comes up.

## Stage 5 — In progress: Reports, remaining pages, settings, final testing
### Completed so far
- `reports/report_generator.py` — full PDF report via ReportLab
  (dataset summary, overview, appliance ranking table, efficiency
  score, anomalies, forecasts, recommendations, embedded appliance-bar
  and daily-trend and time-of-day charts), fully bilingual
- `assets/fonts/FreeSerif.ttf` + `FreeSerifBold.ttf` — **bundled**
  Arabic-capable fonts (GNU FreeFont, GPL+font-exception, freely
  redistributable) with `LICENSE.txt` attribution. This was a real bug
  caught via visual QA: ReportLab's built-in PDF fonts have **zero**
  Arabic glyph coverage, so Arabic report text rendered as solid black
  boxes until this was registered. Bundled rather than relying on
  system fonts since the app must run on Windows.
- Removed emoji/medal glyphs (⚡ 🥇🥈🥉 ⚠) from PDF output entirely --
  ReportLab's fonts don't have emoji glyphs either (same black-box
  failure); replaced with plain numbers/text. Charts (matplotlib) and
  the Tkinter UI keep emoji since those render fine there.
- Refactored `analysis/efficiency.py` to return structured
  `(reason_key, params)` tuples instead of hardcoded English sentences,
  with a new `format_efficiency_reason()` bilingual renderer -- another
  real gap caught by visual QA (reasons were leaking English into
  Arabic reports)
- Fixed peak-usage-window ("Afternoon"/"Evening" etc.) not being
  translated in both the report and the Stage-4 dashboard card

### Verified so far
- Generated **real PDF files** (not just code) and visually inspected
  every page via `pdftoppm` PNG conversion, in both languages -- this
  is how the font and translation bugs above were actually caught
- English report: clean layout, correct currency, correct ranking
- Arabic report: correctly shaped/joined Arabic text, right-aligned
  headings, translated field labels, translated efficiency reasons,
  Riyal symbol renders correctly (glyph confirmed present in the
  bundled font), no black-box glyphs anywhere

### Still to do in Stage 5
- Dedicated views for the 11 placeholder nav pages (Data Explorer with
  full filters, Appliance/Daily/Weekly/Monthly/Hourly Analysis tables,
  Comparisons, Insights, Recommendations + What-If simulator UI,
  Reports page with a "Generate PDF" button wired to
  `report_generator.py`, Settings page)
- Settings page wiring (electricity rate input, data directory picker,
  reset)
- Final testing checklist pass (spec section 63)

## Coming next
- Remaining Stage 5 items above

## Running (once complete)
```
pip install -r requirements.txt
python main.py
```

## Regenerating sample data
```
python data_processing/generate_sample_data.py
```
