import plotly.graph_objects as go

# Marker symbols to visualize
symbols = ["circle", "circle-open", "cross", "diamond", "diamond-open", "square", "square-open", "x"]

# Coordinates for placing the markers
x = list(range(len(symbols)))
y = [0] * len(symbols)
z = [0] * len(symbols)

# Create the scatter3d plot
fig = go.Figure()

for i, symbol in enumerate(symbols):
    fig.add_trace(go.Scatter3d(
        x=[x[i]],
        y=[y[i]],
        z=[z[i]],
        mode='markers+text',
        marker=dict(size=8, symbol=symbol),
        text=[symbol],
        textposition='top center',
        name=symbol
    ))

fig.update_layout(
    scene=dict(
        xaxis_title='X',
        yaxis_title='Y',
        zaxis_title='Z',
    ),
    title='Plotly 3D Scatter Marker Symbols'
)

fig.show()
