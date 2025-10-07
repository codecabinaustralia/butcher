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

# --- Core logic ---
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
            "price_per_kg": price_per_kg,
            "price_AUD": round(cut_price, 2)
        })
    return results, round(total_price, 2)

# --- Streamlit UI ---
st.set_page_config(page_title="Chicken Cut Calculator", page_icon="🐔", layout="centered")

st.title("🐔 Chicken Cut Auto-Pricer")

weight = st.number_input("Enter dressed chicken weight (kg)", min_value=0.5, max_value=5.0, value=2.0, step=0.1)

st.subheader("Custom price overrides (optional)")
custom_prices = {}
for c in get_chicken_cuts():
    new_price = st.number_input(f"{c['cut']} ($/kg)", value=float(c["price_per_kg"]), step=0.5)
    custom_prices[c["cut"]] = new_price

if st.button("Calculate Cuts"):
    data, total = price_chicken(weight, custom_prices)
    st.subheader(f"Results for {weight:.2f} kg Chicken")
    st.table(data)
    st.metric("Total Estimated Value (AUD)", f"${total:.2f}")
