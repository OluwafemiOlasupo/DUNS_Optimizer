import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def calculate_farm_metrics(tractor_count, operating_speed, working_hours, 
                          implement_width, field_efficiency, fuel_cost_per_liter):
    """
    Calculate farm operation metrics based on input parameters.
    
    Args:
        tractor_count: Number of tractors to use
        operating_speed: Speed in km/hr
        working_hours: Hours in workday
        implement_width: Width of the implement in meters
        field_efficiency: Efficiency factor (0.0 to 1.0)
        fuel_cost_per_liter: Cost of fuel in Naira per liter
    
    Returns:
        Dictionary with calculated metrics
    """
    hourly_capacity_per_tractor = (operating_speed * implement_width * field_efficiency) / 10
    daily_capacity_per_tractor = hourly_capacity_per_tractor * working_hours
    total_daily_capacity = daily_capacity_per_tractor * tractor_count
    
    base_consumption = 5  # liters per hectare at 5 km/hr
    speed_factor = (operating_speed / 5) ** 1.5
    fuel_consumption_per_hectare = base_consumption * speed_factor
    total_fuel_consumption = fuel_consumption_per_hectare * total_daily_capacity
    total_fuel_cost = total_fuel_consumption * fuel_cost_per_liter
    
    cost_per_hectare = total_fuel_cost / total_daily_capacity if total_daily_capacity > 0 else 0
    
    return {
        "hourly_capacity_per_tractor": hourly_capacity_per_tractor,
        "daily_capacity_per_tractor": daily_capacity_per_tractor,
        "total_daily_capacity": total_daily_capacity,
        "fuel_consumption_per_hectare": fuel_consumption_per_hectare,
        "total_fuel_consumption": total_fuel_consumption,
        "total_fuel_cost": total_fuel_cost,
        "cost_per_hectare": cost_per_hectare
    }

def find_optimal_speed(target_hectares, tractor_count, min_speed, max_speed, 
                      working_hours, implement_width, field_efficiency, 
                      fuel_cost_per_liter, speed_increment=0.1):
    speeds = np.arange(min_speed, max_speed + speed_increment, speed_increment)
    all_results = []
    
    for speed in speeds:
        metrics = calculate_farm_metrics(
            tractor_count, speed, working_hours, 
            implement_width, field_efficiency, fuel_cost_per_liter
        )
        
        can_complete = metrics["total_daily_capacity"] >= target_hectares
        
        if can_complete:
            adjusted_fuel = metrics["fuel_consumption_per_hectare"] * target_hectares
            adjusted_cost = adjusted_fuel * fuel_cost_per_liter
            time_required = target_hectares / metrics["total_daily_capacity"] * working_hours
            
            results = {
                "speed": speed,
                "can_complete": can_complete,
                "time_required_hours": time_required,
                "fuel_required": adjusted_fuel,
                "total_cost": adjusted_cost,
                "cost_per_hectare": adjusted_cost / target_hectares if target_hectares > 0 else 0,
                **metrics
            }
        else:
            results = {
                "speed": speed,
                "can_complete": can_complete,
                "time_required_hours": working_hours,
                "fuel_required": metrics["total_fuel_consumption"],
                "total_cost": metrics["total_fuel_cost"],
                "cost_per_hectare": metrics["cost_per_hectare"],
                **metrics
            }
            
        all_results.append(results)
    
    results_df = pd.DataFrame(all_results)
    feasible = results_df[results_df["can_complete"]]
    
    if len(feasible) > 0:
        optimal = feasible.loc[feasible["total_cost"].idxmin()]
        status = "optimal"
    else:
        optimal = results_df.iloc[-1]
        status = "infeasible"
        
    return {
        "status": status,
        "optimal_speed": optimal["speed"] if status == "optimal" else None,
        "optimal_metrics": optimal.to_dict() if status == "optimal" else None,
        "all_results": results_df
    }

def calculate_tractors_for_speed(target_hectares, desired_speed, working_hours, 
                                implement_width, field_efficiency, fuel_cost_per_liter):
    """
    Calculate the optimal number of tractors, fuel requirements, and hours for a manually input speed.
    """
    hourly_capacity = (desired_speed * implement_width * field_efficiency) / 10
    daily_capacity = hourly_capacity * working_hours
    fuel_per_hectare = 5 * (desired_speed / 5) ** 1.5
    fuel_required = fuel_per_hectare * target_hectares
    
    tractors_needed = np.ceil(target_hectares / daily_capacity) if daily_capacity > 0 else 0
    time_required = target_hectares / (tractors_needed * daily_capacity) * working_hours if tractors_needed > 0 else 0
    total_fuel_cost = fuel_required * fuel_cost_per_liter
    
    return {
        "tractors_needed": tractors_needed,
        "fuel_required": fuel_required,
        "time_required": time_required,
        "total_fuel_cost": total_fuel_cost
    }

# Streamlit UI
def main():
    st.title("Duns Field Optimizer ⛽🚜🌾")
    
    st.sidebar.header("Farm Parameters")
    tractor_count = st.sidebar.number_input("Number of tractors", min_value=1, max_value=10, value=5)
    target_hectares = st.sidebar.number_input("Target area to cover (hectares)", min_value=1.0, max_value=100.0, value=15.0)
    working_hours = st.sidebar.number_input("Working hours per day", min_value=1.0, max_value=24.0, value=8.0)
    implement_width = st.sidebar.number_input("Implement width (meters)", min_value=0.5, max_value=10.0, value=1.8)
    field_efficiency = st.sidebar.slider("Field efficiency", min_value=0.5, max_value=0.95, value=0.75)
    fuel_cost = st.sidebar.number_input("Fuel cost (Naira/liter)", min_value=100.0, max_value=2000.0, value=1379.0)
    
    st.subheader("Speed Range")
    min_speed = st.number_input("Minimum speed (km/hr)", min_value=1.0, max_value=10.0, value=3.0)
    max_speed = st.number_input("Maximum speed (km/hr)", min_value=1.0, max_value=15.0, value=10.0)
    
    # Run optimization
    result = find_optimal_speed(
        target_hectares, tractor_count, min_speed, max_speed,
        working_hours, implement_width, field_efficiency, fuel_cost
    )
    
    st.header("Optimization Results")
    if result["status"] == "optimal":
        optimal = result["optimal_metrics"]
        st.success(f"✅ Optimal solution found! Speed: {optimal['speed']:.1f} km/hr")
    else:
        st.error("❌ Cannot meet the target area with the given parameters.")
    
    # Optional: Manually Input Desired Speed
    st.subheader("Custom Speed Analysis")
    use_manual_speed = st.checkbox("Use Custom Speed")
    if use_manual_speed:
        desired_speed = st.number_input("Enter your desired speed (km/hr):", min_value=1.0, max_value=15.0, value=5.0)
        custom_results = calculate_tractors_for_speed(
            target_hectares, desired_speed, working_hours, 
            implement_width, field_efficiency, fuel_cost
        )
        st.write(f"🔢 **Tractors Needed:** {custom_results['tractors_needed']}")
        st.write(f"⛽ **Fuel Required:** {custom_results['fuel_required']:.2f} liters")
        st.write(f"⏳ **Time Required:** {custom_results['time_required']:.2f} hours")
        st.write(f"💰 **Total Fuel Cost:** {custom_results['total_fuel_cost']:.2f} Naira")

if __name__ == "__main__":
    main()
