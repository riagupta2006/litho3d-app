import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Virtual Lab: Photolithography", layout="wide")

st.title("🧪 Virtual Lab: Photolithography")

# -------------------------------
# BLOCK FUNCTION (SOLID)
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
# PREBAKE MODEL
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
    st.header("Aim & Objective")

    st.markdown("""
- To understand the **photolithography process used in microfabrication**
- To study **thermal oxidation of silicon**
- To analyze **spin coating and RPM–thickness relationship**
- To observe **photoresist changes during soft baking**
- To visualize **pattern transfer and development using AZ3000 MIF**
""")

# -------------------------------
# THEORY
# -------------------------------
with tabs[1]:
    st.header("Theory")

    st.subheader("1. Thermal Oxidation of Silicon")
    st.markdown("""
Silicon dioxide (SiO₂) is grown by oxidizing silicon at high temperatures (900–1100°C).

Reaction:
Si + O₂ → SiO₂

During this process:
- Silicon is **consumed**
- Approximately **44% of oxide thickness comes from silicon**
- Remaining comes from oxygen incorporation
""")

    st.subheader("2. Spin Coating")
    st.markdown("""
Spin coating is used to deposit a uniform thin film of photoresist.

Process:
- Liquid resist is dispensed on wafer
- Wafer spins at high RPM
- Centrifugal force spreads resist

### Thickness Dependence:
Thickness depends on:
- Spin speed (RPM)
- Viscosity of resist
- Solvent evaporation rate

### Empirical Relation:
Thickness ∝ 1 / √RPM

This is called the **inverse square root law**, meaning:
- Doubling RPM reduces thickness by ~√2
""")

    st.subheader("3. Soft Bake (Pre-bake)")
    st.markdown("""
Purpose:
- Remove solvent
- Improve adhesion
- Stabilize resist

Typical Conditions:
- Temperature: **90–100°C**
- Time: **60–90 seconds**

Effects:
- Thickness reduces (~5–10%)
- Resist becomes **denser and slightly darker**
""")

    st.subheader("4. Exposure & Development")
    st.markdown("""
- UV light modifies resist solubility
- Positive resist → exposed areas removed

### Developer Used:
**AZ 3000 MIF**
- Metal-ion-free developer
- Provides clean and controlled development
""")

# -------------------------------
# PROCEDURE
# -------------------------------
with tabs[2]:
    st.header("Procedure")

    st.markdown("""
**Step 1:** Select oxide thickness (thermal growth)

**Step 2:** Choose photoresist type

**Step 3:** Set target thickness and RPM

**Step 4:** Observe resist thickness after spin coating

**Step 5:** Perform soft bake and note thickness reduction

**Step 6:** Select mask pattern and observe exposure

**Step 7:** Perform development using AZ3000 MIF

**Step 8:** Analyze final pattern
""")

# -------------------------------
# SIMULATION
# -------------------------------
with tabs[3]:

    st.header("Simulation")

    size = 15
    dx = 1/size

    # STEP 0
    st.subheader("Step 0: Silicon Substrate")
    si_thickness = 500

    fig0 = go.Figure()
    fig0.add_trace(create_block(0,0,1,1,0,si_thickness,"gray"))
    st.plotly_chart(fig0, use_container_width=True)

    # STEP 1: OXIDATION
    st.subheader("Step 1: Thermal Oxidation (SiO₂ Growth)")

    sio2_thickness = st.slider("Oxide Thickness (nm)", 50, 300, 150)

    si_consumed = 0.44 * sio2_thickness
    new_si_thickness = si_thickness - si_consumed

    st.markdown(f"""
- Silicon Consumed: **{si_consumed:.1f} nm**
- This follows practical oxidation physics (~44% rule)
""")

    fig1 = go.Figure()
    fig1.add_trace(create_block(0,0,1,1,0,new_si_thickness,"gray"))
    fig1.add_trace(create_block(0,0,1,1,new_si_thickness,sio2_thickness,"blue"))
    st.plotly_chart(fig1, use_container_width=True)

    # STEP 2
    st.subheader("Step 2: Spin Coating")

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

    st.markdown(f"""
- Achieved Thickness: **{resist_thickness:.1f} nm**
- Demonstrates inverse relation between RPM and thickness
""")

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
- Resist becomes darker due to solvent evaporation
""")

    fig_pb = go.Figure()
    fig_pb.add_trace(create_block(0,0,1,1,0,new_si_thickness,"gray"))
    fig_pb.add_trace(create_block(0,0,1,1,new_si_thickness,sio2_thickness,"blue"))
    fig_pb.add_trace(create_block(
        0,0,1,1,
        new_si_thickness+sio2_thickness,
        baked_thickness,
        "#cc5500"
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

    st.markdown("""
**Developer Used: AZ 3000 MIF**
- Metal-ion-free developer
- Removes exposed regions in positive resist
- Ensures clean pattern transfer
""")

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

    q1 = st.radio("Developer used?", ["KOH", "AZ3000 MIF", "HF"])
    q2 = st.radio("Thickness relation?", ["∝ RPM", "∝ 1/√RPM", "∝ Temperature"])

    if st.button("Submit"):
        score = 0
        if q1 == "AZ3000 MIF": score += 1
        if q2 == "∝ 1/√RPM": score += 1

        st.success(f"Score: {score}/2")
