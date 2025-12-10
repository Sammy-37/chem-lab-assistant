import streamlit as st
import pubchempy as pcp

# 1. PAGE SETUP
st.set_page_config(page_title="ChemCalc Pro", page_icon="🧪")

st.title("🧪 ChemCalc: ")
st.markdown("---")


# 2. LOGIC: FETCH FROM PUBCHEM
def get_compound_details(query):
    try:
        # Search PubChem for the compound
        compounds = pcp.get_compounds(query, 'name')

        if not compounds:
            # If name search fails, try formula search
            compounds = pcp.get_compounds(query, 'formula')

        if compounds:
            c = compounds[0]

            # Get Synonyms (Alternative Names) - Top 5
            synonyms = c.synonyms[:5] if c.synonyms else ["No common synonyms found"]

            return {
                "name": c.iupac_name if c.iupac_name else "Unknown Name",
                "formula": c.molecular_formula,
                "weight": float(c.molecular_weight),
                "cid": c.cid,
                "synonyms": ", ".join(synonyms),
                "image": f"https://pubchem.ncbi.nlm.nih.gov/image/imagefly.cgi?cid={c.cid}&width=400&height=400"
            }
        else:
            return None
    except Exception as e:
        return None


# 3. UI: SECTION 1 - COMPOUND VALIDATOR
st.header("1. Compound Validator & Properties")
user_input = st.text_input("Enter Name or Formula (e.g., Aspirin, H2SO4):", "Aspirin")

if st.button("Search & Validate"):
    with st.spinner(f"Searching PubChem for '{user_input}'..."):
        data = get_compound_details(user_input)

    if data:
        st.success(f"✅ Found: {data['name']}")

        col1, col2 = st.columns([1, 2])

        with col1:
            st.image(data['image'], caption=f"PubChem CID: {data['cid']}")

        with col2:
            st.metric("Molecular Formula", data['formula'])
            st.metric("Molar Mass", f"{data['weight']} g/mol")

            st.markdown("### Alternative Names")
            st.info(data['synonyms'])

        # Save mass and name for the next calculator (Section 2)
        st.session_state['saved_mass'] = data['weight']
        st.session_state['saved_name'] = data['name']

    else:
        st.error(f"❌ Compound '{user_input}' not found in PubChem database.")
        st.warning("Note: This validates that the chemical *exists* in nature.")

st.markdown("---")

# 4. UI: SECTION 2 - SOLUTION PREPARATION
st.header("2. Solution Preparation")

# Check if we have a saved compound from Section 1
current_name = st.session_state.get('saved_name', "Custom Compound")

if current_name != "Custom Compound":
    st.success(f"🧪 Preparing solution for: **{current_name}**")
else:
    st.info("Enter Molar Mass manually or validate a compound above.")

# Create columns for inputs
c1, c2 = st.columns(2)

with c1:
    # Auto-fill Molar Mass if available
    default_m = st.session_state.get('saved_mass', 0.0)
    solute_mm = st.number_input("Molar Mass (g/mol)", value=default_m, format="%.3f")

    # Input for Molarity
    molarity = st.number_input("Desired Molarity (M)", value=0.5)

with c2:
    # Input for Volume
    vol = st.number_input("Volume (mL)", value=500.0)

# Calculate Button
if st.button("Calculate Grams Needed"):
    if solute_mm > 0:
        # Stoichiometry Formula: Mass = Molarity * Volume(L) * Molar Mass
        grams = molarity * (vol / 1000) * solute_mm

        st.markdown(f"""
        <div style="background-color: #d1fae5; padding: 20px; border-radius: 10px; border: 1px solid #10b981;">
            <h3 style="color: #065f46; margin:0;">⚖️ Result: Weigh out {grams:.3f} grams</h3>
            <p style="color: #047857;">Dissolve this amount in {vol} mL of solvent to get a {molarity} M solution.</p>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.warning("⚠️ Please enter a valid Molar Mass first.")
