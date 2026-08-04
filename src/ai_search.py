import re
import os
import json
from src.database import CITY_ZIP_MAP, resolve_city_to_zip

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
            "region_label": None,
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
                "zip_code": string or null (5-digit zip code e.g. "53024", or resolve "Chicago" -> "60601"),
                "region_label": string or null (e.g. "Chicago, IL"),
                "trade_in": string or null (e.g. "Yes" or vehicle details if specified),
                "features": list of strings (map synonyms: moonroof/panoramic -> "sunroof", luxury -> "leather", cooled seats -> "ventilated seats"),
                "body_style": string or null (e.g. "SUV", "Sedan", "Truck", "Sports Car"),
                "accident_history": string or null (e.g. "Clean")
            }}
            
            Important rules:
            - "moonroof", "moon roof", "panoramic" all map to the "sunroof" feature
            - "luxury", "leather interior" maps to "leather" feature
            - "Chicago Area", "Chicagoland", "Chicago, IL" -> zip_code "60601", region_label "Chicago, IL"
            - "New York", "NYC" -> zip_code "10001", region_label "New York, NY"
            - "Los Angeles", "LA" -> zip_code "90001", region_label "Los Angeles, CA"
            Output only the raw JSON.
            """
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=300,
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

    # ── HEURISTIC FALLBACK ────────────────────────────────────────────────────

    # 1. City / Region Detection  (MUST run before zip to avoid overwrite)
    resolved_zip, resolved_label = resolve_city_to_zip(query_lower)
    if resolved_zip and not params.get("zip_code"):
        params["zip_code"] = resolved_zip
        params["region_label"] = resolved_label

    # 2. Budget Extraction (e.g. "under 30k", "under $30,000", "< 30000")
    budget_match = re.search(r'\$(\d{1,3}(?:,\d{3})*|\d+)(k)?', query_lower)
    if not budget_match:
        budget_match = re.search(
            r'(?:budget|under|<|less than)\s*(\d{1,3}(?:,\d{3})*|\d+)(k)?(?!\s*miles|\s*k\s*miles|[\d,k])',
            query_lower
        )
    if budget_match:
        val = budget_match.group(1).replace(',', '')
        if budget_match.group(2) == 'k':
            params["budget"] = int(val) * 1000
        else:
            val_int = int(val)
            params["budget"] = val_int * 1000 if val_int < 200 else val_int

    # 3. Mileage Extraction (e.g. "under 50k miles", "< 50,000 miles", "no more than 30,000 miles")
    mileage_match = re.search(
        r'(?:under|<|less than|no more than|max(?:imum)?|at most)?\s*(\d{1,3}(?:,\d{3})*|\d+)(k)?\s*miles',
        query_lower
    )
    if mileage_match:
        val = mileage_match.group(1).replace(',', '')
        if mileage_match.group(2) == 'k':
            params["mileage"] = int(val) * 1000
        else:
            val_int = int(val)
            params["mileage"] = val_int * 1000 if val_int < 300 else val_int

    # 4. Feature Extraction with full synonym support
    common_features = {
        "adaptive cruise": [r'adaptive cruise', r'cruise control'],
        "touchscreen": [r'touchscreen', r'\bscreen\b', r'infotainment'],
        "ventilated seats": [r'ventilated', r'cooled seat', r'cool seat'],
        "heated seats": [r'heated seat', r'seat heat'],
        "towing package": [r'towing', r'tow hitch', r'tow package'],
        "leather": [r'leather', r'leather interior', r'\bluxury\b'],
        "apple carplay": [r'apple carplay', r'apple car play', r'carplay', r'android auto'],
        "third row": [r'third row', r'3rd row', r'3 rows', r'7 seat', r'7-seat'],
        "sunroof": [r'sunroof', r'moonroof', r'moon roof', r'panoramic', r'pano roof', r'glass roof'],
        "awd": [r'\bawd\b', r'all.?wheel.?drive', r'\b4wd\b', r'4x4', r'x-drive', r'xdrive'],
    }
    for feature, patterns in common_features.items():
        if any(re.search(p, query_lower) for p in patterns):
            if feature not in params["features"]:
                params["features"].append(feature)

    # 5. Body Style
    body_styles = {
        "SUV": [r'\bsuv\b', r'\bcrossover\b'],
        "Sedan": [r'\bsedan\b'],
        "Truck": [r'\btruck\b', r'\bpickup\b'],
        "Wagon": [r'\bwagon\b'],
        "Coupe": [r'\bcoupe\b'],
        "Sports Car": [r'sports car', r'sporty'],
        "Convertible": [r'convertible', r'cabriolet'],
        "Minivan": [r'minivan', r'van'],
        "Hatchback": [r'hatchback'],
    }
    for style, patterns in body_styles.items():
        if any(re.search(p, query_lower) for p in patterns):
            params["body_style"] = style
            break

    # 6. Make & Model Extraction
    makes_models = {
        "BMW": [r'\bbmw\b'],
        "Toyota": [r'\btoyota\b'],
        "Honda": [r'\bhonda\b'],
        "Ford": [r'\bford\b'],
        "Tesla": [r'\btesla\b'],
        "Hyundai": [r'\bhyundai\b'],
        "Kia": [r'\bkia\b'],
        "Chevrolet": [r'\bchevrolet\b', r'\bchevy\b'],
        "Subaru": [r'\bsubaru\b'],
        "Volkswagen": [r'\bvolkswagen\b', r'\bvw\b'],
        "Porsche": [r'\bporsche\b'],
    }
    for make_name, patterns in makes_models.items():
        if any(re.search(p, query_lower) for p in patterns):
            params["make"] = make_name
            break

    known_models = {
        "X5": [r'\bx5\b'],
        "X3": [r'\bx3\b'],
        "3 Series": [r'\b3 series\b', r'\b328i\b', r'\b330i\b'],
        "5 Series": [r'\b5 series\b', r'\b530i\b', r'\b540i\b'],
        "Highlander": [r'\bhighlander\b'],
        "CR-V": [r'\bcr-v\b', r'\bcrv\b'],
        "F-150": [r'\bf-150\b', r'\bf150\b'],
        "RAV4": [r'\brav4\b'],
        "Model 3": [r'\bmodel 3\b', r'\bmodel3\b'],
        "Model Y": [r'\bmodel y\b', r'\bmodely\b'],
        "Palisade": [r'\bpalisade\b'],
        "Telluride": [r'\btelluride\b'],
        "Tahoe": [r'\btahoe\b'],
        "Outback": [r'\boutback\b'],
        "Pilot": [r'\bpilot\b'],
        "Sorento": [r'\bsorento\b'],
        "Tiguan": [r'\btiguan\b'],
        "911": [r'\b911\b'],
        "Corvette": [r'\bcorvette\b', r'\bvette\b'],
        "Mustang": [r'\bmustang\b'],
    }
    for model_name, patterns in known_models.items():
        if any(re.search(p, query_lower) for p in patterns):
            params["model"] = model_name
            break

    # 7. Year Range Extraction (e.g. "2024-2026", "2024 to 2026", "2022")
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

    # 8. Accident History
    if "clean" in query_lower and ("accident" in query_lower or "history" in query_lower):
        params["accident_history"] = "Clean"

    # 9. Condition (New vs Used vs CPO)
    if "brand new" in query_lower or " new car" in query_lower or query_lower.startswith("new "):
        params["condition"] = "New"
    elif "cpo" in query_lower or "certified" in query_lower:
        params["condition"] = "Certified Pre-Owned"
    elif "used" in query_lower or "pre-owned" in query_lower or "second hand" in query_lower:
        params["condition"] = "Used"

    # 10. Explicit Zip Code Extraction (5-digit postal code)
    zip_match = re.search(r'\b(\d{5})\b', query)
    if zip_match and not params.get("zip_code"):
        params["zip_code"] = zip_match.group(1)

    # 11. Trade-In Detection
    if "trade" in query_lower or "trading" in query_lower or "trade-in" in query_lower:
        params["trade_in"] = "Yes"

    # Deduplicate features
    params["features"] = list(set(params["features"]))

    return params


def generate_search_platform_links(params: dict) -> list:
    """
    Generates live, pre-filtered search links for CarGurus, Autotrader, and Cars.com
    based on the parsed search parameters so users can explore broader live inventory.
    """
    links = []
    make = params.get("make", "")
    model = params.get("model", "")
    min_year = params.get("min_year", "")
    max_year = params.get("max_year", "")
    mileage = params.get("mileage", "")
    budget = params.get("budget", "")
    zip_code = params.get("zip_code", "60601")
    if not zip_code:
        zip_code = "60601"

    # CarGurus entity IDs (needed for correct model filtering)
    cargurus_entity = {
        "X5": "d393", "X3": "d390", "Highlander": "d298", "CR-V": "d589",
        "F-150": "d337", "RAV4": "d306", "Model 3": "d2475", "Palisade": "d2847",
        "Telluride": "d2757", "Tahoe": "d637", "Outback": "d380", "Pilot": "d599",
        "Sorento": "d620", "Tiguan": "d1028", "911": "d404", "Corvette": "d1",
        "Mustang": "d2", "Model Y": "d2576", "3 Series": "d371", "5 Series": "d376"
    }

    # CarGurus filter URL
    cg_params = f"zip={zip_code}&distance=50"
    if min_year:
        cg_params += f"&startYear={min_year}"
    if max_year:
        cg_params += f"&endYear={max_year}"
    if mileage:
        cg_params += f"&maxMileage={mileage}"
    if budget:
        cg_params += f"&maxPrice={budget}"
    entity = cargurus_entity.get(model, "")
    if make and model and entity:
        make_slug = make.replace(" ", "-")
        model_slug = model.replace(" ", "-").replace("/", "-")
        cg_url = f"https://www.cargurus.com/Cars/l-Used-{make_slug}-{model_slug}-{entity}?{cg_params}"
    elif make:
        cg_url = f"https://www.cargurus.com/Cars/l-Used-{make.replace(' ','-')}?{cg_params}"
    else:
        cg_url = f"https://www.cargurus.com/Cars/l-Used-Cars?{cg_params}"
    links.append(("CarGurus Live Search", cg_url))

    # Autotrader filter URL
    at_make = make.lower().replace(" ", "-") if make else ""
    at_model = model.lower().replace(" ", "-").replace("/", "") if model else ""
    at_params = f"zip={zip_code}&maxMileage={mileage or 100000}&searchRadius=50"
    if min_year:
        at_params += f"&startYear={min_year}"
    if max_year:
        at_params += f"&endYear={max_year}"
    if budget:
        at_params += f"&maxPrice={budget}"
    if make and model:
        at_url = f"https://www.autotrader.com/cars-for-sale/used-cars/{at_make}/{at_model}/?{at_params}"
    elif make:
        at_url = f"https://www.autotrader.com/cars-for-sale/used-cars/{at_make}/?{at_params}"
    else:
        at_url = f"https://www.autotrader.com/cars-for-sale/used-cars/?{at_params}"
    links.append(("Autotrader Live Search", at_url))

    # Cars.com filter URL
    cc_make = make.lower().replace(" ", "-") if make else "all"
    cc_model = model.lower().replace(" ", "-").replace("/", "") if model else "all"
    cc_params = f"maximum_distance=50&zip={zip_code}&stock_type=used"
    if min_year:
        cc_params += f"&year_min={min_year}"
    if max_year:
        cc_params += f"&year_max={max_year}"
    if mileage:
        cc_params += f"&mileage_max={mileage}"
    if budget:
        cc_params += f"&price_max={budget}"
    cc_url = f"https://www.cars.com/shopping/{cc_make}-{cc_model}/?{cc_params}"
    links.append(("Cars.com Live Search", cc_url))

    return links


def generate_followup_questions(params: dict) -> list:
    """
    Generates intelligent follow-up questions based on missing key search criteria.
    """
    questions = []

    if not params.get("condition"):
        questions.append("Are you looking for a **New**, **Used**, or **Certified Pre-Owned** vehicle?")

    if not params.get("zip_code"):
        questions.append("What is your **Zip Code** or City so I can find nearby dealer inventory?")

    if not params.get("trade_in"):
        questions.append("Are you planning to **trade in** a vehicle towards this purchase?")

    if not params.get("budget"):
        questions.append("Do you have a specific **maximum budget** or monthly payment target in mind?")

    return questions


def filter_inventory(df, params):
    """
    Filters the pandas dataframe based on extracted parameters.
    If strict filtering returns 0 matches, performs relaxed matching.
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

        # Location filter: if zip_code/region provided, prefer local dealers
        if p_dict.get("region_label") and "zip_code" in f_df.columns:
            local = f_df[f_df["zip_code"].notna()]
            if not local.empty:
                f_df = local

        return f_df

    # 1. Primary strict filter
    filtered_df = apply_filters(df, params)

    # 2. If no exact matches, relax year constraints
    if filtered_df.empty:
        relaxed_params = params.copy()
        relaxed_params["min_year"] = None
        relaxed_params["max_year"] = None
        filtered_df = apply_filters(df, relaxed_params)

    # 3. If still empty, also relax mileage constraint
    if filtered_df.empty:
        relaxed_params["mileage"] = None
        filtered_df = apply_filters(df, relaxed_params)

    # 4. If still empty, relax features constraint
    if filtered_df.empty:
        relaxed_params["features"] = []
        filtered_df = apply_filters(df, relaxed_params)

    return filtered_df
