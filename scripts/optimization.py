import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Operation-specific fuel consumption data (L/ha at reference speed)
OPERATION_FUEL_DATA = {
    "Ploughing (Moldboard/Disc)": {
        "base": 35, 
        "range": "25-45", 
        "reference_speed": 5,
        "speed_range": "4-6",
        "remarks": "Deep tillage; slower speeds reduce slippage and wear."
    },
    "Harrowing (Disc/Tine)": {
        "base": 15, 
        "range": "10-20", 
        "reference_speed": 7,
        "speed_range": "6-8",
        "remarks": "Second pass after ploughing; moderate depth."
    },
    "Rotavating/Rotary Tillage": {
        "base": 27.5, 
        "range": "20-35", 
        "reference_speed": 4,
        "speed_range": "3-5",
        "remarks": "High PTO load; speed kept low for effective soil pulverization."
    },
    "Ridging/Bed Formation": {
        "base": 15, 
        "range": "10-20", 
        "reference_speed": 6,
        "speed_range": "5-7",
        "remarks": "Depends on ridge height and implement width."
    },
    "Planting/Seeding": {
        "base": 5.5, 
        "range": "3-8", 
        "reference_speed": 5,
        "speed_range": "4-6",
        "remarks": "Controlled, uniform seed placement."
    },
    "Spraying": {
        "base": 2, 
        "range": "1-3", 
        "reference_speed": 8,
        "speed_range": "6-10",
        "remarks": "High speed possible; low drawbar load."
    },
    "Fertilizer Spreading": {
        "base": 2, 
        "range": "1-3", 
        "reference_speed": 10,
        "speed_range": "8-12",
        "remarks": "Uniform distribution; wide swath width increases efficiency."
    },
    "Harvesting (Combine)": {
        "base": 22.5, 
        "range": "15-30", 
        "reference_speed": 4.5,
        "speed_range": "3-6",
        "remarks": "Slower speeds maintain threshing efficiency and reduce grain loss."
    },
    "Transport (Field to Yard)": {
        "base": 12.5, 
        "range": "5-20", 
        "reference_speed": 15,
        "speed_range": "10-20",
        "remarks": "Depends on load, terrain, and road condition."
    },
}

def calculate_fuel_consumption(operation_type, operating_speed):
    """
    Calculate fuel consumption per hectare based on operation type and speed.
    
    Args:
        operation_type: Type of field operation
        operating_speed: Speed in km/hr
    
    Returns:
        Fuel consumption in liters per hectare
    """
    operation_data = OPERATION_FUEL_DATA[operation_type]
    base_consumption = operation_data["base"]
    reference_speed = operation_data["reference_speed"]
    
    # Speed factor: fuel increases with speed (1.5 exponent for resistance)
    speed_factor = (operating_speed / reference_speed) ** 1.5
    fuel_per_hectare = base_consumption * speed_factor
    
    return fuel_per_hectare

def calculate_farm_metrics(tractor_count, operating_speed, working_hours, 
                          implement_width, field_efficiency, fuel_cost_per_liter,
                          operation_type):
    """
    Calculate farm operation metrics based on input parameters.
    
    Returns:
        Dictionary with calculated metrics for FULL DAY operation
    """
    # Capacity calculations
    hourly_capacity_per_tractor = (operating_speed * implement_width * field_efficiency) / 10
    daily_capacity_per_tractor = hourly_capacity_per_tractor * working_hours
    total_daily_capacity = daily_capacity_per_tractor * tractor_count
    
    # Fuel calculations based on operation type
    fuel_consumption_per_hectare = calculate_fuel_consumption(operation_type, operating_speed)
    
    # Total fuel if all tractors work the full day
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
                      fuel_cost_per_liter, operation_type, speed_increment=0.1):
    """
    Find the optimal speed to complete target_hectares at minimum cost.
    All tractors work together to cover the target area.
    """
    speeds = np.arange(min_speed, max_speed + speed_increment, speed_increment)
    all_results = []
    
    for speed in speeds:
        # Calculate capacity metrics
        hourly_capacity_per_tractor = (speed * implement_width * field_efficiency) / 10
        total_hourly_capacity = hourly_capacity_per_tractor * tractor_count
        total_daily_capacity = total_hourly_capacity * working_hours
        
        # Fuel consumption rate at this speed for this operation
        fuel_per_hectare = calculate_fuel_consumption(operation_type, speed)
        
        # Can we complete the target area?
        can_complete = total_daily_capacity >= target_hectares
        
        if can_complete:
            # Calculate actual time and fuel needed for target area
            time_required = target_hectares / total_hourly_capacity
            
            # Fuel for covering target_hectares
            fuel_required = fuel_per_hectare * target_hectares
            total_cost = fuel_required * fuel_cost_per_liter
            cost_per_hectare = total_cost / target_hectares
            
            results = {
                "speed": speed,
                "can_complete": True,
                "time_required_hours": time_required,
                "fuel_required": fuel_required,
                "total_cost": total_cost,
                "cost_per_hectare": cost_per_hectare,
                "total_hourly_capacity": total_hourly_capacity,
                "total_daily_capacity": total_daily_capacity,
                "fuel_per_hectare": fuel_per_hectare
            }
        else:
            # Can't complete target - show what's achievable in a full day
            time_required = working_hours
            fuel_required = fuel_per_hectare * total_daily_capacity
            total_cost = fuel_required * fuel_cost_per_liter
            cost_per_hectare = total_cost / total_daily_capacity if total_daily_capacity > 0 else 0
            
            results = {
                "speed": speed,
                "can_complete": False,
                "time_required_hours": time_required,
                "fuel_required": fuel_required,
                "total_cost": total_cost,
                "cost_per_hectare": cost_per_hectare,
                "total_hourly_capacity": total_hourly_capacity,
                "total_daily_capacity": total_daily_capacity,
                "fuel_per_hectare": fuel_per_hectare,
                "area_achievable": total_daily_capacity
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
                                implement_width, field_efficiency, fuel_cost_per_liter,
                                operation_type):
    """
    Calculate the minimum number of tractors needed to cover target area at a given speed.
    """
    hourly_capacity_per_tractor = (desired_speed * implement_width * field_efficiency) / 10
    daily_capacity_per_tractor = hourly_capacity_per_tractor * working_hours
    
    # Minimum tractors needed
    tractors_needed = np.ceil(target_hectares / daily_capacity_per_tractor) if daily_capacity_per_tractor > 0 else 0
    
    # Actual time required with this many tractors
    total_hourly_capacity = hourly_capacity_per_tractor * tractors_needed
    time_required = target_hectares / total_hourly_capacity if total_hourly_capacity > 0 else 0
    
    # Fuel calculation based on operation type
    fuel_per_hectare = calculate_fuel_consumption(operation_type, desired_speed)
    fuel_required = fuel_per_hectare * target_hectares
    total_fuel_cost = fuel_required * fuel_cost_per_liter
    
    return {
        "tractors_needed": int(tractors_needed),
        "fuel_required": fuel_required,
        "time_required": time_required,
        "total_fuel_cost": total_fuel_cost,
        "fuel_per_hectare": fuel_per_hectare,
        "hourly_capacity_per_tractor": hourly_capacity_per_tractor,
        "total_hourly_capacity": total_hourly_capacity
    }

# Streamlit UI
def main():
    st.title("Duns Field Optimizer ⛽🚜🌾")
    st.caption("Realistic fuel consumption model based on field operation types")
    
    st.sidebar.header("Farm Parameters")
    
    # Operation Type Selection
    operation_type = st.sidebar.selectbox(
        "Select Operation Type",
        list(OPERATION_FUEL_DATA.keys()),
        index=0
    )
    
    # Show fuel consumption range for selected operation
    op_data = OPERATION_FUEL_DATA[operation_type]
    st.sidebar.info(f"📊 **Fuel range:** {op_data['range']} L/ha\n\n"
                   f"⚙️ **Reference speed:** {op_data['reference_speed']} km/hr\n\n"
                   f"🎯 **Recommended speed:** {op_data['speed_range']} km/hr\n\n"
                   f"💡 *{op_data['remarks']}*")
    
    tractor_count = st.sidebar.number_input("Number of tractors", min_value=1, max_value=10, value=5)
    target_hectares = st.sidebar.number_input("Target area to cover (hectares)", min_value=1.0, max_value=100.0, value=15.0)
    working_hours = st.sidebar.number_input("Working hours per day", min_value=1.0, max_value=24.0, value=8.0)
    implement_width = st.sidebar.number_input("Implement width (meters)", min_value=0.5, max_value=10.0, value=1.8)
    field_efficiency = st.sidebar.slider("Field efficiency", min_value=0.5, max_value=0.95, value=0.75)
    fuel_cost = st.sidebar.number_input("Fuel cost (Naira/liter)", min_value=100.0, max_value=2000.0, value=1379.0)
    
    st.subheader("Speed Range for Optimization")
    col1, col2 = st.columns(2)
    with col1:
        min_speed = st.number_input("Minimum speed (km/hr)", min_value=1.0, max_value=10.0, value=3.0)
    with col2:
        max_speed = st.number_input("Maximum speed (km/hr)", min_value=1.0, max_value=15.0, value=10.0)
    
    # Run optimization
    result = find_optimal_speed(
        target_hectares, tractor_count, min_speed, max_speed,
        working_hours, implement_width, field_efficiency, fuel_cost, operation_type
    )
    
    st.header("Optimization Results")
    if result["status"] == "optimal":
        optimal = result["optimal_metrics"]
        st.success(f"✅ Optimal solution found for {operation_type}!")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Optimal Speed", f"{optimal['speed']:.1f} km/hr")
            st.metric("Time Required", f"{optimal['time_required_hours']:.2f} hrs")
        with col2:
            st.metric("Total Fuel", f"{optimal['fuel_required']:.2f} L")
            st.metric("Fuel Rate", f"{optimal['fuel_per_hectare']:.2f} L/ha")
        with col3:
            st.metric("Total Cost", f"₦{optimal['total_cost']:,.2f}")
            st.metric("Cost per Hectare", f"₦{optimal['cost_per_hectare']:,.2f}")
        
        st.info(f"📊 **Capacity:** {optimal['total_hourly_capacity']:.2f} ha/hr with {tractor_count} tractors")
        
        # Show comparison with typical range
        expected_range = op_data['range']
        actual_fuel = optimal['fuel_per_hectare']
        st.caption(f"💡 Your fuel rate ({actual_fuel:.1f} L/ha) vs typical range ({expected_range} L/ha)")
        
    else:
        st.error("❌ Cannot meet the target area with the given parameters.")
        st.warning("Try: Increasing tractors, working hours, or maximum speed.")
    
    # Optional: Manually Input Desired Speed
    st.divider()
    st.subheader("Custom Speed Analysis")
    st.write("Calculate the minimum tractors needed for a specific speed.")
    
    use_manual_speed = st.checkbox("Use Custom Speed")
    if use_manual_speed:
        desired_speed = st.number_input("Enter your desired speed (km/hr):", min_value=1.0, max_value=15.0, value=5.0)
        custom_results = calculate_tractors_for_speed(
            target_hectares, desired_speed, working_hours, 
            implement_width, field_efficiency, fuel_cost, operation_type
        )
        
        st.write("### Results")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("🔢 Tractors Needed", f"{custom_results['tractors_needed']}")
            st.metric("⏳ Time Required", f"{custom_results['time_required']:.2f} hrs")
            st.metric("🚜 Capacity per Tractor", f"{custom_results['hourly_capacity_per_tractor']:.2f} ha/hr")
        with col2:
            st.metric("⛽ Fuel Rate", f"{custom_results['fuel_per_hectare']:.2f} L/ha")
            st.metric("⛽ Total Fuel", f"{custom_results['fuel_required']:.2f} L")
            st.metric("💰 Total Cost", f"₦{custom_results['total_fuel_cost']:,.2f}")
        
        st.info(f"📊 **Combined Capacity:** {custom_results['total_hourly_capacity']:.2f} ha/hr with {custom_results['tractors_needed']} tractors")
        
        # Comparison with typical range
        expected_range = op_data['range']
        actual_fuel = custom_results['fuel_per_hectare']
        st.caption(f"💡 Your fuel rate ({actual_fuel:.1f} L/ha) vs typical range ({expected_range} L/ha)")
    
    # Show operation fuel data table
    with st.expander("📋 View All Operation Fuel Consumption Data"):
        fuel_df = pd.DataFrame([
            {
                "Operation": op,
                "Fuel Range (L/ha)": data["range"],
                "Base (L/ha)": data["base"],
                "Reference Speed (km/h)": data["reference_speed"],
                "Typical Speed Range (km/h)": data["speed_range"],
                "Remarks": data["remarks"]
            }
            for op, data in OPERATION_FUEL_DATA.items()
        ])
        st.dataframe(fuel_df, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
