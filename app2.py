import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Lithography Simulator", layout="wide")

# -------------------------------
# FIXED BLOCK (SOLID)
# -------------------------------
def create_block(x0, y0, dx, dy, z0, dz, color, opacity=1.0):
    x = [x0, x0+dx, x0+dx, x0, x0, x0+dx, x0+dx, x0]
    y = [y0, y0, y0+dy, y0+dy, y0, y0, y0+dy, y0+dy]
    z = [z0, z0, z0, z0, z0+dz, z0+dz, z0+dz, z0+dz]

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
# CENTERED MASK (FIXED)
# -------------------------------
def generate_mask(size, pattern):
    mask = np.zeros((size, size))

    center = size // 2

    if pattern == "Lines":
        for j in range(-2, 3, 2):
            mask[:, center + j] = 1

    elif pattern == "Dots":
        for i in range(center-4, center+5, 4):
            for j in range(center-4, center+5, 4):
                mask[i:i+2, j:j+2] = 1

    elif pattern == "Square":
        mask[center-3:center+3, center-3:center+3] = 1

    return mask

# -------------------------------
# RPM SUGGESTION
# -------------------------------
def rpm_suggestion(resist_type):
    st.subheader("Spin Coating Optimization")

    if resist_type == "AZ1505":
        base_rpm = 3000
        ref_thickness = 500
    else:
        base_rpm = 4000
        ref_thickness = 300

    target_thickness = st.slider("Target Thickness (nm)", 100, 600, 200)

    suggested_rpm = int(base_rpm * (ref_thickness / target_thickness))

    st.markdown(f"""
    **Suggested RPM:** `{suggested_rpm} rpm`

    📌 Thickness ∝ 1 / RPM
    """)

    return base_rpm, ref_thickness

# -------------------------------
# PREBAKE
# -------------------------------
def prebake_effect(resist_type, thickness):
    if resist_type == "AZ1505":
        reduction_percent = np.random.uniform(5, 10)
    else:
        reduction_percent = np.random.uniform(8, 15)

    new_thickness = thickness * (1 - reduction_percent/100)
    return new_thickness, reduction_percent

# -------------------------------
# APP START
# -------------------------------
st.title("3D Lithography Simulator")

size = 15
dx = 1 / size

# -------------------------------
# STEP 0
# -------------------------------
st.header("Step 0: Silicon Substrate")

fig0 = go.Figure()
fig0.add_trace(create_block(0,0,1,1,0,200,"gray"))
st.plotly_chart(fig0, use_container_width=True)

# -------------------------------
# STEP 1
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

base_rpm, ref_thickness = rpm_suggestion(resist_type)

# NEW: RPM CONTROL (instead of thickness)
rpm = st.slider("Spin Speed (RPM)", 1000, 6000, 3000)

# thickness calculation
resist_thickness = ref_thickness * (base_rpm / rpm)

st.write(f"**Resulting Thickness:** {resist_thickness:.1f} nm")

fig2 = go.Figure()
fig2.add_trace(create_block(0,0,1,1,0,200,"gray"))
fig2.add_trace(create_block(0,0,1,1,200,sio2_thickness,"blue"))
fig2.add_trace(create_block(0,0,1,1,200+sio2_thickness,resist_thickness,"orange"))
st.plotly_chart(fig2, use_container_width=True)

# -------------------------------
# STEP 2.5: PREBAKE
# -------------------------------
st.header("Step 2.5: Soft Bake (Pre-bake)")

baked_thickness, reduction = prebake_effect(resist_type, resist_thickness)

st.markdown(f"""
**Soft Bake Conditions (Typical for AZ1505):**
- Temperature: **90–100°C**
- Time: **60–90 seconds**

**Thickness Change:**
- Before Bake: **{resist_thickness:.1f} nm**
- After Bake: **{baked_thickness:.1f} nm**
- Reduction: **{reduction:.2f}%**
""")

fig_pb = go.Figure()
fig_pb.add_trace(create_block(0,0,1,1,0,200,"gray"))
fig_pb.add_trace(create_block(0,0,1,1,200,sio2_thickness,"blue"))
fig_pb.add_trace(create_block(
    0,0,1,1,
    200 + sio2_thickness,
    baked_thickness,
    "darkorange"
))
st.plotly_chart(fig_pb, use_container_width=True)

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

        color = "red" if exposed else "darkorange"

        fig3.add_trace(create_block(
            x0, y0, dx, dx,
            200 + sio2_thickness,
            baked_thickness,
            color
        ))

        if exposed:
            fig3.add_trace(create_block(
                x0, y0, dx, dx,
                200 + sio2_thickness + baked_thickness,
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
                baked_thickness,
                "green"
            ))

st.plotly_chart(fig4, use_container_width=True)

st.success("Simulation Complete!")
