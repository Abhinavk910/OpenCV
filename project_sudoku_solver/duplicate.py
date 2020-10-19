import numpy as np
import json
from skimage import io
from PIL import Image
import cv2
from all_projects.opencv.project_sudoku_solver.sudoku import solve_sudoku, compute

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

def automatic_solve_sudoku(server):

    external_stylesheets = [dbc.themes.CYBORG]
    app = dash.Dash(server = server,external_stylesheets=external_stylesheets,
                    routes_pathname_prefix='/project_sudoku_solver/solver/')
    app.title = 'Sovle Sudoku'
    app.config.suppress_callback_exceptions = True

    filename = "all_projects/opencv/project_sudoku_solver/assets/sudoku.jpg"
    img_app3 = io.imread(filename)

    height, width, _ = img_app3.shape
    canvas_width = 500
    canvas_height = round(height * canvas_width / width)
    scale = canvas_width / width


    app.layout = dbc.Jumbotron([
        html.Div([

            html.Div([
                html.H1(children='Calcualte Sudoku'),

                dcc.Markdown('''
                 Draw on the object of interest, and press calculate'''),
                image_upload_zone('upload-image-bg'),

                html.Hr(),

                dash_canvas.DashCanvas(
                    id='canvas-bg',
                    width=canvas_width,
                    height=canvas_height,
                    scale=scale,
                    image_content=array_to_data_url(img_app3),
                    lineWidth=4,
                    goButtonTitle='Calculate',
                    hide_buttons=['line', 'zoom', 'pan'],
                ),
                html.H6(children=['Digit Box width']),
                dcc.RangeSlider(
                    id='bg-width-slider',
                    marks={i: '{}'.format(i) for i in range(5, 46)},
                    min=5,
                    max=45,
                    step=1,
                    value=[9, 30]
                ),
                html.H6(children=['Digit Box height']),
                dcc.RangeSlider(
                    id='bg-height-slider',
                    marks={i: '{}'.format(i) for i in range(5, 46)},

                    min=5,
                    max=45,
                    step=1,
                    value=[20, 40]
                ),
                html.H6(children=['Bird Eye View']),
                dcc.RadioItems(
                    id='radio-birdeye',
                    options=[
                        {'label': 'No', 'value': False},
                        {'label': 'Yes', 'value': True},
                    ],
                    value=False
                ),
                html.H6(children=['Check ??']),
                dcc.RadioItems(
                    id='radio-calculate',
                    options=[
                        {'label': 'Find Number', 'value': False},
                        {'label': 'Solve Sudoku', 'value': True},
                    ],
                    value=False
                ),

            ], className="seven columns"),

            html.Div([
                html.Hr(),
                html.Img(
                    src='https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png', width='30px'),
                #             html.A(
                #                 id='gh-link',
                #                 children=[
                #                     'View on GitHub'],
                #                 href="http://github.com/plotly/canvas-portal/"
                #                 "blob/master/apps/remove-background/app.py",
                #                 style={'color': 'black',
                #                        'border': 'solid 1px black',
                #                        'float': 'left'}
                #             ),
                html.Hr(),
                html.H3(children='How to use this app and Solve Sudoku',
                        id='bg-title'),
                html.Img(id='segmentation-bg',
                         src='all_projects/opencv/project_sudoku_solver/assets/new.gif',
                         width='40%')
            ], className="four columns")],
            className="row")
    ])


    # ----------------------- Callbacks -----------------------------


    @app.callback(Output('bg-title', 'children'),
                  [Input('canvas-bg', 'json_data')])
    def modify_bg_title(json_data):
        if json_data:
            return "First Check all digit are in green box  and then solve Sudoku"
        else:
            raise PreventUpdate


    @app.callback(Output('segmentation-bg', 'src'),
                  [Input('canvas-bg', 'json_data')],
                  [State('canvas-bg', 'image_content'),
                   State('bg-height-slider', 'value'),
                   State('bg-width-slider', 'value'),
                   State('radio-birdeye', 'value'),
                   State('radio-calculate', 'value'),
                   ])
    def update_figure_upload(string, image, height, width, birdeye, calculation):

        if string:
            if image is None:
                im = img_app3
            else:
                im = image_string_to_PILImage(image)
                im = np.asarray(im)

            dat, locsgrid, locs, gray, output_image = solve_sudoku(
                im, beyeview=birdeye, digit_h=(height[0], height[1]), digit_w=(width[0], width[1]))
            if calculation:
                dat = compute(locsgrid, locs, gray, output_image)
            return array_to_data_url(dat)
        else:
            raise PreventUpdate


    @app.callback(Output('canvas-bg', 'json_data'),
                  [Input('canvas-bg', 'image_content')])
    def clear_data(image_string):
        return ''


    @app.callback(Output('canvas-bg', 'image_content'),
                  [Input('upload-image-bg', 'contents')])
    def update_canvas_upload(image_string):
        if image_string is None:
            raise ValueError
        if image_string is not None:
            return image_string
        else:
            return None


    @app.callback(Output('canvas-bg', 'lineWidth'),
                  [Input('bg-width-slider', 'value')])
    def update_canvas_linewidth(value):
        return value

    return app.server



dbc.Col(


        dbc.Card(
            [
            dbc.CardBody(html.P(children='How to use this app and Solve Sudoku',
                    id='bg-title', className="card-text")),
            dbc.CardImg(html.Img(id='segmentation-bg',
                     src="all_projects/opencv/project_sudoku_solver/assets/sudoku.jpg",
                     ), bottom=True),
            ],
        ), width="auto"

),
