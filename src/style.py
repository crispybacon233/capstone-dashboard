import streamlit as st


def apply_dashboard_style() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

        :root {
            --brand-ink: #e6eef8;
            --brand-blue: #6fb3d8;
            --brand-cyan: #54c2d3;
            --accent-amber: #f0c36d;
            --surface-0: #0b1118;
            --surface-1: #121a24;
            --surface-2: #1a2431;
            --text-main: #dbe6f4;
            --text-subtle: #95a8bf;
            --border-soft: #2b3a4d;
            --shadow-soft: 0 10px 24px rgba(0, 0, 0, 0.35);
            --radius-md: 14px;
            --radius-sm: 10px;
        }

        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(1000px 380px at 88% -6%, rgba(84, 194, 211, 0.16) 0%, rgba(84, 194, 211, 0) 60%),
                radial-gradient(900px 360px at -6% 18%, rgba(111, 179, 216, 0.14) 0%, rgba(111, 179, 216, 0) 62%),
                linear-gradient(180deg, var(--surface-0) 0%, #0a1118 100%);
        }

        .stApp, .stMarkdown, .stText, p, li, label, [data-testid="stMetricValue"] {
            font-family: 'IBM Plex Sans', 'Source Sans Pro', sans-serif;
            color: var(--text-main);
        }

        h1, h2, h3, h4 {
            font-family: 'Space Grotesk', 'Segoe UI', sans-serif;
            letter-spacing: -0.01em;
            color: var(--brand-ink);
        }

        [data-testid="block-container"] {
            padding-top: 1.25rem;
            padding-bottom: 1.5rem;
            max-width: 1500px;
        }

        .hero-wrap {
            background: linear-gradient(135deg, rgba(19, 31, 44, 0.95) 0%, rgba(17, 26, 37, 0.95) 100%);
            border: 1px solid var(--border-soft);
            border-radius: var(--radius-md);
            box-shadow: var(--shadow-soft);
            padding: 1rem 1.2rem;
            margin-bottom: 0.85rem;
        }

        .hero-title {
            font-size: 1.45rem;
            font-weight: 700;
            margin: 0;
            color: var(--brand-ink);
        }

        .hero-subtitle {
            margin-top: 0.25rem;
            margin-bottom: 0;
            color: var(--text-subtle);
            font-size: 0.95rem;
        }

        .hero-meta-card {
            border: 1px solid var(--border-soft);
            border-radius: var(--radius-sm);
            background: var(--surface-1);
            padding: 0.75rem 0.9rem;
            text-align: right;
        }

        .state-badge {
            display: inline-block;
            padding: 0.2rem 0.55rem;
            border-radius: 999px;
            background: rgba(84, 194, 211, 0.12);
            color: var(--brand-blue);
            border: 1px solid rgba(84, 194, 211, 0.35);
            font-size: 0.78rem;
            font-weight: 600;
            letter-spacing: 0.03em;
            text-transform: uppercase;
            margin-bottom: 0.35rem;
        }

        .meta-title {
            font-size: 0.76rem;
            font-weight: 600;
            color: var(--text-subtle);
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 0.2rem;
        }

        .meta-value {
            font-size: 0.98rem;
            font-weight: 600;
            color: var(--brand-ink);
        }

        .kpi-card {
            background: var(--surface-1);
            border: 1px solid var(--border-soft);
            border-radius: var(--radius-sm);
            box-shadow: var(--shadow-soft);
            padding: 0.85rem 0.9rem;
            min-height: 88px;
        }

        .kpi-label {
            font-size: 0.78rem;
            font-weight: 600;
            color: var(--text-subtle);
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 0.35rem;
        }

        .kpi-value {
            font-size: 1.45rem;
            line-height: 1.15;
            font-weight: 700;
            color: var(--brand-ink);
        }

        .chip-row {
            margin-top: 0.35rem;
            margin-bottom: 0.65rem;
        }

        .filter-chip {
            display: inline-block;
            margin-right: 0.45rem;
            margin-bottom: 0.45rem;
            padding: 0.26rem 0.6rem;
            border-radius: 999px;
            background: rgba(84, 194, 211, 0.12);
            border: 1px solid rgba(111, 179, 216, 0.35);
            color: #b9d9ee;
            font-size: 0.78rem;
            font-weight: 600;
        }

        .selection-cta {
            border: 1px dashed rgba(111, 179, 216, 0.45);
            background: rgba(22, 35, 49, 0.8);
            border-radius: var(--radius-sm);
            padding: 0.9rem 1rem;
            margin-top: 0.4rem;
            margin-bottom: 0.35rem;
        }

        .selection-cta h4 {
            margin: 0 0 0.2rem 0;
            font-size: 1rem;
            color: #c6e3f5;
        }

        .selection-cta p {
            margin: 0;
            color: var(--text-subtle);
            font-size: 0.9rem;
        }

        .panel-card {
            background: var(--surface-1);
            border: 1px solid var(--border-soft);
            border-radius: var(--radius-sm);
            box-shadow: var(--shadow-soft);
            padding: 0.8rem;
            margin-bottom: 0.8rem;
        }

        .panel-title {
            font-size: 0.95rem;
            font-weight: 700;
            color: var(--brand-ink);
            margin: 0 0 0.4rem 0;
        }

        [data-baseweb="tab-list"] {
            gap: 0.35rem;
        }

        [data-baseweb="tab"] {
            border: 1px solid var(--border-soft);
            border-radius: 999px;
            padding: 0.35rem 0.8rem;
            background: rgba(24, 37, 52, 0.9);
            color: var(--text-subtle);
            font-weight: 600;
        }

        [aria-selected="true"][data-baseweb="tab"] {
            background: rgba(84, 194, 211, 0.16);
            border-color: rgba(111, 179, 216, 0.6);
            color: #d9eefb;
        }

        .helper-text {
            color: var(--text-subtle);
            font-size: 0.86rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_plotly_layout_defaults() -> dict:
    return {
        "template": "plotly_dark",
        "paper_bgcolor": "rgba(0, 0, 0, 0)",
        "plot_bgcolor": "rgba(0, 0, 0, 0)",
        "font": {
            "family": "IBM Plex Sans, Source Sans Pro, sans-serif",
            "size": 13,
            "color": "#dbe6f4",
        },
        "margin": {"l": 34, "r": 18, "t": 42, "b": 34},
        "legend": {"orientation": "h", "yanchor": "bottom", "y": 1.01, "xanchor": "right", "x": 1.0},
        "hoverlabel": {
            "bgcolor": "#101820",
            "bordercolor": "#2b3a4d",
            "font": {"family": "IBM Plex Sans, Source Sans Pro, sans-serif"},
        },
    }
