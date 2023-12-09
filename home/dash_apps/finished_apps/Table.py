import dash_table
import base64
import io
import pandas as pd
from dash import html, dcc, dash
from dash.dependencies import Input, Output, State
from django_plotly_dash import DjangoDash

# Initialize the Dash app (assuming you are embedding this in Django)
app = DjangoDash('SimpleTable')  # Replace DjangoDash with dash.Dash if you are not using Django

app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Button('Upload File', id='upload-button', n_clicks=0, style={
            'color': 'white',
            'backgroundColor': '#007BFF',
            'padding': '10px',
            'border': 'none',
            'borderRadius': '5px',
            'cursor': 'pointer'
        }),
        multiple=False,
        accept='.csv, application/vnd.ms-excel, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ),
    html.Div(id='table-container')
])


def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            return pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            return pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return None


@app.callback(
    Output('table-container', 'children'),
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def update_table(contents, filename):
    if contents is None:
        return None
    df = parse_contents(contents, filename)
    if df is not None:
        return dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns]
        )
    return 'There was an error processing this file.'
