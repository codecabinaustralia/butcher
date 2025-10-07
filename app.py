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

# --- Calculation logic ---
def wholesale_to_retail_custom_markups(wholesale_per_kg: float, markups: dict):
    """
    Calculate per-cut retail price based on wholesale rate and individual markups.
    """
    cuts = get_chicken_cuts()
    total_percent = sum(c["percent"] for c in cuts)
    retail_data = []

    for c in cuts:
        cut_name = c["cut"]
        yield_fraction = c["percent"] / total_percent

        # Approx cost distribution: each cut takes proportional share of bird
        # (This can be refined later if you want cut-specific yield multipliers)
        wholesale_equiv_cost = wholesale_per_kg / yield_fraction

        # Apply markup for this cut
        markup = markups.get(cut_name, 0)
        retail_price = wholesale_equiv_cost * (1 + markup / 100)

        retail_data.append({
            "cut": cut_name,
            "yield_%": c["percent"],
            "markup_%": markup,
            "wholesale_equiv_cost_per_kg": round(wholesale_equiv_cost, 2),
            "retail_price_per_kg": round(retail_price, 2),
        })

    # Whole chicken retail price (simple markup average)
    avg_markup = sum(markups.values()) / len(markups) if markups else 0
    whole_retail = round(wholesale_per_kg * (1 + avg_markup / 100), 2)

    return retail_data, whole_retail


# --- Streamlit UI ---
st.set_page_config(page_title="Chicken Cut Retail Calculator", page_icon="🐔", layout="centered")

st.title("🐔 Chicken Wholesale → Retail Calculator")

st.write("""
Use this calculator to estimate **retail pricing per cut** based on your wholesale chicken cost.  
You can set **custom markup percentages** for each cut and compare against the whole bird’s retail price.
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
    - *Wholesale Equivalent Cost ($/kg)*: Effective cost per kg for that cut, based on the whole bird price  
    - *Retail Price ($/kg)*: Suggested retail selling price for that cut
    """)

    st.table(retail_data)
