import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# ── LOAD DATA FROM EXCEL ──────────────────────────────
df = pd.read_excel(
    r"C:\Users\nehad\OneDrive\Desktop\ai\melbourne_housing_data.xlsx",
    sheet_name="Suburb_Overview"
)
df_trends = pd.read_excel("melbourne_housing_data.xlsx", sheet_name="Rent_Trends")
df_cost = pd.read_excel("melbourne_housing_data.xlsx", sheet_name="Cost_of_Living")
df_trends['Date'] = pd.to_datetime(df_trends['Date'])

# ── ML FORECAST ───────────────────────────────────────
def forecast_rent(suburb_name, periods=4):
    data = df_trends[df_trends['Suburb'] == suburb_name].sort_values('Date')
    if len(data) < 4:
        return None, None
    X = np.arange(len(data)).reshape(-1, 1)
    y = data['Median_Weekly_Rent_AUD'].values
    model = LinearRegression().fit(X, y)
    future_X = np.arange(len(data), len(data)+periods).reshape(-1, 1)
    preds = model.predict(future_X).astype(int)
    future_dates = pd.date_range(start=data['Date'].iloc[-1], periods=periods+1, freq='QS')[1:]
    return future_dates, preds

# ── APP ───────────────────────────────────────────────
app = dash.Dash(__name__, title="Melbourne Housing Dashboard")

# ── STYLES ────────────────────────────────────────────
C = {
    'bg': '#F8F9FA',
    'white': '#FFFFFF',
    'border': '#E5E7EB',
    'text': '#111827',
    'muted': '#6B7280',
    'blue': '#2563EB',
    'light_blue': '#EFF6FF',
    'green': '#059669',
    'light_green': '#ECFDF5',
    'purple': '#7C3AED',
    'light_purple': '#F5F3FF',
    'orange': '#EA580C',
    'light_orange': '#FFF7ED',
    'red': '#DC2626',
    'light_red': '#FEF2F2',
}

def card(children, style={}):
    base = {
        'background': C['white'],
        'border': f'1px solid {C["border"]}',
        'borderRadius': '12px',
        'padding': '24px',
        'boxShadow': '0 1px 3px rgba(0,0,0,0.06)',
    }
    return html.Div(children, style={**base, **style})

def kpi_card(icon, value, label, color, light):
    return html.Div([
        html.Div([
            html.Span(icon, style={'fontSize': '1.4rem'}),
        ], style={
            'background': light, 'borderRadius': '10px',
            'width': '44px', 'height': '44px',
            'display': 'flex', 'alignItems': 'center',
            'justifyContent': 'center', 'marginBottom': '12px'
        }),
        html.Div(value, style={
            'fontSize': '1.6rem', 'fontWeight': '800',
            'color': color, 'lineHeight': '1', 'marginBottom': '4px'
        }),
        html.Div(label, style={
            'fontSize': '0.75rem', 'color': C['muted'],
            'fontWeight': '600', 'textTransform': 'uppercase',
            'letterSpacing': '0.05em'
        })
    ], style={
        'background': C['white'],
        'border': f'1px solid {C["border"]}',
        'borderRadius': '12px', 'padding': '20px',
        'flex': '1', 'minWidth': '140px',
        'boxShadow': '0 1px 3px rgba(0,0,0,0.06)',
        'borderTop': f'3px solid {color}'
    })

def section_title(text):
    return html.H3(text, style={
        'fontSize': '0.95rem', 'fontWeight': '700',
        'color': C['text'], 'marginBottom': '16px', 'margin': '0 0 16px 0'
    })

label_style = {
    'fontSize': '0.75rem', 'fontWeight': '700',
    'color': C['muted'], 'textTransform': 'uppercase',
    'letterSpacing': '0.06em', 'display': 'block', 'marginBottom': '8px'
}

# ── LAYOUT ────────────────────────────────────────────
app.layout = html.Div([

    # HEADER
    html.Div([
        html.Div([
            html.Div([
                html.H1("Melbourne Housing & Cost of Living",
                       style={'fontSize': '1.4rem', 'fontWeight': '800',
                              'color': C['text'], 'margin': '0 0 2px 0'}),
                html.P("Explore rental prices, liveability scores and cost of living across 40 Melbourne suburbs",
                      style={'color': C['muted'], 'margin': 0, 'fontSize': '0.85rem'})
            ]),
            html.Div([
                html.Span("📊 Interactive Dashboard", style={
                    'background': C['light_blue'], 'color': C['blue'],
                    'padding': '5px 12px', 'borderRadius': '20px',
                    'fontSize': '0.75rem', 'fontWeight': '700',
                    'marginRight': '8px'
                }),
                html.Span("🤖 ML Forecasting", style={
                    'background': C['light_purple'], 'color': C['purple'],
                    'padding': '5px 12px', 'borderRadius': '20px',
                    'fontSize': '0.75rem', 'fontWeight': '700',
                    'marginRight': '8px'
                }),
                html.Span("Built by Neha Durgadmath", style={
                    'color': C['muted'], 'fontSize': '0.78rem'
                })
            ], style={'display': 'flex', 'alignItems': 'center', 'flexWrap': 'wrap', 'gap': '4px'})
        ], style={'display': 'flex', 'justifyContent': 'space-between',
                  'alignItems': 'center', 'flexWrap': 'wrap', 'gap': '12px'})
    ], style={
        'background': C['white'], 'padding': '20px 32px',
        'borderBottom': f'1px solid {C["border"]}',
        'boxShadow': '0 1px 3px rgba(0,0,0,0.06)'
    }),

    # FILTERS BAR
    html.Div([
        html.Div([
            html.Label("Bedrooms", style=label_style),
            dcc.RadioItems(
                id='bedroom-filter',
                options=[
                    {'label': ' 1 Bedroom', 'value': 'Rent_1BR_per_week'},
                    {'label': ' 2 Bedrooms', 'value': 'Rent_2BR_per_week'},
                    {'label': ' 3 Bedrooms', 'value': 'Rent_3BR_per_week'},
                ],
                value='Rent_1BR_per_week', inline=True,
                style={'color': C['text'], 'fontSize': '0.85rem'},
                inputStyle={'marginRight': '5px', 'accentColor': C['blue']},
                labelStyle={'marginRight': '20px', 'cursor': 'pointer'}
            )
        ], style={'flex': '1'}),

        html.Div(style={'width': '1px', 'background': C['border'], 'margin': '0 24px'}),

        html.Div([
            html.Label("Weekly Budget (AUD)", style=label_style),
            dcc.RangeSlider(
                id='budget-slider', min=200, max=1200, step=50,
                value=[200, 1200],
                marks={
                    200:  {'label': '$200',  'style': {'color': C['muted'], 'fontSize': '0.75rem'}},
                    400:  {'label': '$400',  'style': {'color': C['muted'], 'fontSize': '0.75rem'}},
                    600:  {'label': '$600',  'style': {'color': C['muted'], 'fontSize': '0.75rem'}},
                    800:  {'label': '$800',  'style': {'color': C['muted'], 'fontSize': '0.75rem'}},
                    1000: {'label': '$1000', 'style': {'color': C['muted'], 'fontSize': '0.75rem'}},
                    1200: {'label': '$1200', 'style': {'color': C['muted'], 'fontSize': '0.75rem'}},
                },
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], style={'flex': '2'}),

        html.Div(style={'width': '1px', 'background': C['border'], 'margin': '0 24px'}),

        html.Div([
            html.Label("Suburb Type", style=label_style),
            dcc.Dropdown(
                id='suburb-type-filter',
                options=[
                    {'label': '🏙 All Suburbs', 'value': 'All'},
                    {'label': '🏙 Inner (< 5km)', 'value': 'Inner'},
                    {'label': '🏘 Middle (5–15km)', 'value': 'Middle'},
                    {'label': '🌳 Outer (> 15km)', 'value': 'Outer'},
                ],
                value='All', clearable=False,
                style={'fontSize': '0.85rem'}
            )
        ], style={'flex': '1', 'minWidth': '180px'})
    ], style={
        'background': C['white'], 'padding': '16px 32px',
        'borderBottom': f'1px solid {C["border"]}',
        'display': 'flex', 'alignItems': 'center',
        'flexWrap': 'wrap', 'gap': '8px'
    }),

    # MAIN
    html.Div([

        # KPI ROW
        html.Div(id='kpi-row', style={
            'display': 'flex', 'gap': '16px',
            'marginBottom': '24px', 'flexWrap': 'wrap'
        }),

        # ROW 1 — MAP + SCATTER
        html.Div([
            card([
                section_title("🗺 Rental Prices by Suburb"),
                dcc.Graph(id='map-chart', style={'height': '400px'},
                         config={'displayModeBar': False})
            ], {'flex': '1.4', 'marginRight': '16px'}),
            card([
                section_title("📊 Rent vs Distance from CBD"),
                dcc.Graph(id='scatter-chart', style={'height': '400px'},
                         config={'displayModeBar': False})
            ], {'flex': '1'})
        ], style={'display': 'flex', 'marginBottom': '24px'}),

        # ROW 2 — TREND + TOP 10
        html.Div([
            card([
                html.Div([
                    section_title("📈 Rent Trend & ML Forecast"),
                    dcc.Dropdown(
                        id='trend-suburb',
                        options=[{'label': s, 'value': s}
                                 for s in df_trends['Suburb'].unique()],
                        value='Melbourne CBD', clearable=False,
                        style={'fontSize': '0.85rem', 'width': '220px'}
                    )
                ], style={'display': 'flex', 'justifyContent': 'space-between',
                          'alignItems': 'center', 'marginBottom': '16px',
                          'flexWrap': 'wrap', 'gap': '8px'}),
                dcc.Graph(id='trend-chart', style={'height': '340px'},
                         config={'displayModeBar': False})
            ], {'flex': '1.2', 'marginRight': '16px'}),
            card([
                section_title("🏆 Most Affordable Suburbs"),
                dcc.Graph(id='affordable-chart', style={'height': '370px'},
                         config={'displayModeBar': False})
            ], {'flex': '1'})
        ], style={'display': 'flex', 'marginBottom': '24px'}),

        # ROW 3 — LIVEABILITY + COST + INSIGHTS
        html.Div([
            card([
                section_title("⭐ Liveability Radar"),
                dcc.Graph(id='liveability-chart', style={'height': '340px'},
                         config={'displayModeBar': False})
            ], {'flex': '1', 'marginRight': '16px'}),
            card([
                html.Div([
                    section_title("💸 Weekly Cost Breakdown"),
                    dcc.Dropdown(
                        id='cost-suburb',
                        options=[{'label': s, 'value': s} for s in df['Suburb']],
                        value='Melbourne CBD', clearable=False,
                        style={'fontSize': '0.85rem', 'width': '200px'}
                    )
                ], style={'display': 'flex', 'justifyContent': 'space-between',
                          'alignItems': 'center', 'marginBottom': '16px',
                          'flexWrap': 'wrap', 'gap': '8px'}),
                dcc.Graph(id='cost-chart', style={'height': '310px'},
                         config={'displayModeBar': False})
            ], {'flex': '1', 'marginRight': '16px'}),
            card([
                section_title("🤖 AI Insights"),
                html.Div(id='ai-insights', style={'overflowY': 'auto', 'height': '340px'})
            ], {'flex': '0.9'})
        ], style={'display': 'flex', 'marginBottom': '24px'}),

    ], style={'padding': '28px 32px', 'background': C['bg']}),

    # FOOTER
    html.Div([
        html.P([
            "🏠 Melbourne Housing & Cost of Living Dashboard  ·  ",
            html.Strong("Data: Simulated (2026-Q1) — Replace with real data from data.vic.gov.au"),
            "  ·  Built by Neha Durgadmath · AI Engineer & Data Scientist"
        ], style={'color': C['muted'], 'fontSize': '0.78rem', 'margin': 0, 'textAlign': 'center'})
    ], style={
        'background': C['white'], 'padding': '16px 32px',
        'borderTop': f'1px solid {C["border"]}'
    })

], style={'background': C['bg'], 'minHeight': '100vh',
          'fontFamily': "'Segoe UI', -apple-system, sans-serif"})

# ── CALLBACKS ─────────────────────────────────────────

@app.callback(Output('kpi-row', 'children'),
              [Input('bedroom-filter', 'value'),
               Input('budget-slider', 'value'),
               Input('suburb-type-filter', 'value')])
def update_kpis(bedroom, budget, stype):
    filtered = df.copy()
    if stype != 'All':
        filtered = filtered[filtered['Suburb_Type'] == stype]
    in_budget = filtered[
        (filtered[bedroom] >= budget[0]) &
        (filtered[bedroom] <= budget[1])
    ]
    n = len(in_budget)
    avg_rent  = f"${int(in_budget[bedroom].mean()):,}" if n else "N/A"
    avg_trans = f"{int(in_budget['Transport_Score_out_of_100'].mean())}/100" if n else "N/A"
    avg_safe  = f"{int(in_budget['Safety_Score_out_of_100'].mean())}/100" if n else "N/A"
    avg_total = f"${int(in_budget['Weekly_Total_Living_Cost_AUD'].mean()):,}" if n else "N/A"

    return [
        kpi_card("🏠", avg_rent,  "Avg Weekly Rent",    C['blue'],   C['light_blue']),
        kpi_card("🚇", avg_trans, "Transport Score",    C['green'],  C['light_green']),
        kpi_card("🛡", avg_safe,  "Safety Score",       C['purple'], C['light_purple']),
        kpi_card("🏘", str(n),    "Suburbs in Budget",  C['orange'], C['light_orange']),
        kpi_card("💰", avg_total, "Total Weekly Cost",  C['red'],    C['light_red']),
    ]

@app.callback(Output('map-chart', 'figure'),
              [Input('bedroom-filter', 'value'),
               Input('budget-slider', 'value'),
               Input('suburb-type-filter', 'value')])
def update_map(bedroom, budget, stype):
    filtered = df.copy()
    if stype != 'All':
        filtered = filtered[filtered['Suburb_Type'] == stype]

    filtered['in_budget'] = (
        (filtered[bedroom] >= budget[0]) &
        (filtered[bedroom] <= budget[1])
    )
    filtered['marker_color'] = filtered['in_budget'].map(
        {True: 'In Budget', False: 'Over Budget'}
    )

    fig = px.scatter_mapbox(
        filtered, lat='Latitude', lon='Longitude',
        color='marker_color',
        color_discrete_map={'In Budget': '#2563EB', 'Over Budget': '#D1D5DB'},
        size=bedroom, size_max=18,
        hover_name='Suburb',
        hover_data={
            'Latitude': False, 'Longitude': False,
            'marker_color': False,
            bedroom: True,
            'Transport_Score_out_of_100': True,
            'Safety_Score_out_of_100': True,
            'Distance_to_CBD_km': True,
            'Suburb_Type': True
        },
        zoom=10, center={'lat': -37.8136, 'lon': 144.9631},
        mapbox_style='carto-positron',
    )
    fig.update_layout(
        paper_bgcolor='white', plot_bgcolor='white',
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(
            title='', bgcolor='white',
            bordercolor=C['border'], borderwidth=1,
            font=dict(size=11, color=C['text'])
        )
    )
    return fig

@app.callback(Output('scatter-chart', 'figure'),
              [Input('bedroom-filter', 'value'),
               Input('budget-slider', 'value'),
               Input('suburb-type-filter', 'value')])
def update_scatter(bedroom, budget, stype):
    filtered = df.copy()
    if stype != 'All':
        filtered = filtered[filtered['Suburb_Type'] == stype]

    color_map = {'Inner': '#2563EB', 'Middle': '#059669', 'Outer': '#EA580C'}
    fig = go.Figure()

    for st, color in color_map.items():
        sub = filtered[filtered['Suburb_Type'] == st]
        fig.add_trace(go.Scatter(
            x=sub['Distance_to_CBD_km'],
            y=sub[bedroom],
            mode='markers+text',
            name=st,
            text=sub['Suburb'],
            textposition='top center',
            textfont=dict(size=8, color='#9CA3AF'),
            marker=dict(size=10, color=color,
                       opacity=0.8, line=dict(width=1.5, color='white')),
            hovertemplate='<b>%{text}</b><br>Rent: $%{y}/wk<br>Distance: %{x}km<extra></extra>'
        ))

    fig.add_hline(y=budget[0], line_dash='dash', line_color='#10B981', line_width=1.5,
                  annotation_text=f'Min ${budget[0]}',
                  annotation_font=dict(color='#10B981', size=11))
    fig.add_hline(y=budget[1], line_dash='dash', line_color='#EF4444', line_width=1.5,
                  annotation_text=f'Max ${budget[1]}',
                  annotation_font=dict(color='#EF4444', size=11))

    fig.update_layout(
        paper_bgcolor='white', plot_bgcolor='#FAFAFA',
        font=dict(color=C['text'], family='Segoe UI'),
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(title='Distance from CBD (km)', gridcolor=C['border'],
                   color=C['muted'], showline=True, linecolor=C['border']),
        yaxis=dict(title='Weekly Rent ($)', gridcolor=C['border'],
                   color=C['muted'], showline=True, linecolor=C['border']),
        legend=dict(bgcolor='white', bordercolor=C['border'],
                   borderwidth=1, font=dict(size=11))
    )
    return fig

@app.callback(Output('trend-chart', 'figure'), Input('trend-suburb', 'value'))
def update_trend(suburb):
    data = df_trends[df_trends['Suburb'] == suburb].sort_values('Date')
    future_dates, preds = forecast_rent(suburb)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data['Date'], y=data['Median_Weekly_Rent_AUD'],
        mode='lines+markers', name='Historical Rent',
        line=dict(color=C['blue'], width=2.5),
        marker=dict(size=5, color=C['blue']),
        hovertemplate='%{x|%b %Y}: $%{y}/wk<extra></extra>'
    ))

    if future_dates is not None:
        fig.add_trace(go.Scatter(
            x=future_dates, y=preds,
            mode='lines+markers', name='ML Forecast',
            line=dict(color=C['orange'], width=2.5, dash='dot'),
            marker=dict(size=8, color=C['orange'], symbol='diamond'),
            hovertemplate='Forecast %{x|%b %Y}: $%{y}/wk<extra></extra>'
        ))
        fig.add_trace(go.Scatter(
            x=list(future_dates)+list(future_dates[::-1]),
            y=list(preds*1.04)+list(preds*0.96),
            fill='toself', fillcolor='rgba(234,88,12,0.08)',
            line=dict(color='rgba(0,0,0,0)'),
            name='Confidence Range', showlegend=True
        ))

    # COVID annotation
    fig.add_vrect(
        x0='2020-01-01', x1='2021-06-01',
        fillcolor='rgba(239,68,68,0.06)',
        line_width=0,
        annotation_text='COVID-19',
        annotation_position='top left',
        annotation_font=dict(size=10, color='#EF4444')
    )

    fig.update_layout(
        paper_bgcolor='white', plot_bgcolor='#FAFAFA',
        font=dict(color=C['text'], family='Segoe UI'),
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(gridcolor=C['border'], color=C['muted'],
                   showline=True, linecolor=C['border']),
        yaxis=dict(title='Weekly Rent ($)', gridcolor=C['border'],
                   color=C['muted'], showline=True, linecolor=C['border']),
        legend=dict(bgcolor='white', bordercolor=C['border'],
                   borderwidth=1, font=dict(size=11))
    )
    return fig

@app.callback(Output('affordable-chart', 'figure'),
              [Input('bedroom-filter', 'value'),
               Input('suburb-type-filter', 'value')])
def update_affordable(bedroom, stype):
    filtered = df.copy()
    if stype != 'All':
        filtered = filtered[filtered['Suburb_Type'] == stype]
    top10 = filtered.nsmallest(10, bedroom).sort_values(bedroom)

    colors = ['#2563EB' if i >= 7 else '#60A5FA' if i >= 4 else '#BFDBFE'
              for i in range(len(top10))]

    fig = go.Figure(go.Bar(
        x=top10[bedroom], y=top10['Suburb'],
        orientation='h',
        marker_color=colors[::-1],
        text=[f'${v}/wk' for v in top10[bedroom]],
        textposition='outside',
        textfont=dict(size=11, color=C['text']),
        hovertemplate='<b>%{y}</b><br>$%{x}/wk<extra></extra>'
    ))
    fig.update_layout(
        paper_bgcolor='white', plot_bgcolor='#FAFAFA',
        font=dict(color=C['text'], family='Segoe UI'),
        margin=dict(l=10, r=60, t=10, b=10),
        xaxis=dict(title='Weekly Rent ($)', gridcolor=C['border'],
                   color=C['muted'], showline=True, linecolor=C['border']),
        yaxis=dict(gridcolor=C['border'], color=C['text']),
        showlegend=False
    )
    return fig
@app.callback(Output('liveability-chart', 'figure'),
              [Input('bedroom-filter', 'value'),
               Input('budget-slider', 'value'),
               Input('suburb-type-filter', 'value')])
def update_liveability(bedroom, budget, stype):
    filtered = df.copy()
    if stype != 'All':
        filtered = filtered[filtered['Suburb_Type'] == stype]
    in_budget = filtered[
        (filtered[bedroom] >= budget[0]) &
        (filtered[bedroom] <= budget[1])
    ]

    if len(in_budget) == 0:
        return go.Figure()

    top6 = in_budget.nlargest(min(6, len(in_budget)), 'Transport_Score_out_of_100')

    cats = ['Transport', 'Safety', 'Walkability', 'Amenities']
    cols = ['#2563EB','#059669','#7C3AED','#EA580C','#DC2626','#0891B2']
    fig = go.Figure()

    for i, (_, row) in enumerate(top6.iterrows()):
        fig.add_trace(go.Scatterpolar(
            r=[row['Transport_Score_out_of_100'],
               row['Safety_Score_out_of_100'],
               row['Walkability_Score_out_of_100'],
               row['Amenities_Score_out_of_100']],
            theta=cats, fill='toself',
            name=row['Suburb'],
            line=dict(color=cols[i % len(cols)], width=2),
            opacity=0.7
        ))

    fig.update_layout(
        polar=dict(
            bgcolor='#FAFAFA',
            radialaxis=dict(visible=True, range=[0,100],
                           gridcolor=C['border'], color=C['muted'],
                           tickfont=dict(size=9)),
            angularaxis=dict(gridcolor=C['border'],
                            color=C['text'], tickfont=dict(size=11))
        ),
        paper_bgcolor='white',
        font=dict(color=C['text'], family='Segoe UI'),
        margin=dict(l=30, r=30, t=20, b=20),
        legend=dict(bgcolor='white', bordercolor=C['border'],
                   borderwidth=1, font=dict(size=10),
                   orientation='h', yanchor='bottom', y=-0.15)
    )
    return fig


@app.callback(Output('ai-insights', 'children'),
              [Input('bedroom-filter', 'value'),
               Input('budget-slider', 'value'),
               Input('suburb-type-filter', 'value')])
def update_insights(bedroom, budget, stype):
    filtered = df.copy()
    if stype != 'All':
        filtered = filtered[filtered['Suburb_Type'] == stype]
    in_budget = filtered[
        (filtered[bedroom] >= budget[0]) &
        (filtered[bedroom] <= budget[1])
    ]

    def insight(icon, title, text, color, light):
        return html.Div([
            html.Div([
                html.Span(icon, style={'marginRight': '6px'}),
                html.Span(title, style={'fontWeight': '700', 'fontSize': '0.82rem', 'color': color})
            ], style={'marginBottom': '4px'}),
            html.P(text, style={'color': C['muted'], 'fontSize': '0.78rem',
                                'margin': 0, 'lineHeight': '1.55'})
        ], style={
            'background': light,
            'border': f'1px solid {color}22',
            'borderLeft': f'3px solid {color}',
            'borderRadius': '8px', 'padding': '10px 12px',
            'marginBottom': '8px'
        })

    if len(in_budget) == 0:
        return [insight('⚠️', 'No Results',
                       'No suburbs match your current filters. Try widening your budget range.',
                       C['orange'], C['light_orange'])]

    best_t = in_budget.loc[in_budget['Transport_Score_out_of_100'].idxmax()]
    best_v = in_budget.loc[(in_budget[bedroom] / in_budget['Transport_Score_out_of_100']).idxmin()]
    cheapest = in_budget.loc[in_budget[bedroom].idxmin()]
    safest = in_budget.loc[in_budget['Safety_Score_out_of_100'].idxmax()]
    avg = int(in_budget[bedroom].mean())

    return [
        insight('🚇', 'Best Transport',
               f"{best_t['Suburb']} leads with a transport score of {best_t['Transport_Score_out_of_100']}/100 at ${best_t[bedroom]}/wk.",
               C['blue'], C['light_blue']),
        insight('💎', 'Best Value',
               f"{best_v['Suburb']} offers the best rent-to-transport ratio at ${best_v[bedroom]}/wk — smart choice.",
               C['green'], C['light_green']),
        insight('💰', 'Most Affordable',
               f"{cheapest['Suburb']} is the cheapest at ${cheapest[bedroom]}/wk, {cheapest['Distance_to_CBD_km']}km from CBD.",
               C['purple'], C['light_purple']),
        insight('🛡', 'Safest Option',
               f"{safest['Suburb']} has the highest safety score ({safest['Safety_Score_out_of_100']}/100) within your budget.",
               C['orange'], C['light_orange']),
        insight('📊', 'Market Summary',
               f"{len(in_budget)} suburb{'s' if len(in_budget)>1 else ''} match your criteria. Average rent: ${avg}/wk. {'Competitive inner-city pricing.' if avg > 550 else 'Good value options available.'}",
               C['red'], C['light_red']),
    ]
@app.callback(Output('cost-chart', 'figure'), Input('cost-suburb', 'value'))
def update_cost(suburb):
    if suburb is None:
        return go.Figure()
    row = df[df['Suburb'] == suburb]
    if len(row) == 0:
        return go.Figure()
    row = row.iloc[0]
    labels = ['Rent (1BR)', 'Groceries', 'Transport', 'Dining', 'Utilities']
    values = [
        int(row['Rent_1BR_per_week']),
        int(row['Weekly_Groceries_AUD']),
        int(row['Weekly_Transport_Cost_AUD']),
        int(row['Weekly_Dining_Budget_AUD'] * 0.35),
        int(row['Weekly_Utilities_AUD'])
    ]
    colors = [C['blue'], C['green'], C['purple'], C['orange'], C['red']]
    total = sum(values)
    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        marker_colors=colors, hole=0.52,
        textinfo='label+percent',
        textfont=dict(size=11),
        hovertemplate='%{label}<br>$%{value}/wk (%{percent})<extra></extra>'
    ))
    fig.add_annotation(
        text=f'${total}<br>per week',
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=16, color=C['text'], family='Segoe UI')
    )
    fig.update_layout(
        paper_bgcolor='white',
        font=dict(color=C['text'], family='Segoe UI'),
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(bgcolor='white', bordercolor=C['border'],
                   borderwidth=1, font=dict(size=11),
                   orientation='h', yanchor='bottom', y=-0.12)
    )
    return fig

# ── RUN ───────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=False, port=8050)
#  ───────────────────────────────────────────────