import base64
import io
import pandas as pd
import plotly.express as px
from dash import html, dcc, dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from django_plotly_dash import DjangoDash
from gtts import gTTS

speech = True

# Initialize the Dash app
app = DjangoDash('SimpleGraph')


# Function to perform TTS
def text_to_speech_base64(text, lang='en'):
    tts = gTTS(text=text, lang=lang)
    filename = 'temp_audio.mp3'
    tts.save(filename)
    return encode_audio(filename)


def encode_audio(file_path):
    with open(file_path, "rb") as audio_file:
        encoded_string = base64.b64encode(audio_file.read()).decode('utf-8')
    return "data:audio/mpeg;base64," + encoded_string


welcome_audio_base64 = text_to_speech_base64(
    "Welcome to Data Visualization application for Blind. Please hold space bar for 5 seconds to disable the speech mode.")

# Define the app layout with styled components
app.layout = html.Div([
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
    html.Div(
        children=[
            html.Div(id='progress-bar-container', children=[
                html.Div(id='progress-bar', style={'width': '0%'})
            ], style={'width': '100%', 'backgroundColor': '#ddd'}),
        ],
        style={'marginTop': '20px'}
    ),
    html.Div(id='upload-progress-value', style={'display': 'none'}),  # Hidden div to store progress value
    dcc.Interval(id='progress-interval', interval=500, n_intervals=0, disabled=True),  # Interval for updating progress
    html.Div([
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
            )
        ], style={'display': 'inline-block', 'marginRight': '20px'}),

        html.Div([
            html.Label('X-Axis:', style={'marginRight': '10px'}),
            dcc.Dropdown(id='x-axis-dropdown')
        ], style={'display': 'inline-block', 'marginRight': '20px', 'width': '180px'}),

        html.Div([
            html.Label('Y-Axis:', style={'marginRight': '10px'}),
            dcc.Dropdown(id='y-axis-dropdown', disabled=False)
        ], style={'display': 'inline-block', 'width': '180px'}),
    ], style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'marginBottom': '20px'}),

    dcc.Graph(id='graph-output'),
    html.Audio(src=welcome_audio_base64, id='tts-audio', autoPlay=True),  # Audio component for TTS
    html.Div(id='tts-trigger', style={'display': 'none'}),  # Invisible div to trigger the welcome message
    html.Div(
        id='toast-message',
        children='',
        style={
            'display': 'none',
            'position': 'fixed',
            'top': '10px',
            'right': '10px',
            'zIndex': '1000',
            'border': '1px solid #ddd',
            'borderRadius': '5px',
            'backgroundColor': '#f9f9f9',
            'padding': '10px',
            'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.2)'
        }
    ),
], style={'width': '80%', 'margin': '0 auto'})


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
    Output('graph-output', 'figure'),
    [Input('graph-type-radio', 'value'),
     Input('x-axis-dropdown', 'value'),
     Input('y-axis-dropdown', 'value'),
     Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def update_graph(graph_type, x_axis, y_axis, contents, filename):
    if contents is None or graph_type is None:
        return dash.no_update

    # Specific case for pie and histogram where y_axis is not needed
    if (graph_type == 'pie' or graph_type == 'histogram') and x_axis is None:
        return dash.no_update

    # For other graph types, check if both x_axis and y_axis are provided
    elif (graph_type != 'pie' and graph_type != 'histogram') and (x_axis is None or y_axis is None):
        return dash.no_update

    df = parse_contents(contents, filename)
    df = df.sort_values(by=x_axis)

    if graph_type == 'bar':
        fig = px.bar(df, x=x_axis, y=y_axis)
    elif graph_type == 'pie':
        pie_df = df[x_axis].value_counts().reset_index()
        pie_df.columns = [x_axis, 'count']
        fig = px.pie(pie_df, names=x_axis, values='count')
    elif graph_type == 'scatter':
        fig = px.scatter(df, x=x_axis, y=y_axis)
    elif graph_type == 'line':
        fig = px.line(df, x=x_axis, y=y_axis)
    elif graph_type == 'histogram':
        fig = px.histogram(df, x=x_axis)
    else:
        fig = dash.no_update

    return fig


@app.callback(
    Output('y-axis-dropdown', 'disabled'),
    [Input('graph-type-radio', 'value')]
)
def toggle_y_axis_dropdown(graph_type):
    return graph_type in ['pie', 'histogram']


@app.callback(
    [Output('upload-progress', 'value'),
     Output('upload-progress', 'style')],
    [Input('progress-interval', 'n_intervals')],
    [State('upload-progress-value', 'children')]
)
def update_progress_bar(n, progress_value):
    if progress_value is None:
        raise PreventUpdate

    progress = int(progress_value)
    return progress, {'display': 'block'} if progress < 100 else {'display': 'none'}

@app.callback(
    [Output('upload-data', 'children'),
     Output('upload-progress-value', 'children'),
     Output('progress-interval', 'disabled'),
     Output('toast-message', 'children'),
     Output('toast-message', 'style')],
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def handle_upload(contents, filename):
    if contents is None:
        raise PreventUpdate

    # [Your existing file parsing logic]
    # Simulate file upload progress
    progress = 0
    while progress < 100:
        progress += 10  # Simulate progress
        # Update progress value
        return dash.no_update, str(progress), False, dash.no_update, dash.no_update

    return "File Uploaded!", "100", True, "Upload Successful!", {'display': 'block'}
