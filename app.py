import streamlit as st
import time
from cpu import CPUSimulator

st.set_page_config(page_title="CPU X-Ray", layout="wide", page_icon="🖥️")
st.title("🖥️ CPU X-Ray Pro — Advanced Simulator")
st.markdown("Features: Multi-Level Caching, Branch Prediction Penalties, loops, and live performance metrics.")

def render_progress_bar(label, value, max_val, color="🟩"):
    percentage = min(100, int((value / max(1, max_val)) * 100))
    filled = int(percentage / 10)
    bar = (color * filled) + ("⬜" * (10 - filled))
    st.markdown(f"**{label}**: {bar} `{percentage}%`")

if 'cpu' not in st.session_state:
    st.session_state.cpu = CPUSimulator()
    st.session_state.program_loaded = False
    st.session_state.auto_play = False
    st.session_state.built_program = []

# -----------------------------------------
# Sidebar: Visual Code Builder
# -----------------------------------------
with st.sidebar:
    st.header("🛠️ Visual Code Builder")
    st.caption("No typing assembly required. Fill in the blanks!")
    
    with st.expander("➕ Create New Instruction", expanded=True):
        op_choice = st.selectbox("Operation", [
            "SET (Put a Number in a Register)",
            "LOAD (Read from Memory)", 
            "STORE (Write to Memory)", 
            "ADD (Math - Addition)", 
            "SUB (Math - Subtraction)", 
            "MUL (Math - Multiplication)", 
            "DIV (Math - Division)", 
            "LABEL (Create a Loop Point)", 
            "BNE (Branch/Loop if Not Equal)",
            "BEQ (Branch/Loop if Equal)", 
            "JUMP (Go directly to Label)"
        ])
        
        c1, c2, c3 = st.columns(3)
        arg1, arg2, arg3 = "", "", ""
        
        actual_op = op_choice.split()[0]
        
        if actual_op in ["LOAD", "STORE"]:
            with c1: 
                arg1 = st.selectbox("Register", [f"R{i}" for i in range(1, 9)])
            with c2: 
                arg2 = st.text_input("Memory Addr", "100")
                
        elif actual_op == "SET":
            with c1: 
                arg1 = st.selectbox("Register", [f"R{i}" for i in range(1, 9)])
            with c2: 
                arg2 = st.text_input("Number Value", "5")
            
        elif actual_op in ["ADD", "SUB", "MUL", "DIV"]:
            with c1: 
                arg1 = st.selectbox("Dest Reg", [f"R{i}" for i in range(1, 9)])
            with c2: 
                arg2 = st.selectbox("Val 1 (Reg)", [f"R{i}" for i in range(1, 9)])
            with c3: 
                arg3 = st.text_input("Val 2 (Num/Reg)", "1")
                
        elif actual_op in ["BEQ", "BNE"]:
            with c1: 
                arg1 = st.selectbox("Compare 1", [f"R{i}" for i in range(1, 9)])
            with c2: 
                arg2 = st.selectbox("Compare 2", [f"R{i}" for i in range(1, 9)])
            with c3: 
                arg3 = st.text_input("Target Label", "LOOP")
                
        elif actual_op == "JUMP":
            with c1: 
                arg1 = st.text_input("Target Label", "LOOP")
                
        elif actual_op == "LABEL":
            with c1: 
                arg1 = st.text_input("Label Name", "LOOP")

        if st.button("➕ Add to Program", use_container_width=True):
            if actual_op == "LABEL": 
                inst = f"{arg1}:"
            elif actual_op in ["LOAD", "STORE", "SET"]: 
                inst = f"{actual_op} {arg1}, {arg2}"
            elif actual_op in ["ADD", "SUB", "MUL", "DIV"]: 
                inst = f"{actual_op} {arg1}, {arg2}, {arg3}"
            elif actual_op in ["BEQ", "BNE"]: 
                inst = f"{actual_op} {arg1}, {arg2}, {arg3}"
            elif actual_op == "JUMP": 
                inst = f"{actual_op} {arg1}"
            
            st.session_state.built_program.append(inst)
            st.rerun()

    st.divider()
    st.markdown("**📝 Your Current Program:**")
    
    if st.session_state.built_program:
        st.code("\n".join(st.session_state.built_program), language="assembly")
    else:
        st.info("Program is empty. Add instructions above.")
        
    btn1, btn2 = st.columns(2)
    with btn1:
        if st.button("↩️ Undo Last"):
            if st.session_state.built_program:
                st.session_state.built_program.pop()
                st.rerun()
    with btn2:
        if st.button("🗑️ Clear All"):
            st.session_state.built_program = []
            st.rerun()
            
    st.divider()
    
    optimization = st.toggle("🚀 Enable Forwarding", value=False)
    
    if st.button("⚙️ Compile & Load", type="primary", use_container_width=True):
        st.session_state.cpu.reset(optimization=optimization)
        success, msg = st.session_state.cpu.load_program(st.session_state.built_program)
        
        if success:
            st.session_state.program_loaded = True
            st.session_state.auto_play = False
            st.success(msg)
        else:
            st.session_state.program_loaded = False
            st.error(f"❌ COMPILER ERROR:\n{msg}")

    st.divider()
    st.subheader("Execution Controls")
    c_ctrl1, c_ctrl2 = st.columns(2)
    with c_ctrl1:
        if st.button("Step ⏭️") and st.session_state.program_loaded: 
            st.session_state.cpu.step()
    with c_ctrl2:
        if st.button("Reset 🔄"): 
            st.session_state.cpu.reset()
            st.session_state.program_loaded = False
            st.rerun()

    if st.button("🎬 Auto-Play Animation", use_container_width=True) and st.session_state.program_loaded:
        st.session_state.auto_play = True

# -----------------------------------------
# Main UI Layout
# -----------------------------------------
if st.session_state.program_loaded:
    stats = st.session_state.cpu.get_stats()
    
    st.subheader("📊 Live Performance Analytics")
    c1, c2 = st.columns(2)
    with c1:
        cpi = round(stats["cycles"] / max(1, stats["completed_instructions"]), 2)
        st.markdown(f"**⚡ Cycles Per Instruction (CPI):** `{cpi}` *(Lower is better)*")
        st.markdown(f"**🚧 Total Pipeline Flushes (Hazards):** `{stats['hazards']}`")
    with c2:
        total_l1 = stats['l1_hits'] + stats['l1_misses']
        total_l2 = stats['l2_hits'] + stats['l2_misses']
        render_progress_bar("L1 Cache Hit Rate", stats['l1_hits'], total_l1, "🟦")
        render_progress_bar("L2 Cache Hit Rate", stats['l2_hits'], total_l2, "🟪")

    st.divider()

    st.subheader("🛤️ Superscalar Pipeline")
    pipe = st.session_state.cpu.get_pipeline_state()
    p1, p2, p3, p4, p5 = st.columns(5)
    with p1: st.info(f"**Fetch (IF)**\n\n`{pipe.get('IF', 'Empty')}`")
    with p2: st.info(f"**Decode (ID)**\n\n`{pipe.get('ID', 'Empty')}`")
    with p3: st.warning(f"**Execute (EX)**\n\n`{pipe.get('EX', 'Empty')}`")
    with p4: st.error(f"**Memory (MEM)**\n\n`{pipe.get('MEM', 'Empty')}`")
    with p5: st.success(f"**Writeback (WB)**\n\n`{pipe.get('WB', 'Empty')}`")

    st.divider()

    col_reg, col_c1, col_c2, col_mem = st.columns([1, 1, 1, 1])
    
    with col_reg:
        st.subheader("📝 Registers")
        md = "| Reg | Val |\n|---|---|\n"
        for r, v in st.session_state.cpu.get_registers().items(): 
            md += f"| **{r}** | `{v}` |\n"
        st.markdown(md)

    l1, l2 = st.session_state.cpu.get_caches()
    with col_c1:
        st.subheader("⚡ L1 Cache")
        md = "| Addr | Val |\n|---|---|\n"
        for a, v in l1.items(): 
            md += f"| **{a}** | `{v}` |\n"
        st.markdown(md if l1 else "*Empty*")

    with col_c2:
        st.subheader("🐢 L2 Cache")
        md = "| Addr | Val |\n|---|---|\n"
        for a, v in l2.items(): 
            md += f"| **{a}** | `{v}` |\n"
        st.markdown(md if l2 else "*Empty*")

    with col_mem:
        st.subheader("🧠 RAM")
        mem = st.session_state.cpu.get_memory()
        md = "| Addr | Val |\n|---|---|\n"
        for a, v in mem.items(): 
            md += f"| **{a}** | `{v}` |\n"
        st.markdown(md if mem else "*Empty*")

if st.session_state.get('auto_play'):
    cpu = st.session_state.cpu
    if any(cpu.pipeline.values()) or cpu.pc < len(cpu.instructions):
        cpu.step()
        time.sleep(0.6) 
        st.rerun() 
    else:
        st.session_state.auto_play = False
        st.balloons()