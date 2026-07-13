import os
import dash
from dash import dcc, html
import plotly.graph_objects as go
import pandas as pd

# ── Load clean data ──────────────────────────────────────────────────────────
_here = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(_here, "clean_data.csv"))
df["date"] = pd.to_datetime(df["date"])

# Aggregate total sales across all regions per day
daily = df.groupby("date", as_index=False)["sales"].sum().sort_values("date")

PRICE_INCREASE_DATE = "2021-01-15"

# ── App ───────────────────────────────────────────────────────────────────────
app = dash.Dash(__name__)

app.layout = html.Div(
    style={
        "fontFamily": "Segoe UI, sans-serif",
        "backgroundColor": "#f7f8fa",
        "minHeight": "100vh",
        "padding": "32px 40px",
        "maxWidth": "1100px",
        "margin": "0 auto",
    },
    children=[
        # Header
        html.H1(
            "Pink Morsel Sales Visualiser",
            style={"textAlign": "center", "color": "#1f2328", "marginBottom": "6px"},
        ),
        html.P(
            "Daily total sales revenue for Pink Morsels across all regions (2018 – 2022)",
            style={"textAlign": "center", "color": "#57606a", "marginBottom": "32px"},
        ),

        # Chart
        html.Div(
            style={
                "background": "#ffffff",
                "border": "1px solid #e5e7eb",
                "borderRadius": "8px",
                "padding": "24px",
            },
            children=[
                dcc.Graph(
                    id="sales-chart",
                    figure=go.Figure(
                        data=[
                            go.Scatter(
                                x=daily["date"],
                                y=daily["sales"],
                                mode="lines",
                                name="Daily Sales",
                                line={"color": "#3b82d4", "width": 1.5},
                            )
                        ],
                        layout=go.Layout(
                            title={
                                "text": "Daily Pink Morsel Sales",
                                "font": {"size": 16, "color": "#1f2328"},
                            },
                            xaxis={
                                "title": "Date",
                                "showgrid": True,
                                "gridcolor": "#e5e7eb",
                            },
                            yaxis={
                                "title": "Total Sales (USD)",
                                "tickprefix": "$",
                                "showgrid": True,
                                "gridcolor": "#e5e7eb",
                            },
                            plot_bgcolor="#ffffff",
                            paper_bgcolor="#ffffff",
                            font={"family": "Segoe UI, sans-serif", "color": "#1f2328"},
                            margin={"t": 50, "b": 50, "l": 70, "r": 30},
                            legend={"orientation": "h", "y": -0.15},
                            # Vertical line marking the price increase
                            shapes=[
                                {
                                    "type": "line",
                                    "x0": PRICE_INCREASE_DATE,
                                    "x1": PRICE_INCREASE_DATE,
                                    "yref": "paper",
                                    "y0": 0,
                                    "y1": 1,
                                    "line": {"color": "#e53e3e", "width": 2, "dash": "dash"},
                                }
                            ],
                            annotations=[
                                {
                                    "x": PRICE_INCREASE_DATE,
                                    "yref": "paper",
                                    "y": 1,
                                    "xanchor": "left",
                                    "yanchor": "top",
                                    "text": "  Price increase (15 Jan 2021)",
                                    "showarrow": False,
                                    "font": {"color": "#e53e3e", "size": 12},
                                }
                            ],
                        ),
                    ),
                    config={"displayModeBar": False},
                    style={"height": "500px"},
                )
            ],
        ),
    ],
)

if __name__ == "__main__":
    app.run(debug=True)
