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

def generate_mask(mask_type, size=50):
    mask = np.zeros((size, size))

    if mask_type == "Lines":
        mask[:, ::5] = 1
    elif mask_type == "Dots":
        for i in range(0, size, 10):
            for j in range(0, size, 10):
                mask[i:i+2, j:j+2] = 1
    elif mask_type == "Square":
        mask[15:35, 15:35] = 1

    return mask

# -------------------------------
# CREATE SOLID BLOCK
# -------------------------------

def create_block(z_start, thickness, color):
    x = [0, 1, 1, 0, 0, 1, 1, 0]
    y = [0, 0, 1, 1, 0, 0, 1, 1]
    z = [
        z_start, z_start, z_start, z_start,
        z_start + thickness, z_start + thickness,
        z_start + thickness, z_start + thickness
    ]

    return go.Mesh3d(
        x=x, y=y, z=z,
        color=color,
        opacity=1.0,
        flatshading=True
    )

# -------------------------------
# CREATE PATTERNED RESIST
# -------------------------------

def create_patterned_resist(z_start, resist, mask):
    size = resist.shape[0]
    fig_data = []

    for i in range(size):
        for j in range(size):
            if resist[i, j] > 0:
                if mask[i, j] == 0:  # only keep non-developed areas
                    x0, y0 = i/size, j/size
                    dx = 1/size

                    fig_data.append(go.Mesh3d(
                        x=[x0, x0+dx, x0+dx, x0, x0, x0+dx, x0+dx, x0],
                        y=[y0, y0, y0+dx, y0+dx, y0, y0, y0+dx, y0+dx],
                        z=[
                            z_start, z_start, z_start, z_start,
                            z_start + resist[i, j], z_start + resist[i, j],
                            z_start + resist[i, j], z_start + resist[i, j]
                        ],
                        color="green",
                        opacity=1.0,
                        flatshading=True,
                        showscale=False
                    ))

    return fig_data

# -------------------------------
# SIDEBAR
# -------------------------------

tab = st.sidebar.radio("Navigation", ["Simulation", "Theory"])

# -------------------------------
# THEORY
# -------------------------------

if tab == "Theory":
    st.title("Lithography Theory")

    st.markdown("""
    This simulator shows lithography as **solid 3D layers**:

    - Gray → Silicon substrate  
    - Blue → SiO₂  
    - Orange → Photoresist  
    - Green → Developed pattern  

    Unlike simple surface plots, this uses **true volumetric blocks**.
    """)

# -------------------------------
# SIMULATION
# -------------------------------

else:
    st.title("3D Lithography Simulator (Solid Model)")

    size = 30  # reduced for performance

    # -------------------------------
    # STEP 0: SUBSTRATE
    # -------------------------------
    st.header("Step 0: Silicon Substrate")

    substrate_thickness = 200

    fig0 = go.Figure()
    fig0.add_trace(create_block(0, substrate_thickness, "gray"))

    st.plotly_chart(fig0, use_container_width=True)

    # -------------------------------
    # STEP 1: SiO2
    # -------------------------------
    st.header("Step 1: SiO₂ Deposition")

    sio2_thickness = st.slider("SiO₂ Thickness", 100, 1000, 300)

    fig1 = go.Figure()
    fig1.add_trace(create_block(0, substrate_thickness, "gray"))
    fig1.add_trace(create_block(substrate_thickness, sio2_thickness, "blue"))

    st.plotly_chart(fig1, use_container_width=True)

    # -------------------------------
    # STEP 2: PHOTORESIST
    # -------------------------------
    st.header("Step 2: Photoresist")

    resist_type = st.selectbox("Resist", ["AZ1505", "PMMA"])
    resist_thickness = st.slider("Resist Thickness", 100, 1000, 500)

    rpm = rpm_from_thickness(resist_thickness, resist_type)
    st.write(f"Suggested RPM: **{rpm}**")

    fig2 = go.Figure()
    fig2.add_trace(create_block(0, substrate_thickness, "gray"))
    fig2.add_trace(create_block(substrate_thickness, sio2_thickness, "blue"))
    fig2.add_trace(create_block(substrate_thickness + sio2_thickness, resist_thickness, "orange"))

    st.plotly_chart(fig2, use_container_width=True)

    # -------------------------------
    # STEP 3 & 4: DEVELOPMENT
    # -------------------------------
    st.header("Step 3 & 4: Mask + Development")

    mask_type = st.selectbox("Mask", ["Lines", "Dots", "Square"])
    polarity = st.radio("Polarity", ["Positive", "Negative"])

    mask = generate_mask(mask_type, size)

    if polarity == "Negative":
        mask = 1 - mask

    resist = np.ones((size, size)) * resist_thickness

    fig3 = go.Figure()
    fig3.add_trace(create_block(0, substrate_thickness, "gray"))
    fig3.add_trace(create_block(substrate_thickness, sio2_thickness, "blue"))

    patterned_blocks = create_patterned_resist(
        substrate_thickness + sio2_thickness,
        resist,
        mask
    )

    for block in patterned_blocks:
        fig3.add_trace(block)

    st.plotly_chart(fig3, use_container_width=True)

    st.success("Desired lithography is successfully achieved!")
