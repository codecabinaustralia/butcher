import streamlit as st
import pandas as pd
import json
import io

# ==========================================================
# 🔹 Base cut data for each species
# ==========================================================
DEFAULT_CUTS = {
    "chicken": [
        {"cut": "breast (both, bone-in)", "percent": 28},
        {"cut": "thigh (bone-in)", "percent": 18},
        {"cut": "drumstick", "percent": 12},
        {"cut": "wings (both)", "percent": 9},
        {"cut": "tenders", "percent": 2.5},
        {"cut": "back/frames/neck", "percent": 14},
        {"cut": "giblets", "percent": 1.5},
    ],
    "cow": [
        {"cut": "ribeye", "percent": 8},
        {"cut": "sirloin", "percent": 10},
        {"cut": "rump", "percent": 7},
        {"cut": "brisket", "percent": 6},
        {"cut": "chuck", "percent": 14},
        {"cut": "round", "percent": 15},
        {"cut": "shank", "percent": 8},
        {"cut": "trim/offcuts", "percent": 32},
    ],
    "lamb": [
        {"cut": "leg", "percent": 30},
        {"cut": "shoulder", "percent": 20},
        {"cut": "loin", "percent": 15},
        {"cut": "rack", "percent": 8},
        {"cut": "shank", "percent": 5},
        {"cut": "neck", "percent": 5},
        {"cut": "trim/offcuts", "percent": 17},
    ],
    "pig": [
        {"cut": "loin", "percent": 20},
        {"cut": "belly", "percent": 16},
        {"cut": "shoulder (butt)", "percent": 18},
        {"cut": "ham", "percent": 22},
        {"cut": "spare ribs", "percent": 8},
        {"cut": "hock", "percent": 6},
        {"cut": "trim/offcuts", "percent": 10},
    ],
}

# ==========================================================
# 🔹 Calculation Logic
# ==========================================================
def calculate_cut_prices(wholesale_per_kg, markups, weight_kg, cuts):
    total_yield = sum(c["percent"] for c in cuts)
    avg_yield = total_yield / len(cuts)
    results = []
    total_value = 0

    for c in cuts:
        cut_name = c["cut"]
        yield_pct = c["percent"]
        markup = markups.get(cut_name, 0)

        # Smooth adjustment: small cuts slightly higher, capped at 3x
        yield_adjustment = min((avg_yield / yield_pct) ** 0.5, 3)

        retail_price = wholesale_per_kg * (1 + markup / 100) * yield_adjustment
        cut_weight = weight_kg * (yield_pct / 100)
        cut_value = cut_weight * retail_price
        total_value += cut_value

        results.append({
            "cut": cut_name,
            "yield_%": yield_pct,
            "markup_%": markup,
            "cut_weight_kg": round(cut_weight, 3),
            "retail_price_per_kg": round(retail_price, 2),
            "cut_value_AUD": round(cut_value, 2)
        })

    avg_markup = sum(markups.values()) / len(markups) if markups else 0
    whole_retail_per_kg = round(wholesale_per_kg * (1 + avg_markup / 100), 2)
    total_value = round(total_value, 2)

    return results, whole_retail_per_kg, total_value


# ==========================================================
# 🔹 App Layout
# ==========================================================
st.set_page_config(page_title="Butcher Yield Calculator", page_icon="🥩", layout="centered")

st.title("🥩 Multi-Animal Butcher Yield & Retail Calculator (Persistent)")

st.write("""
Estimate retail prices per cut for **cow**, **chicken**, **lamb**, or **pig**,  
based on wholesale cost, carcass weight, and per-cut markup.  
You can also **save and load** your settings and data as JSON files.
""")

# ==========================================================
# 🔹 Load saved data if available
# ==========================================================
uploaded_file = st.file_uploader("📤 Load saved JSON configuration", type=["json"])
loaded_data = None
if uploaded_file:
    try:
        loaded_data = json.load(uploaded_file)
        st.success(f"Loaded saved data for {loaded_data.get('species', '').capitalize()} successfully!")
    except Exception as e:
        st.error(f"Error loading file: {e}")

# ==========================================================
# 🔹 Animal selector
# ==========================================================
st.subheader("Select Animal")

species_choice = st.radio(
    "Choose animal:",
    ["🐔 Chicken", "🐄 Cow", "🐑 Lamb", "🐖 Pig"],
    horizontal=True,
    label_visibility="collapsed"
)

if "Chicken" in species_choice:
    species = "chicken"
elif "Cow" in species_choice:
    species = "cow"
elif "Lamb" in species_choice:
    species = "lamb"
elif "Pig" in species_choice:
    species = "pig"

# ==========================================================
# 🔹 Editable Cut Properties Section
# ==========================================================
st.sidebar.header(f"⚙️ {species.capitalize()} Cut Properties")

st.sidebar.write("Edit cut names and yield percentages below (total should roughly equal 100%).")

# Use loaded data if available
cuts_source = loaded_data["cuts"] if loaded_data and loaded_data.get("species") == species else DEFAULT_CUTS[species]
cuts_df = pd.DataFrame(cuts_source)

edited_cuts = st.sidebar.data_editor(
    cuts_df,
    num_rows="dynamic",
    key=f"{species}_cuts_editor",
    hide_index=True
)

cuts = edited_cuts.to_dict(orient="records")

# ==========================================================
# 🔹 Inputs for pricing
# ==========================================================
wholesale_price = st.number_input(
    "Wholesale price per kg ($)",
    min_value=1.0, max_value=50.0,
    value=loaded_data.get("wholesale_price", 9.85) if loaded_data else 9.85,
    step=0.05,
)

weight_kg = st.number_input(
    "Animal dressed weight (kg)",
    min_value=0.5, max_value=1000.0,
    value=loaded_data.get("weight_kg", 2.0) if loaded_data else 2.0,
    step=0.5,
)

st.subheader("Set markup percentage per cut")

markups = {}
cols = st.columns(2)

# use loaded markups if available
loaded_markups = loaded_data.get("markups", {}) if loaded_data else {}

for i, c in enumerate(cuts):
    col = cols[i % 2]
    with col:
        markups[c["cut"]] = col.number_input(
            f"{c['cut']} markup (%)",
            min_value=0.0, max_value=200.0,
            value=loaded_markups.get(c["cut"], 50.0),
            step=5.0,
        )

# ==========================================================
# 🔹 Run calculation
# ==========================================================
if st.button("📈 Calculate Retail Pricing"):
    retail_data, whole_price, total_value = calculate_cut_prices(
        wholesale_price, markups, weight_kg, cuts
    )

    st.write(f"### 🧾 Whole {species.capitalize()} Retail Price (avg markup): ${whole_price:.2f}/kg")
    st.write(f"### 💰 Total Retail Value for {weight_kg:.2f} kg {species.capitalize()}: ${total_value:.2f}")

    st.caption("""
    **Column guide:**
    - *Cut*: Meat section  
    - *Yield %*: Portion of total carcass weight  
    - *Markup %*: Desired profit margin  
    - *Cut Weight (kg)*: Estimated cut weight based on carcass size  
    - *Retail Price ($/kg)*: Suggested retail selling price per kilogram  
    - *Cut Value ($)*: Total retail value for that cut
    """)

    df = pd.DataFrame(retail_data)
    st.dataframe(df, use_container_width=True)

    # ==========================================================
    # 🔹 Save all data to JSON
    # ==========================================================
    st.subheader("💾 Save or Export Your Data")

    export_dict = {
        "species": species,
        "cuts": cuts,
        "markups": markups,
        "wholesale_price": wholesale_price,
        "weight_kg": weight_kg,
        "results": retail_data,
        "whole_retail_price": whole_price,
        "total_retail_value": total_value
    }

    buffer = io.BytesIO()
    buffer.write(json.dumps(export_dict, indent=2).encode("utf-8"))

    st.download_button(
        label="⬇️ Download configuration as JSON",
        data=buffer.getvalue(),
        file_name=f"{species}_butcher_data.json",
        mime="application/json",
    )

    # Optional: Export results as CSV
    csv = df.to_csv(index=False)
    st.download_button(
        "📊 Export results as CSV",
        csv,
        f"{species}_results.csv",
        "text/csv",
    )
