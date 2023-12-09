import base64
import io
import os

import numpy as np
import pandas as pd
import plotly.express as px
from dash import html, dcc, dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from django_plotly_dash import DjangoDash
from dash.dependencies import ClientsideFunction
import requests
import plotly.io as pio
import kaleido
from datetime import datetime

from gtts import gTTS

from DataVisualisation import settings
from home.dash_apps.finished_apps.Text_to_Speech import synthesize_text
# from home.dash_apps.finished_apps.getDownloadFolder import get_downloads_folder
# from home.dash_apps.finished_apps.getFiles import list_filenames_in_directory

# Initialize the Dash app
app = DjangoDash('SimpleGraph')

state = 'on'

# downloads_folder_path = get_downloads_folder()
# filenames, numbered_files = list_filenames_in_directory(downloads_folder_path)
#
# timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# audio_filename = f'audio/files_audio_{timestamp}.mp3'
#
# audio_file_path = os.path.join(settings.MEDIA_ROOT, audio_filename)
# synthesize_text(numbered_files, audio_file_path)
# audio_url = settings.MEDIA_URL + audio_filename

# Define the app layout with styled components
app.layout = html.Div([
    # html.Audio(src=audio_url, controls=False, autoPlay=True),
    dcc.Upload(
        id='upload-data',
        children=html.Button('Upload File', style={
            'color': 'white',
            'backgroundColor': '#007BFF',
            'padding': '10px',
            'border': 'none',
            'borderRadius': '5px',
            'cursor': 'pointer'
        }),
        multiple=False,
        accept='.csv, application/vnd.ms-excel, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        }
    ),
    html.Div(id='page-load-trigger', style={'display': 'none'}),
    html.Div([
        dcc.RadioItems(
            id='graph-type-radio',
            options=[
                {'label': 'Bar', 'value': 'bar'},
                {'label': 'Pie', 'value': 'pie'},
                {'label': 'Scatter', 'value': 'scatter'},
                {'label': 'Line', 'value': 'line'},
                {'label': 'Histogram', 'value': 'histogram'},
            ],
            value='bar',
            labelStyle={'display': 'inline-block', 'marginRight': '10px'},
            style={'display': 'inline-block'}
        ),
        html.Div([
            html.Label('X-Axis:', style={'marginRight': '10px'}),
            dcc.Dropdown(id='x-axis-dropdown')
        ], style={'display': 'inline-block', 'marginRight': '20px', 'width': '180px'}),
        html.Div([
            html.Label('Y-Axis:', style={'marginRight': '10px'}),
            dcc.Dropdown(id='y-axis-dropdown', disabled=False)
        ], style={'display': 'inline-block', 'width': '180px'}),
    ], style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'marginBottom': '20px'}),
    # dcc.Graph(id='graph-output'),
    # html.Div(id='text-output'),
    dcc.Loading(
        id="loading-1",
        type="default",  # You can choose from 'graph', 'cube', 'circle', 'dot', or 'default'
        children=[
            dcc.Graph(id='graph-output'),
            html.Div(id='text-output'),
            html.Div(html.Audio(id='audio-output', controls=True)),
        ]
    ),
    html.Div(id='initial-cookie-value', style={'display': 'none'}),
    html.Script('''
    document.addEventListener('keydown', function (e) {
        if (e.code === 'Space') {
            var audio = document.getElementById('audio-output');
            if (audio) {
                audio.play();
            }
        }
    });
''')
], style={'width': '80%', 'margin': '0 auto'})

# Function to parse uploaded file contents
def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename or 'xlsx' in filename:
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            return None
    except Exception as e:
        print(e)
        return None
    return df

# Callbacks
@app.callback(
    [Output('x-axis-dropdown', 'options'),
     Output('y-axis-dropdown', 'options')],
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def update_dropdowns(contents, filename):
    if contents is None:
        return [], []
    df = parse_contents(contents, filename)
    options = [{'label': i, 'value': i} for i in df.columns]
    return options, options

@app.callback(
    [Output('graph-output', 'figure'),
     Output('text-output', 'children'),
     Output('audio-output', 'src')],
    [Input('graph-type-radio', 'value'),
     Input('x-axis-dropdown', 'value'),
     Input('y-axis-dropdown', 'value'),
     Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def update_graph(graph_type, x_axis, y_axis, contents, filename):
    global image
    if contents is None or graph_type is None:
        return dash.no_update

    if (graph_type == 'pie' or graph_type == 'histogram') and x_axis is None:
        return dash.no_update
    elif (graph_type != 'pie' and graph_type != 'histogram') and (x_axis is None or y_axis is None):
        return dash.no_update

    df = parse_contents(contents, filename)
    if df is None:
        return dash.no_update

    df = df.sort_values(by=x_axis) if x_axis in df else df

    if graph_type == 'bar':
        fig = px.bar(df, x=x_axis, y=y_axis)
        image = fig
        highest_value = df[y_axis].max()
        lowest_value = df[y_axis].min()
        colors = fig.data[0].marker.color

        text = f"This is a bar graph plotted against {x_axis} on the X-axis and {y_axis} on the Y-axis. "
        text += f"The highest value on the Y-axis is {highest_value}, "
        text += f"the lowest value is {lowest_value}, and The colors used for markers are as follows:\n"
        for i, color in enumerate(colors):
            text += f"Bar {i + 1}: {color}\n"

    elif graph_type == 'pie':
        fig = px.pie(df, names=x_axis, values=y_axis)
        image = fig
        if fig.data and hasattr(fig.data[0], 'labels') and hasattr(fig.data[0], 'values'):
            text = f"This is a pie chart showing the distribution across different categories of {x_axis}. "
            labels = fig.data[0].labels
            values = fig.data[0].values

            # Check if labels and values are not None
            if labels is not None and values is not None:
                labels_list = list(labels)
                values_list = list(values)

                for i, label in enumerate(labels_list):
                    value = values_list[i]
                    text += f"The value for '{label}' is {value}. "
        else:
            text = "Unable to generate pie chart description."
        # try:
        #     image.write_image('image.png',engine='orca')
        #     print("Image exported successfully.")
        # except Exception as e:
        #     print(f"Error exporting image: {e}")

    elif graph_type == 'scatter':
        fig = px.scatter(df, x=x_axis, y=y_axis)
        image = fig
        text = f"This is a scatter plot with {x_axis} on the X-axis and {y_axis} on the Y-axis. "
        text += "It shows the relationship between the two variables. Look for clusters or patterns in the data points."
    elif graph_type == 'line':
        fig = px.line(df, x=x_axis, y=y_axis)
        image = fig
        text = f"This line chart plots {y_axis} against {x_axis}. "
        text += "It is useful for showing trends over time or ordered categories."
    elif graph_type == 'histogram':
        fig = px.histogram(df, x=x_axis)
        image = fig
        text = f"This histogram shows the distribution of {x_axis}. "
        text += "Each bar represents the frequency of data points in each range."
    else:
        fig = dash.no_update

    # try:
    #     image.write_image('image.png')
    #     # image_data = pio.to_image(fig, format='png', engine='orca')
    #     # with open('image.png', 'wb') as f:
    #     #     f.write(image_data)
    #     print("Image exported successfully.")
    # except Exception as e:
    #     print(f"Error exporting image: {e}")

    # if state == 'on':
    #     # fig.write_image("image.png")
    #     image = fig.to_image(format='png')
    #     # with open("image.png", "rb") as image_files:
    #     #     encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    #     #
    #     # "data:audio/mpeg;base64," + encoded_string

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_filename = f'audio/text_audio_{timestamp}.mp3'


    audio_file_path = os.path.join(settings.MEDIA_ROOT, audio_filename)

    # tts = gTTS(text)
    # tts.save(audio_file_path)
    synthesize_text(text, audio_file_path)
    audio_url = settings.MEDIA_URL + audio_filename
    # audio_url = settings.MEDIA_URL + 'text_audio_20231202_091411.mp3'
    return fig, text, audio_url

@app.callback(
    Output('y-axis-dropdown', 'disabled'),
    [Input('graph-type-radio', 'value')]
)
def toggle_y_axis_dropdown(graph_type):
    return graph_type in ['pie', 'histogram']
