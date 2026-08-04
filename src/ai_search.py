import re
import os
import json

def parse_search_query(query: str):
    """
    Parses a natural language query to extract search parameters.
    Attempts to use an Anthropic LLM Agent if an API key is present,
    otherwise falls back to rule-based heuristics.
    """
    query_lower = query.lower()
    
    # Defaults
    params = {
        "budget": None,
        "mileage": None,
        "features": [],
        "body_style": None,
        "accident_history": None
    }
    
    # 0. Agentic Parsing (LLM)
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            prompt = f"""
            You are a car search extraction agent. Extract the details from the query and output ONLY valid JSON.
            Query: "{query}"
            
            JSON schema:
            {{
                "budget": integer or null (e.g., if "under 30k" -> 30000),
                "mileage": integer or null (e.g., if "under 40k miles" -> 40000),
                "features": list of strings (map synonyms to: "adaptive cruise", "touchscreen", "ventilated seats", "heated seats", "towing package", "leather", "apple carplay", "third row", "sunroof", "awd"),
                "body_style": string or null (e.g. "SUV", "Sedan", "Truck", "Wagon"),
                "accident_history": string or null (e.g. "Clean")
            }}
            Output only the raw JSON.
            """
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=200,
                temperature=0,
                messages=[{"role": "user", "content": prompt}]
            )
            text = response.content[0].text
            json_str = text[text.find('{'):text.rfind('}')+1]
            llm_params = json.loads(json_str)
            # Merge with defaults to ensure schema
            for k in params.keys():
                if k in llm_params and llm_params[k] is not None:
                    params[k] = llm_params[k]
            print("🤖 Agentic Parsing Success!")
            return params
        except Exception as e:
            print(f"Agent parsing failed, falling back to regex heuristics: {e}")

    
    # 1. Budget Extraction (e.g. "under 30k", "under $30,000", "< 30000")
    budget_match = re.search(r'\$(\d{1,3}(?:,\d{3})*|\d+)(k)?', query_lower)
    if not budget_match:
        budget_match = re.search(r'(?:budget|under|<|less than)\s*(\d{1,3}(?:,\d{3})*|\d+)(k)?(?!\s*miles)', query_lower)
        
    if budget_match:
        val = budget_match.group(1).replace(',', '')
        if budget_match.group(2) == 'k':
            params["budget"] = int(val) * 1000
        else:
            # if someone writes "under 30", assume 30k if it's too low
            val_int = int(val)
            if val_int < 200:
                params["budget"] = val_int * 1000
            else:
                params["budget"] = val_int

    # 2. Mileage Extraction (e.g. "under 50k miles", "< 50,000 miles")
    mileage_match = re.search(r'(?:under|<|less than)?\s*(\d{1,3}(?:,\d{3})*|\d+)(k)?\s*miles', query_lower)
    if mileage_match:
        val = mileage_match.group(1).replace(',', '')
        if mileage_match.group(2) == 'k':
            params["mileage"] = int(val) * 1000
        else:
            val_int = int(val)
            if val_int < 300:
                params["mileage"] = val_int * 1000
            else:
                params["mileage"] = val_int

    # 3. Features
    common_features = {
        "adaptive cruise": [r'adaptive cruise'],
        "touchscreen": [r'touchscreen', r'screen'],
        "ventilated seats": [r'ventilated', r'cooled seat'],
        "heated seats": [r'heated seat'],
        "towing package": [r'towing', r'tow hitch'],
        "leather": [r'leather'],
        "apple carplay": [r'apple carplay', r'apple car play', r'carplay'],
        "third row": [r'third row', r'3rd row', r'3 rows'],
        "sunroof": [r'sunroof', r'moonroof', r'moon roof', r'panoramic'],
        "awd": [r'\bawd\b', r'all wheel drive', r'4wd', r'4x4']
    }
    for feature, patterns in common_features.items():
        if any(re.search(p, query_lower) for p in patterns):
            params["features"].append(feature)

    # 4. Body Style
    body_styles = ["suv", "sedan", "truck", "wagon", "coupe"]
    for style in body_styles:
        if re.search(r'\b' + style + r'\b', query_lower):
            params["body_style"] = style.upper()
            break

    # 5. Accident History
    if "clean" in query_lower and ("accident" in query_lower or "history" in query_lower):
        params["accident_history"] = "Clean"
        
    return params

def filter_inventory(df, params):
    """
    Filters the pandas dataframe based on extracted parameters.
    """
    filtered_df = df.copy()
    
    if params["budget"]:
        filtered_df = filtered_df[filtered_df["price"] <= params["budget"]]
        
    if params["mileage"]:
        filtered_df = filtered_df[filtered_df["mileage"] <= params["mileage"]]
        
    if params["body_style"]:
        filtered_df = filtered_df[filtered_df["body_style"] == params["body_style"]]
        
    if params["accident_history"]:
        filtered_df = filtered_df[filtered_df["accident_history"] == params["accident_history"]]
        
    if params["features"]:
        # Ensure all required features are present
        def has_features(car_features):
            return all(f in car_features for f in params["features"])
        
        mask = filtered_df["features"].apply(has_features)
        filtered_df = filtered_df[mask]
        
    return filtered_df
