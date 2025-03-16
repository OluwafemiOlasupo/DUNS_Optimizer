import pandas as pd  

def load_equipment_data(filepath="data/equipment.csv"):
    """Loads equipment details."""
    return pd.read_csv(filepath)

def process_fuel_data(filepath="data/fuel_usage.csv"):
    """Processes fuel usage logs."""
    df = pd.read_csv(filepath)
    df["Date"] = pd.to_datetime(df["Date"])
    return df

if __name__ == "__main__":
    equip_data = load_equipment_data()
    print("Equipment Data:\n", equip_data.head())
