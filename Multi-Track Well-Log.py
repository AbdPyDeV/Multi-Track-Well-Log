import streamlit as st
import lasio
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(layout="wide", page_title="LAS Log Viewer")

st.title("Multi-Track Log Visualizer")

# 1. File Upload
uploaded_file = st.sidebar.file_uploader("Upload a LAS file", type=["las"])

if uploaded_file is not None:
    # Read the LAS file
    # We use string decoding because lasio expects a file path or string
    bytes_data = uploaded_file.read().decode("utf-8")
    las = lasio.read(bytes_data)
    df = las.df().reset_index() # Convert to dataframe
    
    # Get available curves
    curves = df.columns.tolist()
    depth_col = curves[0]  # Usually 'DEPTH'
    log_curves = curves[1:]

    # 2. Sidebar Controls
    st.sidebar.header("Settings")
    selected_curves = st.sidebar.multiselect(
        "Select Curves to Plot", options=log_curves, default=log_curves[:3]
    )
    
    depth_range = st.sidebar.slider(
        "Depth Range", 
        float(df[depth_col].min()), 
        float(df[depth_col].max()), 
        (float(df[depth_col].min()), float(df[depth_col].max()))
    )

    if selected_curves:
        # 3. Create Multi-Track Plot
        num_tracks = len(selected_curves)
        fig = make_subplots(
            rows=1, cols=num_tracks, 
            shared_yaxes=True, 
            horizontal_spacing=0.02,
            subplot_titles=selected_curves
        )

        for i, curve in enumerate(selected_curves):
            fig.add_trace(
                go.Scatter(x=df[curve], y=df[depth_col], name=curve),
                row=1, col=i+1
            )
            # Update individual x-axes if needed (e.g., log scales for resistivity)
            fig.update_xaxes(title_text=curve, row=1, col=i+1)

        # 4. General Layout Formatting
        fig.update_yaxes(
            range=[depth_range[1], depth_range[0]], # Reverse for depth
            autorange=False,
            title_text="Depth" if i == 0 else ""
        )
        
        fig.update_layout(
            height=800, 
            showlegend=False,
            margin=dict(l=50, r=50, t=100, b=50)
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Please select at least one curve from the sidebar.")

else:
    st.info("Awaiting LAS file upload. Please upload a file in the sidebar.")