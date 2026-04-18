import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Lithography Simulator", layout="wide")

# -------------------------------
# BLOCK WITH PROPER FACES
# -------------------------------
def create_block(x0, y0, dx, dy, z0, dz, color):
    x = [x0, x0+dx, x0+dx, x0, x0, x0+dx, x0+dx, x0]
    y = [y0, y0, y0+dy, y0+dy, y0, y0, y0+dy, y0+dy]
    z = [z0, z0, z0, z0, z0+dz, z0+dz, z0+dz, z0+dz]

    i = [0,0,0,1,1,2,4,4,5,6,3,2]
    j = [1,2,3,2,5,3,5,6,6,7,7,6]
    k = [2,3,1,5,6,7,6,7,4,4,4,7]

    return go.Mesh3d(
        x=x, y=y, z=z,
        i=i, j=j, k=k,
        color=color,
        opacity=1.0,
        flatshading=True
    )

# -------------------------------
# MASK
# -------------------------------
def generate_mask(size, pattern):
    mask = np.zeros((size, size))

    if pattern == "Lines":
        mask[:, ::4] = 1
    elif pattern == "Dots":
        for i in range(0, size, 6):
            for j in range(0, size, 6):
                mask[i:i+2, j:j+2] = 1
    elif pattern == "Square":
        mask[10:20, 10:20] = 1

    return mask

# -------------------------------
# APP
# -------------------------------

st.title("3D Lithography Simulator (Fixed Solid Model)")

size = 15  # keep small for performance
dx = 1 / size

# -------------------------------
# STEP 0: SUBSTRATE
# -------------------------------
st.header("Step 0: Silicon Substrate")

fig0 = go.Figure()
fig0.add_trace(create_block(0,0,1,1,0,200,"gray"))

st.plotly_chart(fig0, use_container_width=True)

# -------------------------------
# STEP 1: SiO2
# -------------------------------
st.header("Step 1: SiO₂ Deposition")

sio2_thickness = st.slider("SiO₂ Thickness", 100, 500, 200)

fig1 = go.Figure()
fig1.add_trace(create_block(0,0,1,1,0,200,"gray"))
fig1.add_trace(create_block(0,0,1,1,200,sio2_thickness,"blue"))

st.plotly_chart(fig1, use_container_width=True)

# -------------------------------
# STEP 2: PHOTORESIST
# -------------------------------
st.header("Step 2: Photoresist Coating")

resist_thickness = st.slider("Resist Thickness", 100, 500, 200)

fig2 = go.Figure()
fig2.add_trace(create_block(0,0,1,1,0,200,"gray"))
fig2.add_trace(create_block(0,0,1,1,200,sio2_thickness,"blue"))
fig2.add_trace(create_block(0,0,1,1,200+sio2_thickness,resist_thickness,"orange"))

st.plotly_chart(fig2, use_container_width=True)

# -------------------------------
# STEP 3: EXPOSURE
# -------------------------------
st.header("Step 3: Exposure (UV Light)")

pattern = st.selectbox("Mask Pattern", ["Lines", "Dots", "Square"])
mask = generate_mask(size, pattern)

fig3 = go.Figure()

# base layers
fig3.add_trace(create_block(0,0,1,1,0,200,"gray"))
fig3.add_trace(create_block(0,0,1,1,200,sio2_thickness,"blue"))

# PR blocks (color change if exposed)
for i in range(size):
    for j in range(size):
        x0, y0 = i*dx, j*dx
        color = "red" if mask[i,j] == 1 else "orange"

        fig3.add_trace(create_block(
            x0, y0, dx, dx,
            200 + sio2_thickness,
            resist_thickness,
            color
        ))

        # Light beam (transparent yellow)
        if mask[i,j] == 1:
            fig3.add_trace(create_block(
                x0, y0, dx, dx,
                200 + sio2_thickness + resist_thickness,
                200,
                "yellow"
            ))

fig3.update_traces(opacity=0.2, selector=dict(color="yellow"))

st.plotly_chart(fig3, use_container_width=True)

# -------------------------------
# STEP 4: DEVELOPMENT
# -------------------------------
st.header("Step 4: Development")

fig4 = go.Figure()

# base layers
fig4.add_trace(create_block(0,0,1,1,0,200,"gray"))
fig4.add_trace(create_block(0,0,1,1,200,sio2_thickness,"blue"))

# remove exposed PR
for i in range(size):
    for j in range(size):
        if mask[i,j] == 0:  # keep only unexposed
            x0, y0 = i*dx, j*dx

            fig4.add_trace(create_block(
                x0, y0, dx, dx,
                200 + sio2_thickness,
                resist_thickness,
                "green"
            ))

st.plotly_chart(fig4, use_container_width=True)

st.success("Lithography execute successfully!")
