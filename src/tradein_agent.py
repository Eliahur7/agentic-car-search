def evaluate_trade_in(year: int, make: str, model: str, trim: str, mileage: int, condition: str, loan_balance: float = 0.0, target_car_price: float = 0.0):
    """
    Specialized AI Trade-In Valuation Engine.
    Calculates estimated Dealer Trade-In value, Private Party value, Net Equity,
    Tax Savings, and high-leverage negotiation tactics.
    """
    # 1. Base Valuation Model
    current_year = 2024
    age = max(0, current_year - int(year))
    
    # Base estimated original value heuristics
    luxury_makes = ["BMW", "Porsche", "Tesla", "Mercedes-Benz", "Audi", "Lexus"]
    base_new_price = 45000 if make in luxury_makes else 30000
    
    # Depreciation curve
    depreciated_val = base_new_price * ((0.85) ** age)
    mileage_deduction = (int(mileage) / 1000) * 120
    raw_value = max(1500, depreciated_val - mileage_deduction)
    
    # Condition multipliers
    cond_lower = str(condition).lower()
    if "excellent" in cond_lower:
        cond_mult = 1.10
    elif "fair" in cond_lower:
        cond_mult = 0.85
    elif "poor" in cond_lower:
        cond_mult = 0.70
    else:  # "Good" default
        cond_mult = 1.00
        
    trade_in_value = round(raw_value * cond_mult, -2)
    trade_in_min = round(trade_in_value * 0.92, -2)
    trade_in_max = round(trade_in_value * 1.08, -2)
    
    private_party_value = round(trade_in_value * 1.18, -2)
    
    # Equity & Tax Savings
    net_equity = trade_in_value - loan_balance
    tax_rate = 0.05  # Average state sales tax
    taxable_reduction = min(trade_in_value, target_car_price) if target_car_price > 0 else trade_in_value
    tax_savings = round(taxable_reduction * tax_rate, 2)
    
    # Tailored Negotiation Advice
    tactics = [
        "💵 **Get Written Backup Offers**: Get instant cash quotes from CarMax, Carvana, or KBB Instant Cash Offer before visiting the dealer. Use them as leverage.",
        "🏷️ **Negotiate Purchase Price First**: Keep your trade-in a secret until you have agreed on the out-the-door purchase price of your new vehicle.",
        "🧾 **Claim Your Tax Credit**: Ensure the dealership deducts your trade-in value from the taxable total. In most states, this saves you ~5-8% in sales tax on the trade amount!",
        "🧼 **Detail Your Car**: A $150 detail job can boost dealer trade-in appraisal offers by $500–$1,000."
    ]
    
    return {
        "year": year,
        "make": make,
        "model": model,
        "trim": trim,
        "mileage": mileage,
        "condition": condition.title() if condition else "Good",
        "loan_balance": loan_balance,
        "trade_in_value": trade_in_value,
        "trade_in_min": trade_in_min,
        "trade_in_max": trade_in_max,
        "private_party_value": private_party_value,
        "net_equity": net_equity,
        "tax_savings": tax_savings,
        "tactics": tactics
    }
