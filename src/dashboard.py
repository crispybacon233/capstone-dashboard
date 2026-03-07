import glob
import os
import time
from typing import Iterable

import certifi
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import polars as pl
import streamlit as st
from openai import OpenAI
from plotly.subplots import make_subplots

from src.city_config import CityConfig
from src.keywords import load_keyword_data
from src.style import apply_dashboard_style, get_plotly_layout_defaults


MODEL = "gpt-4.1-mini-2025-04-14"
ESTABLISHMENTS_PATH = "data/all/all_establishments.parquet"
REVIEWS_GLOB = "data/all/reviews/*.parquet"
FILTER_DEFAULT_RATING_RANGE = (1.0, 5.0)
ABSOLUTE_RATING_COLOR_SCALE = [
    [0.00, "#b2182b"],
    [0.25, "#ef8a62"],
    [0.50, "#fee08b"],
    [0.75, "#66bd63"],
    [1.00, "#1a9850"],
]


def _apply_plotly_defaults(fig: go.Figure) -> go.Figure:
    fig.update_layout(**get_plotly_layout_defaults())
    fig.update_xaxes(showline=True, linecolor="#2f4155", gridcolor="#263648")
    fig.update_yaxes(showline=True, linecolor="#2f4155", gridcolor="#263648")
    return fig


def _build_patterns(word_pairs: list[tuple[str, str]]) -> list[str]:
    return [rf"\b{word1}\b.*\b{word2}\b" for word1, word2 in word_pairs]


@st.cache_data(show_spinner=False)
def _load_categories(state: str) -> list[str]:
    query = """
    WITH category_counts AS (
        SELECT
            category,
            COUNT(category) AS count
        FROM read_parquet('data/all/all_establishments.parquet')
        WHERE state = ?
        GROUP BY category
    )
    SELECT DISTINCT category
    FROM category_counts
    WHERE count >= 50
    ORDER BY category ASC
    """
    with duckdb.connect() as con:
        rows = con.execute(query, [state]).fetchall()
    return [row[0] for row in rows if row[0] is not None]


@st.cache_resource(show_spinner=False)
def _get_openai_client() -> OpenAI | None:
    os.environ["SSL_CERT_FILE"] = certifi.where()
    try:
        openai_key = st.secrets["openai_key"]
    except Exception:
        return None

    if not openai_key:
        return None

    return OpenAI(api_key=openai_key)


def _load_data() -> tuple[pl.LazyFrame, pl.LazyFrame]:
    review_paths = glob.glob(REVIEWS_GLOB)
    if not review_paths:
        raise FileNotFoundError(f"No review parquet files found using: {REVIEWS_GLOB}")

    establishments = pl.scan_parquet(ESTABLISHMENTS_PATH)
    reviews = pl.concat([pl.scan_parquet(path) for path in review_paths])
    return establishments, reviews


def _stream_llm_completion(client: OpenAI, prompt: str) -> Iterable[str]:
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are an authority on food and beverage establishments. Help me anaylze review texts.",
            },
            {"role": "user", "content": prompt},
        ],
        stream=True,
    )

    for chunk in completion:
        if hasattr(chunk.choices[0].delta, "content"):
            content = chunk.choices[0].delta.content
            if content is not None:
                yield content
                time.sleep(0.02)


def _single_query_llm(client: OpenAI, review_str: str) -> Iterable[str]:
    prompt = f"""
    Tell me the strengths and weaknesses of this places.
    Give a analysis of what customers like and dislike: {review_str}.
    """
    return _stream_llm_completion(client, prompt)


def _query_llm(client: OpenAI, review_str: str) -> Iterable[str]:
    prompt = f"""
    Tell me the strengths and weaknesses of these places. Don't mention specific places.
    Give a general analysis of what customers like and dislike: {review_str}.
    Then tell me the speicifc best place by name and why it's the best. Then the specific worst place by name and why it's the worst.
    Then tell me the best strategy to exploit the weaknesses of these places such that I can open my own place nearby and be successful.
    """
    return _stream_llm_completion(client, prompt)


def _selected_point_indices(map_selection: object) -> list[int]:
    selection = getattr(map_selection, "selection", None)
    if not selection:
        return []
    point_indices = selection.get("point_indices", [])
    return point_indices or []


def _load_filtered_reviews(reviews: pl.LazyFrame, facility_ids: list[str]) -> pd.DataFrame:
    if not facility_ids:
        return pd.DataFrame(columns=["facility_id", "text", "rating"])

    return (
        reviews.filter(pl.col("facility_id").is_in(facility_ids))
        .filter(pl.col("text").is_not_null())
        .select("facility_id", "text", "rating")
        .collect()
        .to_pandas()
    )


def _build_concise_reviews(
    reviews: pl.LazyFrame,
    establishments: pl.LazyFrame,
    facility_ids: list[str],
    patterns: list[str],
) -> pl.DataFrame:
    if not facility_ids or not patterns:
        return pl.DataFrame()

    pattern_count_exprs = [
        pl.col("text").str.count_matches(pattern, literal=False) for pattern in patterns
    ]

    return (
        reviews.join(
            establishments.select("facility_id", "restaurant_name", "average_rating"),
            on="facility_id",
        )
        .filter(pl.col("facility_id").is_in(facility_ids))
        .filter(pl.col("text").is_not_null())
        .head(100000)
        .with_columns(pl.sum_horizontal(pattern_count_exprs).alias("match_count"))
        .with_columns(
            (pl.col("match_count") / pl.col("text").str.len_chars()).alias("match_ratio")
        )
        .filter(pl.col("match_count") > 0)
        .sort(by="match_ratio", descending=True)
        .collect()
        .unique(["facility_id", "text", "timestamp", "rating"])
    )


def _build_reviews_prompt_text(tab_reviews: pl.DataFrame) -> str:
    if tab_reviews.height == 0:
        return ""

    primary = (
        tab_reviews.filter(pl.col("match_ratio").is_between(0.001, 0.01))
        .with_columns(
            reviews_str=pl.concat_str(
                [pl.col("restaurant_name"), pl.col("text")], separator="\n"
            )
        )
        .sort(by="rating")
        .unique()
        .head(700)
    )

    if primary.height >= 700:
        selected = primary
    else:
        selected = (
            tab_reviews.filter(pl.col("match_ratio").is_between(0.0001, 0.50))
            .with_columns(
                reviews_str=pl.concat_str(
                    [pl.col("restaurant_name"), pl.col("text")], separator="\n"
                )
            )
            .sort(by="rating")
            .unique()
            .head(700)
        )

    if selected.height == 0:
        return ""

    return "\n\n".join(selected.get_column("reviews_str").to_list())


def _compute_kpis(
    filtered_map_df: pd.DataFrame, selected_fac_ids: list[str]
) -> dict[str, float | int]:
    if filtered_map_df.empty:
        return {
            "visible_count": 0,
            "selected_count": 0,
            "avg_rating": 0.0,
            "median_reviews": 0,
        }

    visible_count = int(filtered_map_df["facility_id"].nunique())
    selected_count = int(len(selected_fac_ids))
    avg_rating = float(filtered_map_df["average_rating"].mean())
    median_reviews = int(filtered_map_df["n_reviews"].fillna(0).median())

    return {
        "visible_count": visible_count,
        "selected_count": selected_count,
        "avg_rating": avg_rating,
        "median_reviews": median_reviews,
    }


@st.cache_data(show_spinner=False)
def _build_rating_distribution(filtered_map_df: pd.DataFrame) -> pd.DataFrame:
    if filtered_map_df.empty:
        return pd.DataFrame(columns=["average_rating"])

    return filtered_map_df[["average_rating"]].dropna().copy()


@st.cache_data(show_spinner=False)
def _build_top_categories(
    filtered_map_df: pd.DataFrame, limit: int = 10
) -> pd.DataFrame:
    if filtered_map_df.empty:
        return pd.DataFrame(columns=["category", "est_count", "avg_rating"])

    category_df = filtered_map_df.copy()
    category_df["category"] = category_df["category"].fillna("Unknown")
    top_categories = (
        category_df.groupby("category", as_index=False)
        .agg(est_count=("facility_id", "nunique"), avg_rating=("average_rating", "mean"))
        .sort_values(["est_count", "avg_rating"], ascending=[False, False])
        .head(limit)
    )
    return top_categories


def _build_monthly_metrics(
    state_establishments: pl.LazyFrame, reviews: pl.LazyFrame, fac_ids: list[str]
) -> pl.DataFrame:
    metrics_frame = (
        state_establishments.select("facility_id")
        .join(reviews, on="facility_id")
        .with_columns(pl.col("timestamp").cast(pl.Datetime("us")).alias("review_dt"))
        .filter(pl.col("review_dt").is_not_null())
    )

    if fac_ids:
        metrics_frame = metrics_frame.filter(pl.col("facility_id").is_in(fac_ids))

    return (
        metrics_frame.filter(pl.col("review_dt").dt.year() >= 2020)
        .with_columns(pl.col("review_dt").dt.strftime("%Y-%m").alias("year_month"))
        .group_by("year_month")
        .agg(
            pl.col("rating").mean().alias("monthly_rating"),
            pl.len().alias("review_count"),
        )
        .sort(by="year_month")
        .with_columns(pl.col("monthly_rating").rolling_mean(window_size=6).alias("rolling_mean"))
        .collect()
    )


def _render_kpi_cards(kpis: dict[str, float | int]) -> None:
    kpi_cols = st.columns(4)
    card_values = [
        ("Establishments visible", f"{int(kpis['visible_count']):,}"),
        ("Establishments selected", f"{int(kpis['selected_count']):,}"),
        ("Average rating", f"{float(kpis['avg_rating']):.2f}"),
        ("Median total reviews", f"{int(kpis['median_reviews']):,}"),
    ]

    for col, (label, value) in zip(kpi_cols, card_values):
        with col:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _render_active_filter_chips(chips: list[str]) -> None:
    if not chips:
        return

    chip_html = "".join([f'<span class="filter-chip">{chip}</span>' for chip in chips])
    st.markdown(f'<div class="chip-row">{chip_html}</div>', unsafe_allow_html=True)


def _render_selection_cta() -> None:
    st.markdown(
        """
        <div class="selection-cta">
            <h4>Select one or more venues in the Dashboard tab</h4>
            <p>Use click, box, or lasso selection on the map. Reviews and Deep Insights run only on selected venues.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _prepare_filter_keys(config: CityConfig) -> dict[str, str]:
    prefix = f"{config.slug}_filters"
    return {
        "categories": f"{prefix}_categories",
        "rating_range": f"{prefix}_rating_range",
        "min_reviews": f"{prefix}_min_reviews",
        "reset": f"{prefix}_reset",
    }


def _reset_filter_state(filter_keys: dict[str, str]) -> None:
    for state_key in (
        filter_keys["categories"],
        filter_keys["rating_range"],
        filter_keys["min_reviews"],
    ):
        if state_key in st.session_state:
            del st.session_state[state_key]


def render_city_dashboard(config: CityConfig) -> None:
    apply_dashboard_style()
    _, word_pairs = load_keyword_data()
    patterns = _build_patterns(word_pairs)

    establishments, reviews = _load_data()
    state_establishments = (
        establishments.join(
            reviews.select("facility_id").unique(), on="facility_id", how="semi"
        ).filter(
            (pl.col("state") == config.state)
            & (pl.col("longitude").is_not_null())
            & (pl.col("average_rating").is_not_null())
        )
    )

    raw_map_df = state_establishments.collect().to_pandas()
    if raw_map_df.empty:
        st.warning("No establishments available for this state.")
        return

    raw_map_df["n_reviews"] = raw_map_df["n_reviews"].fillna(0)
    all_categories = _load_categories(config.state)
    category_options = sorted(all_categories)

    filter_keys = _prepare_filter_keys(config)
    max_reviews = int(raw_map_df["n_reviews"].max()) if not raw_map_df.empty else 0
    defaults = {
        filter_keys["categories"]: [],
        filter_keys["rating_range"]: FILTER_DEFAULT_RATING_RANGE,
        filter_keys["min_reviews"]: 0,
    }

    for state_key, default_value in defaults.items():
        if state_key not in st.session_state:
            st.session_state[state_key] = default_value

    hero_left, hero_right = st.columns([8, 4], vertical_alignment="center")
    with hero_left:
        st.markdown(
            f"""
            <div class="hero-wrap">
                <p class="hero-title">Dishing Out Data</p>
                <p class="hero-subtitle">Explore restaurant performance across {config.title} with interactive map-first analysis.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with hero_right:
        st.markdown(
            f"""
            <div class="hero-meta-card">
                <span class="state-badge">{config.state}</span>
                <div class="meta-title">Data scope</div>
                <div class="meta-value">State-level filter</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    controls_col, helper_col = st.columns([2, 4], vertical_alignment="center")
    with controls_col:
        with st.popover("Filters", use_container_width=True):
            st.markdown("#### Category filters")

            st.multiselect(
                "Categories",
                options=category_options,
                key=filter_keys["categories"],
                placeholder="All categories",
            )

            st.markdown("#### Quality filters")
            st.slider(
                "Average rating range",
                min_value=1.0,
                max_value=5.0,
                step=0.1,
                key=filter_keys["rating_range"],
            )
            st.slider(
                "Minimum total reviews",
                min_value=0,
                max_value=max(max_reviews, 0),
                step=10 if max_reviews >= 100 else 1,
                key=filter_keys["min_reviews"],
            )

            st.button(
                "Reset filters",
                key=filter_keys["reset"],
                use_container_width=True,
                on_click=_reset_filter_state,
                kwargs={"filter_keys": filter_keys},
            )

    with helper_col:
        st.markdown(
            '<p class="helper-text">Use the filter popover to refine the market, then use the Dashboard tab map selection to unlock Reviews and Deep Insights.</p>',
            unsafe_allow_html=True,
        )

    selected_categories = list(st.session_state[filter_keys["categories"]])
    rating_min, rating_max = st.session_state[filter_keys["rating_range"]]
    min_reviews = int(st.session_state[filter_keys["min_reviews"]])

    filtered_map_df = raw_map_df.copy()
    if selected_categories:
        filtered_map_df = filtered_map_df[filtered_map_df["category"].isin(selected_categories)]
    filtered_map_df = filtered_map_df[
        filtered_map_df["average_rating"].between(rating_min, rating_max)
    ]
    filtered_map_df = filtered_map_df[filtered_map_df["n_reviews"] >= min_reviews]

    active_filters: list[str] = []
    if selected_categories:
        active_filters.append(f"Categories: {len(selected_categories)} selected")
    if (rating_min, rating_max) != FILTER_DEFAULT_RATING_RANGE:
        active_filters.append(f"Rating: {rating_min:.1f} to {rating_max:.1f}")
    if min_reviews > 0:
        active_filters.append(f"Min reviews: {min_reviews:,}")

    _render_active_filter_chips(active_filters)
    dashboard_tab, trends_tab, reviews_tab, insights_tab = st.tabs(
        ["Dashboard", "Trends", "Reviews", "Deep Insights"]
    )

    selected_fac_ids: list[str] = []
    with dashboard_tab:
        kpi_placeholder = st.container()
        map_col, snapshot_col = st.columns([8, 4], gap="large")
        selected_indices: list[int] = []

        with map_col:
            if filtered_map_df.empty:
                st.warning("No establishments match the current filters. Try widening your filter range.")
            else:
                map_fig = px.scatter_map(
                    data_frame=filtered_map_df,
                    lat="latitude",
                    lon="longitude",
                    zoom=config.default_zoom,
                    center={
                        "lat": config.default_center_lat,
                        "lon": config.default_center_lon,
                    },
                    color="average_rating",
                    color_continuous_scale=ABSOLUTE_RATING_COLOR_SCALE,
                    range_color=[1.0, 5.0],
                    opacity=0.72,
                    map_style="carto-darkmatter",
                    hover_name="restaurant_name",
                    custom_data=["restaurant_name", "average_rating", "n_reviews", "category"],
                )
                map_fig.update_traces(
                    hovertemplate=(
                        "%{customdata[0]}<br>"
                        "Avg rating: %{customdata[1]:.2f}<br>"
                        "Total reviews: %{customdata[2]:,.0f}<br>"
                        "Category: %{customdata[3]}<extra></extra>"
                    ),
                    marker={"size": 8},
                )
                _apply_plotly_defaults(map_fig)
                map_fig.update_layout(height=760)
                map_fig.update_coloraxes(showscale=False)

                map_selection = st.plotly_chart(
                    map_fig,
                    on_select="rerun",
                    use_container_width=True,
                )
                selected_indices = _selected_point_indices(map_selection)
                if selected_indices:
                    selected_fac_ids = (
                        filtered_map_df.iloc[selected_indices]["facility_id"].dropna().unique().tolist()
                    )

        with snapshot_col:
            st.markdown('<div class="panel-card" style="visibility: hidden;">', unsafe_allow_html=True)
            st.markdown('<p class="panel-title">Market snapshot</p>', unsafe_allow_html=True)

            rating_distribution_df = _build_rating_distribution(filtered_map_df)
            if rating_distribution_df.empty:
                st.info("No rating data for current filters.")
            else:
                hist_fig = px.histogram(
                    rating_distribution_df,
                    x="average_rating",
                    nbins=24,
                    labels={"average_rating": "Average rating"},
                )
                hist_fig.update_traces(marker_color="#54c2d3", opacity=0.88)
                _apply_plotly_defaults(hist_fig)
                hist_fig.update_layout(height=260, title_text="Rating distribution")
                st.plotly_chart(hist_fig, use_container_width=True)

            top_categories_df = _build_top_categories(filtered_map_df, limit=10)
            if top_categories_df.empty:
                st.info("No category data for current filters.")
            else:
                category_fig = px.bar(
                    top_categories_df.sort_values("est_count", ascending=True),
                    x="est_count",
                    y="category",
                    orientation="h",
                    color="avg_rating",
                    color_continuous_scale="Tealgrn",
                    labels={
                        "est_count": "Venues",
                        "category": "Category",
                        "avg_rating": "Avg rating",
                    },
                )
                _apply_plotly_defaults(category_fig)
                category_fig.update_layout(height=360, title_text="Top categories by venue count")
                st.plotly_chart(category_fig, use_container_width=True)

            st.markdown("</div>", unsafe_allow_html=True)

        kpis = _compute_kpis(filtered_map_df, selected_fac_ids)
        with kpi_placeholder:
            _render_kpi_cards(kpis)

    scoped_fac_ids = (
        selected_fac_ids
        if selected_fac_ids
        else filtered_map_df["facility_id"].dropna().unique().tolist()
    )

    with trends_tab:
        monthly_metrics = _build_monthly_metrics(state_establishments, reviews, scoped_fac_ids)
        if monthly_metrics.height == 0:
            st.info("No monthly review trend available for the current scope.")
        else:
            trend_df = monthly_metrics.to_pandas()
            trend_fig = make_subplots(specs=[[{"secondary_y": True}]])
            trend_fig.add_trace(
                go.Bar(
                    x=trend_df["year_month"],
                    y=trend_df["review_count"],
                    name="Review volume",
                    marker_color="#4f7fa1",
                    opacity=0.5,
                ),
                secondary_y=True,
            )
            trend_fig.add_trace(
                go.Scatter(
                    x=trend_df["year_month"],
                    y=trend_df["rolling_mean"],
                    name="Rolling avg rating (6m)",
                    mode="lines+markers",
                    line={"color": "#6fc6e3", "width": 3},
                    marker={"size": 4},
                ),
                secondary_y=False,
            )
            trend_fig.add_trace(
                go.Scatter(
                    x=trend_df["year_month"],
                    y=trend_df["monthly_rating"],
                    name="Monthly avg rating",
                    mode="lines",
                    line={"color": "#9bc9df", "width": 1.8, "dash": "dot"},
                ),
                secondary_y=False,
            )
            _apply_plotly_defaults(trend_fig)
            trend_fig.update_layout(height=540, title_text="Rating and review volume over time")
            trend_fig.update_yaxes(title_text="Average rating", secondary_y=False, range=[2, 5])
            trend_fig.update_yaxes(title_text="Review count", secondary_y=True)
            st.plotly_chart(trend_fig, use_container_width=True)

    with reviews_tab:
        if not selected_fac_ids:
            _render_selection_cta()
        else:
            st.markdown(
                f"Selected venues: **{len(selected_fac_ids):,}**",
            )
            filtered_reviews = _load_filtered_reviews(reviews, selected_fac_ids)
            selected_df = (
                filtered_map_df[filtered_map_df["facility_id"].isin(selected_fac_ids)]
                .sort_values(by="average_rating", ascending=False)
                .copy()
            )

            agg_df = pd.merge(
                selected_df[["facility_id", "google_name"]],
                filtered_reviews,
                left_on="facility_id",
                right_on="facility_id",
                how="left",
            )

            st.dataframe(
                agg_df,
                hide_index=True,
                column_config={
                    "facility_id": None,
                    "google_name": "Restaurant",
                    "text": "Review",
                    "rating": "Review rating",
                },
                use_container_width=True,
            )

            concise_reviews = _build_concise_reviews(
                reviews=reviews,
                establishments=establishments,
                facility_ids=selected_fac_ids,
                patterns=patterns,
            )

            if concise_reviews.height == 0:
                st.info("No keyword-matched review signals were found for selected venues.")
            else:
                st.markdown("Keyword-matched review signals")
                review_col, rating_col = st.columns([3, 2], gap="large")
                with review_col:
                    st.dataframe(
                        concise_reviews.select(
                            [
                                "restaurant_name",
                                "rating",
                                "match_ratio",
                                "text",
                            ]
                        ),
                        hide_index=True,
                        use_container_width=True,
                    )

                with rating_col:
                    rating_counts = (
                        concise_reviews.select(pl.col("rating").value_counts())
                        .unnest("rating")
                        .sort("rating")
                        .to_pandas()
                    )
                    rating_fig = px.bar(
                        rating_counts,
                        x="rating",
                        y="count",
                        labels={"rating": "Rating", "count": "Matched reviews"},
                    )
                    rating_fig.update_traces(marker_color="#54c2d3")
                    _apply_plotly_defaults(rating_fig)
                    rating_fig.update_layout(height=320, title_text="Matched review ratings")
                    st.plotly_chart(rating_fig, use_container_width=True)

    with insights_tab:
        if not selected_fac_ids:
            _render_selection_cta()
        else:
            st.markdown(
                f"Selected venues: **{len(selected_fac_ids):,}**",
            )
            tab_reviews = _build_concise_reviews(
                reviews=reviews,
                establishments=establishments,
                facility_ids=selected_fac_ids,
                patterns=patterns,
            )
            review_str = _build_reviews_prompt_text(tab_reviews)

            response_container = st.container(height=620)
            with response_container:
                if not review_str:
                    st.info("No review text available to summarize for this selection.")
                else:
                    client = _get_openai_client()
                    if client is None:
                        st.warning("Missing `openai_key` in Streamlit secrets.")
                    elif len(selected_fac_ids) == 1:
                        with st.spinner("Generating insights for the selected venue..."):
                            st.write_stream(_single_query_llm(client, review_str))
                    else:
                        with st.spinner("Generating cross-venue insights..."):
                            st.write_stream(_query_llm(client, review_str))
