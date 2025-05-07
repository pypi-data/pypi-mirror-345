import json
import pandas as pd
import dash
from dash import dcc
from dash import html, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from waitress import serve
import requests
import time
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash_extensions.javascript import arrow_function, assign
from .tools import *


def forecaster(tags, api_key, weather=None, production=None, jupyter_mode=None, raw=False):
    from tools import Flow
    flow = Flow(api_key=api_key, flow_tags=tags)
    if raw is True:
        fcst_dict = {}
        for tag in tags:
            fcst = flow.forecast(tag_name=tag, weather=weather)
            fcst_dict[tag] = fcst

        return fcst_dict
    else:
        app = dash.Dash(__name__,
                        title='Forecasting',
                        external_stylesheets=[dbc.themes.COSMO, dbc.icons.BOOTSTRAP],
                        meta_tags=[{"name": "viewport", "content": "width=device-width"}],
                        suppress_callback_exceptions=True)

        # the style arguments for the sidebar. We use position:fixed and a fixed width
        SIDEBAR_STYLE = {
            "position": "fixed",
            "top": 0,
            "left": 0,
            "bottom": 0,
            "width": "16rem",
            "padding": "2rem 1rem",
            # "background-color": "#f8f9fa",
        }

        # the styles for the main content position it to the right of the sidebar and
        # add some padding.
        CONTENT_STYLE = {
            "margin-left": "18rem",
            "margin-right": "2rem",
            "padding": "2rem 1rem",

        }
        LOGO = "https://raw.githubusercontent.com/waterworksai/pydata/main/wwvt323.png"

        navbar = dbc.Navbar(
            dbc.Container(
                [
                    html.A(
                        # Use row and col to control vertical alignment of logo / brand
                        dbc.Row(
                            [
                                dbc.Col(html.Img(src=LOGO, height="15px")),
                            ],
                            align="center",
                            className="g-0",
                        ),
                        href="/",
                        style={"textDecoration": "none"},
                    ),
                    dbc.NavLink(dbc.Button("API Docs", color='link', outline=True), href="https://www.api.waterworks.ai")

                ]
            ),
            color="white",
            # dark=True,
        )

        #saved_figures = [f for f in os.listdir(output_dir) if f.endswith('.json')]
        #options = [{'label': os.path.splitext(f)[0], 'value': f} for f in saved_figures]

        # initial_figure = from_json(initial_figure_path)

        content = html.Div(
            [html.Br(),
             dbc.Container(dbc.Row(html.H1('Forecasting', style={"text-align": "center", "font-weight": "bold"}))),
             html.Br(),
             # dbc.Container(buttons, style={'text-align':'center'})
             dbc.Row(html.P('Select flow series below.',
                            style={"text-align": "center"}, className='lead')),
             dbc.Container(dbc.Row(dbc.Select(id='tag-dropdown', options=[{'label': t, 'value': t} for t in tags])), style={'width':'30%'}),
             html.Br(),
             dbc.Container(dbc.Row(dcc.Graph(id='forecast-plot')))
             ])

        # if current_user.is_authenticated:
        app.layout = html.Div([dcc.Location(id="url"), navbar, content])


        @app.callback(
            Output('forecast-plot', 'figure'),
            [Input('tag-dropdown', 'value')]
        )
        def update_graph(tag):
            import plotly.graph_objs as go
            df = tags[tag]

            fcst = flow.forecast(tag_name=tag, weather=weather)
            df = df.iloc[-10*fcst.shape[0]:]
            trace = go.Scatter(
                name='Past flow',
                mode='lines',
                x=list(df['ds']),
                y=list(df['y']),
                marker=dict(
                    color='grey',
                    line=dict(width=1)
                )
            )
            trace1 = go.Scatter(
                name='Forecast',
                mode='lines',
                x=list(fcst['ds']),
                y=list(fcst['yhat']),
                marker=dict(
                    color='#ed729d',
                    line=dict(width=1)
                )
            )
            upper_band = go.Scatter(
                name='Upper band',
                mode='lines',
                x=list(fcst['ds']),
                y=list(fcst['hi-90']),
                line=dict(color='#A7C7E7'),
                fill='tonexty'
            )
            lower_band = go.Scatter(
                name='Lower band',
                mode='lines',
                x=list(fcst['ds']),
                y=list(fcst['lo-90']),
                line=dict(color='#A7C7E7')
            )
            data = [trace, lower_band, upper_band, trace1]

            layout = dict(title=tag+' Forecast',
                          xaxis=dict(title='Dates'))

            fig = dict(data=data, layout=layout)
            return fig

        if production is not None:
            serve(app.server, host='0.0.0.0', port=production)
        else:
            app.run_server(debug=False, jupyter_mode=jupyter_mode)

def leak_detector(tags, api_key, unit, mode='anomaly', production=None, jupyter_mode=None):
    flow = Flow(api_key=api_key, flow_tags=tags)
    app = dash.Dash(__name__,
                    title='Leak Detector',
                    external_stylesheets=[dbc.themes.COSMO, dbc.icons.BOOTSTRAP],
                    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
                    suppress_callback_exceptions=True)

    # the style arguments for the sidebar. We use position:fixed and a fixed width
    SIDEBAR_STYLE = {
        "position": "fixed",
        "top": 0,
        "left": 0,
        "bottom": 0,
        "width": "16rem",
        "padding": "2rem 1rem",
        # "background-color": "#f8f9fa",
    }

    # the styles for the main content position it to the right of the sidebar and
    # add some padding.
    CONTENT_STYLE = {
        "margin-left": "18rem",
        "margin-right": "2rem",
        "padding": "2rem 1rem",

    }
    LOGO = "https://raw.githubusercontent.com/waterworksai/pydata/main/wwvt323.png"

    navbar = dbc.Navbar(
        dbc.Container(
            [
                html.A(
                    # Use row and col to control vertical alignment of logo / brand
                    dbc.Row(
                        [
                            dbc.Col(html.Img(src=LOGO, height="15px")),
                        ],
                        align="center",
                        className="g-0",
                    ),
                    href="/",
                    style={"textDecoration": "none"},
                ),
                dbc.NavLink(dbc.Button("API Docs", color='link', outline=True), href="https://www.api.waterworks.ai")

            ]
        ),
        color="white",
        # dark=True,
    )


    if mode == 'anomaly':
        content = html.Div(
        [html.Br(),
         dbc.Container(dbc.Row(html.H1('Leak Detector', style={"text-align": "center", "font-weight": "bold"}))),
         html.Br(),
         dbc.Row(html.P('Any identified leaks will be listed below.',
                        style={"text-align": "center"}, className='lead')),
         # dbc.Container(buttons, style={'text-align':'center'})
         dcc.Loading(id='loading', children=dbc.Container(dbc.Row(dbc.Select(id='tag-dropdown')), style={'width':'30%'})),
         html.Br(),
         dbc.Row(html.P('Flow & Alarm',
                        style={"text-align": "center", 'font-weight': 'bold'}, className='lead')),
         html.Br(),
         dbc.Container(dbc.Row(dcc.Graph(id='anomaly-plot'))),
         dcc.Store(id='leak-store')
         ])
    else:
        content = html.Div(
            [html.Br(),
             dbc.Container(dbc.Row(html.H1('Leak Detector', style={"text-align": "center", "font-weight": "bold"}))),
             html.Br(),
             dbc.Row(html.P('Select Time Series Below',
                            style={"text-align": "center"}, className='lead')),
             # dbc.Container(buttons, style={'text-align':'center'})
             dcc.Loading(id='loading',
                         children=dbc.Container(dbc.Row(dbc.Select(id='tag-dropdown')), style={'width': '30%'})),
             html.Br(),
             dbc.Row(html.P('Flow, Night Flow & Trend',
                            style={"text-align": "center", 'font-weight': 'bold'}, className='lead')),
             html.Br(),
             dbc.Container(dbc.Row(dcc.Graph(id='night-plot'))),
             html.Br(),
             dbc.Row(html.P('Totals',
                            style={"text-align": "center", 'font-weight': 'bold'}, className='lead')),
             html.Br(),
             dbc.Container(dbc.Row(dcc.Graph(id='night-totals'))),
             html.Br(),
             dbc.Row(html.P('Metrics',
                            style={"text-align": "center"}, className='lead')),
             html.Div(id='night-metrics'),
             dcc.Store(id='leak-store')
             ])

    # if current_user.is_authenticated:
    app.layout = html.Div([dcc.Location(id="url"), navbar, content])

    @app.callback(
        [Output('tag-dropdown', 'options'),
         Output('leak-store','data')],
        Input('url','pathname')
    )
    def loop(pathname):
        import plotly.graph_objs as go
        options = []
        data = []
        if mode == 'anomaly':
            for tag in tags:
                d = {}
                df, active = flow.detect_leak(tag, mode=mode, unit=unit)

                if active > 0:
                    options.append({'label': tag, 'value': df.to_json(orient='records',date_format='iso')})
                else:
                    pass
                time.sleep(1)
                d['Name'] = tag
                d['Active'] = active
                data.append(d)
            return options, json.dumps(data)
        else:
            for tag in tags:
                d = {}

                fcst, avg, trend = flow.detect_leak(tag, mode=mode, unit=unit)

                options.append({'label': tag, 'value': fcst.to_json(orient='records', date_format='iso')})

                time.sleep(1)
                d['Name'] = tag
                d['Night'] = avg
                d['Trend'] = trend
                data.append(d)

            return options, json.dumps(data)


    @app.callback(
        Output('anomaly-plot', 'figure'),
        [Input('tag-dropdown', 'value')]
    )
    def update_graph(tag):
        import plotly.graph_objs as go
        df = pd.read_json(tag, orient='records')
        df = df.reset_index()


        trace = go.Scatter(
            name='Past flow',
            mode='lines',
            x=list(df['ds']),
            y=list(df['y']),
            marker=dict(
                color='grey',
                line=dict(width=1)
            )
        )

        anomaly = go.Scatter(
            name='Alarm',
            mode='markers',
            x=list(df['ds']),
            y=list(df['Alarm']),
            line=dict(color='red'),
        )

        data = [trace, anomaly]

        layout = dict(title='Potential Leaks',
                      xaxis=dict(title='Dates'))

        fig = dict(data=data, layout=layout)
        return fig

    @app.callback(
        Output('night-plot', 'figure'),
        [Input('tag-dropdown', 'value')]
    )
    def update_graph_night(tag):
        import plotly.graph_objs as go
        df = pd.read_json(tag, orient='records')
        df = df.reset_index()

        trace = go.Scatter(
            name='Past flow',
            mode='lines',
            x=list(df['ds']),
            y=list(df['y']),
            marker=dict(
                color='grey',
                line=dict(width=1)
            )
        )

        anomaly = go.Scatter(
            name='Night',
            mode='lines',
            x=list(df['ds']),
            y=list(df['night']),
            line=dict(color='red'),
        )

        data = [trace, anomaly]

        layout = dict(title='Night Flow',
                      xaxis=dict(title='Dates'))

        fig = dict(data=data, layout=layout)
        return fig

    @app.callback(
        [Output('night-totals', 'figure'), Output('night-metrics', 'children')],
        [Input('leak-store', 'data')]
    )
    def update_graph_totals(data):
        import plotly.express as px
        df = pd.read_json(data, orient='records')
        table = dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns])
        div = [dbc.Container(dbc.Row(table))]
        df = df.sort_values(by=['Night'])
        fig = px.bar(df, x='Name', y='Night')

        return fig, div

    if production is not None:
        serve(app.server, host='0.0.0.0', port=production)
    else:
        app.run_server(debug=False, jupyter_mode=jupyter_mode)

def blockage_detector(tags, api_key, production=None, jupyter_mode=None):
    if raw is True:
        blockage_list = []
        for tag in tags:
            df = tags[tag]
            x = requests.post('https://www.waterworks.ai/api/blockage',
                              json={'df': df.to_json(orient='records', date_format='iso'), 'api_key': api_key})
            js = x.json()
            # fig = plotly.io.from_json(json.dumps(js))
            fcst = pd.read_json(json.dumps(js), orient='records')
            df['ds'] = pd.to_datetime(df['ds'])
            fcst['ds'] = pd.to_datetime(fcst['ds'])
            df = df.set_index('ds')
            fcst = fcst.set_index('ds')
            df['Alarm'] = fcst['anomaly']
            active = fcst.iloc[-3:]['anomaly'].sum()

            if active > 0:
                blockage_list.append(tag)
            else:
                pass
            time.sleep(1)

        return blockage_list
    else:
        flow = Flow(api_key=api_key, flow_tags=tags)
        app = dash.Dash(__name__,
                        title='Blockage Detector',
                        external_stylesheets=[dbc.themes.COSMO, dbc.icons.BOOTSTRAP],
                        meta_tags=[{"name": "viewport", "content": "width=device-width"}],
                        suppress_callback_exceptions=True)

        # the style arguments for the sidebar. We use position:fixed and a fixed width
        SIDEBAR_STYLE = {
            "position": "fixed",
            "top": 0,
            "left": 0,
            "bottom": 0,
            "width": "16rem",
            "padding": "2rem 1rem",
            # "background-color": "#f8f9fa",
        }

        # the styles for the main content position it to the right of the sidebar and
        # add some padding.
        CONTENT_STYLE = {
            "margin-left": "18rem",
            "margin-right": "2rem",
            "padding": "2rem 1rem",

        }
        LOGO = "https://raw.githubusercontent.com/waterworksai/pydata/main/wwvt323.png"

        navbar = dbc.Navbar(
            dbc.Container(
                [
                    html.A(
                        # Use row and col to control vertical alignment of logo / brand
                        dbc.Row(
                            [
                                dbc.Col(html.Img(src=LOGO, height="15px")),
                            ],
                            align="center",
                            className="g-0",
                        ),
                        href="/",
                        style={"textDecoration": "none"},
                    ),
                    dbc.NavLink(dbc.Button("API Docs", color='link', outline=True), href="https://www.api.waterworks.ai")

                ]
            ),
            color="white",
            # dark=True,
        )

        content = html.Div(
            [html.Br(),
             dbc.Container(dbc.Row(html.H1('Blockage Detector', style={"text-align": "center", "font-weight": "bold"}))),
             html.Br(),
             dbc.Row(html.P('Any identified blockages will be listed below.',
                            style={"text-align": "center"}, className='lead')),
             dcc.Loading(id='loading',
                         children=dbc.Container(dbc.Row(dbc.Select(id='tag-dropdown')), style={'width': '30%'})),
             html.Br(),
             dbc.Row(html.P('Flow & Alarm',
                            style={"text-align": "center", 'font-weight': 'bold'}, className='lead')),
             html.Br(),
             dbc.Container(dbc.Row(dcc.Graph(id='anomaly-plot')))
             ])

        # if current_user.is_authenticated:
        app.layout = html.Div([dcc.Location(id="url"), navbar, content])

        @app.callback(
            Output('tag-dropdown', 'options'),
            Input('url', 'pathname')
        )
        def loop(pathname):
            import plotly.graph_objs as go
            options = []
            for tag in tags:
                df, active = flow.detect_blockage(tag)
                if active > 0:
                    options.append({'label': tag, 'value': df.to_json(orient='records', date_format='iso')})
                else:
                    pass
                time.sleep(1)

            return options

        @app.callback(
            Output('anomaly-plot', 'figure'),
            [Input('tag-dropdown', 'value')]
        )
        def update_graph(tag):
            import plotly.graph_objs as go
            df = pd.read_json(tag, orient='records')
            df = df.reset_index()

            trace = go.Scatter(
                name='Past flow',
                mode='lines',
                x=list(df['ds']),
                y=list(df['y']),
                marker=dict(
                    color='grey',
                    line=dict(width=1)
                )
            )

            anomaly = go.Scatter(
                name='Alarm',
                mode='markers',
                x=list(df['ds']),
                y=list(df['Alarm']),
                line=dict(color='red'),
            )

            data = [trace, anomaly]

            layout = dict(title='Potential Blockages',
                          xaxis=dict(title='Dates'))

            fig = dict(data=data, layout=layout)
            return fig

        if production is not None:
            serve(app.server, host='0.0.0.0', port=production)
        else:
            app.run_server(debug=False, jupyter_mode=jupyter_mode)

def inflow_infiltration(tags, api_key, infil_mode='pe', aggregate=False, coordinates=False, person_equivalents=None, snowmelt=False, production=None, jupyter_mode=None):
    from tools import Flow
    flow = Flow(api_key, flow_tags=tags)
    app = dash.Dash(__name__,
                    title='Inflow & Infiltration',
                    external_stylesheets=[dbc.themes.COSMO, dbc.icons.BOOTSTRAP],
                    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
                    suppress_callback_exceptions=True)

    # the style arguments for the sidebar. We use position:fixed and a fixed width
    SIDEBAR_STYLE = {
        "position": "fixed",
        "top": 0,
        "left": 0,
        "bottom": 0,
        "width": "16rem",
        "padding": "2rem 1rem",
        # "background-color": "#f8f9fa",
    }

    # the styles for the main content position it to the right of the sidebar and
    # add some padding.
    CONTENT_STYLE = {
        "margin-left": "18rem",
        "margin-right": "2rem",
        "padding": "2rem 1rem",

    }
    LOGO = "https://raw.githubusercontent.com/waterworksai/pydata/main/wwvt323.png"

    navbar = dbc.Navbar(
        dbc.Container(
            [
                html.A(
                    # Use row and col to control vertical alignment of logo / brand
                    dbc.Row(
                        [
                            dbc.Col(html.Img(src=LOGO, height="15px")),
                        ],
                        align="center",
                        className="g-0",
                    ),
                    href="/",
                    style={"textDecoration": "none"},
                ),
                dbc.NavLink(dbc.Button("API Docs", color='link', outline=True), href="https://www.api.waterworks.ai")

            ]
        ),
        color="white",
        # dark=True,
    )

    if aggregate:

        content = html.Div(
            [html.Br(),
             dbc.Container(
                 dbc.Row(html.H1('Inflow & Infiltration', style={"text-align": "center", "font-weight": "bold"}))),
             html.Br(),
             # dbc.Container(buttons, style={'text-align':'center'})
             dbc.Container(
                 dbc.Row(html.H3('Aggregated Analysis', style={"text-align": "center", "font-weight": "bold"}))),
             html.Br(),
             dcc.Loading(id='loading', children=[
                 dbc.Row(html.P('Select flow component.',
                                style={"text-align": "center"}, className='lead')),
                 dbc.Container(dbc.Row(html.Div(
                     [
                         dbc.Tabs(
                             id="tabs",
                             active_tab='tab-1'
                         ),
                     ]
                 )))
             ]),
             html.Br(),
             dbc.Container(
                 dbc.Row(html.H3('Individual Analysis', style={"text-align": "center", "font-weight": "bold"}))),
             html.Br(),
             dbc.Row(html.P('Select flow series below.',
                            style={"text-align": "center"}, className='lead')),
             dbc.Container(dbc.Row(dbc.Select(id='tag-dropdown-agg')),
                           style={'width': '30%'}),
             html.Br(),
             dbc.Row(html.P('Flow composition over time',
                            style={"text-align": "center", 'font-weight': 'bold'}, className='lead')),
             html.Br(),
             dbc.Container(dbc.Row(dcc.Graph(id='anomaly-plot-agg'))),
             html.Br(),
             dbc.Row(html.P('Flow totals',
                            style={"text-align": "center", 'font-weight': 'bold'}, className='lead')),
             html.Br(),
             dbc.Container(dbc.Row(dcc.Graph(id='volume-plot-agg'))),
             html.Div(id='snowmelt-div')

             ])

    else:
        content = html.Div(
            [html.Br(),
             dbc.Container(
                 dbc.Row(html.H1('Inflow & Infiltration', style={"text-align": "center", "font-weight": "bold"}))),
             html.Br(),
             # dbc.Container(buttons, style={'text-align':'center'})
             dbc.Row(html.P('Select flow series below.',
                            style={"text-align": "center"}, className='lead')),
             dbc.Container(dbc.Row(dbc.Select(id='tag-dropdown', options=[{'label': t, 'value': t} for t in tags])),
                           style={'width': '30%'}),
             html.Br(),
             dbc.Row(html.P('Flow composition over time',
                            style={"text-align": "center", 'font-weight': 'bold'}, className='lead')),
             html.Br(),
             dbc.Container(dbc.Row(dcc.Graph(id='anomaly-plot'))),
             html.Br(),
             dbc.Row(html.P('Flow totals',
                            style={"text-align": "center", 'font-weight': 'bold'}, className='lead')),
             html.Br(),
             dbc.Container(dbc.Row(dcc.Graph(id='volume-plot'))),
             html.Div(id='snowmelt-div')

             ])

    # if current_user.is_authenticated:
    app.layout = html.Div([dcc.Location(id="url"), navbar, content])

    @app.callback([Output('tabs', 'children'), Output('tag-dropdown-agg', 'options')],
                  Input("url", "pathname"))
    def loop(pathname):
        import json
        df_agg = pd.DataFrame()
        options_individual = []
        for tag in tags:
            df_ = pd.DataFrame()
            if infil_mode == 'pe' and person_equivalents is not None:
                fcst, vol, inflow_rainfall, inflow_snowmelt = flow.inflow_infiltration(tag, infil_mode=infil_mode,
                                                                                       person_equivalents=
                                                                                       person_equivalents[tag])
            else:
                fcst, vol, inflow_rainfall, inflow_snowmelt = flow.inflow_infiltration(tag, infil_mode=infil_mode)

            if 'Infiltration' in vol['Type'].tolist():
                df_['Name'] = [tag]
                df_['Sewage'] = [
                    round(100 * (vol.loc[vol['Type'] == 'Sewage'].iloc[0]['Volume'] / vol['Volume'].sum()))]
                df_['Inflow'] = [
                    round(100 * (vol.loc[vol['Type'] == 'Inflow'].iloc[0]['Volume'] / vol['Volume'].sum()))]
                df_['Infiltration'] = [
                    round(10 * (vol.loc[vol['Type'] == 'Infiltration'].iloc[0]['Volume'] / vol['Volume'].sum()))]
                if coordinates:
                    df_['Lat'] = [coordinates[tag][0]]
                    df_['Lon'] = [coordinates[tag][1]]
                else:
                    df_['Lat'] = None
                    df_['Lon'] = None
                df_agg = pd.concat([df_agg, df_])

            else:
                df_['Name'] = [tag]
                df_['Sewage'] = [
                    round(100 * (vol.loc[vol['Type'] == 'Sewage'].iloc[0]['Volume'] / vol['Volume'].sum()))]
                df_['Inflow'] = [
                    round(100 * (vol.loc[vol['Type'] == 'Inflow'].iloc[0]['Volume'] / vol['Volume'].sum()))]
                df_['Infiltration'] = [None]
                if coordinates:
                    df_['Lat'] = [coordinates[tag][0]]
                    df_['Lon'] = [coordinates[tag][1]]
                else:
                    df_['Lat'] = None
                    df_['Lon'] = None
                df_agg = pd.concat([df_agg, df_])

            options_individual.append({'label': tag,
                                       'value': json.dumps({'df': fcst.to_json(orient='records',
                                                                               date_format='iso'),
                                                            'vol': vol.to_json(orient='records')})})
        # options = [{'label':'Sewage','value':df_agg[['Name', 'Sewage', 'Lat','Lon']].to_json(orient='records', date_format='iso')},
        #           {'label':'Inflow','value':df_agg[['Name', 'Inflow','Lat','Lon']].to_json(orient='records', date_format='iso')},
        #           {'label':'Infiltration','value':df_agg[['Name', 'Infiltration','Lat','Lon']].to_json(orient='records', date_format='iso')}]
        import plotly.express as px

        if coordinates:
            df_agg['Size'] = 4  # size=plot
            fig_map1 = px.scatter_mapbox(df_agg, lat="Lat", lon="Lon", color='Sewage', size='Size', hover_name='Name',
                                         color_continuous_scale='ylorrd', size_max=15, mapbox_style='carto-positron')
            fig_map2 = px.scatter_mapbox(df_agg, lat="Lat", lon="Lon", color='Inflow', size='Size', hover_name='Name',
                                         color_continuous_scale='ylorrd', size_max=15, mapbox_style='carto-positron')

        df_ = df_agg.sort_values(by=['Sewage'], ascending=False)
        fig_sort = px.bar(df_, x='Name', y='Sewage')
        tab1 = [dbc.Container(dbc.Row(dcc.Graph(figure=fig_map1, style={'height': '800px'}))),
                html.Br(),
                dbc.Row(html.P('Totals',
                               style={"text-align": "center"}, className='lead')),
                html.Br(),
                dbc.Container(dbc.Row(dcc.Graph(figure=fig_sort, id='totals')))]

        df_ = df_agg.sort_values(by=['Inflow'], ascending=False)
        fig_sort = px.bar(df_, x='Name', y='Inflow')
        tab2 = [dbc.Container(dbc.Row(dcc.Graph(figure=fig_map2, style={'height': '800px'}))),
                html.Br(),
                dbc.Row(html.P('Totals',
                               style={"text-align": "center"}, className='lead')),
                html.Br(),
                dbc.Container(dbc.Row(dcc.Graph(figure=fig_sort, id='totals')))]
        if 'Infiltration' in df_agg.columns:
            if coordinates:
                df_agg['Size'] = 4  # size=plot
                fig_map3 = px.scatter_mapbox(df_agg, lat="Lat", lon="Lon", color='Infiltration', size='Size',
                                             hover_name='Name',
                                             color_continuous_scale='ylorrd', size_max=15,
                                             mapbox_style='carto-positron')

            df_ = df_agg.sort_values(by=['Infiltration'], ascending=False)
            fig_sort = px.bar(df_, x='Name', y='Infiltration')
            tab3 = [dbc.Container(dbc.Row(dcc.Graph(figure=fig_map3, style={'height': '800px'}))),
                    html.Br(),
                    dbc.Row(html.P('Totals',
                                   style={"text-align": "center"}, className='lead')),
                    html.Br(),
                    dbc.Container(dbc.Row(dcc.Graph(figure=fig_sort, id='totals')))]
            tabs = [
                dbc.Tab(tab1, label="Sewage", tab_id="tab-1"),
                dbc.Tab(tab2, label="Inflow", tab_id="tab-2"),
                dbc.Tab(tab3, label="Infiltration", tab_id="tab-3"),
            ]
        else:
            tabs = [
                dbc.Tab(tab1, label="Sewage", tab_id="tab-1"),
                dbc.Tab(tab2, label="Inflow", tab_id="tab-2"),
                dbc.Tab(label="Infiltration", tab_id="tab-3", disabled=True),
            ]

        return [tabs, options_individual]

    @app.callback(
        [Output('anomaly-plot-agg', 'figure'), Output('volume-plot-agg', 'figure')],  # snowmelt
        [Input('tag-dropdown-agg', 'value')]
    )
    def update_graph_agg(tag):
        import requests
        import plotly.graph_objs as go
        import plotly.express as px
        import json
        fcst = pd.read_json(json.loads(tag)['df'], orient='records')
        vol = pd.read_json(json.loads(tag)['vol'], orient='records')
        if infil_mode == 'pe' and person_equivalents is not None:

            inflow = go.Scatter(
                name='Inflow',
                mode='lines',
                x=list(fcst['ds']),
                y=list(fcst['y']),
                marker=dict(
                    color='#4C78A8',
                    # line=dict(width=1)
                ),
                fill='tonexty'

            )
            sewage = go.Scatter(
                name='Sewage',
                mode='lines',
                x=list(fcst['ds']),
                y=list(fcst['DWF']),
                line=dict(color='#E45756'),
                fill='tonexty'

            )
            infiltration = go.Scatter(
                name='Infiltration',
                mode='lines',
                x=list(fcst['ds']),
                y=list(fcst['BF']),
                line=dict(color='#9D755D'),
                fill='tozeroy'

            )

            data = [infiltration, sewage, inflow]
        elif infil_mode == 'night':

            inflow = go.Scatter(
                name='Inflow',
                mode='lines',
                x=list(fcst['ds']),
                y=list(fcst['y']),
                marker=dict(
                    color='#4C78A8',
                    # line=dict(width=1)
                ),
                fill='tonexty'

            )
            sewage = go.Scatter(
                name='Sewage',
                mode='lines',
                x=list(fcst['ds']),
                y=list(fcst['DWF']),
                line=dict(color='#E45756'),
                fill='tonexty'

            )
            infiltration = go.Scatter(
                name='Infiltration',
                mode='lines',
                x=list(fcst['ds']),
                y=list(fcst['BF']),
                line=dict(color='#9D755D'),
                fill='tozeroy'

            )

            data = [infiltration, sewage, inflow]
        else:
            inflow = go.Scatter(
                name='Inflow',
                mode='lines',
                x=list(fcst['ds']),
                y=list(fcst['y']),
                line=dict(color='#4C78A8'),
                # marker=dict(
                #    color='grey',
                #    line=dict(width=1)
                # ),
                fill='tonexty'

            )

            dwf = go.Scatter(
                name='Sewage',
                mode='lines',
                x=list(fcst['ds']),
                y=list(fcst['DWF']),
                line=dict(color='#E45756'),
                fill='tozeroy'

            )

            data = [dwf, inflow]

        layout = dict(title='Inflow',
                      xaxis=dict(title='Dates'))

        fig = dict(data=data, layout=layout)

        vol_fig = px.pie(vol, values='Volume', names='Type', color='Type', color_discrete_map={'Inflow': '#4C78A8',
                                                                                               'Sewage': '#E45756',
                                                                                               'Infiltration': '#9D755D'})

        return fig, vol_fig

    @app.callback(
        [Output('anomaly-plot', 'figure'), Output('volume-plot', 'figure'), Output('snowmelt-div', 'children')],
        [Input('tag-dropdown', 'value')]
    )
    def update_graph(tag):
        import requests
        import plotly.graph_objs as go
        import plotly.express as px

        if infil_mode == 'pe' and person_equivalents is not None:
            fcst, vol, inflow_rainfall, inflow_snowmelt = flow.inflow_infiltration(tag, infil_mode=infil_mode,
                                                                                   person_equivalents=
                                                                                   person_equivalents[tag])

            inflow = go.Scatter(
                name='Inflow',
                mode='lines',
                x=list(fcst['ds']),
                y=list(fcst['y']),
                marker=dict(
                    color='#4C78A8',
                    # line=dict(width=1)
                ),
                fill='tonexty'

            )
            sewage = go.Scatter(
                name='Sewage',
                mode='lines',
                x=list(fcst['ds']),
                y=list(fcst['DWF']),
                line=dict(color='#E45756'),
                fill='tonexty'

            )
            infiltration = go.Scatter(
                name='Infiltration',
                mode='lines',
                x=list(fcst['ds']),
                y=list(fcst['BF']),
                line=dict(color='#9D755D'),
                fill='tozeroy'

            )

            data = [infiltration, sewage, inflow]
        elif infil_mode == 'night':
            fcst, vol, inflow_rainfall, inflow_snowmelt = flow.inflow_infiltration(tag, infil_mode=infil_mode)

            inflow = go.Scatter(
                name='Inflow',
                mode='lines',
                x=list(fcst['ds']),
                y=list(fcst['y']),
                marker=dict(
                    color='#4C78A8',
                    # line=dict(width=1)
                ),
                fill='tonexty'

            )
            sewage = go.Scatter(
                name='Sewage',
                mode='lines',
                x=list(fcst['ds']),
                y=list(fcst['DWF']),
                line=dict(color='#E45756'),
                fill='tonexty'

            )
            infiltration = go.Scatter(
                name='Infiltration',
                mode='lines',
                x=list(fcst['ds']),
                y=list(fcst['BF']),
                line=dict(color='#9D755D'),
                fill='tozeroy'

            )

            data = [infiltration, sewage, inflow]
        else:
            fcst, vol, inflow_rainfall, inflow_snowmelt = flow.inflow_infiltration(tag, infil_mode=infil_mode)
            inflow = go.Scatter(
                name='Inflow',
                mode='lines',
                x=list(fcst['ds']),
                y=list(fcst['y']),
                line=dict(color='#4C78A8'),
                # marker=dict(
                #    color='grey',
                #    line=dict(width=1)
                # ),
                fill='tonexty'

            )

            dwf = go.Scatter(
                name='Sewage',
                mode='lines',
                x=list(fcst['ds']),
                y=list(fcst['DWF']),
                line=dict(color='#E45756'),
                fill='tozeroy'

            )

            data = [dwf, inflow]

        layout = dict(title='Inflow',
                      xaxis=dict(title='Dates'))

        fig = dict(data=data, layout=layout)

        vol_fig = px.pie(vol, values='Volume', names='Type', color='Type', color_discrete_map={'Inflow': '#4C78A8',
                                                                                               'Sewage': '#E45756',
                                                                                               'Infiltration': '#9D755D'})
        if snowmelt is True:

            season = pd.DataFrame()
            season['Inflow Type'] = ['Rainfall', 'Snowmelt']
            season['Volume'] = [inflow_rainfall,
                                inflow_snowmelt]

            season_fig = px.bar(season, x='Inflow Type', y='Volume', color='Inflow Type',
                                color_discrete_map={'Rainfall': '#4C78A8',
                                                    'Snowmelt': '#4C78A8'})
            season_fig.update_layout(
                plot_bgcolor='white'
            )

            snowmelt_div = [html.Br(),
                            dbc.Row(html.P('Rainfall vs Snowmelt',
                                           style={"text-align": "center", 'font-weight': 'bold'}, className='lead')),
                            html.Br(),
                            dbc.Container(dbc.Row(dcc.Graph(figure=season_fig)))]
        else:
            snowmelt_div = []

        return fig, vol_fig, snowmelt_div

    if production is not None:
        serve(app.server, host='0.0.0.0', port=production)
    else:
        app.run_server(debug=False, jupyter_mode=jupyter_mode)

def pipe_network(pipe_gdf, api_key, id_col=None, construction_col=None, renovation_col=None, material_col=None, dimension_col=None, length_col=None, production=None, jupyter_mode=None):
    pipes = PipeNetwork(pipe_gdf)
    gdf_lof = pipes.get_lof(api_key, id_col, construction_col, renovation_col, material_col, dimension_col, length_col)
    gdf_cof = pipes.get_cof(api_key, id_col, dimension_col)
    gdf_rof = pipes.get_rof(gdf_lof, gdf_cof, id_col)
    app = dash.Dash(__name__,
                    title='Pipe Network',
                    external_stylesheets=[dbc.themes.COSMO, dbc.icons.BOOTSTRAP],
                    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
                    suppress_callback_exceptions=True)

    # the style arguments for the sidebar. We use position:fixed and a fixed width
    SIDEBAR_STYLE = {
        "position": "fixed",
        "top": 0,
        "left": 0,
        "bottom": 0,
        "width": "16rem",
        "padding": "2rem 1rem",
        # "background-color": "#f8f9fa",
    }

    # the styles for the main content position it to the right of the sidebar and
    # add some padding.
    CONTENT_STYLE = {
        "margin-left": "18rem",
        "margin-right": "2rem",
        "padding": "2rem 1rem",

    }
    LOGO = "https://raw.githubusercontent.com/waterworksai/pydata/main/wwvt323.png"

    navbar = dbc.Navbar(
        dbc.Container(
            [
                html.A(
                    # Use row and col to control vertical alignment of logo / brand
                    dbc.Row(
                        [
                            dbc.Col(html.Img(src=LOGO, height="15px")),
                        ],
                        align="center",
                        className="g-0",
                    ),
                    href="/",
                    style={"textDecoration": "none"},
                ),
                dbc.NavLink(dbc.Button("API Docs", color='link', outline=True), href="https://www.api.waterworks.ai")

            ]
        ),
        color="white",
        # dark=True,
    )

    style_handle = {
        "variable": "dashExtensions.default.styleHandle"
    }

    content = html.Div(
        [html.Br(),
         dbc.Container(dbc.Row(html.H1('Pipe Network', style={"text-align": "center", "font-weight": "bold"}))),
         html.Br(),

         dbc.Container(dbc.Row(html.Div(
             [
                 dbc.Label("Choose Metric to Plot"),
                 dbc.RadioItems(
                     id="select",
                     options=[
                         {"label": "Condition", "value": "LoF"},
                         {"label": "Consequence", "value": "CoF"},
                         {"label": "Risk", "value": "RoF"},
                     ],
                     value='LoF',
                     inline=True,
                 ),
             ]
         )), style={'text-align': 'center'}),
         html.Br(),

         dbc.Container(dbc.Row(html.Div(id='pipe-map'))),
         html.Br(),
         dbc.Row(html.H3('Renewal Need',
                         style={"text-align": "center"}, className='lead')),
         html.Br(),
         dbc.Row(html.P('Simulates annual renewal need (km pipe) per material, based on a set renewal rate (%).',
                        style={"text-align": "center"}, className='lead')),
         dbc.Container(dbc.Row(html.Div(
             [
                 dbc.Label("Set Yearly Renewal Rate (%)", html_for="slider"),
                 dcc.Slider(id="slider", min=0, max=5, step=0.5, value=0),
             ]
         ))),
         dbc.Container(dbc.Row(dcc.Graph(id='renewal-chart'))),
         html.Br(),
         dbc.Row(html.H3('5-Year Plan',
                         style={"text-align": "center"})),
         dbc.Row(html.P('These are the pipes that should be prioritized for renewal, '
                        'based on the set renewal rate and the estimated risk of failure (RoF).',
                        style={"text-align": "center"}, className='lead')),
         dbc.Container(dbc.Row(dash_table.DataTable(id='pipe-table', style_table={
             'overflowY': 'scroll',
             'height': '250px',
         }, style_as_list_view=True))),

         ])

    # if current_user.is_authenticated:
    app.layout = html.Div([dcc.Location(id="url"), navbar, content])

    @app.callback(
        Output('pipe-map', 'children'),
        [Input('select', 'value')],
    )
    def update_map(tag):
        clr = tag
        gdf = gdf_rof.copy()
        gjs = eval(gdf[[id_col, clr, 'geometry']].dropna().to_json())
        classes = [round(gdf[clr].min(), 1), round(((gdf[clr].max() - gdf[clr].min()) / 7), 1),
                   round(2 * ((gdf[clr].max() - gdf[clr].min()) / 7), 1),
                   round(3 * ((gdf[clr].max() - gdf[clr].min()) / 7), 1),
                   round(4 * ((gdf[clr].max() - gdf[clr].min()) / 7), 1),
                   round(5 * ((gdf[clr].max() - gdf[clr].min()) / 7), 1),
                   round(6 * ((gdf[clr].max() - gdf[clr].min()) / 7), 1),
                   round(gdf[clr].max(), 1)]
        colorscale = [
            '#006837',  # dark green
            '#31a354',  # medium green
            '#78c679',  # light green
            '#c2e699',  # pale green
            '#ffffb2',  # pale yellow
            '#fecc5c',  # yellow-orange
            '#fd8d3c',  # orange
            '#e31a1c'  # red
        ]

        style = dict(weight=3, opacity=1, dashArray='3', fillOpacity=0.7)
        # Create colorbar.
        ctg = ["{}".format(cls, classes[i + 1]) for i, cls in enumerate(classes[:-1])] + ["{}".format(classes[-1])]
        colorbar = dlx.categorical_colorbar(categories=ctg, colorscale=colorscale, width=300, height=30,
                                            position="bottomleft")
        # Geojson rendering logic, must be JavaScript as it is executed in clientside.

        # Create geojson.
        geojson = dl.GeoJSON(data=gjs,  # url to geojson file
                             style=style_handle,  # how to style each polygon
                             zoomToBounds=True,  # when true, zooms to bounds when data changes (e.g. on load)
                             zoomToBoundsOnClick=True,
                             # when true, zooms to bounds of feature (e.g. polygon) on click
                             hoverStyle=arrow_function(dict(weight=5, color='#666', dashArray='')),
                             # style applied on hover
                             hideout=dict(colorscale=colorscale, classes=classes, style=style, colorProp=clr),
                             id="geojson")
        # Create info control.
        info = dbc.Card(id="info", className="info",
                        style={"position": "absolute", "top": "10px", "right": "10px", "zIndex": "1000"})
        # Create app.
        children = dl.Map(children=[
            dl.TileLayer(
                url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
                attribution=(
                    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors '
                    '&copy; <a href="https://carto.com/">CARTO</a>'
                )
            ), geojson, colorbar, info
        ], style={'height': '80vh'}, center=[56, 10], zoom=6)  # dl.TileLayer() for osm

        return children

    @app.callback(Output("info", "children"),
                  [Input('select', 'value'), Input("geojson", "hoverData")])
    def info_hover(tag, feature):
        clr = tag

        def get_info(feature=None):
            header = [html.P("Pipe Info", style={'font-weight':'bold'})]
            if not feature:
                return header + [html.P("Hover over a pipe")]
            return header + [html.B(feature["properties"][id_col]), html.Br(),
                             str(clr)+" = {}".format(feature["properties"][clr])]

        return get_info(feature)

    @app.callback([Output('renewal-chart', 'figure'),
                   Output('pipe-table', 'data'), Output('pipe-table', 'columns')],
                  Input('slider', 'value'))
    def renewal(renewal_rate):
        import plotly.express as px

        df_all, five_year_plan = pipes.get_renewal_need(renewal_rate, gdf_lof, gdf_rof, id_col, material_col, length_col)
        fig = px.area(df_all, x='Year', y='Renewal Need (km)', color='Material')
        five_year_plan = five_year_plan.drop(['geometry'], axis=1)

        return fig, five_year_plan.to_dict('records'), [{"name": i, "id": i} for i in five_year_plan.columns]

    if production is not None:
        serve(app.server, host='0.0.0.0', port=production)
    else:
        app.run_server(debug=False, jupyter_mode=jupyter_mode)

def earth_observation(api_key, municipality, dem=None, band_red_current=None, band_red_past=None, band_nir_current=None,band_nir_past=None, pipe_network_path=None, production=None, jupyter_mode=None):
    from tools import EO
    eo = EO(api_key, municipality, dem, band_red_current, band_red_past, band_nir_current, band_nir_past, pipe_network_path)

    app = dash.Dash(__name__,
                    title='Earth Observation',
                    external_stylesheets=[dbc.themes.COSMO, dbc.icons.BOOTSTRAP],
                    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
                    suppress_callback_exceptions=True)

    # the style arguments for the sidebar. We use position:fixed and a fixed width
    SIDEBAR_STYLE = {
        "position": "fixed",
        "top": 0,
        "left": 0,
        "bottom": 0,
        "width": "16rem",
        "padding": "2rem 1rem",
        # "background-color": "#f8f9fa",
    }

    # the styles for the main content position it to the right of the sidebar and
    # add some padding.
    CONTENT_STYLE = {
        "margin-left": "18rem",
        "margin-right": "2rem",
        "padding": "2rem 1rem",

    }
    LOGO = "https://raw.githubusercontent.com/waterworksai/pydata/main/wwvt323.png"

    navbar = dbc.Navbar(
        dbc.Container(
            [
                html.A(
                    # Use row and col to control vertical alignment of logo / brand
                    dbc.Row(
                        [
                            dbc.Col(html.Img(src=LOGO, height="15px")),
                        ],
                        align="center",
                        className="g-0",
                    ),
                    href="/",
                    style={"textDecoration": "none"},
                ),
                dbc.NavLink(dbc.Button("API Docs", color='link', outline=True), href="https://www.api.waterworks.ai")

            ]
        ),
        color="white",
        # dark=True,
    )

    content = html.Div(
        [html.Br(),
         dbc.Container(
             dbc.Row(html.H1('Earth Observation', style={"text-align": "center", "font-weight": "bold"}))),
         html.Br(),
         # dbc.Container(buttons, style={'text-align':'center'})
         dcc.Loading(id='loading', children=[
             dbc.Row(html.P('Select analysis.',
                            style={"text-align": "center"}, className='lead')),
             dbc.Container(dbc.Row(html.Div(
                 [
                     dbc.Tabs(
                         id="tabs",
                         active_tab='tab-1'
                     ),
                 ]
             )))
         ]),

         ])

    # if current_user.is_authenticated:
    app.layout = html.Div([dcc.Location(id="url"), navbar, content])

    @app.callback(Output('tabs', 'children'),
                  Input("url", "pathname"))
    def loop(pathname):
        import plotly.express as px
        impervious_gdf, impervious_change = eo.impervious()
        if impervious_change > 0:
            clr = 'red'
        else:
            clr = 'green'
        depressions = eo.depressions()
        water = eo.water()
        # water_ = water.copy()
        aoi = eo.aoi
        aoi['centroid'] = aoi.geometry.centroid
        lat = aoi.iloc[0]['centroid'].y
        lon = aoi.iloc[0]['centroid'].x

        fig_dem = px.choropleth_mapbox(depressions, geojson=eval(depressions['geometry'].to_json()), locations=depressions.index,
                                       center={"lat": lat, "lon": lon}, zoom=11, mapbox_style='carto-positron',
                                       opacity=0.5)
        fig_impervious = px.choropleth_mapbox(impervious_gdf, geojson=eval(impervious_gdf['geometry'].to_json()),
                                              locations=impervious_gdf.index,
                                              center={"lat": lat, "lon": lon}, zoom=11, mapbox_style='carto-positron',
                                              opacity=0.5, color='cluster')
        fig_water = px.choropleth_mapbox(water, geojson=eval(water['geometry'].to_json()), locations=water.index,
                                         center={"lat": lat, "lon": lon}, zoom=11, mapbox_style='carto-positron',
                                         opacity=0.5)

        depressions['Risk'] = 'Infiltration, Flooding'
        water['Risk'] = 'Infiltration, Flooding, Contamination'
        # water_['Risk'] = 'Contamination'
        impervious_gdf['Risk'] = 'Inflow'

        gdf_risk = pd.concat(
            [depressions[['Risk', 'geometry']], water[['Risk', 'geometry']], impervious_gdf[['Risk', 'geometry']]])
        gdf_risk = gdf_risk.reset_index()

        fig_map = px.choropleth_mapbox(gdf_risk, geojson=eval(gdf_risk['geometry'].to_json()), locations=gdf_risk.index,
                                       center={"lat": lat, "lon": lon}, zoom=11, mapbox_style='carto-positron',
                                       opacity=0.5, color='Risk')
        tab1 = [dbc.Container(dbc.Row(dcc.Graph(figure=fig_map, style={'height': '800px'}))),
                html.Br(),
                dbc.Row(html.P('Risk Map',
                               style={"text-align": "center"}, className='lead'))]

        tab2 = [dbc.Container(dbc.Row(dcc.Graph(figure=fig_impervious, style={'height': '800px'}))),
                html.Br(),
                dbc.Row(html.P('Change in Impervious Areas',
                               style={"text-align": "center"}, className='lead')),
                dbc.Container(dbc.Row(html.H2(str(round(impervious_change)) + ' %')),
                              style={'text-align': 'center', 'font-weight': 'bold', 'color': clr})]

        tab3 = [dbc.Container(dbc.Row(dcc.Graph(figure=fig_dem, style={'height': '800px'}))),
                html.Br(),
                dbc.Row(html.P('DEM Conditioning',
                               style={"text-align": "center"}, className='lead'))]

        tab4 = [dbc.Container(dbc.Row(dcc.Graph(figure=fig_water, style={'height': '800px'}))),
                html.Br(),
                dbc.Row(html.P('Water Content',
                               style={"text-align": "center"}, className='lead'))]

        tabs = [
            dbc.Tab(tab1, label="Overall Risk", tab_id="tab-1"),
            dbc.Tab(tab2, label="Impervious Areas", tab_id="tab-2"),
            dbc.Tab(tab3, label="DEM", tab_id="tab-3"),
            dbc.Tab(tab4, label="Water Bodies", tab_id="tab-4")
        ]
        return tabs

    if production is not None:
        serve(app.server, host='0.0.0.0', port=production)
    else:
        app.run_server(debug=False, jupyter_mode=jupyter_mode)