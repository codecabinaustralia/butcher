import streamlit as st

# --- Chicken data ---
def get_chicken_cuts():
    return [
        {"cut": "breast (both, bone-in)", "percent": 28, "price_per_kg": 13.00},
        {"cut": "thigh (bone-in)", "percent": 18, "price_per_kg": 13.00},
        {"cut": "drumstick", "percent": 12, "price_per_kg": 6.00},
        {"cut": "wings (both)", "percent": 9, "price_per_kg": 6.00},
        {"cut": "tenders", "percent": 2.5, "price_per_kg": 13.00},
        {"cut": "back/frames/neck", "percent": 14, "price_per_kg": 1.00},
        {"cut": "giblets", "percent": 1.5, "price_per_kg": 2.00},
    ]


# --- Core logic: pricing by weight ---
def price_chicken(weight_kg: float, custom_prices: dict = None):
    cuts = get_chicken_cuts()
    results = []
    total_price = 0
    for c in cuts:
        price_per_kg = custom_prices.get(c["cut"], c["price_per_kg"]) if custom_prices else c["price_per_kg"]
        cut_weight = weight_kg * (c["percent"] / 100)
        cut_price = cut_weight * price_per_kg
        total_price += cut_price
        results.append({
            "cut": c["cut"],
            "percent": c["percent"],
            "weight_kg": round(cut_weight, 3),
            "price_per_kg": round(price_per_kg, 2),
            "price_AUD": round(cut_price, 2)
        })
    return results, round(total_price, 2)


# --- Core logic: wholesale → retail calculator ---
def wholesale_to_retail(wholesale_per_kg: float, markup_percent: float):
    cuts = get_chicken_cuts()
    retail_results = []
    total_percent = sum([c["percent"] for c in cuts])
    cost_per_cut = {}

    # Determine relative yield fraction for each cut
    for c in cuts:
        fraction = c["percent"] / total_percent
        cut_cost = wholesale_per_kg / fraction  # effective per kg cost per cut (before markup)
        retail_price = cut_cost * (1 + markup_percent / 100)
        retail_results.append({
            "cut": c["cut"],
            "yield_%": c["percent"],
            "retail_price_per_kg": round(retail_price, 2),
            "wholesale_equiv_cost": round(cut_cost, 2),
        })

    whole_chicken_retail = round(wholesale_per_kg * (1 + markup_percent / 100), 2)
    return retail_results, whole_chicken_retail


# --- Streamlit UI ---
st.set_page_config(page_title="Chicken Cut Calculator", page_icon="🐔", layout="centered")

st.title("🐔 Chicken Cut Calculator")

tab1, tab2 = st.tabs(["Cut Weight & Value", "Wholesale → Retail Calculator"])

# ---------------------------------------------------------------------
# TAB 1: Weight-based calculator
# ---------------------------------------------------------------------
with tab1:
    st.subheader("Cut Weight & Retail Value Calculator")

    weight = st.number_input("Enter dressed chicken weight (kg)", min_value=0.5, max_value=5.0, value=2.0, step=0.1)

    st.subheader("Custom price overrides (optional)")
    custom_prices = {}
    for c in get_chicken_cuts():
        new_price = st.number_input(f"{c['cut']} ($/kg)", value=float(c["price_per_kg"]), step=0.5)
        custom_prices[c["cut"]] = new_price

    if st.button("💰 Calculate Retail Value", key="calc_values"):
        data, total = price_chicken(weight, custom_prices)
        st.subheader(f"Results for {weight:.2f} kg Chicken")
        st.table(data)
        st.metric("Total Estimated Value (AUD)", f"${total:.2f}")


# ---------------------------------------------------------------------
# TAB 2: Wholesale to Retail Calculator
# ---------------------------------------------------------------------
with tab2:
    st.subheader("Wholesale to Retail Price Calculator")

    wholesale_price = st.number_input("Wholesale price per kg of whole chicken ($)", min_value=1.0, max_value=20.0, value=9.85, step=0.05)
    markup = st.number_input("Desired markup percentage (%)", min_value=0.0, max_value=200.0, value=50.0, step=5.0)

    if st.button("📈 Calculate Retail Pricing", key="calc_retail"):
        retail_data, whole_price = wholesale_to_retail(wholesale_price, markup)
        st.write(f"### Whole Chicken Retail Price: ${whole_price:.2f}/kg")
        st.table(retail_data)
        st.caption("Retail price per kg is calculated based on yield distribution and desired markup.")
