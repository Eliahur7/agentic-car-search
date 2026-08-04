import re
import os
import json

def parse_search_query(query: str, previous_params: dict = None):
    """
    Parses a natural language query to extract search parameters.
    Attempts to use an Anthropic LLM Agent if an API key is present,
    otherwise falls back to rule-based heuristics.
    """
    query_lower = query.lower()
    
    # Defaults or carry-over from previous
    if previous_params:
        params = previous_params.copy()
        if "features" not in params:
            params["features"] = []
    else:
        params = {
            "make": None,
            "model": None,
            "min_year": None,
            "max_year": None,
            "budget": None,
            "mileage": None,
            "condition": None,
            "zip_code": None,
            "trade_in": None,
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
            User Query: "{query}"
            
            Previous Search Parameters Context (Update these based on the user query):
            {json.dumps(params)}
            
            JSON schema:
            {{
                "make": string or null (e.g. "Toyota", "Honda", "Porsche", "BMW"),
                "model": string or null (e.g. "X5", "Highlander", "CR-V", "Corvette", "911", "Model 3"),
                "min_year": integer or null (e.g., if "2024-2026" -> 2024),
                "max_year": integer or null (e.g., if "2024-2026" -> 2026),
                "budget": integer or null (e.g., if "under 30k" -> 30000),
                "mileage": integer or null (e.g., if "under 40k miles" -> 40000),
                "condition": string or null ("New", "Used", or "Certified Pre-Owned"),
                "zip_code": string or null (5-digit zip code e.g. "53024"),
                "trade_in": string or null (e.g. "Yes" or vehicle details if specified),
                "features": list of strings (map synonyms to: "adaptive cruise", "touchscreen", "ventilated seats", "heated seats", "towing package", "leather", "apple carplay", "third row", "sunroof", "awd"),
                "body_style": string or null (e.g. "SUV", "Sedan", "Truck", "Wagon", "Coupe", "Sports Car", "Convertible"),
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
        # Prevent backtracking into 'k miles' or digits/commas
        budget_match = re.search(r'(?:budget|under|<|less than)\s*(\d{1,3}(?:,\d{3})*|\d+)(k)?(?!\s*miles|\s*k\s*miles|[\d,k])', query_lower)
        
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
        "leather": [r'leather', r'luxury'],
        "apple carplay": [r'apple carplay', r'apple car play', r'carplay'],
        "third row": [r'third row', r'3rd row', r'3 rows'],
        "sunroof": [r'sunroof', r'moonroof', r'moon roof', r'panoramic'],
        "awd": [r'\bawd\b', r'all wheel drive', r'4wd', r'4x4']
    }
    for feature, patterns in common_features.items():
        if any(re.search(p, query_lower) for p in patterns):
            params["features"].append(feature)

    # 4. Body Style
    body_styles = {
        "SUV": ["suv"],
        "Sedan": ["sedan"],
        "Truck": ["truck"],
        "Wagon": ["wagon"],
        "Coupe": ["coupe"],
        "Sports Car": ["sports car", "sporty"],
        "Convertible": ["convertible"],
        "Minivan": ["minivan"],
        "Hatchback": ["hatchback"]
    }
    for style, patterns in body_styles.items():
        if any(re.search(r'\b' + p + r'\b', query_lower) for p in patterns):
            params["body_style"] = style
            break
            
    # Make & Model Extraction (regex heuristic)
    makes_models = {
        "BMW": ["bmw"],
        "Toyota": ["toyota"],
        "Honda": ["honda"],
        "Ford": ["ford"],
        "Tesla": ["tesla"],
        "Hyundai": ["hyundai"],
        "Kia": ["kia"],
        "Chevrolet": ["chevrolet", "chevy"],
        "Subaru": ["subaru"],
        "Volkswagen": ["volkswagen", "vw"],
        "Porsche": ["porsche"]
    }
    for make_name, patterns in makes_models.items():
        if any(re.search(r'\b' + p + r'\b', query_lower) for p in patterns):
            params["make"] = make_name
            break

    known_models = {
        "X5": ["x5"],
        "Highlander": ["highlander"],
        "CR-V": ["cr-v", "crv"],
        "F-150": ["f-150", "f150"],
        "RAV4": ["rav4"],
        "Model 3": ["model 3", "model3"],
        "Palisade": ["palisade"],
        "Telluride": ["telluride"],
        "Tahoe": ["tahoe"],
        "Outback": ["outback"],
        "Pilot": ["pilot"],
        "Sorento": ["sorento"],
        "Tiguan": ["tiguan"],
        "911": ["911"],
        "Corvette": ["corvette", "vette"],
        "Mustang": ["mustang"]
    }
    for model_name, patterns in known_models.items():
        if any(re.search(r'\b' + p + r'\b', query_lower) for p in patterns):
            params["model"] = model_name
            break

    # Year Range Extraction (e.g. "2024-2026", "2024 to 2026", "2022")
    year_range_match = re.search(r'\b(20[0-2][0-9])\s*[-–to]+\s*(20[0-2][0-9])\b', query_lower)
    if year_range_match:
        params["min_year"] = int(year_range_match.group(1))
        params["max_year"] = int(year_range_match.group(2))
    else:
        single_year_match = re.search(r'\b(20[0-2][0-9])\b', query_lower)
        if single_year_match and not params.get("min_year"):
            y = int(single_year_match.group(1))
            params["min_year"] = y
            params["max_year"] = y

    # 5. Accident History
    if "clean" in query_lower and ("accident" in query_lower or "history" in query_lower):
        params["accident_history"] = "Clean"
        
    # 6. Condition (New vs Used vs CPO)
    if "brand new" in query_lower or " new car" in query_lower or query_lower.startswith("new "):
        params["condition"] = "New"
    elif "cpo" in query_lower or "certified" in query_lower:
        params["condition"] = "Certified Pre-Owned"
    elif "used" in query_lower or "pre-owned" in query_lower or "second hand" in query_lower:
        params["condition"] = "Used"

    # 7. Zip Code Extraction (5-digit postal code)
    zip_match = re.search(r'\b(\d{5})\b', query)
    if zip_match:
        params["zip_code"] = zip_match.group(1)

    # 8. Trade-In Detection
    if "trade" in query_lower or "trading" in query_lower or "trade-in" in query_lower:
        params["trade_in"] = "Yes"

    # Deduplicate features
    params["features"] = list(set(params["features"]))
        
    return params

def generate_followup_questions(params: dict) -> list:
    """
    Generates intelligent follow-up questions based on missing key search criteria.
    """
    questions = []
    
    if not params.get("condition"):
        questions.append("Are you looking for a **New**, **Used**, or **Certified Pre-Owned** vehicle?")
        
    if not params.get("zip_code"):
        questions.append("What is your **Zip Code** so I can prioritize nearby dealer inventory?")
        
    if not params.get("trade_in"):
        questions.append("Are you planning to **trade in** a vehicle towards this purchase?")
        
    if not params.get("budget"):
        questions.append("Do you have a specific **maximum budget** or monthly payment target in mind?")
        
    return questions

def filter_inventory(df, params):
    """
    Filters the pandas dataframe based on extracted parameters.
    If strict filtering returns 0 matches, performs relaxed matching so the user gets helpful recommendations.
    """
    def apply_filters(input_df, p_dict):
        f_df = input_df.copy()
        
        if p_dict.get("budget"):
            f_df = f_df[f_df["price"] <= p_dict["budget"]]
            
        if p_dict.get("mileage"):
            f_df = f_df[f_df["mileage"] <= p_dict["mileage"]]
            
        if p_dict.get("min_year"):
            f_df = f_df[f_df["year"] >= p_dict["min_year"]]
            
        if p_dict.get("max_year"):
            f_df = f_df[f_df["year"] <= p_dict["max_year"]]
            
        if p_dict.get("body_style"):
            f_df = f_df[f_df["body_style"].str.lower() == p_dict["body_style"].lower()]
            
        if p_dict.get("make"):
            f_df = f_df[f_df["make"].str.lower() == p_dict["make"].lower()]
            
        if p_dict.get("model"):
            f_df = f_df[f_df["model"].str.lower() == p_dict["model"].lower()]
            
        if p_dict.get("accident_history"):
            f_df = f_df[f_df["accident_history"] == p_dict["accident_history"]]
            
        if p_dict.get("features"):
            def has_features(car_features):
                return all(f in car_features for f in p_dict["features"])
            mask = f_df["features"].apply(has_features)
            f_df = f_df[mask]
            
        return f_df

    # 1. Primary strict filter
    filtered_df = apply_filters(df, params)
    
    # 2. If no exact matches, try relaxing year constraints first, then mileage constraints
    if filtered_df.empty:
        relaxed_params = params.copy()
        # Drop year filter to find closest model years
        relaxed_params["min_year"] = None
        relaxed_params["max_year"] = None
        filtered_df = apply_filters(df, relaxed_params)
        
    if filtered_df.empty:
        # If still empty, drop mileage constraint as well
        relaxed_params["mileage"] = None
        filtered_df = apply_filters(df, relaxed_params)
        
    return filtered_df
