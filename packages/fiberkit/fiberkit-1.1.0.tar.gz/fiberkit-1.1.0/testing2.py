#%% Moment Curvature Analysis Data
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default = "browser"   
from plotly.subplots import make_subplots
import fkit
import math

fiber_unconfined = fkit.patchfiber.Todeschini(fpc=5, take_tension=True)
fiber_confined   = fkit.patchfiber.Mander(fpc=6, eo=0.004, emax=0.014, default_color="gray", take_tension=True)
fiber_steel      = fkit.nodefiber.Bilinear(fy=60, fu=90, Es=29000)
section1 = fkit.sectionbuilder.rectangular_confined(width = 15, 
                                                    height = 24, 
                                                    cover = 1.5, 
                                                    top_bar = [0.6, 3, 1, 0], 
                                                    bot_bar = [0.6, 3, 2, 3], 
                                                    core_fiber = fiber_confined, 
                                                    cover_fiber = fiber_unconfined, 
                                                    steel_fiber = fiber_steel,
                                                    mesh_nx=0.95,
                                                    mesh_ny=0.95)

mk_results = section1.run_moment_curvature(phi_target=0.0003/2)

df_nodefibers, df_patchfibers = section1.get_all_fiber_data()



#%% Initalize Plot
fig = make_subplots(rows=1, cols=2,
                    subplot_titles=("Section Stress Profile", "Moment Curvature"),
                    column_widths=[0.5, 0.5],
                    horizontal_spacing=0.02,
                    specs = [[{"type":"scene"}, {"type":"xy"}]])

unit_moment = "k.in"
unit_curvature = "1/in"
unit_stress = "ksi"
hovertemplate = '%{text}<extra></extra>'




#%% Set up animation
N_FRAME=len(section1.curvature)
INIT_STEP = 78
STEP = 0

frames = []
print("Generating animation frames...")
for i in range(N_FRAME):
    print(f"\t step {STEP}")
    data = []
    #############################################
    #  MOMENT CURVATURE LINE
    #############################################
    mk_trace = go.Scatter(x = mk_results["Curvature"],
                            y = mk_results["Moment"],
                            mode="lines",
                            line_width = 2,
                            line_color = "mediumblue",
                            showlegend=False,
                            hovertemplate=f'Moment = %{{y}} {unit_moment}<br>Curvature = %{{x:.2e}}<extra></extra>')
    if STEP == 0:
        fig.add_trace(mk_trace, row=1, col=2)
    else:
        pass
        #data.append(mk_trace)
    
    

    #############################################
    #  STATIC PATCH FIBER MESH
    #############################################
    # loop through all patch fibers and construct mesh connectivity
    x_list, y_list, z_list = [], [], []
    i_list, j_list, k_list = [], [], []
    facecolor_list = []
    for i in range(len(df_patchfibers)):
        vertices = df_patchfibers.loc[i, "vertices"]
        for j in range(4):
            x_list.append(vertices[j][0])
            y_list.append(0)
            z_list.append(vertices[j][1]) # swapped y <> z for plotting
        
        # first triangle (bottom right)
        i_list.append(i*4)
        j_list.append(i*4 + 1)
        k_list.append(i*4 + 2)
        
        # second triangle (top left)
        i_list.append(i*4 + 2)
        j_list.append(i*4 + 3)
        k_list.append(i*4)
        
        # face color
        color = df_patchfibers.loc[i, "default_color"]
        facecolor_list.append(color)
        facecolor_list.append(color)
        
    # plot patch fibers
    patch_trace = go.Mesh3d(x = x_list, 
                            y = y_list,
                            z = z_list,
                            i = i_list,
                            j = j_list,
                            k = k_list,
                            hoverinfo="skip",
                            facecolor=facecolor_list,
                            showlegend=False)
    if STEP == 0:
        fig.add_trace(patch_trace, row=1, col=1)
    else:
        pass
        #data.append(patch_trace)
    
    
    
    
    
    
    #############################################
    #  STATIC NODE FIBER MESH
    #############################################
    # loop through all node fibers
    x_list, y_list, z_list = [], [], []
    i_list, j_list, k_list = [], [], []
    facecolor_list = []
    thetas = np.linspace(0, 2*np.pi, 9)
    for i in range(len(df_nodefibers)):
        xc = df_nodefibers.loc[i, "x"]
        zc = df_nodefibers.loc[i, "y"] # swapped y <> z for plotting
        area = df_nodefibers.loc[i, "area"]
        radius = (area/np.pi)**(1/2)
        
        # each node fiber is converted into 10 points around a circle. 0 at center, 1-9 along perimeter. Last pt repeated.
        x_list.append(xc)
        y_list.append(0.1)
        z_list.append(zc)
        for j in range(len(thetas)):
            x_list.append(xc + radius*np.cos(thetas[j]))
            y_list.append(0.1)
            z_list.append(zc + radius*np.sin(thetas[j]))
            
        # do this twice because i want to plot node fiber on both sides of section
        x_list.append(xc)
        y_list.append(-0.1)
        z_list.append(zc)
        for j in range(len(thetas)):
            x_list.append(xc + radius*np.cos(thetas[j]))
            y_list.append(-0.1)
            z_list.append(zc + radius*np.sin(thetas[j]))
        
        # approximate circle as a polygon with 8 triangles
        for j in range(8):
            i_list.append(  (20*i)+(j+1)  )
            j_list.append(  (20*i)+(j+2)  )
            k_list.append(  (20*i)  )
        
        # again repeat for both sides
        for j in range(8):
            i_list.append(  (20*i) +10+j+1  )
            j_list.append(  (20*i) +10+j+2  )
            k_list.append(  (20*i) +10 )
        
        # face color
        color = df_nodefibers.loc[i, "default_color"]
        for j in range(16):
            facecolor_list.append(color)
        
    # plot nodes
    node_trace = go.Mesh3d(x = x_list, 
                           y = y_list,
                           z = z_list,
                           i = i_list,
                           j = j_list,
                           k = k_list,
                           hoverinfo="skip",
                           facecolor=facecolor_list,
                           showlegend=False)
    if STEP == 0:
        fig.add_trace(node_trace, row=1, col=1)
    else:
        pass
        #data.append(node_trace)
    
    
    
    
    
    
    #############################################
    #  STRESS ARROW PLOTS (PATCH)
    #############################################
    # scaling size of vector
    SCALE = 0.5
    u_max = SCALE * 16
    stress_max = 0 # usually negative for compression
    for i in range(len(df_patchfibers)):
        stresses = df_patchfibers.loc[i, "stress"]
        max_stress_for_this_fiber = abs(max(stresses, key=abs))
        if stress_max < max_stress_for_this_fiber:
            stress_max = max_stress_for_this_fiber
        
    # plot patch fiber stresses
    x_list, y_list, z_list = [], [], []
    x_listnode, y_listnode, z_listnode = [], [], []
    hoverinfo_list = []
    color_node = []
    color_line = []
    for i in range(len(df_patchfibers)):
        xc, zc = df_patchfibers.loc[i, "centroid"]
        stresses = df_patchfibers.loc[i, "stress"]
        strains = df_patchfibers.loc[i, "strain"]
        fid = df_patchfibers.loc[i, "tag"]
        strain = strains[STEP]
        stress = stresses[STEP]
        
        if not math.isclose(stress, 0):
            color_raw = df_patchfibers.loc[i, "color_list"]
            color = color_raw[STEP]
                
            u = stress / stress_max * u_max
            
            x_list+=[xc, xc, None]
            y_list+=[0, u, None]
            z_list+=[zc, zc, None]
            color_line+=[color,color,"rgba(255, 255, 255, 0)"]
            
            x_listnode+=[xc]
            y_listnode+=[u]
            z_listnode+=[zc]
            color_node+=[color]
            
            hoverinfo = (
                 "<b>Patch Fiber {:.0f}</b><br>".format(fid) +
                 "<b>x, y</b>: ({:.2f}, {:.2f}) <br>".format(xc, zc) +
                 "<b>strain</b>: {:.2e} <br>".format(strain) +
                 "<b>stress</b>: {:.2f} {}<br>".format(stress, unit_stress)
                         )
            hoverinfo_list.append(hoverinfo)
            
            
            
    #############################################
    #  STRESS ARROW PLOTS (NODES)
    #############################################
    for i in range(len(df_nodefibers)):
        xc = df_nodefibers.loc[i, "x"] 
        zc = df_nodefibers.loc[i, "y"]
        
        stresses = df_nodefibers.loc[i, "stress"]
        strains = df_nodefibers.loc[i, "strain"]
        fid = df_nodefibers.loc[i, "tag"]
        strain = strains[STEP]
        stress = stresses[STEP]
        
        if not math.isclose(stress, 0):
            color_raw = df_nodefibers.loc[i, "color_list"]
            color = color_raw[STEP]
                
            if stress > 0:
                scaling = min(stress / stress_max, 1)
            else:
                scaling = max(stress / stress_max, -1)
            u = scaling * u_max * 2
            
            x_list+=[xc, xc, None]
            y_list+=[0, u, None]
            z_list+=[zc, zc, None]
            color_line+=[color,color,"rgba(255, 255, 255, 0)"]
            
            x_listnode+=[xc]
            y_listnode+=[u]
            z_listnode+=[zc]
            color_node+=[color]
            
            hoverinfo = (
                 "<b>Node Fiber {:.0f}</b><br>".format(fid) +
                 "<b>x, y</b>: ({:.2f}, {:.2f}) <br>".format(xc, zc) +
                 "<b>strain</b>: {:.2e} <br>".format(strain) +
                 "<b>stress</b>: {:.2f} {}<br>".format(stress, unit_stress)
                         )
            hoverinfo_list.append(hoverinfo)
            
    # plot stress arrows
    stress_trace = go.Scatter3d(x = x_list, 
                                y = y_list,
                                z = z_list,
                                mode="lines",
                                line_color=color_line,
                                line_width=6,
                                hoverinfo="skip",
                                showlegend=False)
    stress_tip_trace = go.Scatter3d(x = x_listnode, 
                                    y = y_listnode,
                                    z = z_listnode,
                                    mode="markers",
                                    marker_size=6,
                                    marker_color=color_node,
                                    showlegend=False,
                                    text=hoverinfo_list,
                                    hovertemplate=hovertemplate,
                                    hoverlabel_bgcolor="beige",
                                    hoverlabel_bordercolor="black",
                                    hoverlabel_font_color="black",
                                    hoverlabel_font_size=16
                                    )
    if STEP == 0:
        fig.add_trace(stress_trace, row=1, col=1)
        fig.add_trace(stress_tip_trace, row=1, col=1)
    else:
        data.append(stress_trace)
        data.append(stress_tip_trace)
        
        
        
    ################################################
    #  MOMENT CURVATURE MARKER AND INDICATOR LINES
    ################################################
    phi = mk_results["Curvature"].tolist()[STEP]
    M = mk_results["Moment"].tolist()[STEP]
    mk_trace2 = go.Scatter(x = [phi],
                           y = [M],
                            mode="markers",
                            marker_size = 12,
                            line_color = "blue",
                            showlegend=False,
                            hoverinfo="skip")
    mk_trace3 = go.Scatter(x = [phi, phi, None, 0, phi],
                           y = [0, M, None, M, M],
                            mode="lines",
                            line_color = "blue",
                            line_dash = "dash",
                            showlegend=False,
                            hoverinfo="skip")

    if STEP == 0:
        fig.add_trace(mk_trace2, row=1, col=2)
        fig.add_trace(mk_trace3, row=1, col=2)
    else:
        data.append(mk_trace2)
        data.append(mk_trace3)
        
    frames.append(go.Frame(data=data, name=str(STEP), traces=[3,4,5,6]))
    STEP +=1

fig.update(frames=frames)








#############################################
#  SLIDER SETUP
#############################################
sliders = [
    {"steps": [{"args": [[str(k)],
                         {"frame": {"duration": 0, "redraw": True},
                          "mode": "immediate"}
                         ],
                "label": "",
                "method": "animate"
                } for k in range(N_FRAME)
               ],
     "active": 0,
     "transition": {"duration": 0},
     "x": 0.505,
     "xanchor": "left",
     "len": 0.50,
     "y": -0.04,
     "yanchor": "top"}
]
fig.add_annotation(text = "Load Step:",
                   x=0.52,
                   y=-0.06,
                   xref="paper",
                   yref="paper",
                   showarrow=False,
                   font_size=14)

fig.update_layout(sliders=sliders)






#%% Styling

# 3D plot: adjust zoom level and default camera position
fig.update_scenes(camera_eye=dict(x=1.5, y=1.5, z=0.5))


# 3D plot: change origin to be on the bottom left corner. Also adjust aspect ratio
fig.update_scenes(xaxis_autorange="reversed",
                  yaxis_autorange=False,
                  yaxis_range=[u_max * 2,-u_max * 2],
                  aspectmode="data")

# 3D plot: hide axes
fig.update_scenes(xaxis_backgroundcolor="white",
                  yaxis_backgroundcolor="white",
                  xaxis_gridcolor="grey",
                  yaxis_gridcolor="grey",
                  xaxis_gridwidth=0.5,
                  yaxis_gridwidth=0.5,
                  zaxis_visible=False,
                  xaxis_visible=False,
                  yaxis_visible=False)


# 2D plot: plot background color and hover box style
fig.update_layout(plot_bgcolor="white",
                  margin_pad=5,
                  hoverlabel_bgcolor="beige",
                  hoverlabel_bordercolor="black",
                  hoverlabel_font_color="black",
                  hoverlabel_font_size=16)

# 2D plot: axes labels and styling
fig.update_yaxes(title_text=f"Moment ({unit_moment})",
                 gridcolor="lightgrey",
                 zerolinecolor="black",
                 tickformat=",.0f",
                 showspikes=True)
fig.update_xaxes(title_text=f"Curvature ({unit_curvature})",
                 gridcolor="lightgrey",
                 zerolinecolor="black",
                 showexponent="all",
                 exponentformat="power",
                 showspikes=True)

# add fig title and adjust margin
fig.update_layout(title="<b>Fiber Kit - 3D Moment Curvature Visualization</b>",
                  title_xanchor="center",
                  title_font_size=22,
                  title_x=0.5, 
                  title_y=0.98,
                  title_font_color="black",
                  margin_b=120,
                  paper_bgcolor="white",
                  font_color="black")

# display figure
fig.show()

