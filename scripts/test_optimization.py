from optimization import create_optimization_model

def test_optimization():
    model = create_optimization_model()
    model.solve()  # Solve the optimization problem

    # Print results
    print("\nTest Results:")
    for var in model.variables():
        print(f"{var.name}: {var.varValue}")
    print(f"Objective Value: {model.objective.value()}")

if __name__ == "__main__":
    test_optimization()
