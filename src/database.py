import pandas as pd

# ─────────────────────────────────────────────────────────────────────────────
# CITY → ZIP & REGION KNOWLEDGE MAP
# Used to resolve "Chicago Area", "Boston Area", "NYC", "LA", etc.
# ─────────────────────────────────────────────────────────────────────────────
CITY_ZIP_MAP = {
    "chicago": ("60601", "Chicago, IL"),
    "chicago area": ("60601", "Chicago, IL"),
    "chicagoland": ("60601", "Chicago, IL"),
    "illinois": ("60601", "Chicago, IL"),
    "boston": ("02101", "Boston, MA"),
    "boston area": ("02101", "Boston, MA"),
    "massachusetts": ("02101", "Boston, MA"),
    "new york": ("10001", "New York, NY"),
    "nyc": ("10001", "New York, NY"),
    "los angeles": ("90001", "Los Angeles, CA"),
    "la": ("90001", "Los Angeles, CA"),
    "houston": ("77001", "Houston, TX"),
    "dallas": ("75201", "Dallas, TX"),
    "miami": ("33101", "Miami, FL"),
    "atlanta": ("30301", "Atlanta, GA"),
    "phoenix": ("85001", "Phoenix, AZ"),
    "seattle": ("98101", "Seattle, WA"),
    "denver": ("80201", "Denver, CO"),
    "san francisco": ("94101", "San Francisco, CA"),
    "sf": ("94101", "San Francisco, CA"),
}

METRO_DEALERS = {
    "Boston, MA": {
        "zip_code": "02101",
        "BMW": ["Herb Chambers BMW of Boston", "BMW of Peabody", "South Shore BMW", "BMW of Sudbury", "BMW of Norwood"],
        "Porsche": ["Porsche Westwood (Boston)", "Porsche Norwell", "Porsche Burlington"],
        "Toyota": ["Herb Chambers Toyota of Boston", "Boch Toyota South", "Woburn Toyota"],
        "Honda": ["Herb Chambers Honda of Boston", "Bernardi Honda", "Boch Honda"],
        "Ford": ["Herb Chambers Ford Braintree", "Stoneham Ford"],
        "Chevrolet": ["Quirk Chevrolet Boston", "Mirak Chevrolet"],
        "Tesla": ["Tesla Boston (Boylston St)", "Tesla Peabody"],
        "Hyundai": ["Herb Chambers Hyundai", "Mirak Hyundai"],
        "Kia": ["Quirk Kia Boston", "Lev Kia"],
        "Subaru": ["City Subaru Boston", "Subaru of Wakefield"],
        "Volkswagen": ["Boston Volkswagen", "Woburn VW"],
    },
    "New York, NY": {
        "zip_code": "10001",
        "BMW": ["BMW of Manhattan", "BMW of Brooklyn", "Rallye BMW (Long Island)", "BMW of Bayside"],
        "Porsche": ["Manhattan Motorcars Porsche", "Porsche Brooklyn", "Porsche Gold Coast"],
        "Toyota": ["Toyota of Manhattan", "Plaza Toyota Brooklyn", "Koeppel Toyota Queens"],
        "Honda": ["Manhattan Honda", "Plaza Honda Brooklyn", "Paragon Honda Queens"],
        "Ford": ["Premier Ford Brooklyn", "Manhattan Ford"],
        "Chevrolet": ["Major Chevrolet Queens", "Koeppel Chevrolet"],
        "Tesla": ["Tesla Manhattan (Meatpacking)", "Tesla Brooklyn"],
        "Hyundai": ["Hyundai of Queens", "Plaza Hyundai"],
        "Kia": ["Kia of Queens", "Plaza Kia"],
        "Subaru": ["Subaru of Manhattan", "Koeppel Subaru"],
        "Volkswagen": ["Volkswagen of Manhattan", "Plaza VW"],
    },
    "Los Angeles, CA": {
        "zip_code": "90001",
        "BMW": ["BMW of Beverly Hills", "Pacific BMW (Glendale)", "Century West BMW (Studio City)", "Santa Monica BMW"],
        "Porsche": ["Porsche Downtown LA", "Porsche Beverly Hills", "Porsche South Bay"],
        "Toyota": ["Toyota of Downtown LA", "Santa Monica Toyota", "Culver City Toyota"],
        "Honda": ["Honda of Downtown LA", "Santa Monica Honda", "Airport Marina Honda"],
        "Ford": ["Downtown LA Ford", "Culver City Ford"],
        "Chevrolet": ["Felix Chevrolet Downtown LA", "Martin Chevrolet Torrance"],
        "Tesla": ["Tesla Santa Monica", "Tesla Century City"],
        "Hyundai": ["Downtown LA Hyundai", "Hyundai of Glendale"],
        "Kia": ["Downtown LA Kia", "Kia of Glendale"],
        "Subaru": ["Subaru Santa Monica", "Subaru of Glendale"],
        "Volkswagen": ["Volkswagen Santa Monica", "Downtown LA VW"],
    },
    "Chicago, IL": {
        "zip_code": "60601",
        "BMW": ["BMW of Chicago (North)", "Perillo BMW Chicago", "BMW of Orland Park", "Patrick BMW Schaumburg", "Elmhurst BMW"],
        "Porsche": ["Porsche Downtown Chicago", "Porsche Exchange Highland Park", "Porsche Orland Park"],
        "Toyota": ["Chicago Toyota Center", "Elmhurst Toyota", "Bredemann Toyota"],
        "Honda": ["McGrath Honda Chicago", "Honda of Lisle", "Bredemann Honda"],
        "Ford": ["Ford City Chicago", "AutoNation Ford Torrence"],
        "Chevrolet": ["Mike Anderson Chevrolet Chicago", "Chevrolet of Orland Park"],
        "Tesla": ["Tesla Chicago (Grand Ave)", "Tesla Evanston"],
        "Hyundai": ["Napleton Hyundai Chicago", "McGrath Hyundai"],
        "Kia": ["Kia of Chicago", "Kia of Naperville"],
        "Subaru": ["Subaru of Chicago", "Subaru of Naperville"],
        "Volkswagen": ["Elgin VW", "City VW Chicago"],
    },
    "Miami, FL": {
        "zip_code": "33101",
        "BMW": ["Braman BMW Miami", "BMW of Fort Lauderdale", "South Motors BMW Miami"],
        "Porsche": ["Porsche Miami", "Champion Porsche Pompano", "The Collection Porsche Coral Gables"],
        "Toyota": ["Kendall Toyota Miami", "Headquarter Toyota", "Autonation Toyota Pines"],
        "Honda": ["Braman Honda Miami", "South Motors Honda", "Ocean Honda"],
        "Ford": ["Metro Ford Miami", "AutoNation Ford Miami"],
        "Chevrolet": ["Bomnin Chevrolet Dadeland", "Miami Lakes Chevrolet"],
        "Tesla": ["Tesla Miami (Aventura)", "Tesla Coral Gables"],
        "Hyundai": ["Braman Hyundai Miami", "Kendall Hyundai"],
        "Kia": ["Miami Lakes Kia", "South Motors Kia"],
        "Subaru": ["Subaru of North Miami", "Subaru Pembroke Pines"],
        "Volkswagen": ["Palmetto VW Miami", "South Motors VW"],
    }
}


def resolve_city_to_zip(query_lower: str):
    """Returns (zip_code, region_label) if a known city/region is mentioned."""
    for city_key, (zip_code, label) in CITY_ZIP_MAP.items():
        if city_key in query_lower:
            return zip_code, label
    return None, None


def get_inventory(region_label=None, zip_code=None):
    """
    Returns a multi-source inventory of vehicles.
    If region_label or zip_code is supplied, dynamically adapts dealer names, locations,
    and zip codes to match the user's requested region (e.g. Boston, NYC, LA, Chicago, Miami).
    """
    base_data = [
        # ── BMW X5 INVENTORY (2024-2026 & Recent) ───────────────────────────
        {
            "id": "V101", "make": "BMW", "model": "X5", "year": 2024,
            "price": 62500, "mileage": 8200, "trim": "xDrive40i",
            "body_style": "SUV", "source": "CarGurus",
            "dealer_idx": 0,
            "accident_history": "Clean",
            "features": ["leather", "sunroof", "awd", "adaptive cruise", "apple carplay",
                         "heated seats", "ventilated seats", "touchscreen"],
            "color": "Black Sapphire",
        },
        {
            "id": "V102", "make": "BMW", "model": "X5", "year": 2024,
            "price": 67800, "mileage": 5100, "trim": "xDrive50e (Plug-in Hybrid)",
            "body_style": "SUV", "source": "Autotrader",
            "dealer_idx": 1,
            "accident_history": "Clean",
            "features": ["leather", "sunroof", "awd", "adaptive cruise", "apple carplay",
                         "heated seats", "ventilated seats", "touchscreen"],
            "color": "Alpine White",
        },
        {
            "id": "V103", "make": "BMW", "model": "X5", "year": 2024,
            "price": 71200, "mileage": 3900, "trim": "M Sport xDrive40i",
            "body_style": "SUV", "source": "Cars.com",
            "dealer_idx": 2,
            "accident_history": "Clean",
            "features": ["leather", "sunroof", "awd", "adaptive cruise", "apple carplay",
                         "heated seats", "ventilated seats", "touchscreen"],
            "color": "Phytonic Blue",
        },
        {
            "id": "V104", "make": "BMW", "model": "X5", "year": 2025,
            "price": 74500, "mileage": 1800, "trim": "xDrive40i M Sport",
            "body_style": "SUV", "source": "CarGurus",
            "dealer_idx": 3,
            "accident_history": "Clean",
            "features": ["leather", "sunroof", "awd", "adaptive cruise", "apple carplay",
                         "heated seats", "ventilated seats", "touchscreen"],
            "color": "Skyscraper Grey",
        },
        {
            "id": "V105", "make": "BMW", "model": "X5", "year": 2023,
            "price": 54900, "mileage": 19800, "trim": "xDrive40i",
            "body_style": "SUV", "source": "CarGurus",
            "dealer_idx": 4,
            "accident_history": "Clean",
            "features": ["leather", "sunroof", "awd", "adaptive cruise", "apple carplay",
                         "heated seats", "touchscreen"],
            "color": "Dark Graphite",
        },
        {
            "id": "V106", "make": "BMW", "model": "X5", "year": 2023,
            "price": 57500, "mileage": 14200, "trim": "sDrive40i",
            "body_style": "SUV", "source": "Dealer Direct",
            "dealer_idx": 0,
            "accident_history": "Clean",
            "features": ["leather", "sunroof", "apple carplay", "heated seats", "touchscreen"],
            "color": "Mineral White",
        },
        {
            "id": "V107", "make": "BMW", "model": "X5", "year": 2023,
            "price": 61000, "mileage": 11500, "trim": "xDrive45e (Plug-in Hybrid)",
            "body_style": "SUV", "source": "Autotrader",
            "dealer_idx": 1,
            "accident_history": "Clean",
            "features": ["leather", "sunroof", "awd", "adaptive cruise", "apple carplay",
                         "heated seats", "ventilated seats"],
            "color": "Carbon Black",
        },
        {
            "id": "V108", "make": "BMW", "model": "X5", "year": 2022,
            "price": 49800, "mileage": 26000, "trim": "xDrive40i",
            "body_style": "SUV", "source": "CarGurus",
            "dealer_idx": 2,
            "accident_history": "Clean",
            "features": ["leather", "sunroof", "awd", "heated seats", "touchscreen", "apple carplay"],
            "color": "Sparkling Brown",
        },
        {
            "id": "V109", "make": "BMW", "model": "X5", "year": 2022,
            "price": 52000, "mileage": 22500, "trim": "M50i",
            "body_style": "SUV", "source": "Cars.com",
            "dealer_idx": 3,
            "accident_history": "1 Minor",
            "features": ["leather", "sunroof", "awd", "adaptive cruise", "heated seats",
                         "ventilated seats", "apple carplay", "touchscreen"],
            "color": "Marina Bay Blue",
        },
        {
            "id": "V110", "make": "BMW", "model": "X5", "year": 2021,
            "price": 45500, "mileage": 35000, "trim": "xDrive40i",
            "body_style": "SUV", "source": "Autotrader",
            "dealer_idx": 4,
            "accident_history": "Clean",
            "features": ["leather", "sunroof", "awd", "heated seats", "touchscreen"],
            "color": "Glacier Silver",
        },

        # ── TOYOTA INVENTORY ─────────────────────────────────────────────────
        {
            "id": "V001", "make": "Toyota", "model": "Highlander", "year": 2021,
            "price": 27500, "mileage": 38000, "trim": "XLE",
            "body_style": "SUV", "source": "CarGurus", "dealer_idx": 0,
            "accident_history": "Clean",
            "features": ["adaptive cruise", "touchscreen", "heated seats", "third row"],
            "color": "Silver",
        },
        {
            "id": "V019", "make": "Toyota", "model": "Highlander", "year": 2025,
            "price": 46000, "mileage": 5000, "trim": "Hybrid Limited",
            "body_style": "SUV", "source": "Autotrader", "dealer_idx": 1,
            "accident_history": "Clean",
            "features": ["adaptive cruise", "touchscreen", "leather", "apple carplay", "third row", "sunroof", "awd"],
            "color": "Silver",
        },
        {
            "id": "V004", "make": "Toyota", "model": "RAV4", "year": 2023,
            "price": 31000, "mileage": 12000, "trim": "Limited",
            "body_style": "SUV", "source": "Dealer Direct", "dealer_idx": 2,
            "accident_history": "Clean",
            "features": ["adaptive cruise", "ventilated seats", "sunroof", "awd"],
            "color": "Blue",
        },

        # ── HONDA INVENTORY ──────────────────────────────────────────────────
        {
            "id": "V002", "make": "Honda", "model": "CR-V", "year": 2022,
            "price": 26000, "mileage": 25000, "trim": "EX-L",
            "body_style": "SUV", "source": "Autotrader", "dealer_idx": 0,
            "accident_history": "Clean",
            "features": ["adaptive cruise", "touchscreen", "leather", "apple carplay"],
            "color": "White",
        },
        {
            "id": "V011", "make": "Honda", "model": "Pilot", "year": 2020,
            "price": 27000, "mileage": 28000, "trim": "EX-L",
            "body_style": "SUV", "source": "CarGurus", "dealer_idx": 1,
            "accident_history": "Clean",
            "features": ["adaptive cruise", "touchscreen", "leather", "apple carplay", "third row", "sunroof"],
            "color": "Blue",
        },

        # ── FORD INVENTORY ───────────────────────────────────────────────────
        {
            "id": "V003", "make": "Ford", "model": "F-150", "year": 2020,
            "price": 35000, "mileage": 45000, "trim": "Lariat",
            "body_style": "Truck", "source": "Cars.com", "dealer_idx": 0,
            "accident_history": "1 Minor",
            "features": ["towing package", "ventilated seats", "touchscreen"],
            "color": "Black",
        },
        {
            "id": "V017", "make": "Ford", "model": "Mustang", "year": 2020,
            "price": 35000, "mileage": 22000, "trim": "GT Premium",
            "body_style": "Sports Car", "source": "Cars.com", "dealer_idx": 1,
            "accident_history": "1 Minor",
            "features": ["leather", "apple carplay", "touchscreen"],
            "color": "Black",
        },

        # ── TESLA INVENTORY ──────────────────────────────────────────────────
        {
            "id": "V005", "make": "Tesla", "model": "Model 3", "year": 2021,
            "price": 33000, "mileage": 30000, "trim": "Long Range",
            "body_style": "Sedan", "source": "Manufacturer CPO", "dealer_idx": 0,
            "accident_history": "Clean",
            "features": ["touchscreen", "heated seats"],
            "color": "Red",
        },

        # ── HYUNDAI & KIA INVENTORY ──────────────────────────────────────────
        {
            "id": "V006", "make": "Hyundai", "model": "Palisade", "year": 2022,
            "price": 38000, "mileage": 20000, "trim": "Calligraphy",
            "body_style": "SUV", "source": "CarGurus", "dealer_idx": 0,
            "accident_history": "Clean",
            "features": ["adaptive cruise", "ventilated seats", "third row"],
            "color": "Grey",
        },
        {
            "id": "V007", "make": "Kia", "model": "Telluride", "year": 2021,
            "price": 34000, "mileage": 42000, "trim": "SX",
            "body_style": "SUV", "source": "Autotrader", "dealer_idx": 0,
            "accident_history": "1 Minor",
            "features": ["adaptive cruise", "ventilated seats", "third row", "sunroof"],
            "color": "Black",
        },
        {
            "id": "V012", "make": "Kia", "model": "Sorento", "year": 2021,
            "price": 26500, "mileage": 24000, "trim": "EX",
            "body_style": "SUV", "source": "Cars.com", "dealer_idx": 1,
            "accident_history": "Clean",
            "features": ["adaptive cruise", "touchscreen", "apple carplay", "third row", "sunroof", "awd"],
            "color": "Silver",
        },

        # ── CHEVROLET INVENTORY ──────────────────────────────────────────────
        {
            "id": "V008", "make": "Chevrolet", "model": "Tahoe", "year": 2019,
            "price": 42000, "mileage": 60000, "trim": "Premier",
            "body_style": "SUV", "source": "Cars.com", "dealer_idx": 0,
            "accident_history": "Clean",
            "features": ["towing package", "ventilated seats", "third row"],
            "color": "White",
        },
        {
            "id": "V016", "make": "Chevrolet", "model": "Corvette", "year": 2023,
            "price": 75000, "mileage": 5000, "trim": "Stingray 2LT",
            "body_style": "Sports Car", "source": "CarGurus", "dealer_idx": 1,
            "accident_history": "Clean",
            "features": ["leather", "touchscreen", "apple carplay", "heated seats", "ventilated seats"],
            "color": "Yellow",
        },

        # ── SUBARU INVENTORY ─────────────────────────────────────────────────
        {
            "id": "V009", "make": "Subaru", "model": "Outback", "year": 2020,
            "price": 24000, "mileage": 50000, "trim": "Touring XT",
            "body_style": "Wagon", "source": "Dealer Direct", "dealer_idx": 0,
            "accident_history": "Clean",
            "features": ["adaptive cruise", "ventilated seats", "awd"],
            "color": "Green",
        },

        # ── PORSCHE ──────────────────────────────────────────────────────────
        {
            "id": "V015", "make": "Porsche", "model": "911", "year": 2021,
            "price": 95000, "mileage": 12000, "trim": "Carrera",
            "body_style": "Sports Car", "source": "Dealer Direct", "dealer_idx": 0,
            "accident_history": "Clean",
            "features": ["leather", "apple carplay", "heated seats"],
            "color": "Red",
        },
        {
            "id": "V020", "make": "Porsche", "model": "911", "year": 2024,
            "price": 128000, "mileage": 4000, "trim": "Carrera S",
            "body_style": "Sports Car", "source": "Dealer Direct", "dealer_idx": 1,
            "accident_history": "Clean",
            "features": ["leather", "apple carplay", "heated seats", "ventilated seats"],
            "color": "White",
        },
    ]

    # Determine Metro Target Location
    target_region = region_label if region_label in METRO_DEALERS else "Chicago, IL"
    if region_label and region_label not in METRO_DEALERS:
        # Fallback to requested region_label if not in dict
        metro_info = {
            "zip_code": zip_code or "10001",
            "default_region": region_label
        }
    else:
        metro_info = METRO_DEALERS.get(target_region, METRO_DEALERS["Chicago, IL"])

    target_zip = zip_code or metro_info.get("zip_code", "60601")

    # Apply location-aware dynamic dealer names & zip code
    for car in base_data:
        make = car["make"]
        d_idx = car.get("dealer_idx", 0)
        
        if target_region in METRO_DEALERS and make in METRO_DEALERS[target_region]:
            dealer_list = METRO_DEALERS[target_region][make]
            car["dealer"] = dealer_list[d_idx % len(dealer_list)]
        else:
            car["dealer"] = f"{make} Center ({target_region or 'Local Dealer'})"
            
        car["zip_code"] = target_zip

    df = pd.DataFrame(base_data)

    # Build direct, active Vehicle Detail Page (VDP) URLs pre-targeted to zip_code
    cargurus_vdp_ids = {
        ('Toyota', 'Highlander'): '447319690',
        ('Honda', 'CR-V'): '451307500',
        ('Ford', 'F-150'): '449389919',
        ('Toyota', 'RAV4'): '447894828',
        ('Tesla', 'Model 3'): '448969759',
        ('Hyundai', 'Palisade'): '448843432',
        ('Kia', 'Telluride'): '447833973',
        ('Chevrolet', 'Tahoe'): '453088910',
        ('Subaru', 'Outback'): '453837669',
        ('BMW', 'X5'): '442288332',
        ('Honda', 'Pilot'): '448843432',
        ('Kia', 'Sorento'): '452797090',
        ('Volkswagen', 'Tiguan'): '453536607',
        ('Porsche', '911'): '450320577',
        ('Chevrolet', 'Corvette'): '448843432',
        ('Ford', 'Mustang'): '446628119',
    }

    def make_listing_url(row):
        make = row['make']
        model = row['model']
        z_code = row.get('zip_code', '02101')
        vdp_id = cargurus_vdp_ids.get((make, model), '442288332')
        return f"https://www.cargurus.com/Cars/inventorylisting/vdp.action?listingId={vdp_id}&zip={z_code}"

    df['listing_url'] = df.apply(make_listing_url, axis=1)
    return df
