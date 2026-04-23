import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Virtual Lab: Photolithography", layout="wide")

st.title("Virtual Lab: Photolithography")

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
# MASK (CENTERED)
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
    st.header("Aim & Objective")
    st.markdown("""
- Understand photolithography process  
- Study SiO₂ growth from silicon  
- Analyze RPM vs thickness relation  
- Observe soft bake effects  
- Visualize exposure and development  
""")

# -------------------------------
# THEORY
# -------------------------------
with tabs[1]:
    st.header("Theory")

    st.subheader("Thermal Oxidation")
    st.write("SiO₂ is grown from Si. ~44% oxide thickness comes from consumed silicon.")

    st.subheader("Spin Coating")
    st.write("""
Thickness ∝ 1 / √RPM  
Higher RPM → thinner film  
Controlled by viscosity and evaporation
""")

    st.subheader("Soft Bake")
    st.write("""
90–100°C for 60–90 sec  
Removes solvent → reduces thickness → darkens resist
""")

    st.subheader("Development")
    st.write("Developer used: AZ3000 MIF")

# -------------------------------
# PROCEDURE (ALIGNED WITH SIM)
# -------------------------------
with tabs[2]:
    st.header("Procedure")

    st.markdown("""
**Step 0:** Observe silicon substrate  

**Step 1:** Select oxide thickness and observe Si consumption  

**Step 2:** Choose resist type, set target thickness, and adjust RPM  

**Step 3:** Observe coated resist thickness  

**Step 4:** Perform soft bake and note thickness reduction  

**Step 5:** Select mask pattern and observe UV exposure  

**Step 6:** Observe development using AZ3000 MIF  
""")

# -------------------------------
# SIMULATION
# -------------------------------
with tabs[3]:

    size = 15
    dx = 1/size

    # STEP 0
    st.subheader("Step 0: Silicon Substrate")
    si_thickness = 500

    fig0 = go.Figure()
    fig0.add_trace(create_block(0,0,1,1,0,si_thickness,"gray"))
    st.plotly_chart(fig0, use_container_width=True)

    # STEP 1: OXIDATION
    st.subheader("Step 1: SiO₂ Growth")

    sio2_thickness = st.slider("Oxide Thickness (nm)", 50, 300, 150)

    si_consumed = 0.44 * sio2_thickness
    new_si_thickness = si_thickness - si_consumed

    st.write(f"Silicon Consumed: {si_consumed:.1f} nm")

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

    st.write(f"Reduction: {reduction:.2f}%")

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

    # STEP 3: EXPOSURE (WITH LIGHT BACK)
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

            # 🔥 YELLOW UV LIGHT (RESTORED)
            if exposed:
                fig3.add_trace(create_block(
                    x0, y0, dx, dx,
                    new_si_thickness+sio2_thickness+baked_thickness,
                    200,
                    "yellow",
                    opacity=0.2
                ))

    st.plotly_chart(fig3, use_container_width=True)

    # STEP 4
    st.subheader("Step 4: Development")

    st.write("Developer Used: AZ3000 MIF")

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
