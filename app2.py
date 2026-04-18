import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="3D Lithography Simulator", layout="wide")

# -------------------------------
# FUNCTIONS
# -------------------------------

def rpm_from_thickness(thickness, material):
    if material == "AZ1505":
        return int(3000 * (500 / thickness))
    elif material == "PMMA":
        return int(4000 * (300 / thickness))

def generate_mask(mask_type, size=100):
    mask = np.zeros((size, size))

    if mask_type == "Lines":
        mask[:, ::10] = 1
    elif mask_type == "Dots":
        for i in range(0, size, 15):
            for j in range(0, size, 15):
                mask[i:i+3, j:j+3] = 1
    elif mask_type == "Square":
        mask[30:70, 30:70] = 1

    return mask

def create_3d_layers(substrate, sio2=None, resist=None, developed=None):
    size = substrate.shape[0]
    x = np.linspace(0, 1, size)
    y = np.linspace(0, 1, size)
    X, Y = np.meshgrid(x, y)

    fig = go.Figure()

    # Silicon substrate (GRAY)
    fig.add_trace(go.Surface(
        z=substrate,
        x=X, y=Y,
        colorscale=[[0, "gray"], [1, "gray"]],
        showscale=False,
        opacity=1.0,
        name="Silicon"
    ))

    # SiO2 layer (BLUE)
    if sio2 is not None:
        fig.add_trace(go.Surface(
            z=substrate + sio2,
            x=X, y=Y,
            colorscale=[[0, "blue"], [1, "blue"]],
            showscale=False,
            opacity=0.9,
            name="SiO2"
        ))

    # Photoresist (ORANGE)
    if resist is not None:
        fig.add_trace(go.Surface(
            z=substrate + sio2 + resist,
            x=X, y=Y,
            colorscale=[[0, "orange"], [1, "orange"]],
            showscale=False,
            opacity=0.8,
            name="Photoresist"
        ))

    # Developed pattern (GREEN)
    if developed is not None:
        fig.add_trace(go.Surface(
            z=substrate + sio2 + developed,
            x=X, y=Y,
            colorscale=[[0, "green"], [1, "green"]],
            showscale=False,
            opacity=1.0,
            name="Developed Pattern"
        ))

    fig.update_layout(
        scene=dict(
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Height',
        ),
        height=600
    )

    return fig

# -------------------------------
# SIDEBAR
# -------------------------------

tab = st.sidebar.radio("Navigation", ["Simulation", "Theory"])

# -------------------------------
# THEORY TAB
# -------------------------------

if tab == "Theory":
    st.title("Lithography Theory")

    st.markdown("""
    ### Steps in Lithography

    **1. Silicon Substrate**
    - Base wafer for fabrication

    **2. SiO₂ Deposition**
    - Insulating oxide layer

    **3. Photoresist Coating**
    - Spin coating defines thickness via RPM

    **4. Mask & Exposure**
    - UV light transfers pattern

    **5. Development**
    - Removes selected regions

    This simulator shows these as stacked 3D layers.
    """)

# -------------------------------
# SIMULATION TAB
# -------------------------------

else:
    st.title("3D Lithography Simulator")

    size = 100

    # -------------------------------
    # STEP 0: SUBSTRATE
    # -------------------------------
    st.header("Step 0: Silicon Substrate")

    substrate_height = 200
    substrate = np.ones((size, size)) * substrate_height

    fig0 = create_3d_layers(substrate)
    st.plotly_chart(fig0, use_container_width=True)

    # -------------------------------
    # STEP 1: SiO2
    # -------------------------------
    st.header("Step 1: SiO₂ Deposition")

    sio2_thickness = st.slider("SiO₂ Thickness (nm)", 100, 1000, 300)
    sio2 = np.ones((size, size)) * sio2_thickness

    fig1 = create_3d_layers(substrate, sio2=sio2)
    st.plotly_chart(fig1, use_container_width=True)

    # -------------------------------
    # STEP 2: PHOTORESIST
    # -------------------------------
    st.header("Step 2: Photoresist Coating")

    resist_type = st.selectbox("Photoresist Type", ["AZ1505", "PMMA"])
    thickness = st.slider("Photoresist Thickness (nm)", 100, 1000, 500)

    rpm = rpm_from_thickness(thickness, resist_type)
    st.write(f"Suggested Spin Speed: **{rpm} RPM**")

    resist = np.ones((size, size)) * thickness

    fig2 = create_3d_layers(substrate, sio2, resist)
    st.plotly_chart(fig2, use_container_width=True)

    # -------------------------------
    # STEP 3 & 4: MASK + DEVELOPMENT
    # -------------------------------
    st.header("Step 3 & 4: Mask Exposure + Development")

    mask_type = st.selectbox("Mask Type", ["Lines", "Dots", "Square"])
    polarity = st.radio("Polarity", ["Positive", "Negative"])

    mask = generate_mask(mask_type, size)

    if polarity == "Positive":
        exposed = mask
    else:
        exposed = 1 - mask

    developed = resist.copy()

    if polarity == "Positive":
        developed[exposed == 1] = 0
    else:
        developed[exposed == 0] = 0

    fig3 = create_3d_layers(substrate, sio2, resist, developed)
    st.plotly_chart(fig3, use_container_width=True)

    st.success("Simulation Complete!")
