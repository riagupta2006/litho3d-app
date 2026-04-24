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
Occurs at 800–1200°C. Dry (slow) and wet (fast) oxidation methods are used.
""")

    st.subheader("Spin Coating")
    st.markdown("""
Final thickness depends on RPM:

t = k / √ω  

k calibrated for ~0.5 µm at 4000 RPM.
""")

    st.subheader("Soft Bake")
    st.markdown("""
Removes solvent, improves adhesion, prevents defects.  
Above 110°C: PAC degradation. Above 140°C: resist damage.
""")

    st.subheader("Exposure")
    st.markdown("""
UV light passes through mask. Exposed regions become soluble in developer.
""")

    st.subheader("Development")
    st.markdown("""
Exposed regions dissolve forming pattern.  
AZ1505 → AZ3000MIF  
PMMA → Isopropanol
""")

# -------------------------------
# PROCEDURE
# -------------------------------
with tab3:
    st.header("Procedure")
    st.markdown("""
Follow simulation steps. Adjust oxide thickness, select resist, tune RPM, observe bake, exposure, and development.
""")

# -------------------------------
# SIMULATION
# -------------------------------
with tab4:

    st.markdown("<h3 style='font-size:28px;'>Follow steps below</h3>", unsafe_allow_html=True)

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
        elif pattern=="Dots":
            for i in range(c-4,c+5,4):
                for j in range(c-4,c+5,4):
                    mask[i:i+2,j:j+2]=1
        else:
            mask[c-3:c+3,c-3:c+3]=1
        return mask

    def prebake_effect(resist,thick):
        red=np.random.uniform(5,10) if resist=="AZ1505" else np.random.uniform(8,15)
        return thick*(1-red/100),red

    size=15
    dx=1/size

    # STEP 0
    st.header("Step 0: Silicon")
    st.markdown("<p style='font-size:18px;'>Base wafer</p>",unsafe_allow_html=True)
    fig=go.Figure()
    fig.add_trace(create_block(0,0,1,1,0,200,"red"))
    st.plotly_chart(fig)

    # STEP 1
    st.header("Step 1: SiO₂ Growth")
    st.markdown("<p style='font-size:18px;'>Adjust oxide</p>",unsafe_allow_html=True)

    sio2=st.slider("Thickness",100,500,200)
    si_cons=0.44*sio2
    st.warning(f"Silicon Consumed: {si_cons:.2f} nm")

    fig=go.Figure()
    fig.add_trace(create_block(0,0,1,1,0,200-si_cons,"red"))
    fig.add_trace(create_block(0,0,1,1,200-si_cons,sio2,"blue"))
    st.plotly_chart(fig)

    # STEP 2
    st.header("Step 2: Photoresist")
    st.markdown("<p style='font-size:18px;'>Adjust coating</p>",unsafe_allow_html=True)

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
    st.markdown("<p style='font-size:18px;'>Heating reduces thickness</p>",unsafe_allow_html=True)

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
    st.markdown("<p style='font-size:18px;'>Pattern forms</p>",unsafe_allow_html=True)

    fig=go.Figure()
    fig.add_trace(create_block(0,0,1,1,0,200-si_cons,"red"))
    fig.add_trace(create_block(0,0,1,1,200-si_cons,sio2,"blue"))

    for i in range(size):
        for j in range(size):
            if mask[i,j]==0:
                fig.add_trace(create_block(i*dx,j*dx,dx,dx,200-si_cons+sio2,baked,"green"))

    st.plotly_chart(fig)

# -------------------------------
# QUIZ
# -------------------------------
with tab5:
    st.header("Quiz")
    ans=st.radio("Soft bake purpose?",["Remove solvent","Grow oxide","Etch wafer"])
    if ans=="Remove solvent":
        st.success("Correct!")
