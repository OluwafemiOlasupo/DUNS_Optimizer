import streamlit as st
import os
import requests
from dotenv import load_dotenv

# Load environment variables securely
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

if not DEEPSEEK_API_KEY:
    st.error("❌ DeepSeek API key is missing! Please set it in the .env file.")
    st.stop()

def get_deepseek_prediction(prompt):
    """Fetches AI prediction from DeepSeek API."""
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise error for non-200 responses
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "⚠️ No response from AI.")
    except requests.exceptions.RequestException as e:
        return f"❌ API Error: {e}"

# Constants for area coverage per implement
AREA_COVERAGE_RATES = {
    "Plough": 4,         # hectares in 8 hours for 1m width disc plough
    "Harrow": 10.75,     # hectares in 8 hours for 22 disc offset harrow
    "Ridger": 6,         # hectares in 8 hours for 4 disc ridger
    "Harvester": 9.6     # hectares in 8 hours for Ruilong Plus ++ harvester
}

FUEL_PER_HECTARE = 2  # Litres of fuel required per hectare
DAYS_PER_WEEK = 6
DAYS_PER_MONTH = 25

def calculate_fuel(tractors, hectares):
    """Calculates fuel requirement based on number of tractors and hectares."""
    return tractors * hectares * FUEL_PER_HECTARE

def area_covered_per_day(implement, count):
    """Calculates total daily area coverage for a specific implement."""
    rate = AREA_COVERAGE_RATES.get(implement, 0)
    return count * rate

def main():
    st.title("🌾 DUNS Farm Tractor Optimization System 🚜")
    
    # Tractor Input
    tractors = st.number_input("Number of tractors:", min_value=1, max_value=10, value=1, step=1)
    
    # Implements Input
    ploughs = st.number_input("Number of ploughs:", min_value=0, max_value=10, value=1, step=1)
    harrows = st.number_input("Number of harrows:", min_value=0, max_value=10, value=1, step=1)
    ridgers = st.number_input("Number of ridgers:", min_value=0, max_value=10, value=1, step=1)
    harvesters = st.number_input("Number of harvesters:", min_value=0, max_value=10, value=1, step=1)
    
    # Desired Tractor Speed
    tractor_speed = st.number_input("Enter desired tractor speed (km/h):", min_value=1, max_value=50, value=5, step=1)
    
    # Total hectares input
    total_hectares = st.number_input("Total hectares to cover:", min_value=1, max_value=5000, value=100, step=1)
    
    # Calculate daily coverage for each operation
    ploughing_area = area_covered_per_day("Plough", ploughs)
    harrowing_area = area_covered_per_day("Harrow", harrows)
    ridging_area = area_covered_per_day("Ridger", ridgers)
    harvesting_area = area_covered_per_day("Harvester", harvesters)
    
    # Calculate fuel requirements
    fuel_required_daily = calculate_fuel(tractors, total_hectares)
    fuel_required_weekly = fuel_required_daily * DAYS_PER_WEEK
    fuel_required_monthly = fuel_required_daily * DAYS_PER_MONTH
    
    # Calculate estimated operational days
    total_daily_area = ploughing_area + harrowing_area + ridging_area + harvesting_area
    if total_daily_area > 0:
        estimated_days = total_hectares / total_daily_area
    else:
        estimated_days = 0
    
    # AI Optimization via DeepSeek
    if st.button("🚀 Optimize with AI"):
        prompt = f"""
        Given the following parameters:
        - Total tractors: {tractors}
        - Desired tractor speed: {tractor_speed} km/h
        - Total hectares: {total_hectares}
        - Implements: {ploughs} ploughs, {harrows} harrows, {ridgers} ridgers, {harvesters} harvesters
        - Area covered per day by plough: {ploughing_area:.2f} hectares
        - Area covered per day by harrow: {harrowing_area:.2f} hectares
        - Area covered per day by ridger: {ridging_area:.2f} hectares
        - Area covered per day by harvester: {harvesting_area:.2f} hectares
        - Total estimated operational days: {estimated_days:.2f} days
        - Fuel requirements (daily, weekly, monthly): {fuel_required_daily}L, {fuel_required_weekly}L, {fuel_required_monthly}L
        Suggest an optimized operational plan.
        """
        deepseek_response = get_deepseek_prediction(prompt)
        st.subheader("🧠 DeepSeek AI Prediction:")
        st.write(deepseek_response)
    
    # Display results
    st.subheader("📏 Estimated Work Area:")
    st.write(f"🌱 **Ploughing:** {ploughing_area:.2f} hectares per day")
    st.write(f"🌿 **Harrowing:** {harrowing_area:.2f} hectares per day")
    st.write(f"🚜 **Ridging:** {ridging_area:.2f} hectares per day")
    st.write(f"🌾 **Harvesting:** {harvesting_area:.2f} hectares per day")
    
    st.subheader("⏳ Estimated Operational Days:")
    st.write(f"🕒 **Total Estimated Days to Cover {total_hectares} Hectares:** {estimated_days:.2f} days")
    
    st.subheader("⛽ Fuel Requirements:")
    st.write(f"🔋 **Daily Fuel Needed:** {fuel_required_daily:.2f} litres")
    st.write(f"🔋 **Weekly Fuel Needed:** {fuel_required_weekly:.2f} litres")
    st.write(f"🔋 **Monthly Fuel Needed:** {fuel_required_monthly:.2f} litres")
    
    st.info("🔧 *Note: Remember to update area coverage rates for implements if needed to ensure accuracy!*")

if __name__ == "__main__":
    main()
