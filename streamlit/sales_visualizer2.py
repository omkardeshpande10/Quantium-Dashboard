import os
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd

# ── Data ─────────────────────────────────────────────────────────────────────
_here = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(_here, "clean_data.csv"))
df["date"] = pd.to_datetime(df["date"])

PRICE_INCREASE_DATE = pd.Timestamp("2021-01-15")
REGIONS = ["north", "south", "east", "west"]
REGION_COLORS = {
    "north": "#3b82d4",
    "south": "#7c5cd8",
    "east":  "#0ea472",
    "west":  "#e5a220",
    "all":   "#3b82d4",
}

DATE_MIN = df["date"].min()
DATE_MAX = df["date"].max()

# Pre-compute all unique dates as sorted list for the range slider marks
all_dates = sorted(df["date"].unique())
slider_marks = {}
for d in pd.date_range(DATE_MIN, DATE_MAX, freq="YS"):
    idx = min(range(len(all_dates)), key=lambda i: abs(all_dates[i] - d))
    slider_marks[idx] = str(d.year)

# ── App ───────────────────────────────────────────────────────────────────────
app = dash.Dash(__name__)

CARD_STYLE = {
    "background": "#ffffff",
    "border": "1px solid #e5e7eb",
    "borderRadius": "10px",
    "padding": "20px 28px",
    "textAlign": "center",
    "flex": "1",
}

app.layout = html.Div(
    style={"fontFamily": "Segoe UI, sans-serif", "backgroundColor": "#f0f2f5", "minHeight": "100vh"},
    children=[

        # ── Banner header ────────────────────────────────────────────────────
        html.Div(
            style={
                "background": "linear-gradient(135deg, #1f2328 0%, #2d3748 100%)",
                "padding": "36px 48px 28px",
                "marginBottom": "32px",
            },
            children=[
                html.H1(
                    "Pink Morsel Sales Dashboard",
                    style={"color": "#ffffff", "margin": "0 0 6px 0", "fontSize": "28px", "letterSpacing": "0.5px"},
                ),
                html.P(
                    "Daily revenue for Pink Morsels across all regions · Feb 2018 – Feb 2022",
                    style={"color": "#a0aec0", "margin": "0", "fontSize": "14px"},
                ),
            ],
        ),

        html.Div(
            style={"maxWidth": "1140px", "margin": "0 auto", "padding": "0 32px 48px"},
            children=[

                # ── KPI Cards ────────────────────────────────────────────────
                html.Div(
                    id="kpi-row",
                    style={"display": "flex", "gap": "16px", "marginBottom": "28px"},
                ),

                # ── Controls ─────────────────────────────────────────────────
                html.Div(
                    style={
                        "background": "#ffffff",
                        "border": "1px solid #e5e7eb",
                        "borderRadius": "10px",
                        "padding": "18px 24px",
                        "marginBottom": "20px",
                        "display": "flex",
                        "alignItems": "center",
                        "gap": "32px",
                        "flexWrap": "wrap",
                    },
                    children=[
                        html.Div([
                            html.Label("Region", style={"fontWeight": "600", "color": "#1f2328", "marginRight": "12px", "fontSize": "13px"}),
                            dcc.RadioItems(
                                id="region-filter",
                                options=[{"label": r.capitalize(), "value": r} for r in ["all"] + REGIONS],
                                value="all",
                                inline=True,
                                inputStyle={"marginRight": "4px"},
                                labelStyle={"marginRight": "16px", "fontSize": "13px", "color": "#1f2328", "cursor": "pointer"},
                            ),
                        ]),
                        html.Div([
                            html.Label("Show 7-day average", style={"fontWeight": "600", "color": "#1f2328", "marginRight": "10px", "fontSize": "13px"}),
                            dcc.Checklist(
                                id="show-avg",
                                options=[{"label": "", "value": "show"}],
                                value=["show"],
                                inline=True,
                            ),
                        ]),
                    ],
                ),

                # ── Chart card ───────────────────────────────────────────────
                html.Div(
                    style={
                        "background": "#ffffff",
                        "border": "1px solid #e5e7eb",
                        "borderRadius": "10px",
                        "padding": "24px 24px 8px",
                        "marginBottom": "20px",
                    },
                    children=[
                        dcc.Graph(
                            id="sales-chart",
                            config={"displayModeBar": True, "modeBarButtonsToRemove": ["select2d", "lasso2d"], "displaylogo": False},
                            style={"height": "480px"},
                        ),
                    ],
                ),

                # ── Date range slider ─────────────────────────────────────────
                html.Div(
                    style={
                        "background": "#ffffff",
                        "border": "1px solid #e5e7eb",
                        "borderRadius": "10px",
                        "padding": "20px 36px 24px",
                    },
                    children=[
                        html.Label("Date Range", style={"fontWeight": "600", "color": "#1f2328", "fontSize": "13px", "marginBottom": "12px", "display": "block"}),
                        dcc.RangeSlider(
                            id="date-slider",
                            min=0,
                            max=len(all_dates) - 1,
                            value=[0, len(all_dates) - 1],
                            marks=slider_marks,
                            tooltip={"placement": "bottom", "always_visible": False},
                            allowCross=False,
                        ),
                    ],
                ),
            ],
        ),
    ],
)

# ── Callbacks ─────────────────────────────────────────────────────────────────

@app.callback(
    Output("sales-chart", "figure"),
    Output("kpi-row", "children"),
    Input("region-filter", "value"),
    Input("date-slider", "value"),
    Input("show-avg", "value"),
)
def update_chart(region, slider_range, show_avg):
    # Filter by region
    if region == "all":
        filtered = df.copy()
    else:
        filtered = df[df["region"] == region].copy()

    # Aggregate by date
    daily = filtered.groupby("date", as_index=False)["sales"].sum().sort_values("date")

    # Filter by date slider
    d_start = all_dates[slider_range[0]]
    d_end   = all_dates[slider_range[1]]
    daily = daily[(daily["date"] >= d_start) & (daily["date"] <= d_end)]

    color = REGION_COLORS.get(region, "#3b82d4")

    traces = []

    # Filled area trace
    traces.append(go.Scatter(
        x=daily["date"],
        y=daily["sales"],
        mode="lines",
        name="Daily Sales",
        line={"color": color, "width": 1.8},
        fill="tozeroy",
        fillcolor=f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.08)",
        hovertemplate="<b>%{x|%d %b %Y}</b><br>Sales: $%{y:,.0f}<extra></extra>",
    ))

    # 7-day rolling average
    if show_avg:
        daily["rolling"] = daily["sales"].rolling(7, center=True, min_periods=1).mean()
        traces.append(go.Scatter(
            x=daily["date"],
            y=daily["rolling"],
            mode="lines",
            name="7-day avg",
            line={"color": "#e5a220", "width": 2, "dash": "dot"},
            hovertemplate="<b>%{x|%d %b %Y}</b><br>7-day avg: $%{y:,.0f}<extra></extra>",
        ))

    # Price increase line (only if it falls within selected range)
    shapes, annotations = [], []
    if d_start <= PRICE_INCREASE_DATE <= d_end:
        shapes.append({
            "type": "line",
            "x0": PRICE_INCREASE_DATE, "x1": PRICE_INCREASE_DATE,
            "yref": "paper", "y0": 0, "y1": 1,
            "line": {"color": "#e53e3e", "width": 2, "dash": "dash"},
        })
        annotations.append({
            "x": PRICE_INCREASE_DATE,
            "yref": "paper", "y": 0.97,
            "xanchor": "left", "yanchor": "top",
            "text": "  Price increase<br>  15 Jan 2021",
            "showarrow": False,
            "font": {"color": "#e53e3e", "size": 11},
            "bgcolor": "rgba(255,255,255,0.7)",
            "bordercolor": "#e53e3e",
            "borderwidth": 1,
            "borderpad": 4,
        })

    fig = go.Figure(data=traces)
    fig.update_layout(
        xaxis={
            "title": {"text": "Date", "font": {"size": 13}},
            "showgrid": True, "gridcolor": "#f0f0f0",
            "rangeslider": {"visible": False},
        },
        yaxis={
            "title": {"text": "Total Sales (USD)", "font": {"size": 13}},
            "tickprefix": "$",
            "showgrid": True, "gridcolor": "#f0f0f0",
        },
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        font={"family": "Segoe UI, sans-serif", "color": "#1f2328"},
        margin={"t": 20, "b": 40, "l": 70, "r": 30},
        legend={"orientation": "h", "y": -0.12, "font": {"size": 12}},
        hovermode="x unified",
        shapes=shapes,
        annotations=annotations,
    )

    # ── KPI cards ──────────────────────────────────────────────────────────
    before = daily[daily["date"] < PRICE_INCREASE_DATE]["sales"].sum()
    after  = daily[daily["date"] >= PRICE_INCREASE_DATE]["sales"].sum()
    total  = daily["sales"].sum()
    avg    = daily["sales"].mean()
    pct_change = ((after / len(daily[daily["date"] >= PRICE_INCREASE_DATE]) -
                   before / max(len(daily[daily["date"] < PRICE_INCREASE_DATE]), 1)) /
                  max(before / max(len(daily[daily["date"] < PRICE_INCREASE_DATE]), 1), 1)) * 100

    def kpi_card(label, value, sub=None, accent="#1f2328"):
        return html.Div(style=CARD_STYLE, children=[
            html.P(label, style={"color": "#57606a", "margin": "0 0 4px 0", "fontSize": "12px", "fontWeight": "600", "textTransform": "uppercase", "letterSpacing": "0.5px"}),
            html.H2(value, style={"color": accent, "margin": "0 0 4px 0", "fontSize": "22px"}),
            html.P(sub or "", style={"color": "#57606a", "margin": "0", "fontSize": "11px"}),
        ])

    arrow = "▲" if pct_change >= 0 else "▼"
    arrow_color = "#0ea472" if pct_change >= 0 else "#e53e3e"

    cards = [
        kpi_card("Total Sales", f"${total:,.0f}", "selected period", "#1f2328"),
        kpi_card("Avg Daily Sales", f"${avg:,.0f}", "selected period", "#3b82d4"),
        kpi_card("Before Price Increase", f"${before:,.0f}", "cumulative", "#7c5cd8"),
        kpi_card("After Price Increase", f"${after:,.0f}", "cumulative", "#e53e3e"),
        kpi_card("Avg Daily Δ After Increase", f"{arrow} {abs(pct_change):.1f}%", "vs before", arrow_color),
    ]

    return fig, cards


if __name__ == "__main__":
    app.run(debug=True)
