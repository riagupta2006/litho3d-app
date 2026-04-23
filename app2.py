import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Virtual Lithography Lab", layout="wide")

# -------------------------------
# BLOCK FUNCTION
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
# CENTERED MASK
# -------------------------------
def generate_mask(size, pattern):
    mask = np.zeros((size, size))
    c = size // 2

    if pattern == "Lines":
        for j in range(-2, 3, 2):
            mask[:, c+j] = 1
    elif pattern == "Dots":
        for i in range(c-4, c+5, 4):
            for j in range(c-4, c+5, 4):
                mask[i:i+2, j:j+2] = 1
    elif pattern == "Square":
        mask[c-3:c+3, c-3:c+3] = 1

    return mask

# -------------------------------
# PREBAKE
# -------------------------------
def prebake_effect(thickness):
    reduction = np.random.uniform(5, 10)
    return thickness * (1 - reduction/100), reduction

# -------------------------------
# TABS
# -------------------------------
tabs = st.tabs(["Aim", "Theory", "Procedure", "Simulation", "Quiz"])

# -------------------------------
# AIM
# -------------------------------
with tabs[0]:
    st.header("Aim")

    st.markdown("""
### Objective
- To understand the **photolithography process**
- To study the effect of **spin coating (RPM vs thickness)**
- To observe **thermal oxidation of silicon**
- To analyze **photoresist behavior during soft baking**
- To visualize **pattern transfer and development**
""")

# -------------------------------
# THEORY
# -------------------------------
with tabs[1]:
    st.header("Theory")

    st.markdown("""
### Photolithography Overview
Photolithography is a microfabrication technique used to transfer patterns onto substrates.

### Key Steps:
1. **Thermal Oxidation**
   - Si + O₂ → SiO₂
   - Consumes silicon (~44% of oxide thickness)

2. **Spin Coating**
   - Thickness inversely proportional to RPM

3. **Soft Bake**
   - Removes solvent
   - Improves adhesion

4. **Exposure**
   - UV light modifies resist solubility

5. **Development**
   - Exposed regions removed (positive resist)
   - Developer: **AZ 3000 MIF**

### Important Relation:
- Thickness ∝ 1 / RPM
""")

# -------------------------------
# PROCEDURE
# -------------------------------
with tabs[2]:
    st.header("Procedure")

    st.markdown("""
1. Select oxide thickness (thermal growth)
2. Choose resist type
3. Set target thickness and RPM
4. Observe resist thickness after spin coating
5. Perform soft bake and note reduction
6. Select mask pattern
7. Observe exposure and development
""")

# -------------------------------
# SIMULATION
# -------------------------------
with tabs[3]:

    st.title("Lithography Simulation")

    size = 15
    dx = 1/size

    # STEP 0
    st.subheader("Step 0: Silicon Substrate")
    si_thickness = 500

    fig0 = go.Figure()
    fig0.add_trace(create_block(0,0,1,1,0,si_thickness,"gray"))
    st.plotly_chart(fig0, use_container_width=True)

    # STEP 1: THERMAL OXIDATION
    st.subheader("Step 1: SiO₂ Growth")

    sio2_thickness = st.slider("Oxide Thickness (nm)", 50, 300, 150)

    # Si consumption ≈ 0.44 × oxide thickness
    si_consumed = 0.44 * sio2_thickness
    new_si_thickness = si_thickness - si_consumed

    st.write(f"Silicon Consumed: {si_consumed:.1f} nm")

    fig1 = go.Figure()
    fig1.add_trace(create_block(0,0,1,1,0,new_si_thickness,"gray"))
    fig1.add_trace(create_block(0,0,1,1,new_si_thickness,sio2_thickness,"blue"))
    st.plotly_chart(fig1, use_container_width=True)

    # STEP 2
    st.subheader("Step 2: Photoresist Coating")

    resist_type = st.selectbox("Resist Type", ["AZ1505", "PMMA"])

    if resist_type == "AZ1505":
        base_rpm = 3000
        ref_thickness = 500
    else:
        base_rpm = 4000
        ref_thickness = 300

    target_thickness = st.slider("Target Thickness (nm)", 100, 600, 200)
    suggested_rpm = int(base_rpm * (ref_thickness / target_thickness))

    st.write(f"Suggested RPM: {suggested_rpm}")

    rpm = st.slider("Spin Speed (RPM)", 1000, 6000, suggested_rpm)

    resist_thickness = ref_thickness * (base_rpm / rpm)

    st.write(f"Achieved Thickness: {resist_thickness:.1f} nm")

    fig2 = go.Figure()
    fig2.add_trace(create_block(0,0,1,1,0,new_si_thickness,"gray"))
    fig2.add_trace(create_block(0,0,1,1,new_si_thickness,sio2_thickness,"blue"))
    fig2.add_trace(create_block(
        0,0,1,1,
        new_si_thickness+sio2_thickness,
        resist_thickness,
        "orange"
    ))
    st.plotly_chart(fig2, use_container_width=True)

    # STEP 2.5
    st.subheader("Step 2.5: Soft Bake")

    baked_thickness, reduction = prebake_effect(resist_thickness)

    st.markdown(f"""
- Temperature: **90–100°C**
- Time: **60–90 sec**
- Thickness Reduction: **{reduction:.2f}%**
""")

    fig_pb = go.Figure()
    fig_pb.add_trace(create_block(0,0,1,1,0,new_si_thickness,"gray"))
    fig_pb.add_trace(create_block(0,0,1,1,new_si_thickness,sio2_thickness,"blue"))
    fig_pb.add_trace(create_block(
        0,0,1,1,
        new_si_thickness+sio2_thickness,
        baked_thickness,
        "#cc5500"   # darker resist
    ))
    st.plotly_chart(fig_pb, use_container_width=True)

    # STEP 3
    st.subheader("Step 3: Exposure")

    pattern = st.selectbox("Mask Pattern", ["Lines", "Dots", "Square"])
    mask = generate_mask(size, pattern)

    fig3 = go.Figure()
    fig3.add_trace(create_block(0,0,1,1,0,new_si_thickness,"gray"))
    fig3.add_trace(create_block(0,0,1,1,new_si_thickness,sio2_thickness,"blue"))

    for i in range(size):
        for j in range(size):
            x0, y0 = i*dx, j*dx
            exposed = mask[i,j] == 1

            color = "red" if exposed else "#cc5500"

            fig3.add_trace(create_block(
                x0,y0,dx,dx,
                new_si_thickness+sio2_thickness,
                baked_thickness,
                color
            ))

    st.plotly_chart(fig3, use_container_width=True)

    # STEP 4
    st.subheader("Step 4: Development")

    st.write("Developer Used: **AZ 3000 MIF**")

    fig4 = go.Figure()
    fig4.add_trace(create_block(0,0,1,1,0,new_si_thickness,"gray"))
    fig4.add_trace(create_block(0,0,1,1,new_si_thickness,sio2_thickness,"blue"))

    for i in range(size):
        for j in range(size):
            if mask[i,j] == 0:
                x0, y0 = i*dx, j*dx

                fig4.add_trace(create_block(
                    x0,y0,dx,dx,
                    new_si_thickness+sio2_thickness,
                    baked_thickness,
                    "green"
                ))

    st.plotly_chart(fig4, use_container_width=True)

# -------------------------------
# QUIZ
# -------------------------------
with tabs[4]:
    st.header("Quiz")

    q1 = st.radio(
        "1. What is the developer used for AZ1505?",
        ["KOH", "AZ 3000 MIF", "HF"]
    )

    q2 = st.radio(
        "2. Thickness is inversely proportional to?",
        ["Temperature", "RPM", "Exposure time"]
    )

    if st.button("Submit"):
        score = 0
        if q1 == "AZ 3000 MIF":
            score += 1
        if q2 == "RPM":
            score += 1

        st.success(f"Score: {score}/2")
