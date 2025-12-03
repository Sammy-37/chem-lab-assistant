import streamlit as st
import re

st.set_page_config(page_title="ChemCalc Pro", page_icon="⚗️")

st.title("⚗️ ChemCalc: Lab Assistant")

# --- DEBUGGING SECTION ---
# This block attempts to load the library and tells you if it fails
try:
    with st.spinner("Loading Periodic Table Database..."):
        from mendeleev import element
    st.success("✅ System Status: Mendeleev Library Loaded Successfully")
except ImportError:
    st.error("❌ Critical Error: 'mendeleev' library not found. Please run 'pip install mendeleev'.")
    st.stop()
except Exception as e:
    st.error(f"❌ Database Error: {e}")
    st.info("Try running 'mendeleev-install' in your terminal to fix the database.")
    st.stop()


# --- LOGIC ---
def calculate_molar_mass(formula):
    if not formula:
        return 0, "Please enter a formula"

    # Regex to capture "Element" and "Count"
    tokens = re.findall(r'([A-Z][a-z]*)(\d*)', formula)

    if not tokens:
        return 0, "Error: Check capitalization (e.g., Use 'H', not 'h')"

    total_mass = 0
    details = []

    for symbol, count in tokens:
        try:
            # FETCH DATA FROM LIBRARY
            atom = element(symbol)  # This queries the database
            mass_val = atom.atomic_weight

            num_atoms = int(count) if count else 1
            total_mass += mass_val * num_atoms
            details.append(f"{num_atoms}x{symbol} ({mass_val:.2f})")

        except Exception:
            return 0, f"Error: Element '{symbol}' does not exist in the periodic table."

    return total_mass, " + ".join(details)


# --- UI ---
st.header("1. Molar Mass Calculator")
formula_input = st.text_input("Enter Formula:", "C6H12O6")

if st.button("Calculate Mass"):
    mass, log = calculate_molar_mass(formula_input)

    if mass > 0:
        st.success(f"Molar Mass: {mass:.3f} g/mol")
        st.text(f"Breakdown: {log}")
        st.session_state['saved_mass'] = mass
    else:
        st.error(log)

st.markdown("---")

st.header("2. Solution Prep")
c1, c2 = st.columns(2)
with c1:
    default_m = st.session_state.get('saved_mass', 0.0)
    solute_mm = st.number_input("Molar Mass (g/mol)", value=float(default_m), format="%.3f")
    molarity = st.number_input("Molarity (M)", value=0.5)
with c2:
    vol = st.number_input("Volume (mL)", value=500.0)

if st.button("Calculate Grams"):
    if solute_mm > 0:
        grams = molarity * (vol / 1000) * solute_mm
        st.info(f"Weigh out **{grams:.3f} g**")
    else:
        st.warning("Calculate Molar Mass first!")