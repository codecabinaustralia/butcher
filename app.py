import streamlit as st

# --- Chicken cuts data ---
def get_chicken_cuts():
    return [
        {"cut": "breast (both, bone-in)", "percent": 28},
        {"cut": "thigh (bone-in)", "percent": 18},
        {"cut": "drumstick", "percent": 12},
        {"cut": "wings (both)", "percent": 9},
        {"cut": "tenders", "percent": 2.5},
        {"cut": "back/frames/neck", "percent": 14},
        {"cut": "giblets", "percent": 1.5},
    ]

# --- New calculation logic (normalized yield model) ---
def wholesale_to_retail_custom_markups(wholesale_per_kg: float, markups: dict):
    cuts = get_chicken_cuts()
    # convert markups % -> multiplier (1.5 for 50%)
    for c in cuts:
        c["markup_factor"] = 1 + (markups.get(c["cut"], 0) / 100)

    # compute weighted average factor so we can normalize around the whole bird
    total_weight = sum(c["percent"] for c in cuts)
    weighted_avg_factor = sum((c["percent"] / total_weight) * c["markup_factor"] for c in cuts)

    retail_data = []
    for c in cuts:
        yield_pct = c["percent"]
        markup_factor = c["markup_factor"]
        # normalize so overall average = 1× wholesale
        normalized_factor = markup_factor / weighted_avg_factor
        retail_price = wholesale_per_kg * normalized_factor
        retail_data.append({
            "cut": c["cut"],
            "yield_%": yield_pct,
            "markup_%": markups.get(c["cut"], 0),
            "retail_price_per_kg": round(retail_price, 2)
        })

    # whole chicken retail (weighted avg markup)
    avg_markup = sum(markups.values()) / len(markups) if markups else 0
    whole_retail = round(wholesale_per_kg * (1 + avg_markup / 100), 2)

    return retail_data, whole_retail


# --- Streamlit UI ---
st.set_page_config(page_title="Chicken Retail Calculator", page_icon="🐔", layout="centered")

st.title("🐔 Chicken Wholesale → Retail Calculator")

st.write("""
Use this calculator to estimate **realistic retail pricing per cut** based on your wholesale chicken cost.  
Each cut can have its own **markup percentage**, and prices are normalized by yield so they stay proportional and realistic.
""")

# Inputs
wholesale_price = st.number_input(
    "Wholesale price per kg of whole chicken ($)",
    min_value=1.0, max_value=20.0, value=9.85, step=0.05,
    help="Your supplier cost per kilogram of whole chicken."
)

st.subheader("Set desired markup percentage for each cut")

markups = {}
cols = st.columns(2)
cuts = get_chicken_cuts()

for i, c in enumerate(cuts):
    col = cols[i % 2]
    with col:
        markups[c["cut"]] = col.number_input(
            f"{c['cut']} markup (%)",
            min_value=0.0, max_value=200.0, value=50.0, step=5.0,
            help=f"Markup percentage for {c['cut']}."
        )

# Calculate button
if st.button("📈 Calculate Retail Prices"):
    retail_data, whole_price = wholesale_to_retail_custom_markups(wholesale_price, markups)

    st.write(f"### Whole Chicken Retail Price (average markup): ${whole_price:.2f}/kg")

    st.caption("""
    **Column guide:**
    - *Cut*: Chicken part  
    - *Yield %*: Portion of total bird weight  
    - *Markup %*: Desired profit margin for that cut  
    - *Retail Price ($/kg)*: Suggested retail selling price per kg, normalized by yield
    """)

    st.table(retail_data)
