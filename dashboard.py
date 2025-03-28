import dash
from dash import dcc, html
import plotly.express as px
import requests
import pandas as pd
from dash.dependencies import Input, Output
from flask import Flask
import dash.dash_table as dt  # Adicione essa importação no topo


def get_flight_data():
    url = "https://opensky-network.org/api/states/all"
    response = requests.get(url)
    data = response.json()

    flights = []
    for flight in data['states'][:20]:  # Pegando os primeiros 20 voos
        flights.append({
            "Aeronave": flight[1],
            "País": flight[2],
            "Latitude": flight[6],
            "Longitude": flight[5],
            "Altitude": flight[7],
            "ICAO24": flight[0]
        })
    
    df = pd.DataFrame(flights)
    df.to_json("data/flight_history.json", orient="records")  # Salvando histórico
    return df

def create_dashboard(server):
    app = dash.Dash(server=server, routes_pathname_prefix="/dashboard/")
    df = get_flight_data()

    app.layout = html.Div(children=[
        html.H1("Airport Management Dashboard", style={'textAlign': 'center'}),

        html.Div([
            html.Label("Selecione um aeroporto (IATA/ICAO):"),
            dcc.Input(id="airport-input", type="text", placeholder="Ex: JFK, LAX, GRU"),
            html.Button("Buscar", id="search-button", n_clicks=0)
        ], style={'margin-bottom': '20px'}),

        dcc.Graph(id="flight-map"),
        dcc.Graph(id="traffic-chart"),

        html.H3("Histórico de Voos"),
        dt.DataTable(id="flight-history-table")
    ])

    @app.callback(
        Output("flight-map", "figure"),
        Output("traffic-chart", "figure"),
        Output("flight-history-table", "children"),
        Input("search-button", "n_clicks"),
        Input("airport-input", "value")
    )
    def update_dashboard(n_clicks, airport_code):
        filtered_df = df if not airport_code else df[df["Aeronave"].str.contains(airport_code, na=False)]

        # Mapa de tráfego aéreo
        map_fig = px.scatter_mapbox(filtered_df,
                                    lat="Latitude",
                                    lon="Longitude",
                                    hover_name="Aeronave",
                                    hover_data=["País", "Altitude"],
                                    zoom=2,
                                    height=500)
        map_fig.update_layout(mapbox_style="open-street-map")

        # Gráfico de tráfego aéreo
        traffic_fig = px.bar(filtered_df, x="País", y="Altitude", color="Aeronave",
                             title="Tráfego Aéreo por País", height=400)

        # Histórico de voos
        table_rows = [
            html.Tr([html.Td(filtered_df.iloc[i][col]) for col in filtered_df.columns])
            for i in range(len(filtered_df))
        ]

        return map_fig, traffic_fig, table_rows

    return app.server
