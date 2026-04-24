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
1. Understand photolithography process from oxide growth to development.  
2. Simulate spin coating of positive photoresist on grown SiO2.  
3. Analyze emperical relationship between RPM and thickness of photorests film.  
4. Observe thermal effects of the Soft Bake process on film densification and photoactive compound stability.  
5. Visualize mask creation, exposure of photoresist and development of photoresist.
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
Two methods are commonly used- dry oxidation (lengthy process) and wet oxidation (faster process)
""")

    st.subheader("Spin Coating")
    st.markdown("""
Spin coating is used to deposit uniform thin films onto flat substrates.
The final film thickness (t) depends heavily on the spin speed (ω in RPM) and the viscosity of the photoresist.
For AZ 1505, this can be approximated using the inverse square root law:

        t = k / √ω
        
k is a resist-specific constant calibrated to yield ~0.5 µm at 4000 RPM.
""")

    st.subheader("Soft Bake")
    st.markdown("""
Photoresist is heated at 90–100°C for 60–90 seconds in order to:

i)   Remove excess solvent from photoresist coating.

ii)  Increase adhesion of photoresist to the underlying material (SiO2).

iii) Reduce contamination and mask damage.

Temperatures above 110°C risk thermally degrading the Photoactive Compound (PAC). 
Temperatures above 140°C cause the resist to cross-link and char, rendering it useless for UV exposure.
""")

    st.subheader("Exposure")
    st.markdown("""
UV light (wavelength of 365nm) is passed through the mask chosen.

When certain areas are exposed to UV light, photoresist becomes soluble in developer in those areas.

During exposure, ultraviolet (UV) light is passed through a mask onto the photoresist.  
In positive photoresist (AZ1505 and PMMA), exposed regions undergo chemical changes that increase their solubility in the developer.  
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
1. Navigate the simulation tab.
2. Observe the Silicon substrate to be operated on.
3. Adjust the slider to the desired amount of growth required and observe how much silicon gets consumed.
4. Choose the preferred positive photoresist.
5. Select preferred thickness of photoresist if unsure of spin speed of spin coater. The suggested RPM is automatically selected.
6. Observe the reduction in thickness of photoresist as it is heated during the Soft Bake process.
7. Choose the desired mask and observe how the photoresist is exposed to the UV light.
8. The simulation is concluded with the develpment process where the required pattern is created on the photoresist.
""")

# -------------------------------
# SIMULATION
# -------------------------------
with tab4:

    def create_block(x0, y0, dx, dy, z0, dz, color, opacity=1.0):
        x = [x0,x0+dx,x0+dx,x0,x0,x0+dx,x0+dx,x0]
        y = [y0,y0,y0+dy,y0+dy,y0,y0,y0+dy,y0+dy]
        z = [z0,z0,z0,z0,z0+dz,z0+dz,z0+dz,z0+dz]

        i=[0,0,4,4,0,0,2,2,1,1,0,0]
        j=[1,2,5,6,1,5,3,7,2,6,3,7]
        k=[2,3,6,7,5,4,7,6,6,5,7,4]

        return go.Mesh3d(x=x,y=y,z=z,i=i,j=j,k=k,color=color,opacity=opacity)

    def generate_mask(size,pattern):
        mask=np.zeros((size,size))
        c=size//2
        if pattern=="Lines":
            for j in range(-2,3,2):
                mask[:,c+j]=1
        elif pattern == "Dots":
            radius = size // 10
            for i in range(size):
                for j in range(size):
                    if (i - center)**2 + (j - center)**2 <= radius**2:
                        mask[i, j] = 1
        else:
            mask[c-3:c+3,c-3:c+3]=1
        return mask

    def prebake_effect(resist,thick):
        red=np.random.uniform(5,10) if resist=="AZ1505" else np.random.uniform(8,15)
        return thick*(1-red/100),red

size = 50
dx = 1 / size

    # STEP 0
    st.header("Step 0: Silicon substrate is taken")
    st.markdown("<p style='font-size:18px;'>Base wafer of 200nm is taken and cleaned by following the rca procedures.</p>",unsafe_allow_html=True)
    fig=go.Figure()
    fig.add_trace(create_block(0,0,1,1,0,200,"red"))
    st.plotly_chart(fig)

    # STEP 1
    st.header("Step 1: SiO₂ Growth on Silicon Substrate")
    st.markdown("<p style='font-size:18px;'>Thickness of SiO2 is decided by understanding growth rates determined by temperature and time. SiO2 is grown by consuming 44% of underlying Silicon.</p>",unsafe_allow_html=True)
    sio2=st.slider("Thickness",100,500,200)
    si_cons=0.44*sio2
    st.warning(f"Silicon Consumed: {si_cons:.2f} nm")

    fig=go.Figure()
    fig.add_trace(create_block(0,0,1,1,0,200-si_cons,"red"))
    fig.add_trace(create_block(0,0,1,1,200-si_cons,sio2,"blue"))
    st.plotly_chart(fig)

    # STEP 2
    st.header("Step 2: Photoresist")
    st.markdown("<p style='font-size:18px;'>Use the RPM slider to decide speed at which photoresist of desired thickness is coated (use the target thickness rpm recommender if unsure).</p>",unsafe_allow_html=True)

    rtype=st.selectbox("Resist",["AZ1505","PMMA"])
    base=3000 if rtype=="AZ1505" else 4000
    ref=500 if rtype=="AZ1505" else 300

    tgt=st.slider("Thickness",100,600,200)
    rpm=st.slider("RPM",int(base*(ref/600)),int(base*(ref/100)),int(base*(ref/tgt)))
    rthick=ref*(base/rpm)

    fig=go.Figure()
    fig.add_trace(create_block(0,0,1,1,0,200-si_cons,"red"))
    fig.add_trace(create_block(0,0,1,1,200-si_cons,sio2,"blue"))
    fig.add_trace(create_block(0,0,1,1,200-si_cons+sio2,rthick,"orange"))
    st.plotly_chart(fig)

    # STEP 3
    st.header("Step 3: Soft Bake")
    st.markdown("<p style='font-size:18px;'>Observe redusction of thickness.</p>",unsafe_allow_html=True)

    baked,red=prebake_effect(rtype,rthick)

    st.markdown(f"""
Temperature: 90–100°C  
Time: 60–90 sec  

Before: {rthick:.1f} nm  
After: {baked:.1f} nm  
Reduction: {red:.2f}%
""")

    fig=go.Figure()
    fig.add_trace(create_block(0,0,1,1,0,200-si_cons,"red"))
    fig.add_trace(create_block(0,0,1,1,200-si_cons,sio2,"blue"))
    fig.add_trace(create_block(0,0,1,1,200-si_cons+sio2,baked,"tomato"))
    st.plotly_chart(fig)

    # STEP 4
    st.header("Step 4: Exposure")
    st.markdown("<p style='font-size:18px;'>Choose desired pattern to be used as mask.</p>",unsafe_allow_html=True)
    pat=st.selectbox("Mask",["Lines","Dots","Square"])
    mask=generate_mask(size,pat)

    fig=go.Figure()
    fig.add_trace(create_block(0,0,1,1,0,200-si_cons,"red"))
    fig.add_trace(create_block(0,0,1,1,200-si_cons,sio2,"blue"))

    for i in range(size):
        for j in range(size):
            x,y=i*dx,j*dx
            exp=mask[i,j]==1
            col="red" if exp else "tomato"

            fig.add_trace(create_block(x,y,dx,dx,200-si_cons+sio2,baked,col))

            if exp:
                fig.add_trace(create_block(x,y,dx,dx,200-si_cons+sio2+baked,200,"yellow",0.2))

    st.plotly_chart(fig)

    # STEP 5
    st.header("Step 5: Development")
    st.markdown("<p style='font-size:18px;'>Developer (AZ3000MIF/Isopropanol) is used to develop the photoresist after exposure and the desired pattern is obtained.</p>",unsafe_allow_html=True)

    fig=go.Figure()
    fig.add_trace(create_block(0,0,1,1,0,200-si_cons,"red"))
    fig.add_trace(create_block(0,0,1,1,200-si_cons,sio2,"blue"))

    for i in range(size):
        for j in range(size):
            if mask[i,j]==0:
                fig.add_trace(create_block(i*dx,j*dx,dx,dx,200-si_cons+sio2,baked,"green"))

    st.plotly_chart(fig)
st.success("Simulation Successfully Completed!")

# -------------------------------
# QUIZ
# -------------------------------
# -------------------------------
# QUIZ
# -------------------------------
with tab5:
    st.header("Quiz")

    score = 0

    # Q1
    q1 = st.radio(
        "1. During thermal oxidation, what fraction of SiO₂ thickness comes from consumed silicon?",
        ["~20%", "~44%", "~70%", "~100%"]
    )
    if q1 == "~44%":
        st.success("Correct!")
        score += 1
    else:
        st.error("Incorrect. About 44% comes from silicon consumption.")

    # Q2
    q2 = st.radio(
        "2. What is the relationship between spin speed (RPM) and photoresist thickness?",
        ["t ∝ RPM", "t ∝ 1/RPM", "t ∝ 1/√RPM", "t ∝ √RPM"]
    )
    if q2 == "t ∝ 1/√RPM":
        st.success("Correct!")
        score += 1
    else:
        st.error("Incorrect. Thickness follows inverse square root relation.")

    # Q3
    q3 = st.radio(
        "3. What is the main purpose of soft bake?",
        ["Grow oxide", "Remove solvent", "Etch silicon", "Increase exposure"]
    )
    if q3 == "Remove solvent":
        st.success("Correct!")
        score += 1
    else:
        st.error("Incorrect. Soft bake removes solvent and stabilizes resist.")

    # Q4
    q4 = st.radio(
        "4. In positive photoresist, what happens to exposed regions?",
        ["They harden", "They become insoluble", "They become more soluble", "Nothing happens"]
    )
    if q4 == "They become more soluble":
        st.success("Correct!")
        score += 1
    else:
        st.error("Incorrect. Exposure increases solubility.")

    # Q5
    q5 = st.radio(
        "5. Which developer is used for AZ1505?",
        ["Water", "Acetone", "AZ3000MIF", "Isopropanol"]
    )
    if q5 == "AZ3000MIF":
        st.success("Correct!")
        score += 1
    else:
        st.error("Incorrect. AZ3000MIF is used.")

    # Final Score
    st.markdown("---")
    st.subheader(f"Your Score: {score}/5")

    if score == 5:
        st.balloons()
        st.success("Excellent! You have a strong understanding of photolithography.")
    elif score >= 3:
        st.info("Good job! Review a few concepts to improve further.")
    else:
        st.warning("Revise the theory and try again.")
