import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Lithography Simulator", layout="wide")

# -------------------------------
# FIXED BLOCK (PROPER SOLID 3D)
# -------------------------------
def create_block(x0, y0, dx, dy, z0, dz, color, opacity=1.0):
    # 8 vertices
    x = [x0, x0+dx, x0+dx, x0, x0, x0+dx, x0+dx, x0]
    y = [y0, y0, y0+dy, y0+dy, y0, y0, y0+dy, y0+dy]
    z = [z0, z0, z0, z0, z0+dz, z0+dz, z0+dz, z0+dz]

    # 12 triangles (2 per face)
    i = [0,0, 4,4, 0,0, 2,2, 1,1, 0,0]
    j = [1,2, 5,6, 1,5, 3,7, 2,6, 3,7]
    k = [2,3, 6,7, 5,4, 7,6, 6,5, 7,4]

    return go.Mesh3d(
        x=x, y=y, z=z,
        i=i, j=j, k=k,
        color=color,
        opacity=opacity,
        flatshading=True
    )

# -------------------------------
# MASK GENERATION
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
# RPM INFO FUNCTION
# -------------------------------
def show_rpm_info(resist_type, thickness):
    st.subheader("Spin Coating Insights")

    if resist_type == "AZ1505":
        base_rpm = 3000
        ref_thickness = 500
    else:
        base_rpm = 4000
        ref_thickness = 300

    rpm = int(base_rpm * (ref_thickness / thickness))

    st.markdown("""
    **Relationship:**
    - Thickness ∝ 1 / RPM (simplified)
    - Higher RPM → thinner film  
    - Lower RPM → thicker film  
    """)

    rpm_vals = np.linspace(1000, 6000, 50)
    thickness_vals = ref_thickness * (base_rpm / rpm_vals)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=rpm_vals,
        y=thickness_vals,
        mode='lines'
    ))

    fig.update_layout(
        title="RPM vs Thickness",
        xaxis_title="RPM",
        yaxis_title="Thickness (nm)"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.write("### Typical Values")

    table_rpm = [1000, 2000, 3000, 4000, 5000]
    table_thickness = [int(ref_thickness * (base_rpm / r)) for r in table_rpm]

    st.table({
        "RPM": table_rpm,
        "Thickness (nm)": table_thickness
    })

# -------------------------------
# APP START
# -------------------------------

st.title("3D Lithography Simulator")

size = 15
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

sio2_thickness = st.slider("SiO₂ Thickness (nm)", 100, 500, 200)

fig1 = go.Figure()
fig1.add_trace(create_block(0,0,1,1,0,200,"gray"))
fig1.add_trace(create_block(0,0,1,1,200,sio2_thickness,"blue"))
st.plotly_chart(fig1, use_container_width=True)

# -------------------------------
# STEP 2: PHOTORESIST
# -------------------------------
st.header("Step 2: Photoresist Coating")

resist_type = st.selectbox("Resist Type", ["AZ1505", "PMMA"])
resist_thickness = st.slider("Resist Thickness (nm)", 100, 500, 200)

show_rpm_info(resist_type, resist_thickness)

fig2 = go.Figure()
fig2.add_trace(create_block(0,0,1,1,0,200,"gray"))
fig2.add_trace(create_block(0,0,1,1,200,sio2_thickness,"blue"))
fig2.add_trace(create_block(0,0,1,1,200+sio2_thickness,resist_thickness,"orange"))
st.plotly_chart(fig2, use_container_width=True)

# -------------------------------
# STEP 3: EXPOSURE
# -------------------------------
st.header("Step 3: Exposure")

pattern = st.selectbox("Mask Pattern", ["Lines", "Dots", "Square"])
mask = generate_mask(size, pattern)

fig3 = go.Figure()

fig3.add_trace(create_block(0,0,1,1,0,200,"gray"))
fig3.add_trace(create_block(0,0,1,1,200,sio2_thickness,"blue"))

for i in range(size):
    for j in range(size):
        x0, y0 = i*dx, j*dx
        exposed = mask[i,j] == 1

        color = "red" if exposed else "orange"

        fig3.add_trace(create_block(
            x0, y0, dx, dx,
            200 + sio2_thickness,
            resist_thickness,
            color
        ))

        if exposed:
            fig3.add_trace(create_block(
                x0, y0, dx, dx,
                200 + sio2_thickness + resist_thickness,
                200,
                "yellow",
                opacity=0.2
            ))

st.plotly_chart(fig3, use_container_width=True)

# -------------------------------
# STEP 4: DEVELOPMENT
# -------------------------------
st.header("Step 4: Development")

fig4 = go.Figure()

fig4.add_trace(create_block(0,0,1,1,0,200,"gray"))
fig4.add_trace(create_block(0,0,1,1,200,sio2_thickness,"blue"))

for i in range(size):
    for j in range(size):
        if mask[i,j] == 0:
            x0, y0 = i*dx, j*dx

            fig4.add_trace(create_block(
                x0, y0, dx, dx,
                200 + sio2_thickness,
                resist_thickness,
                "green"
            ))

st.plotly_chart(fig4, use_container_width=True)

st.success("Simulation Complete!")
