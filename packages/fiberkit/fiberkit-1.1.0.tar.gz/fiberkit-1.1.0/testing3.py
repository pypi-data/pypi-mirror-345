import plotly.graph_objects as go



static_trace = go.Scatter(x=[0, 1], y=[0, 1], line_color="red")
frame1_line = go.Scatter(x=[1, 2], y=[1, 2], line_color="blue")
frame2_line = go.Scatter(x=[1, 4], y=[1, 4], line_color="blue")
frame3_line = go.Scatter(x=[3, 4], y=[3, 4], line_color="blue")

frame1_marker = go.Scatter(x=[5], y=[5], marker_color="green")
frame2_marker = go.Scatter(x=[6], y=[6], marker_color="green")
frame3_marker = go.Scatter(x=[7], y=[7], marker_color="green")

fig = go.Figure(
    data=[static_trace, frame1_line, frame1_marker],
    layout=go.Layout(xaxis=dict(range=[0, 10], autorange=False),
                     yaxis=dict(range=[0, 10], autorange=False),
                     title=dict(text="Start Title"),
                     updatemenus=[dict(type="buttons",
                                       buttons=[dict(label="Play",
                                                     method="animate",
                                                     args=[None]
                                                    )
                                               ]
                                        )
                                  ]
                     ),
    frames=[go.Frame(data=[frame1_line, frame1_marker], traces=[1,2]),
            go.Frame(data=[frame2_line, frame2_marker], traces=[1,2]),
            go.Frame(data=[frame3_line, frame3_marker], traces=[1,2])]
)

fig.show()