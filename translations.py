"""
localization/translations.py

Centralized EN/AR translation dictionary for WattWise.
Every user-facing string in the app must be looked up through t(key, lang)
so nothing is ever hard-coded in English inside the UI layer.

Arabic strings are stored in logical (not visually reshaped) order.
The UI layer is responsible for applying arabic-reshaper + python-bidi
before rendering, and for switching the layout direction to RTL.
"""

from __future__ import annotations

translations: dict[str, dict[str, str]] = {
    "en": {
        # App
        "app_title": "WattWise — Intelligent Electricity Usage Analyzer",

        # Sidebar navigation
        "nav_dashboard": "Dashboard",
        "nav_data_explorer": "Data Explorer",
        "nav_appliance_analysis": "Appliance Analysis",
        "nav_daily_analysis": "Daily Analysis",
        "nav_weekly_analysis": "Weekly Analysis",
        "nav_monthly_analysis": "Monthly Analysis",
        "nav_hourly_analysis": "Hourly Analysis",
        "nav_comparisons": "Comparisons",
        "nav_insights": "Insights",
        "nav_recommendations": "Recommendations",
        "nav_reports": "Reports",
        "nav_settings": "Settings",

        # Quick actions
        "action_load_csv": "＋ Load CSV",
        "action_load_custom_csv": "＋ Load Custom CSV",
        "action_analyze_data": "📊 Analyze Data",
        "action_monthly_analysis": "📅 Monthly Analysis",
        "action_appliance_usage": "⚡ Appliance Usage",
        "action_trends": "📈 Trends",
        "action_recommendations": "💡 Recommendations",
        "action_generate_report": "📄 Generate Report",
        "action_settings": "⚙ Settings",

        # Dashboard cards
        "card_total_energy": "Total Energy",
        "card_estimated_cost": "Estimated Cost",
        "card_avg_daily_usage": "Average Daily Usage",
        "card_peak_usage": "Peak Usage",
        "card_highest_appliance": "Highest-Consuming Appliance",
        "card_lowest_appliance": "Lowest-Consuming Appliance",
        "card_efficiency_score": "Efficiency Score",
        "card_potential_savings": "Potential Savings",

        # Settings
        "settings_appearance": "Appearance",
        "settings_light_mode": "Light Mode",
        "settings_dark_mode": "Dark Mode",
        "settings_language": "Language",
        "settings_currency": "Currency",
        "settings_electricity_rate": "Electricity Rate",
        "settings_data_directory": "Data Directory",
        "settings_reset": "Reset Settings",

        # Month names
        "month_1": "January", "month_2": "February", "month_3": "March",
        "month_4": "April", "month_5": "May", "month_6": "June",
        "month_7": "July", "month_8": "August", "month_9": "September",
        "month_10": "October", "month_11": "November", "month_12": "December",

        # Appliances
        "appliance_Air Conditioner": "Air Conditioner",
        "appliance_Electric Fan": "Electric Fan",
        "appliance_Water Heater": "Water Heater",
        "appliance_Refrigerator": "Refrigerator",
        "appliance_Television": "Television",
        "appliance_Lights": "Lights",
        "appliance_Washing Machine": "Washing Machine",
        "appliance_Water Pump": "Water Pump",
        "appliance_Microwave": "Microwave",
        "appliance_Electric Oven": "Electric Oven",
        "appliance_Computer": "Computer",
        "appliance_Laptop": "Laptop",
        "appliance_Iron": "Iron",
        "appliance_Kitchen Appliances": "Kitchen Appliances",
        "appliance_Other Appliances": "Other Appliances",

        # Errors / notifications
        "error_empty_csv": "The selected file is empty.",
        "error_missing_columns": "This file is missing required columns.",
        "error_invalid_data": "Some rows contain invalid data and were skipped.",
        "error_file_not_found": "The file could not be found.",
        "info_data_loaded": "Data loaded successfully.",
    },
    "ar": {
        # App
        "app_title": "واط وايز — محلل استهلاك الكهرباء الذكي",

        # Sidebar navigation
        "nav_dashboard": "لوحة التحكم",
        "nav_data_explorer": "مستكشف البيانات",
        "nav_appliance_analysis": "تحليل الأجهزة",
        "nav_daily_analysis": "التحليل اليومي",
        "nav_weekly_analysis": "التحليل الأسبوعي",
        "nav_monthly_analysis": "التحليل الشهري",
        "nav_hourly_analysis": "التحليل بالساعة",
        "nav_comparisons": "المقارنات",
        "nav_insights": "الرؤى الذكية",
        "nav_recommendations": "التوصيات",
        "nav_reports": "التقارير",
        "nav_settings": "الإعدادات",

        # Quick actions
        "action_load_csv": "＋ تحميل ملف CSV",
        "action_load_custom_csv": "＋ تحميل ملف مخصص",
        "action_analyze_data": "📊 تحليل البيانات",
        "action_monthly_analysis": "📅 التحليل الشهري",
        "action_appliance_usage": "⚡ استخدام الأجهزة",
        "action_trends": "📈 الاتجاهات",
        "action_recommendations": "💡 التوصيات",
        "action_generate_report": "📄 إنشاء تقرير",
        "action_settings": "⚙ الإعدادات",

        # Dashboard cards
        "card_total_energy": "إجمالي الطاقة",
        "card_estimated_cost": "التكلفة المقدرة",
        "card_avg_daily_usage": "متوسط الاستخدام اليومي",
        "card_peak_usage": "ذروة الاستخدام",
        "card_highest_appliance": "الجهاز الأعلى استهلاكاً",
        "card_lowest_appliance": "الجهاز الأقل استهلاكاً",
        "card_efficiency_score": "درجة الكفاءة",
        "card_potential_savings": "التوفير المحتمل",

        # Settings
        "settings_appearance": "المظهر",
        "settings_light_mode": "الوضع الفاتح",
        "settings_dark_mode": "الوضع الداكن",
        "settings_language": "اللغة",
        "settings_currency": "العملة",
        "settings_electricity_rate": "سعر الكهرباء",
        "settings_data_directory": "مجلد البيانات",
        "settings_reset": "إعادة تعيين الإعدادات",

        # Month names
        "month_1": "يناير", "month_2": "فبراير", "month_3": "مارس",
        "month_4": "أبريل", "month_5": "مايو", "month_6": "يونيو",
        "month_7": "يوليو", "month_8": "أغسطس", "month_9": "سبتمبر",
        "month_10": "أكتوبر", "month_11": "نوفمبر", "month_12": "ديسمبر",

        # Appliances
        "appliance_Air Conditioner": "مكيف الهواء",
        "appliance_Electric Fan": "مروحة كهربائية",
        "appliance_Water Heater": "سخان الماء",
        "appliance_Refrigerator": "الثلاجة",
        "appliance_Television": "التلفاز",
        "appliance_Lights": "الإضاءة",
        "appliance_Washing Machine": "الغسالة",
        "appliance_Water Pump": "مضخة الماء",
        "appliance_Microwave": "الميكروويف",
        "appliance_Electric Oven": "الفرن الكهربائي",
        "appliance_Computer": "الحاسوب",
        "appliance_Laptop": "الحاسوب المحمول",
        "appliance_Iron": "المكواة",
        "appliance_Kitchen Appliances": "أجهزة المطبخ",
        "appliance_Other Appliances": "أجهزة أخرى",

        # Errors / notifications
        "error_empty_csv": "الملف المحدد فارغ.",
        "error_missing_columns": "هذا الملف يفتقد إلى أعمدة مطلوبة.",
        "error_invalid_data": "بعض الصفوف تحتوي على بيانات غير صالحة وتم تجاهلها.",
        "error_file_not_found": "تعذر العثور على الملف.",
        "info_data_loaded": "تم تحميل البيانات بنجاح.",
    },
}


def t(key: str, language: str = "en") -> str:
    """Look up a translated string. Falls back to English, then to the key itself."""
    lang_dict = translations.get(language, translations["en"])
    return lang_dict.get(key, translations["en"].get(key, key))


def translate_appliance(name: str, language: str) -> str:
    """Translate a raw appliance name (as it appears in CSV data) into the
    active language. Unknown/custom appliance names pass through unchanged,
    since user-uploaded CSVs can contain arbitrary appliance labels."""
    return t(f"appliance_{name}", language) if f"appliance_{name}" in translations.get(language, {}) else name


def is_rtl(language: str) -> bool:
    return language == "ar"


# Chart titles and time-of-day category labels used specifically by ui/charts.py
CHART_LABELS = {
    "en": {
        "chart_appliance_consumption": "Appliance Consumption",
        "chart_appliance_contribution": "Appliance Contribution",
        "chart_appliance_cost": "Appliance Cost",
        "chart_appliance_duration": "Appliance Duration",
        "chart_appliance_comparison": "Appliance Comparison",
        "chart_daily_consumption": "Daily Consumption",
        "chart_daily_cost": "Daily Cost",
        "chart_weekly_consumption": "Weekly Consumption",
        "chart_monthly_consumption": "Monthly Consumption",
        "chart_hourly_consumption": "Hourly Consumption",
        "chart_time_of_day": "Time-of-Day Usage",
        "chart_heatmap": "Usage Heatmap (Day x Hour)",
        "chart_forecast": "Forecast",
        "chart_comparison": "Comparison",
        "tod_Night": "Night",
        "tod_Morning": "Morning",
        "tod_Afternoon": "Afternoon",
        "tod_Evening": "Evening",
        "tod_Late Night": "Late Night",
        "weekday_Monday": "Monday", "weekday_Tuesday": "Tuesday", "weekday_Wednesday": "Wednesday",
        "weekday_Thursday": "Thursday", "weekday_Friday": "Friday", "weekday_Saturday": "Saturday",
        "weekday_Sunday": "Sunday",
        "series_historical": "Historical",
        "series_forecast": "Forecast",
    },
    "ar": {
        "chart_appliance_consumption": "استهلاك الأجهزة",
        "chart_appliance_contribution": "مساهمة الأجهزة",
        "chart_appliance_cost": "تكلفة الأجهزة",
        "chart_appliance_duration": "مدة تشغيل الأجهزة",
        "chart_appliance_comparison": "مقارنة الأجهزة",
        "chart_daily_consumption": "الاستهلاك اليومي",
        "chart_daily_cost": "التكلفة اليومية",
        "chart_weekly_consumption": "الاستهلاك الأسبوعي",
        "chart_monthly_consumption": "الاستهلاك الشهري",
        "chart_hourly_consumption": "الاستهلاك بالساعة",
        "chart_time_of_day": "الاستهلاك حسب وقت اليوم",
        "chart_heatmap": "خريطة الاستهلاك الحرارية (اليوم × الساعة)",
        "chart_forecast": "التوقعات",
        "chart_comparison": "مقارنة",
        "tod_Night": "الليل",
        "tod_Morning": "الصباح",
        "tod_Afternoon": "بعد الظهر",
        "tod_Evening": "المساء",
        "tod_Late Night": "آخر الليل",
        "weekday_Monday": "الإثنين", "weekday_Tuesday": "الثلاثاء", "weekday_Wednesday": "الأربعاء",
        "weekday_Thursday": "الخميس", "weekday_Friday": "الجمعة", "weekday_Saturday": "السبت",
        "weekday_Sunday": "الأحد",
        "series_historical": "بيانات سابقة",
        "series_forecast": "توقع",
    },
}


def chart_label(key: str, language: str = "en") -> str:
    """Look up a chart-specific label (title, category, series name)."""
    lang_dict = CHART_LABELS.get(language, CHART_LABELS["en"])
    return lang_dict.get(key, CHART_LABELS["en"].get(key, key))
