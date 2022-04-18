import ssl
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_daq as daq
import plotly.express as px

from data import *

MAPBOX_ACCESS_TOKEN: str = open("mapbox_token").read()
MAPBOX_STYLE = "mapbox://styles/plotlymapbox/cjyivwt3i014a1dpejm5r7dwr"

app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)

# This is for gunicorn
server = app.server

# Dash_DAQ elements

utc = html.Div(
    id="control-panel-utc",
    children=[
        daq.LEDDisplay(
            id="control-panel-utc-component",
            value="16:23",
            label="Time",
            size=40,
            color="#fec036",
            backgroundColor="#2b2b2b",
        )
    ],
    n_clicks=0,
)

map_toggle = daq.ToggleSwitch(
    id="control-panel-toggle-map",
    value=True,
    label=["Hide path", "Show path"],
    color="#ffe102",
    style={"color": "#black"},
)

# Side panel
# Mapbox

satellite_dropdown = dcc.Dropdown(
    id="dropdown-component",
    options=country_emissions()['Country'].unique(),
    clearable=False,
    value="France",
)

satellite_dropdown_text = html.P(
    id="satellite-dropdown-text", children=["Air Pollution", html.Br(), " Dashboard"]
)

satellite_title = html.H1(id="satellite-name", children="")

satellite_body = html.P(
    className="satellite-description", id="satellite-description", children=[""]
)

side_panel_layout = html.Div(
    id="panel-side",
    children=[
        satellite_dropdown_text,
        html.Div(id="satellite-dropdown", children=satellite_dropdown),
        html.Div(id="panel-side-text", children=[satellite_title, satellite_body]),
    ],
)

# Satellite location tracker

# Helper to straighten lines on the map
def flatten_path(xy1, xy2):
    diff_rate = (xy2 - xy1) / 100
    res_list = []
    for i in range(100):
        res_list.append(xy1 + i * diff_rate)
    return res_list


map_graph2 = html.Div(
    id="world-map-wrapper",
    children=[
        dcc.Graph(
            id="world-map",
            config={"displayModeBar": False, "scrollZoom": True},
        ),
    ],
)

# Histogram

histogram = html.Div(
    id="histogram-container",
    children=[
        html.Div(
            id="histogram-header",
            children=[
                html.H1(
                    id="histogram-title", children=["Gothenburg Protocol, LRTAP Convention"],
                )
            ],
        ),
        dcc.Graph(
            id="histogram-graph",
            config={"displayModeBar": False},
        ),
    ],
)

# -----------------------------------------------------------------------------------------------------------------------
# Mapbox

@app.callback(Output('world-map', 'figure'),
              Input('dropdown-component', 'value'))
def show_map(value):

    figure = px.scatter_mapbox(country_df(value),
                               lat="Latitude", lon="Longitude", hover_name="countryName",
                               hover_data=["EPRTRSectorCode", "emissions"],
                               color_discrete_sequence=["fuchsia"], zoom=4.5, height=650)
    figure.update_layout(mapbox_accesstoken=MAPBOX_ACCESS_TOKEN,
                         mapbox_style=MAPBOX_STYLE,
                         margin={"r": 0, "t": 0, "l": 0, "b": 0},
                         autosize=True,
                         paper_bgcolor="#1e1e1e",
                         plot_bgcolor="#1e1e1e")
    return figure


@app.callback(Output('histogram-graph', 'figure'),
              Input('dropdown-component', 'value'))
def show_histogram_graph(value):
    figure = px.bar(sector_emissions_per_country(value),
                    x='Year', y='Emissions', color='Sector_name', barmode="overlay",
                    height=750, color_discrete_sequence=px.colors.qualitative.Vivid)
    figure.update_layout(margin={'t': 30, 'r': 35, 'b': 40, 'l': 50},
                         legend=dict(title=None, orientation='h', y=1, yanchor='bottom', x=0.5, xanchor='center'),
                         font=dict(color='gray'),
                         paper_bgcolor='#2b2b2b',
                         plot_bgcolor='#2b2b2b',
                         autosize=True,
                         bargap=0.1,
                         xaxis={"dtick": 5, "gridcolor": "#636363", "showline": False},
                         yaxis={"showgrid": False})
    return figure

# -----------------------------------------------------------------------------------------------------------------------

# Control panel + map
main_panel_layout = html.Div(
    id="panel-upper-lower",
    children=[
        dcc.Interval(id="interval", interval=1 * 2000, n_intervals=0),
        map_graph2,
        html.Div(
            id="panel",
            children=[
                histogram,
                html.Div(
                    id="panel-lower",
                    children=[
                        html.Div(
                            id="panel-lower-1",
                            children=[
                                html.Div(
                                    id="panel-lower-indicators",
                                    children=[
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
)

# Root
root_layout = html.Div(
    id="root",
    children=[
        dcc.Store(id="store-placeholder")

        ,
        # For the case no components were clicked, we need to know what type of graph to preserve
        dcc.Store(id="store-data-config", data={"info_type": "", "satellite_type": 0}),
        side_panel_layout,
        main_panel_layout,
    ],
)

app.layout = root_layout



@app.callback(
    Output("satellite-name", "children"),
    [Input("satellite-dropdown-component", "value")],
)
def update_satellite_name(val):
    if val == "France":
        return "France"
    elif val == "l12-5":
        return "Satellite\nL12-5"
    else:
        return ""


@app.callback(
    Output("satellite-description", "children"),
    [Input("satellite-dropdown-component", "value")],
)
def update_satellite_description(val):
    text = "Select a satellite to view using the dropdown above."

    if val == "France":
        text = (
            "Revolution tam tam tam."
        )

    elif val == "Germany":
        text = (
            "ich liebe dih; und nine"
        )
    return text


def update_communication_component(clicks, satellite_type):
    if clicks % 2 == 0:
        return False
    else:
        return True


if __name__ == "__main__":
    app.run_server(debug=True)