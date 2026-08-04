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


def calculate_out_the_door(car_price: float, state_tax_rate: float = 0.05, doc_fee: float = 399.0, reg_fee: float = 225.0, trade_in_value: float = 0.0, loan_balance: float = 0.0, apr: float = 6.5, loan_months: int = 60):
    """
    Calculates exact Out-The-Door (OTD) purchase cost, taking into account
    sales tax, doc fees, title/registration, trade-in tax savings, and equity.
    """
    # 1. Taxable Amount (Trade-in reduces taxable base in most states)
    taxable_amount = max(0.0, car_price - trade_in_value)
    sales_tax = taxable_amount * state_tax_rate
    
    # 2. Total OTD before Trade Net Equity
    subtotal_with_tax_and_fees = car_price + sales_tax + doc_fee + reg_fee
    
    # 3. Net Trade-In Contribution (Trade Value minus remaining loan)
    net_trade_equity = trade_in_value - loan_balance
    
    # 4. Final Cash Needed Out-The-Door
    final_otd_price = subtotal_with_tax_and_fees - net_trade_equity
    
    # 5. Estimated Monthly Payment (Financing)
    r = (apr / 100) / 12
    n = loan_months
    amount_financed = max(0.0, final_otd_price)
    if r > 0 and n > 0 and amount_financed > 0:
        monthly_payment = amount_financed * (r * (1 + r)**n) / ((1 + r)**n - 1)
    else:
        monthly_payment = amount_financed / max(1, n)
        
    return {
        "asking_price": car_price,
        "sales_tax": round(sales_tax, 2),
        "doc_fee": doc_fee,
        "reg_fee": reg_fee,
        "tax_savings_from_trade": round(min(car_price, trade_in_value) * state_tax_rate, 2),
        "net_trade_equity": net_trade_equity,
        "final_otd_price": round(final_otd_price, 2),
        "monthly_payment": round(monthly_payment, 2),
        "loan_months": loan_months,
        "apr": apr
    }
