def evaluate_deal(car):
    """
    Evaluates the deal value of a vehicle based on year, mileage, and make.
    Returns a dictionary with rating, estimated_market_value, and explanation.
    """
    # Simple heuristic market value estimator
    base_values = {
        "Highlander": 35000,
        "CR-V": 30000,
        "F-150": 45000,
        "RAV4": 32000,
        "Model 3": 40000,
        "Palisade": 42000,
        "Telluride": 40000,
        "Tahoe": 55000,
        "Outback": 31000,
        "X5": 60000
    }
    
    model = car["model"]
    base_value = base_values.get(model, 35000)
    
    # Age depreciation: roughly 8% per year from 2024
    age = max(0, 2024 - car["year"])
    depreciation_factor = (0.92 ** age)
    
    # Mileage depreciation: roughly $0.10 per mile over 12k/year
    expected_miles = age * 12000
    mileage_diff = car["mileage"] - expected_miles
    mileage_penalty = mileage_diff * 0.10
    
    estimated_market_value = (base_value * depreciation_factor) - mileage_penalty
    
    # Compare with asking price
    asking_price = car["price"]
    price_diff = estimated_market_value - asking_price
    
    # Rating logic
    if price_diff > 2000:
        rating = "🔥 Great Deal"
        color = "green"
        explanation = f"Priced ${price_diff:,.0f} below market value."
    elif price_diff >= -1500:
        rating = "🟢 Fair Price"
        color = "blue"
        explanation = f"Priced around market value."
    else:
        rating = "⚠️ Overpriced"
        color = "red"
        explanation = f"Priced ${abs(price_diff):,.0f} above market value."
        
    return {
        "rating": rating,
        "color": color,
        "estimated_market_value": estimated_market_value,
        "explanation": explanation,
        "price_diff": price_diff
    }
