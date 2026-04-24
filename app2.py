import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Lithography Virtual Lab", layout="wide")

st.title("Virtual Lab: Photolithography")

# -------------------------------
# TABS
# -------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Aim", "Theory", "Procedure", "Simulation", "Quiz"])

# -------------------------------
# AIM
# -------------------------------
with tab1:
    st.header("Aim")
    st.markdown("""
Understand photolithography process from oxide growth to development.  
Simulate spin coating of positive photoresist on grown SiO2.  
Analyze emperical relationship between RPM and thickness of photorests film.  
Observe thermal effects of the Soft Bake process on film densification and photoactive compound stability.  
Visualize mask creation, exposure of photoresist and development of photoresist.
""")

# -------------------------------
# THEORY
# -------------------------------
with tab2:
    st.header("Theory")

    st.subheader("Thermal Oxidation")
    st.markdown("""
SiO₂ is grown from Si where ~44% oxide thickness comes from consumed silicon.  
This process takes place in a diffusion furnace at temperatures between 800°C and 1200°C to grow SiO2.  
Two methods are commonly used — dry oxidation (lengthy process) and wet oxidation (faster process).
""")

    st.subheader("Spin Coating")
    st.markdown("""
Spin coating is used to deposit uniform thin films onto flat substrates.  
The final film thickness (t) depends heavily on the spin speed (ω in RPM) and the viscosity of the photoresist.  

For AZ 1505:
t = k / √ω  

k is a resist-specific constant calibrated to yield ~0.5 µm at 4000 RPM.
""")

    st.subheader("Soft Bake")
    st.markdown("""
Photoresist is heated at 90–100°C for 60–90 seconds in order to:  
i) Remove excess solvent from photoresist coating  
ii) Increase adhesion of photoresist to SiO2  
iii) Reduce contamination and mask damage  

Temperatures above 110°C risk thermally degrading the Photoactive Compound (PAC).  
Above 140°C, resist cross-links and chars.
""")

    st.subheader("Exposure")
    st.markdown("""
During exposure, ultraviolet (UV) light is passed through a mask onto the photoresist.  
In positive photoresist (AZ1505), exposed regions undergo chemical changes that increase their solubility in the developer.  
The intensity and duration of exposure determine the resolution and accuracy of the transferred pattern.
""")

    st.subheader("Development")
    st.markdown("""
Development removes portions of the photoresist altered by light exposure, converting a latent image into a physical pattern.  

Developer used:  
- AZ1505 → AZ3000MIF  
- PMMA → Isopropanol
""")

# -------------------------------
# PROCEDURE
# -------------------------------
with tab3:
    st.header("Procedure")
    st.markdown("""
Navigate the simulation tab.  
Observe the Silicon substrate to be operated on.  
Adjust the slider to the desired amount of growth required and observe how much silicon gets consumed.  
Choose the preferred positive photoresist.  
Select preferred thickness of photoresist if unsure of spin speed of spin coater. The suggested RPM is automatically selected.  
Observe the reduction in thickness of photoresist as it is heated during the Soft Bake process.  
Choose the desired mask and observe how the photoresist is exposed to the UV light.  
The simulation is concluded with the development process where the required pattern is created on the photoresist.
""")

# -------------------------------
# SIMULATION (UNCHANGED)
# -------------------------------
with tab4:

    st.markdown("<h3 style='font-size:28px;'>Follow the steps below to run the simulation</h3>", unsafe_allow_html=True)

    # -------------------------------
    # (YOUR ORIGINAL SIMULATION CODE STARTS HERE)
    # NOTHING CHANGED EXCEPT INSTRUCTION FONT SIZE
    # -------------------------------

    def create_block(x0, y0, dx, dy, z0, dz, color, opacity=1.0):
        x = [x0, x0+dx, x0+dx, x0, x0, x0+dx, x0+dx, x0]
        y = [y0, y0, y0+dy, y0+dy, y0, y0, y0+dy, y0+dy]
        z = [z0, z0, z0, z0, z0+dz, z0+dz, z0+dz, z0+dz]

        i = [0,0, 4,4, 0,0, 2,2, 1,1, 0,0]
        j = [1,2, 5,6, 1,5, 3,7, 2,6, 3,7]
        k = [2,3, 6,7, 5,4, 7,6, 6,5, 7,4]

        return go.Mesh3d(x=x,y=y,z=z,i=i,j=j,k=k,color=color,opacity=opacity,flatshading=True)

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

    def prebake_effect(resist_type, thickness):
        if resist_type == "AZ1505":
            reduction_percent = np.random.uniform(5, 10)
        else:
            reduction_percent = np.random.uniform(8, 15)
        return thickness*(1-reduction_percent/100), reduction_percent

    size = 15
    dx = 1/size

    st.header("Step 0: Silicon Substrate")
    st.markdown("<p style='font-size:18px;'>This is the base wafer.</p>", unsafe_allow_html=True)

    fig0 = go.Figure()
    fig0.add_trace(create_block(0,0,1,1,0,200,"red"))
    st.plotly_chart(fig0, use_container_width=True)

    st.header("Step 1: SiO₂ Growth")
    st.markdown("<p style='font-size:18px;'>Adjust oxide thickness and observe silicon consumption.</p>", unsafe_allow_html=True)

    sio2_thickness = st.slider("SiO₂ Thickness (nm)", 100, 500, 200)
    si_consumed = 0.44 * sio2_thickness

    st.warning(f"Silicon Consumed: {si_consumed:.2f} nm")

    fig1 = go.Figure()
    fig1.add_trace(create_block(0,0,1,1,0,200-si_consumed,"red"))
    fig1.add_trace(create_block(0,0,1,1,200-si_consumed,sio2_thickness,"blue"))
    st.plotly_chart(fig1, use_container_width=True)

    st.header("Step 2: Photoresist")
    st.markdown("<p style='font-size:18px;'>Select resist and adjust RPM/thickness.</p>", unsafe_allow_html=True)

    resist_type = st.selectbox("Resist Type", ["AZ1505","PMMA"])

    base_rpm = 3000 if resist_type=="AZ1505" else 4000
    ref_thickness = 500 if resist_type=="AZ1505" else 300

    target_thickness = st.slider("Target Thickness (nm)", 100, 600, 200)
    suggested_rpm = int(base_rpm*(ref_thickness/target_thickness))

    rpm = st.slider("RPM", int(base_rpm*(ref_thickness/600)), int(base_rpm*(ref_thickness/100)), suggested_rpm)
    resist_thickness = ref_thickness*(base_rpm/rpm)

    fig2 = go.Figure()
    fig2.add_trace(create_block(0,0,1,1,0,200-si_consumed,"red"))
    fig2.add_trace(create_block(0,0,1,1,200-si_consumed,sio2_thickness,"blue"))
    fig2.add_trace(create_block(0,0,1,1,200-si_consumed+sio2_thickness,resist_thickness,"orange"))
    st.plotly_chart(fig2, use_container_width=True)

st.header("Step 3: Soft Bake")
st.markdown("<p style='font-size:18px;'>Observe thickness reduction after heating.</p>", unsafe_allow_html=True)

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
fig_pb.add_trace(create_block(0,0,1,1,0,200-si_consumed,"red"))
fig_pb.add_trace(create_block(0,0,1,1,200-si_consumed,sio2_thickness,"blue"))
fig_pb.add_trace(create_block(
    0,0,1,1,
    200-si_consumed+sio2_thickness,
    baked_thickness,
    "orangered"
))
st.plotly_chart(fig_pb, use_container_width=True)


for i in range(size):
    for j in range(size):
        x0, y0 = i*dx, j*dx
        exposed = mask[i,j] == 1

        color = "red" if exposed else "orangered"

        fig3.add_trace(create_block(
            x0, y0, dx, dx,
            200-si_consumed+sio2_thickness,
            baked_thickness,
            color
        ))

        # ---- UV LIGHT (RESTORED) ----
        if exposed:
            fig3.add_trace(create_block(
                x0, y0, dx, dx,
                200-si_consumed+sio2_thickness+baked_thickness,
                200,
                "yellow",
                opacity=0.2
            ))


st.header("Step 5: Development")
st.markdown("<p style='font-size:18px;'>Unexposed regions remain while exposed regions are removed, forming the final pattern.</p>", unsafe_allow_html=True)

fig4 = go.Figure()
fig4.add_trace(create_block(0,0,1,1,0,200-si_consumed,"red"))
fig4.add_trace(create_block(0,0,1,1,200-si_consumed,sio2_thickness,"blue"))

for i in range(size):
    for j in range(size):
        if mask[i,j] == 0:
            x0, y0 = i*dx, j*dx

            fig4.add_trace(create_block(
                x0, y0, dx, dx,
                200-si_consumed+sio2_thickness,
                baked_thickness,
                "green"
            ))

st.plotly_chart(fig4, use_container_width=True)


# -------------------------------
# QUIZ
# -------------------------------
with tab5:
    st.header("Quiz")

    q1 = st.radio("What happens during soft bake?",
                  ["Solvent removal", "Oxide growth", "Etching"])
    if q1 == "Solvent removal":
        st.success("Correct!")
