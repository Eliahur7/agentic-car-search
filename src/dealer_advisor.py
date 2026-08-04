def generate_dealer_questions(car):
    """
    Generates tailored, high-leverage questions to ask the dealer.
    """
    questions = []
    
    # General questions
    questions.append("Are there any dealer add-ons or mandatory accessories not reflected in the online price?")
    questions.append("Can you provide the most recent multi-point inspection report?")
    
    # Mileage / Age specific
    if car["mileage"] > 40000:
        questions.append("Has the transmission fluid or differential fluid been serviced yet?")
        
    if 2024 - car["year"] > 3:
        questions.append("How old are the current tires and brake pads?")
        
    # Accident specific
    if car["accident_history"] != "Clean":
        questions.append(f"I see the vehicle has a {car['accident_history']} history. Do you have documentation on the repairs?")
        
    # Source specific
    if car["source"] == "Manufacturer CPO":
        questions.append("What exactly is covered under the remaining CPO warranty, and is there a deductible?")
    elif car["source"] in ["CarGurus", "Autotrader", "Cars.com"]:
        questions.append("Is there any remaining factory warranty, or would it be sold strictly as-is?")
        
    return questions


def summarize_history(car):
    """
    Provides a quick summarization of the vehicle history.
    """
    # Simulated history summary based on the accident_history field
    if car["accident_history"] == "Clean":
        return {
            "status": "Positive",
            "summary": "Clean title, 0 accidents reported. Regular maintenance records indicated."
        }
    elif "Minor" in car["accident_history"]:
        return {
            "status": "Warning",
            "summary": f"{car['accident_history']} reported. Likely cosmetic damage (e.g., bumper scrape). Ensure repairs were done by a certified shop."
        }
    else:
        return {
            "status": "Danger",
            "summary": f"{car['accident_history']} reported. Request structural/frame inspection before purchase."
        }
