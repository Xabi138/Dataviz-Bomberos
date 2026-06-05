import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, callback
from plotly.colors import n_colors
import warnings
warnings.filterwarnings('ignore')

# ==================== CARGA Y PREPROCESAMIENTO ====================
df = pd.read_csv("bomberos.csv")

# Corregir outlier de longitud
outlier_idx = df[(df["Longitud"] < -7) | (df["Longitud"] > -2)].index[0]
df.loc[outlier_idx, "Longitud"] = 180 - 179.998698

# Columnas por tipo
categorical_columns = ['Motivo', 'Intervencion', 'Origen', 'Franja', 'Lugar']
temporal_columns = ["Año", "Mes"]

# Datos para línea temporal
temporal = df.groupby(["Año", "Mes", "Fecha"]).size().reset_index(name="intervenciones").sort_values("Fecha")

# Preparar columnas categóricas para selects
df["Año"] = df["Año"].astype(str)
df["Mes"] = df["Mes"].astype(str)

columnas_categoricas = df.select_dtypes(include=['object', 'category']).columns.tolist()
for col in ["Mes", "Año"]:
    if col in df.columns and col not in columnas_categoricas:
        columnas_categoricas.append(col)

# Valores para filtros
tipos_disponibles = ["Todos"] + sorted(df["Motivo"].dropna().unique().tolist())
años_disponibles = ["Todos"] + sorted(df["Año"].dropna().unique().tolist())
meses_disponibles = ["Todos"] + sorted(df["Mes"].dropna().unique().tolist(), key=lambda x: int(x))
franjas_disponibles = ["Todos"] + sorted(df["Franja"].dropna().unique().tolist())
origen_disponible = ["Todos"] + sorted(df["Origen"].dropna().unique().tolist())
intervencion_disponible = ["Todos"] + sorted(df["Intervencion"].dropna().unique().tolist())

# Rangos para sliders
max_heridos, max_fallecidos, max_recursos = int(df["Heridos"].max()), int(df["Fallecidos"].max()), int(df["Recursos"].max())

# Colores bomberos
COLORS = {
    'primary': '#c0392b',
    'secondary': '#e67e22',
    'dark': '#2c3e50',
    'light': '#ecf0f1',
    'accent': '#f39c12',
    'background': '#fdf2e9'
}

# ==================== INICIALIZAR APP ====================
app = Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    # HEADER
    html.Div([
        html.H1("¿Cuál es la labor de los Bomberos en Bizkaia?",
                style={'textAlign': 'center', 'color': COLORS['dark'], 'marginBottom': '10px'}),
        html.P("""Análisis exploratorio en 6 visualizaciones interactivas sobre 69,423 intervenciones
        realizadas entre 2021 y 2025""",
               style={'textAlign': 'center', 'color': '#666', 'marginBottom': '30px'})
    ]),

    # ==================== SECCIÓN 1 ====================
    html.Div([
        html.Div([
            html.H2("1. Motivo de las Intervenciones y Origen de los Avisos",
                    style={'color': COLORS['dark'], 'borderLeft': f'5px solid {COLORS["primary"]}', 'paddingLeft': '15px'}),
            html.P("""Una imágen habitual de los cuerpos de bomberos es en los incendios, pero la realidad
            es que su labor se extiende más allá de ahí, realizando otras muchas acciones que podemos observar
            en el histograma. De forma similar, podemos pensar que las llamadas al 112 son la única vía
            de aviso que tienen, pero podemos observar otras curiosas vías de aviso en un gráfico de tarta.
            Ambos pueden mostrar otras variables categóricas para explorar sus distribuciones.
            """,
                   style={'color': COLORS['dark'], 'marginBottom': '20px'}),
        ]),
        html.Div([
            html.Div([
                html.Label("Selecciona categoría para Histograma:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(id='categorical-dropdown', options=[{'label': col, 'value': col} for col in categorical_columns],
                            value='Motivo', clearable=False)
            ], style={'width': '48%', 'display': 'inline-block'}),
            html.Div([
                html.Label("Selecciona categoría para Gráfico de Tarta:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(id='pie-dropdown', options=[{'label': col, 'value': col} for col in categorical_columns],
                            value='Origen', clearable=False)
            ], style={'width': '48%', 'display': 'inline-block', 'marginLeft': '20px'}),
        ]),
        html.Div([
            html.Div([dcc.Graph(id='histogram-plot', style={'height': '450px'})], style={'width': '48%', 'display': 'inline-block'}),
            html.Div([dcc.Graph(id='pie-plot', style={'height': '450px'})], style={'width': '48%', 'display': 'inline-block', 'float': 'right'})
        ])
    ], style={'backgroundColor': COLORS['background'], 'padding': '20px', 'borderRadius': '10px', 'marginBottom': '30px'}),

    # ==================== SECCIÓN 2 ====================
    html.Div([
        html.Div([
            html.H2("2. Análisis Temporal de las Intervenciones",
                    style={'color': COLORS['dark'], 'borderLeft': f'5px solid {COLORS["primary"]}', 'paddingLeft': '15px'}),
            html.P("""Podemos mostrar las intervenciones por mes y año realizadas, observando que en tres
            de esos años son muy altas durante los primeros meses, decayendo durante el verano, mientras que
            dos de los años son más estables y con menos intervenciones. ¿Aumentarán las intervenciones en
            verano si filtramos solo los incendios?""",
                   style={'color': COLORS['dark'], 'marginBottom': '20px'}),
        ]),
        html.Div([
            html.Div([
                html.Label("Filtrar por Motivo:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(id='motivo-filter', options=[{'label': 'Todos', 'value': 'Todos'}] + [{'label': m, 'value': m} for m in sorted(df['Motivo'].unique())],
                            value='Todos', clearable=False)
            ], style={'width': '30%', 'display': 'inline-block'}),
            html.Div([
                html.Label("Filtrar por Origen:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(id='origen-filter', options=[{'label': 'Todos', 'value': 'Todos'}] + [{'label': o, 'value': o} for o in sorted(df['Origen'].unique())],
                            value='Todos', clearable=False)
            ], style={'width': '30%', 'display': 'inline-block', 'marginLeft': '20px'}),
        ]),
        dcc.Graph(id='temporal-line', style={'marginTop': '20px'})
    ], style={'padding': '20px', 'borderRadius': '10px', 'marginBottom': '30px'}),

    # ==================== SECCIÓN 3 ====================
    html.Div([
        html.Div([
            html.H2("3. Relaciones entre Variables",
                    style={'color': COLORS['dark'], 'borderLeft': f'5px solid {COLORS["primary"]}', 'paddingLeft': '15px'}),
            html.P("""En el gráfico anterior pudimos ver que no aumentaban en verano las
            intervenciones por incendios, pero lo hacían las auxiliares (principalmente
            el tratamiento de avisperos). Ahora podemos ver otra dimensión temporal, la franja
            horaria en que suceden. Suceden más intervenciones a principio de año y durante la
            noche y filtrando por el motivo de Incendios, vemos que estos siguen esta misma
            tendencia. Sin embargo, fitrando por Auxiliar, vemos que estas actuaciones suceden durante
            el verano y durante la mañana, relacionandose así la franja horaria y los meses.""",
                   style={'color': COLORS['dark'], 'marginBottom': '20px'}),
        ]),
        html.Div([
            html.Div([html.Label("Eje X:"), dcc.Dropdown(id="selector-x", options=[{"label": c, "value": c} for c in columnas_categoricas],
                        value="Mes", clearable=False)], style={"width": "48%", "display": "inline-block"}),
            html.Div([html.Label("Eje Y:"), dcc.Dropdown(id="selector-y", options=[{"label": c, "value": c} for c in columnas_categoricas],
                        value="Franja", clearable=False)], style={"width": "48%", "display": "inline-block", "marginLeft": "20px"})
        ]),
        html.Div([
            html.Div([html.Label("Motivo:"), dcc.Dropdown(id="filtro-tipo", options=[{"label": t, "value": t} for t in tipos_disponibles], value="Todos")], style={"width": "32%", "display": "inline-block"}),
            html.Div([html.Label("Origen aviso:"), dcc.Dropdown(id="filtro-origen", options=[{"label": o, "value": o} for o in origen_disponible], value="Todos")], style={"width": "32%", "display": "inline-block"}),
            html.Div([html.Label("Intervención:"), dcc.Dropdown(id="filtro-intervencion", options=[{"label": i, "value": i} for i in intervencion_disponible], value="Todos")], style={"width": "32%", "display": "inline-block"})
        ]),
        html.Div([
            html.Div([html.Label("Franja horaria:"), dcc.Dropdown(id="filtro-franja", options=[{"label": f, "value": f} for f in franjas_disponibles], value="Todos")], style={"width": "32%", "display": "inline-block"}),
            html.Div([html.Label("Año:"), dcc.Dropdown(id="filtro-año", options=[{"label": a, "value": a} for a in años_disponibles], value="Todos")], style={"width": "32%", "display": "inline-block"}),
            html.Div([html.Label("Mes:"), dcc.Dropdown(id="filtro-mes", options=[{"label": m, "value": m} for m in meses_disponibles], value="Todos")], style={"width": "32%", "display": "inline-block"})
        ]),
        html.Div([
            html.Div([html.Label("Heridos:"), dcc.RangeSlider(id="rango-heridos", min=0, max=max_heridos, step=1, value=[0, max_heridos])], style={"width": "30%", "display": "inline-block"}),
            html.Div([html.Label("Fallecidos:"), dcc.RangeSlider(id="rango-fallecidos", min=0, max=max_fallecidos, step=1, value=[0, max_fallecidos])], style={"width": "30%", "display": "inline-block"}),
            html.Div([html.Label("Recursos:"), dcc.RangeSlider(id="rango-recursos", min=0, max=max_recursos, step=1, value=[0, max_recursos])], style={"width": "30%", "display": "inline-block"})
        ]),
        dcc.Graph(id="heatmap", style={"height": "60vh", "marginTop": "10px"})
    ], style={'backgroundColor': COLORS['background'], 'padding': '20px', 'borderRadius': '10px', 'marginBottom': '30px'}),

    # ==================== SECCIÓN 4 ====================
    html.Div([
        html.Div([
            html.H2("4. Análisis de Proporciones por Categoría",
                    style={'color': COLORS['dark'], 'borderLeft': f'5px solid {COLORS["primary"]}', 'paddingLeft': '15px'}),
            html.P("""Un gráfico de barras horizontales puede mostrar el porcentaje que representa cada clase
            de una categoría (como si se ha requerido o no intervencion ante un aviso) para cada clase de otra
            variable en el eje Y (como el motivo de la intervención). Los incendios tienen más falsas alarmas
            que el resto y en muchas alertas de suicidio no termina siendo necesaria la intervención. Otras
            combinaciones de variables también resultan muy interesantes.""",
                   style={'color': COLORS['dark'], 'marginBottom': '20px'}),
        ]),
        html.Div([
            html.Div([
                html.Label("Eje Y (agrupador principal):", style={'fontWeight': 'bold'}),
                dcc.Dropdown(id='selector-y-bar', options=[{"label": c, "value": c} for c in categorical_columns],
                            value="Motivo", clearable=False)
            ], style={'width': '30%', 'display': 'inline-block'}),
            html.Div([
                html.Label("Color (variable a comparar):", style={'fontWeight': 'bold'}),
                dcc.Dropdown(id='selector-color', options=[{"label": c, "value": c} for c in categorical_columns + temporal_columns if c in df.columns],
                            value="Intervencion", clearable=False)
            ], style={'width': '30%', 'display': 'inline-block', 'marginLeft': '20px'})
        ]),
        dcc.Graph(id="bar-chart", style={"height": "70vh", "marginTop": "20px"})
    ], style={'padding': '20px', 'borderRadius': '10px', 'marginBottom': '30px'}),

    # ==================== SECCIÓN 5 ====================
    html.Div([
        html.Div([
            html.H2("5. Distribución Geográfica de Intervenciones",
                    style={'color': COLORS['dark'], 'borderLeft': f'5px solid {COLORS["primary"]}', 'paddingLeft': '15px'}),
            html.P("""Las coordenadas nor permiten construir un mapa de calor, que muestra las zonas con
            mayor concentración de intervenciones. Estas resultan ser las grandes áreas urbanas (exceptuando
            Bilbao, que cuenta con su propio cuerpo de bomberos) y filtrando los incendios podremos ver que
            suceden en estas, confirmando que la mayoría son urbanos y no rurales. Los accidentes de tráfico
            siguen las principales autovías y la neutralización de avisperos se extiende a las áreas rurales.
            Podemos ver un mapa de puntos con las intervenciones concretas, además de poder filtrar por muchas
            variables.""",
                   style={'color': COLORS['dark'], 'marginBottom': '20px'}),
        ]),
        html.Div([
            html.Div([html.Label("Motivo:"), dcc.Dropdown(id="filtro-tipo-map", options=[{"label": t, "value": t} for t in tipos_disponibles], value="Todos")], style={"width": "32%", "display": "inline-block"}),
            html.Div([html.Label("Origen aviso:"), dcc.Dropdown(id="filtro-origen-map", options=[{"label": o, "value": o} for o in origen_disponible], value="Todos")], style={"width": "32%", "display": "inline-block"}),
            html.Div([html.Label("Intervención:"), dcc.Dropdown(id="filtro-intervencion-map", options=[{"label": i, "value": i} for i in intervencion_disponible], value="Todos")], style={"width": "32%", "display": "inline-block"})
        ]),
        html.Div([
            html.Div([html.Label("Franja horaria:"), dcc.Dropdown(id="filtro-franja-map", options=[{"label": f, "value": f} for f in franjas_disponibles], value="Todos")], style={"width": "32%", "display": "inline-block"}),
            html.Div([html.Label("Año:"), dcc.Dropdown(id="filtro-año-map", options=[{"label": a, "value": a} for a in años_disponibles], value="Todos")], style={"width": "32%", "display": "inline-block"}),
            html.Div([html.Label("Mes:"), dcc.Dropdown(id="filtro-mes-map", options=[{"label": m, "value": m} for m in meses_disponibles], value="Todos")], style={"width": "32%", "display": "inline-block"})
        ]),
        html.Div([
            html.Div([html.Label("Heridos:"), dcc.RangeSlider(id="rango-heridos-map", min=0, max=max_heridos, step=1, value=[0, max_heridos])], style={"width": "30%", "display": "inline-block"}),
            html.Div([html.Label("Fallecidos:"), dcc.RangeSlider(id="rango-fallecidos-map", min=0, max=max_fallecidos, step=1, value=[0, max_fallecidos])], style={"width": "30%", "display": "inline-block"}),
            html.Div([html.Label("Recursos:"), dcc.RangeSlider(id="rango-recursos-map", min=0, max=max_recursos, step=1, value=[0, max_recursos])], style={"width": "30%", "display": "inline-block"})
        ]),
        html.Div([
            html.Div([html.Label("Radio mapa:"), dcc.Slider(id="radio-slider-map", min=5, max=30, step=1, value=20)], style={"width": "48%", "display": "inline-block"}),
            html.Div([html.Label("Tipo mapa:"), dcc.RadioItems(id="mapa-tipo-map", options=[{"label": "Calor", "value": "density"}, {"label": "Puntos", "value": "scatter"}],
                        value="density", inline=True)], style={"width": "48%", "display": "inline-block"})
        ]),
        dcc.Graph(id="mapa-calor", style={"height": "65vh", "marginTop": "10px"})
    ], style={'backgroundColor': COLORS['background'], 'padding': '20px', 'borderRadius': '10px', 'marginBottom': '30px'}),

    # ==================== SECCIÓN 6 ====================
    html.Div([
        html.Div([
            html.H2("6. Distribución de Recursos destinados y de Víctimas",
                    style={'color': COLORS['dark'], 'borderLeft': f'5px solid {COLORS["primary"]}', 'paddingLeft': '15px'}),
            html.P("""Dos últimas variables de interés: Los recursos destinados en cada intervención y
            las víctimas resultantes (heridos o fallecidos). Separando los recursos destinados por municipio
            vemos que Bermeo tiene una mediana superior al resto, mientras que Galdakao tiene el outlier de
            mayor tamaño. Separando por motivo, vemos que los incendios tienen outliers con muchos recursos
            destinados, pero que las alertas de suicidio son las que de media más recursos desplazan.
            Afortunadamente, no suelen resultar víctimas en ningún tipo de intervención y la media es
            consistentemente 0, por lo que los outliers son lo más interesante de la segunda gráfica.""",
                   style={'color': COLORS['dark'], 'marginBottom': '20px'})
        ]),
        html.Div([
            html.Div([
                html.Label("Selecciona categoría para Recursos:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(id='categoria-dropdown-recursos', options=[{'label': c, 'value': c} for c in ['Motivo', 'Origen', 'Intervencion', 'Año', 'Mes', 'Franja', 'Lugar']],
                            value='Lugar', clearable=False)
            ], style={'width': '48%', 'display': 'inline-block'}),
            html.Div([
                html.Label("Selecciona categoría para Víctimas:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(id='categoria-dropdown-victimas', options=[{'label': c, 'value': c} for c in ['Motivo', 'Origen', 'Intervencion', 'Año', 'Mes', 'Franja', 'Lugar']],
                            value='Motivo', clearable=False)
            ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'})
        ], style={'marginBottom': '30px'}),
        html.Div([
            html.Div([dcc.Graph(id='grafico-violin-recursos', style={'height': '700px'})], style={'width': '48%', 'display': 'inline-block'}),
            html.Div([dcc.Graph(id='grafico-violin-victimas', style={'height': '700px'})], style={'width': '48%', 'display': 'inline-block', 'float': 'right'})
        ])
    ], style={'padding': '20px', 'borderRadius': '10px', 'marginBottom': '30px'}),

    # FOOTER
    html.P("Visualización creada por Xabier Rodríguez para la asignatura Visualización de Datos del máster de Ciencia de Datos de la UOC. Datos: Intervenciones del SPEIS de Bizkaia (Open Data Bizkaia, https://www.opendatabizkaia.eus/es/catalogo/intervenciones-speis)",
           style={'color': '#555', 'marginBottom': '20px', 'textAlign': 'center', 'fontSize': '12px'})
])

# ==================== CALLBACKS ====================

@callback(
    [Output('histogram-plot', 'figure'), Output('pie-plot', 'figure')],
    [Input('categorical-dropdown', 'value'), Input('pie-dropdown', 'value')]
)
def update_categorical_plots(selected_col, selected_pie):
    top_hist = df[selected_col].value_counts().head(14).reset_index()
    top_hist.columns = [selected_col, 'frecuencia']
    hist_fig = px.bar(top_hist, x=selected_col, y='frecuencia', title=f'Histograma de {selected_col}',
                      color='frecuencia', color_continuous_scale='Oranges', text='frecuencia')
    hist_fig.update_traces(textposition='outside', marker_line_color=COLORS['primary'], marker_line_width=0.5)

    top_pie = df[selected_pie].value_counts().head(14).reset_index()
    top_pie.columns = [selected_pie, 'frecuencia']
    pie_fig = px.pie(top_pie, values='frecuencia', names=selected_pie, title=f'Distribución de {selected_pie}',
                     hole=0.3, color_discrete_sequence=px.colors.qualitative.Dark2)
    return hist_fig, pie_fig

@callback(
    Output('temporal-line', 'figure'),
    [Input('motivo-filter', 'value'), Input('origen-filter', 'value')]
)
def update_temporal_plot(selected_motivo, selected_origen):
    filtered_data = df.copy()
    if selected_motivo != 'Todos':
        filtered_data = filtered_data[filtered_data['Motivo'] == selected_motivo]
    if selected_origen != 'Todos':
        filtered_data = filtered_data[filtered_data['Origen'] == selected_origen]

    filtered_df = filtered_data.groupby(["Año", "Mes", "Fecha"]).size().reset_index(name="intervenciones").sort_values("Fecha")

    fig = px.line(filtered_df, x="Mes", y="intervenciones", color="Año",
                  title="Comparación estacional por año (meses superpuestos)", markers=True,
                  color_discrete_sequence=px.colors.qualitative.Dark2)
    fig.update_xaxes(tickmode="array", tickvals=list(range(1,13)),
                     ticktext=["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"])
    return fig

@callback(
    Output("heatmap", "figure"),
    [Input("selector-x", "value"), Input("selector-y", "value"),
     Input("filtro-tipo", "value"), Input("filtro-año", "value"), Input("filtro-franja", "value"),
     Input("filtro-origen", "value"), Input("filtro-mes", "value"), Input("filtro-intervencion", "value"),
     Input("rango-heridos", "value"), Input("rango-fallecidos", "value"), Input("rango-recursos", "value")]
)
def update_heatmap(x_col, y_col, tipo, año, franja, origen, mes, intervencion, rango_heridos, rango_fallecidos, rango_recursos):
    df_filtrado = df.copy()
    if tipo != "Todos": df_filtrado = df_filtrado[df_filtrado["Motivo"] == tipo]
    if año != "Todos": df_filtrado = df_filtrado[df_filtrado["Año"] == año]
    if franja != "Todos": df_filtrado = df_filtrado[df_filtrado["Franja"] == franja]
    if origen != "Todos": df_filtrado = df_filtrado[df_filtrado["Origen"] == origen]
    if mes != "Todos": df_filtrado = df_filtrado[df_filtrado["Mes"] == mes]
    if intervencion != "Todos": df_filtrado = df_filtrado[df_filtrado["Intervencion"] == intervencion]

    df_filtrado = df_filtrado[(df_filtrado["Heridos"] >= rango_heridos[0]) & (df_filtrado["Heridos"] <= rango_heridos[1])]
    df_filtrado = df_filtrado[(df_filtrado["Fallecidos"] >= rango_fallecidos[0]) & (df_filtrado["Fallecidos"] <= rango_fallecidos[1])]
    df_filtrado = df_filtrado[(df_filtrado["Recursos"] >= rango_recursos[0]) & (df_filtrado["Recursos"] <= rango_recursos[1])]

    heatmap_data = df_filtrado.groupby([x_col, y_col]).size().reset_index(name="frecuencia")
    heatmap_data[x_col] = heatmap_data[x_col].astype(str)
    heatmap_data[y_col] = heatmap_data[y_col].astype(str)

    category_orders = {}
    if x_col == "Mes": category_orders[x_col] = ["1","2","3","4","5","6","7","8","9","10","11","12"]
    if y_col == "Mes": category_orders[y_col] = ["1","2","3","4","5","6","7","8","9","10","11","12"]

    fig = px.density_heatmap(heatmap_data, x=x_col, y=y_col, z="frecuencia",
                              title=f"Frecuencia por {x_col} y {y_col} ({len(df_filtrado)} intervenciones)",
                              color_continuous_scale="Oranges", text_auto=True, category_orders=category_orders)
    fig.update_layout(height=600)
    return fig

@callback(
    Output("bar-chart", "figure"),
    [Input("selector-y-bar", "value"), Input("selector-color", "value")]
)
def update_chart(var_y, var_col):
    df_temp = df.copy()
    if var_y in ["Año", "Mes"]: df_temp[var_y] = df_temp[var_y].astype(str)
    if var_col in ["Año", "Mes"]: df_temp[var_col] = df_temp[var_col].astype(str)

    temp_df = df.groupby([var_y, var_col]).size().reset_index(name="frecuencia")
    temp_df["porcentaje"] = temp_df.groupby(var_y)["frecuencia"].transform(lambda x: x / x.sum() * 100)

    if var_col == "Mes":
        orden = [str(i) for i in range(1, 13) if str(i) in temp_df[var_col].unique()]
    else:
        orden = temp_df.groupby(var_col)["frecuencia"].sum().sort_values(ascending=False).index.tolist()

    fig = px.bar(temp_df, x="porcentaje", y=var_y, color=var_col, category_orders={var_col: orden},
                 title=f"Porcentaje de cada {var_col} separado por {var_y}",
                 labels={"porcentaje": "Porcentaje (%)"}, height=max(500, temp_df[var_y].nunique() * 40),
                 color_discrete_sequence=px.colors.qualitative.Dark2)
    return fig

@callback(
    Output("mapa-calor", "figure"),
    [Input("filtro-tipo-map", "value"), Input("filtro-año-map", "value"), Input("filtro-mes-map", "value"),
     Input("filtro-franja-map", "value"), Input("filtro-origen-map", "value"), Input("filtro-intervencion-map", "value"),
     Input("rango-heridos-map", "value"), Input("rango-fallecidos-map", "value"), Input("rango-recursos-map", "value"),
     Input("radio-slider-map", "value"), Input("mapa-tipo-map", "value")]
)
def update_map(tipo, año, mes, franja, origen, intervencion, rango_heridos, rango_fallecidos, rango_recursos, radio, mapa_tipo):
    df_filtrado = df.copy()
    if tipo != "Todos": df_filtrado = df_filtrado[df_filtrado["Motivo"] == tipo]
    if año != "Todos": df_filtrado = df_filtrado[df_filtrado["Año"] == año]
    if mes != "Todos": df_filtrado = df_filtrado[df_filtrado["Mes"] == mes]
    if franja != "Todos": df_filtrado = df_filtrado[df_filtrado["Franja"] == franja]
    if origen != "Todos": df_filtrado = df_filtrado[df_filtrado["Origen"] == origen]
    if intervencion != "Todos": df_filtrado = df_filtrado[df_filtrado["Intervencion"] == intervencion]

    df_filtrado = df_filtrado[(df_filtrado["Heridos"] >= rango_heridos[0]) & (df_filtrado["Heridos"] <= rango_heridos[1])]
    df_filtrado = df_filtrado[(df_filtrado["Fallecidos"] >= rango_fallecidos[0]) & (df_filtrado["Fallecidos"] <= rango_fallecidos[1])]
    df_filtrado = df_filtrado[(df_filtrado["Recursos"] >= rango_recursos[0]) & (df_filtrado["Recursos"] <= rango_recursos[1])]

    if len(df_filtrado) == 0:
        fig = go.Figure()
        fig.add_annotation(text="No hay datos con esos filtros", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig

    heatmap_geo = df_filtrado.groupby(["Longitud", "Latitud"]).size().reset_index(name="frecuencia")
    centro_mapa = {"lat": 43.25, "lon": -2.95}
    titulo = f"Intervenciones: {tipo if tipo != 'Todos' else 'Todos'} ({len(df_filtrado)} casos)"

    if mapa_tipo == "density":
        fig = px.density_map(heatmap_geo, lat="Latitud", lon="Longitud", z="frecuencia",
                            radius=radio, center=centro_mapa, zoom=10, map_style="open-street-map", title=titulo)
        fig.update_traces(colorscale="Oranges")
    else:
        fig = px.scatter_map(df_filtrado, lat="Latitud", lon="Longitud", color="Motivo",
                            hover_data=["Año", "Franja", "Victimas", "Recursos"],
                            center=centro_mapa, zoom=10, map_style="carto-positron", title=titulo,
                            color_discrete_sequence=px.colors.qualitative.Dark2)
    fig.update_layout(margin={"r":0, "t":40, "l":0, "b":0})
    return fig

def create_violin_plot(df, categoria, variable, titulo):
    top_20 = df[categoria].value_counts().head(20).index
    datos_por_categoria, etiquetas = [], []

    for cat in top_20:
        valores = df[df[categoria] == cat][variable].dropna()
        if len(valores) >= 5:
            datos_por_categoria.append(valores.values)
            etiqueta = str(cat)[:37] + '...' if len(str(cat)) > 40 else str(cat)
            etiquetas.append(etiqueta)

    medianas = [np.median(d) for d in datos_por_categoria]
    indices_orden = np.argsort(medianas)
    datos_ordenados = [datos_por_categoria[i] for i in indices_orden]
    etiquetas_ordenadas = [etiquetas[i] for i in indices_orden]

    colores = n_colors('rgb(230, 126, 34)', 'rgb(192, 57, 43)', len(datos_ordenados), colortype='rgb')

    fig = go.Figure()
    for datos, color, etiqueta in zip(datos_ordenados, colores, etiquetas_ordenadas):
        fig.add_trace(go.Violin(x=datos, line_color=color, name=etiqueta, orientation='h', side='positive',
                                 width=2.5, points='outliers', marker=dict(size=3, opacity=0.4, color='gray'),
                                 meanline_visible=True, fillcolor='rgba(200, 200, 200, 0.1)',
                                 hovertemplate=f"<b>{etiqueta}</b><br>Mediana: %{{x:.1f}}<br>Casos: %{{text}}<extra></extra>",
                                 text=[f"{len(datos)}"] * len(datos)))

    fig.update_layout(title=titulo, title_x=0.5, xaxis_title=variable.capitalize(),
                      height=max(600, len(datos_ordenados) * 35), showlegend=False,
                      margin=dict(l=200, r=30, t=50, b=30), plot_bgcolor='white',
                      xaxis=dict(showgrid=True, gridcolor='lightgray', zeroline=True))
    return fig

@callback(Output('grafico-violin-recursos', 'figure'), Input('categoria-dropdown-recursos', 'value'))
def update_recursos_violin(categoria):
    return create_violin_plot(df, categoria, 'Recursos', f"Distribución de recursos por {categoria}")

@callback(Output('grafico-violin-victimas', 'figure'), Input('categoria-dropdown-victimas', 'value'))
def update_victimas_violin(categoria):
    return create_violin_plot(df, categoria, 'Victimas', f"Número de víctimas por {categoria}")

if __name__ == '__main__':
    app.run(debug=True, port=2071)
