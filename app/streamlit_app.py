from pathlib import Path
import sys
import json

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from midnight_propulsion_lab.mission import BASELINES, Scenario, evaluate  # noqa: E402

st.set_page_config(page_title="Midnight Propulsion Lab", layout="wide")
st.markdown("""<style>
    .stApp {background: #121517; color: #f1ede3;}
    [data-testid="stSidebar"] {background: #191d20;}
    h1, h2, h3 {color: #f4f0e6 !important; letter-spacing: .02em;}
    .stCaption {color: #aeb6b8 !important;}
    [data-testid="stDataFrame"] {border: 1px solid #355257; border-radius: 6px;}
    .stButton button, .stDownloadButton button {border-color: #61c4cc; color: #61c4cc;}
</style>""", unsafe_allow_html=True)
st.title("The Crossover Problem")
st.caption("A transparent mass-and-thrust screening model. It is not a low-thrust trajectory optimizer.")
with st.sidebar:
    st.header("Mission assumptions")
    mass = st.slider("Initial mass [kg]", 5_000, 50_000, 20_000, 500)
    payload = st.slider("Payload [kg]", 0, 10_000, 2_000, 100)
    dv = st.slider("Equivalent Δv [m/s]", 1_000, 25_000, 9_000, 250)
    days = st.slider("Allowed duration [days]", 30, 1_500, 365, 5)
scenario = Scenario(initial_mass_kg=mass, payload_kg=payload, delta_v_m_s=dv, duration_days=days)
rows = [evaluate(scenario, a).record() for a in BASELINES.values()]
feasible = sum(row["feasible"] for row in rows)
left, right = st.columns(2)
left.metric("Feasible architectures", f"{feasible} / {len(rows)}")
right.metric("NEP radiator estimate", f"{rows[-1]['radiator_area_m2']:.1f} m²")
st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
st.info("NEP feasibility uses Δv / allowed time as a necessary acceleration proxy. A mission that passes this test still requires trajectory optimization.")
trajectory_file = ROOT / "results" / "trajectory_comparison.json"
if trajectory_file.exists():
    trajectory = json.loads(trajectory_file.read_text(encoding="utf-8"))["trajectory"]
    st.subheader("Separate trajectory benchmark")
    st.caption("Circular-coplanar, Sun-only surrogate with loose arrival gates; not an operational Earth-to-Mars trajectory.")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Arrival gate passed", "Yes" if trajectory["success"] else "No")
    c2.metric("Optimizer converged", "Yes" if trajectory.get("optimizer_converged", False) else "No")
    c3.metric("Position residual", f"{trajectory['final_position_error_m']/1e3:.1f} km")
    c4.metric("Propellant used", f"{trajectory['propellant_used_kg']:.1f} kg")
st.download_button("Download current screen as CSV", pd.DataFrame(rows).to_csv(index=False), "architecture_screen.csv", "text/csv")
