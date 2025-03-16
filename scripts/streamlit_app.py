import streamlit as st
import matplotlib.pyplot as plt
from pulp import LpProblem, LpVariable, LpMinimize, LpStatus, value

def create_optimization_model(fuel_cost, max_fuel, max_tractors, coverage_per_tractor, fuel_per_tractor):
    model = LpProblem("Farm_Optimization", LpMinimize)
    
    # Decision Variables
    fuel_usage = LpVariable("Fuel_Usage", lowBound=0)
    hectares_covered = LpVariable("Hectares_Covered", lowBound=0)
    tractors_used = LpVariable("Tractors_Used", lowBound=0, cat='Integer')
    
    # Objective function: minimize cost per hectare
    model += (fuel_cost * fuel_usage) / (hectares_covered + 1), "Minimize_Cost_Per_Hectare"
    
    # Constraints
    model += hectares_covered == tractors_used * coverage_per_tractor, "Coverage_Constraint"
    model += fuel_usage == tractors_used * fuel_per_tractor, "Fuel_Usage_Constraint"
    model += fuel_usage <= max_fuel, "Fuel_Limit"
    model += tractors_used <= max_tractors, "Tractor_Limit"
    
    return model

def solve_and_display(fuel_cost, max_fuel, max_tractors, coverage_per_tractor, fuel_per_tractor):
    model = create_optimization_model(fuel_cost, max_fuel, max_tractors, coverage_per_tractor, fuel_per_tractor)
    model.solve()
    
    # Check the status first
    print("Solver Status:", LpStatus[model.status])

    # Fetch results
    fuel_used = value(model.variablesDict()["Fuel_Usage"])
    hectares = value(model.variablesDict()["Hectares_Covered"])
    tractors = value(model.variablesDict()["Tractors_Used"])
    
    print("Fuel Used:", fuel_used)
    print("Hectares Covered:", hectares)
    print("Tractors Used:", tractors)

    return fuel_used, hectares, tractors, LpStatus[model.status]


def main():
    st.title("🚜 Farm Optimization Dashboard")
    st.sidebar.header("🔧 Adjust Parameters")
    
    # Sidebar Inputs
    fuel_cost = st.sidebar.number_input("💰 Fuel Cost per Liter (₦)", min_value=100, max_value=5000, value=1379)
    max_fuel = st.sidebar.slider("⛽ Max Fuel Available (Liters)", 100, 5000, 1000)
    max_tractors = st.sidebar.slider("🚜 Max Tractors Available", 1, 10, 5)
    coverage_per_tractor = st.sidebar.slider("🌾 Coverage per Tractor (Hectares/Day)", 1.0, 10.0, 2.5)
    fuel_per_tractor = st.sidebar.slider("⛽ Fuel per Tractor (Liters/Day)", 5, 100, 25)
    
    if st.button("Run Optimization"):  
        fuel_used, hectares, tractors, status = solve_and_display(fuel_cost, max_fuel, max_tractors, coverage_per_tractor, fuel_per_tractor)
        
        st.subheader("📊 Optimization Results")
        if status == "Optimal":
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Fuel Used", f"{fuel_used:.2f} Liters")
            col2.metric("Total Hectares Covered", f"{hectares:.2f} Hectares")
            col3.metric("Tractors Used", f"{tractors:.0f}")
            
            # Bar Chart Visualization
            fig, ax = plt.subplots()
            labels = ["Fuel Used (L)", "Hectares Covered", "Tractors Used"]
            values = [fuel_used, hectares, tractors]
            ax.bar(labels, values, color=['red', 'green', 'blue'])
            ax.set_ylabel("Quantity")
            ax.set_title("Optimization Metrics")
            st.pyplot(fig)
        else:
            st.error("🚨 No optimal solution found. Adjust the parameters and try again!")
    
if __name__ == "__main__":
    main()
