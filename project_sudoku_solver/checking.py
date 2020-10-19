import numpy as np
import json
from skimage import io
from PIL import Image

import dash
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go

import dash_canvas
from dash_canvas.utils import (parse_jsonstring,
                               superpixel_color_segmentation,
                               image_with_contour, image_string_to_PILImage,
                               array_to_data_url)
from dash_canvas.components import image_upload_zone
import dash_bootstrap_components as dbc

external_stylesheets = [dbc.themes.GRID]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.config.suppress_callback_exceptions = True

filename = "assets/sudoku.jpg"
img_app3 = io.imread(filename)

app.layout =  html.Div(
    [dbc.Jumbotron([


        dbc.Row(
            [
                dbc.Col(html.Div("One of two columns"), width=4),
                dbc.Col(html.Div("One of two columns"), width=4),
            ],
            justify="start",
        ),
        dbc.Row(
            [
                dbc.Col(html.Div("One of two columns"), width=4),
                dbc.Col(html.Div("One of two columns"), width=4),
            ],
            justify="center",
        ),
        dbc.Row(
            [
                dbc.Col(html.Div("One of two columns"), width=4),
                dbc.Col(html.Div("One of two columns"), width=4),
            ],
            justify="end",
        ),
        dbc.Row(
            [
                dbc.Col(html.Div("One of two columns"), width=4),
                dbc.Col(html.Div("One of two columns"), width=4),
            ],
            justify="between",
        ),
        dbc.Row(
            [
                dbc.Col(dash_canvas.DashCanvas(
                                            id='canvas-bg',
                                            width=500,
                                            height=500,
                                            scale=1,
                                            image_content=array_to_data_url(img_app3),
                                            lineWidth=4,
                                            goButtonTitle='Calculate',
                                            hide_buttons=['line', 'zoom', 'pan'],
                                        ),),
                dbc.Col(dash_canvas.DashCanvas(
                                            id='canvas-bgf',
                                            width=500,
                                            height=500,
                                            scale=1,
                                            image_content=array_to_data_url(img_app3),
                                            lineWidth=4,
                                            goButtonTitle='Calculate',
                                            hide_buttons=['line', 'zoom', 'pan'],
                                        ),),
            ],
            justify="around",
        ),
        ])
    ]
)


if __name__ == '__main__':
    app.run_server(debug=True)
