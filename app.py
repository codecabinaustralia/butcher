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


# --- Core logic: yield-weighted realistic model ---
def wholesale_to_retail_custom_markups(wholesale_per_kg: float, markups: dict, bird_weight_kg: float):
    cuts = get_chicken_cuts()
    total_yield = sum(c["percent"] for c in cuts)
    avg_yield = total_yield / len(cuts)
    retail_data = []
    total_value = 0

    for c in cuts:
        cut_name = c["cut"]
        yield_pct = c["percent"]
        markup = markups.get(cut_name, 0)

        # Smooth yield adjustment (small cuts get modest bump, capped at 3×)
        yield_adjustment = min((avg_yield / yield_pct) ** 0.5, 3)

        # Retail price per kg for this cut
        retail_price = wholesale_per_kg * (1 + markup / 100) * yield_adjustment

        # Cut weight (based on bird weight)
        cut_weight = bird_weight_kg * (yield_pct / 100)

        # Total retail value for this cut
        cut_value = cut_weight * retail_price
        total_value += cut_value

        retail_data.append({
            "cut": cut_name,
            "yield_%": yield_pct,
            "markup_%": markup,
            "cut_weight_kg": round(cut_weight, 3),
            "retail_price_per_kg": round(retail_price, 2),
            "cut_value_AUD": round(cut_value, 2)
        })

    avg_markup = sum(markups.values()) / len(markups) if markups else 0
    whole_retail_per_kg = round(wholesale_per_kg * (1 + avg_markup / 100), 2)
    total_retail_value = round(total_value, 2)

    return retail_data, whole_retail_per_kg, total_retail_value


# --- Streamlit UI ---
st.set_page_config(page_title="Chicken Retail Calculator", page_icon="🐔", layout="centered")
st.title("🐔 Chicken Wholesale → Retail Calculator")

st.write("""
Estimate **realistic retail pricing and yield by cut** based on your wholesale chicken cost.  
Enter your bird weight and markups to see per-cut weights, retail prices, and total values.
""")

# Inputs
wholesale_price = st.number_input(
    "Wholesale price per kg of whole chicken ($)",
    min_value=1.0, max_value=20.0, value=9.85, step=0.05,
)

bird_weight = st.number_input(
    "Bird dressed weight (kg)",
    min_value=0.5, max_value=5.0, value=2.0, step=0.1,
    help="The total processed chicken weight you are breaking down."
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
        )

if st.button("📈 Calculate Retail Prices"):
    retail_data, whole_price, total_value = wholesale_to_retail_custom_markups(
        wholesale_price, markups, bird_weight
    )

    st.write(f"### Whole Chicken Retail Price (avg markup): ${whole_price:.2f}/kg")
    st.write(f"### Total Retail Value for {bird_weight:.2f} kg Bird: ${total_value:.2f}")

    st.caption("""
    **Column guide:**
    - *Cut*: Chicken part  
    - *Yield %*: Portion of total bird weight  
    - *Markup %*: Desired profit margin for that cut  
    - *Cut Weight (kg)*: Estimated cut weight based on total bird weight  
    - *Retail Price ($/kg)*: Suggested retail selling price per kg  
    - *Cut Value ($)*: Total retail value of that cut  
    """)

    st.table(retail_data)
