def estimate_tco(car):
    """
    Calculates the 5-Year Total Cost of Ownership (TCO).
    Returns a dictionary breakdown and total.
    """
    asking_price = car["price"]
    
    # 1. Depreciation (Assume 35% over 5 years for used, slightly less for older)
    age = max(0, 2024 - car["year"])
    depreciation_rate = 0.35 if age < 3 else 0.25
    depreciation = asking_price * depreciation_rate
    
    # 2. Maintenance & Repairs (Rough estimate based on age & make)
    base_maint = 800 * 5
    if car["make"] in ["BMW", "Tesla"]:
        base_maint *= 1.5
    elif car["make"] in ["Toyota", "Honda"]:
        base_maint *= 0.8
        
    age_multiplier = 1 + (age * 0.1)
    maintenance = base_maint * age_multiplier
    
    # 3. Fuel Costs / Energy
    if car["make"] == "Tesla":
        fuel_cost = 500 * 5  # Electricity
    elif car["body_style"] in ["Truck", "SUV"]:
        fuel_cost = 2000 * 5
    else:
        fuel_cost = 1500 * 5
        
    # 4. Insurance
    base_insurance = 1200 * 5
    if car["make"] in ["BMW", "Tesla"]:
        base_insurance *= 1.3
        
    insurance = base_insurance
    
    total = depreciation + maintenance + fuel_cost + insurance
    
    return {
        "Total 5-Year Cost": total,
        "Depreciation": depreciation,
        "Maintenance & Repairs": maintenance,
        "Fuel/Energy": fuel_cost,
        "Insurance": insurance
    }
