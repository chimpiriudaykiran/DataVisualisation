import plotly.express as px
import plotly.io as pio

import plotly.io as pio
print(pio.orca.status)
print(pio.kaleido.scope)

pio.orca.config.executable = r'C:\Users\chuda\AppData\Local\Programs\orca\orca.exe'
pio.orca.config.save()
print(pio.orca.status)

import kaleido #required
print(kaleido.__version__) #0.2.1

import plotly
plotly.__version__ #5.5.0

#now this works:
import plotly.graph_objects as go

fig = go.Figure()
fig.write_image('aaa.jpg')

# Sample data
data = {
    'x': [1, 2, 3, 4, 5],
    'y': [5, 4, 3, 2, 1]
}

# Create a scatter plot
fig = px.scatter(data, x='x', y='y', title='Simple Scatter Plot')

# Export the chart as a PNG image using Kaleido
pio.write_image(fig, './simple_scatter_plot.jpg', format='jpg')

print("Chart exported as simple_scatter_plot.png")
print(plotly.__version__)