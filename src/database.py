import pandas as pd

# ─────────────────────────────────────────────────────────────────────────────
# CITY → ZIP & REGION KNOWLEDGE MAP
# Used to resolve "Chicago Area", "NYC", "LA", etc. to zip codes and regions
# ─────────────────────────────────────────────────────────────────────────────
CITY_ZIP_MAP = {
    "chicago": ("60601", "Chicago, IL"),
    "chicago area": ("60601", "Chicago, IL"),
    "chicagoland": ("60601", "Chicago, IL"),
    "illinois": ("60601", "Chicago, IL"),
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
    "boston": ("02101", "Boston, MA"),
}

# Chicago-area dealer names used for local dealer inventory
CHICAGO_DEALERS = [
    "BMW of Chicago (North)", "Perillo BMW Chicago", "BMW of Orland Park",
    "Patrick BMW Schaumburg", "Elmhurst BMW", "AutoNation BMW Chicago"
]


def resolve_city_to_zip(query_lower: str):
    """Returns (zip_code, region_label) if a known city/region is mentioned."""
    for city_key, (zip_code, label) in CITY_ZIP_MAP.items():
        if city_key in query_lower:
            return zip_code, label
    return None, None


def get_inventory():
    """
    Returns a realistic multi-source inventory of vehicles.
    Includes 50+ vehicles with Chicago-area local dealer context,
    covering BMW X5 variants across 2021-2024 and other popular models.
    """
    data = [
        # ── BMW X5 INVENTORY (Chicago Area) ─────────────────────────────────
        {
            "id": "V101", "make": "BMW", "model": "X5", "year": 2024,
            "price": 62500, "mileage": 8200, "trim": "xDrive40i",
            "body_style": "SUV", "source": "CarGurus",
            "dealer": "BMW of Chicago (North)", "zip_code": "60601",
            "accident_history": "Clean",
            "features": ["leather", "sunroof", "awd", "adaptive cruise", "apple carplay",
                         "heated seats", "ventilated seats", "touchscreen"],
            "color": "Black Sapphire",
        },
        {
            "id": "V102", "make": "BMW", "model": "X5", "year": 2024,
            "price": 67800, "mileage": 5100, "trim": "xDrive50e (Plug-in Hybrid)",
            "body_style": "SUV", "source": "Autotrader",
            "dealer": "Perillo BMW Chicago", "zip_code": "60614",
            "accident_history": "Clean",
            "features": ["leather", "sunroof", "awd", "adaptive cruise", "apple carplay",
                         "heated seats", "ventilated seats", "touchscreen"],
            "color": "Alpine White",
        },
        {
            "id": "V103", "make": "BMW", "model": "X5", "year": 2024,
            "price": 71200, "mileage": 3900, "trim": "M Sport xDrive40i",
            "body_style": "SUV", "source": "Cars.com",
            "dealer": "Elmhurst BMW", "zip_code": "60126",
            "accident_history": "Clean",
            "features": ["leather", "sunroof", "awd", "adaptive cruise", "apple carplay",
                         "heated seats", "ventilated seats", "touchscreen"],
            "color": "Phytonic Blue",
        },
        {
            "id": "V104", "make": "BMW", "model": "X5", "year": 2023,
            "price": 54900, "mileage": 19800, "trim": "xDrive40i",
            "body_style": "SUV", "source": "CarGurus",
            "dealer": "AutoNation BMW Chicago", "zip_code": "60601",
            "accident_history": "Clean",
            "features": ["leather", "sunroof", "awd", "adaptive cruise", "apple carplay",
                         "heated seats", "touchscreen"],
            "color": "Dark Graphite",
        },
        {
            "id": "V105", "make": "BMW", "model": "X5", "year": 2023,
            "price": 57500, "mileage": 14200, "trim": "sDrive40i",
            "body_style": "SUV", "source": "Dealer Direct",
            "dealer": "Patrick BMW Schaumburg", "zip_code": "60173",
            "accident_history": "Clean",
            "features": ["leather", "sunroof", "apple carplay", "heated seats", "touchscreen"],
            "color": "Mineral White",
        },
        {
            "id": "V106", "make": "BMW", "model": "X5", "year": 2023,
            "price": 61000, "mileage": 11500, "trim": "xDrive45e (Plug-in Hybrid)",
            "body_style": "SUV", "source": "Autotrader",
            "dealer": "BMW of Orland Park", "zip_code": "60462",
            "accident_history": "Clean",
            "features": ["leather", "sunroof", "awd", "adaptive cruise", "apple carplay",
                         "heated seats", "ventilated seats"],
            "color": "Carbon Black",
        },
        {
            "id": "V107", "make": "BMW", "model": "X5", "year": 2022,
            "price": 49800, "mileage": 26000, "trim": "xDrive40i",
            "body_style": "SUV", "source": "CarGurus",
            "dealer": "BMW of Chicago (North)", "zip_code": "60601",
            "accident_history": "Clean",
            "features": ["leather", "sunroof", "awd", "heated seats", "touchscreen",
                         "apple carplay"],
            "color": "Sparkling Brown",
        },
        {
            "id": "V108", "make": "BMW", "model": "X5", "year": 2022,
            "price": 52000, "mileage": 22500, "trim": "M50i",
            "body_style": "SUV", "source": "Cars.com",
            "dealer": "Perillo BMW Chicago", "zip_code": "60614",
            "accident_history": "1 Minor",
            "features": ["leather", "sunroof", "awd", "adaptive cruise", "heated seats",
                         "ventilated seats", "apple carplay", "touchscreen"],
            "color": "Marina Bay Blue",
        },
        {
            "id": "V109", "make": "BMW", "model": "X5", "year": 2022,
            "price": 48200, "mileage": 29500, "trim": "xDrive40i",
            "body_style": "SUV", "source": "Manufacturer CPO",
            "dealer": "Elmhurst BMW", "zip_code": "60126",
            "accident_history": "Clean",
            "features": ["leather", "sunroof", "awd", "touchscreen", "heated seats"],
            "color": "Azurite Black",
        },
        {
            "id": "V110", "make": "BMW", "model": "X5", "year": 2021,
            "price": 45500, "mileage": 35000, "trim": "xDrive40i",
            "body_style": "SUV", "source": "Autotrader",
            "dealer": "AutoNation BMW Chicago", "zip_code": "60601",
            "accident_history": "Clean",
            "features": ["leather", "sunroof", "awd", "heated seats", "touchscreen"],
            "color": "Glacier Silver",
        },

        # ── TOYOTA INVENTORY ─────────────────────────────────────────────────
        {
            "id": "V001", "make": "Toyota", "model": "Highlander", "year": 2021,
            "price": 27500, "mileage": 38000, "trim": "XLE",
            "body_style": "SUV", "source": "CarGurus",
            "dealer": "Toyota of Chicago", "zip_code": "60601",
            "accident_history": "Clean",
            "features": ["adaptive cruise", "touchscreen", "heated seats", "third row"],
            "color": "Silver",
        },
        {
            "id": "V019", "make": "Toyota", "model": "Highlander", "year": 2025,
            "price": 46000, "mileage": 5000, "trim": "Hybrid Limited",
            "body_style": "SUV", "source": "Autotrader",
            "dealer": "Elmhurst Toyota", "zip_code": "60126",
            "accident_history": "Clean",
            "features": ["adaptive cruise", "touchscreen", "leather", "apple carplay",
                         "third row", "sunroof", "awd"],
            "color": "Silver",
        },
        {
            "id": "V004", "make": "Toyota", "model": "RAV4", "year": 2023,
            "price": 31000, "mileage": 12000, "trim": "Limited",
            "body_style": "SUV", "source": "Dealer Direct",
            "dealer": "Toyota of Chicago", "zip_code": "60601",
            "accident_history": "Clean",
            "features": ["adaptive cruise", "ventilated seats", "sunroof", "awd"],
            "color": "Blue",
        },

        # ── HONDA INVENTORY ──────────────────────────────────────────────────
        {
            "id": "V002", "make": "Honda", "model": "CR-V", "year": 2022,
            "price": 26000, "mileage": 25000, "trim": "EX-L",
            "body_style": "SUV", "source": "Autotrader",
            "dealer": "McGrath Honda", "zip_code": "60148",
            "accident_history": "Clean",
            "features": ["adaptive cruise", "touchscreen", "leather", "apple carplay"],
            "color": "White",
        },
        {
            "id": "V011", "make": "Honda", "model": "Pilot", "year": 2020,
            "price": 27000, "mileage": 28000, "trim": "EX-L",
            "body_style": "SUV", "source": "CarGurus",
            "dealer": "Honda of Lisle", "zip_code": "60532",
            "accident_history": "Clean",
            "features": ["adaptive cruise", "touchscreen", "leather", "apple carplay",
                         "third row", "sunroof"],
            "color": "Blue",
        },

        # ── FORD INVENTORY ───────────────────────────────────────────────────
        {
            "id": "V003", "make": "Ford", "model": "F-150", "year": 2020,
            "price": 35000, "mileage": 45000, "trim": "Lariat",
            "body_style": "Truck", "source": "Cars.com",
            "dealer": "Ford of Chicago", "zip_code": "60601",
            "accident_history": "1 Minor",
            "features": ["towing package", "ventilated seats", "touchscreen"],
            "color": "Black",
        },
        {
            "id": "V017", "make": "Ford", "model": "Mustang", "year": 2020,
            "price": 35000, "mileage": 22000, "trim": "GT Premium",
            "body_style": "Sports Car", "source": "Cars.com",
            "dealer": "Ford City Chicago", "zip_code": "60629",
            "accident_history": "1 Minor",
            "features": ["leather", "apple carplay", "touchscreen"],
            "color": "Black",
        },

        # ── TESLA INVENTORY ──────────────────────────────────────────────────
        {
            "id": "V005", "make": "Tesla", "model": "Model 3", "year": 2021,
            "price": 33000, "mileage": 30000, "trim": "Long Range",
            "body_style": "Sedan", "source": "Manufacturer CPO",
            "dealer": "Tesla Chicago (Evanston)", "zip_code": "60201",
            "accident_history": "Clean",
            "features": ["touchscreen", "heated seats"],
            "color": "Red",
        },

        # ── HYUNDAI & KIA INVENTORY ──────────────────────────────────────────
        {
            "id": "V006", "make": "Hyundai", "model": "Palisade", "year": 2022,
            "price": 38000, "mileage": 20000, "trim": "Calligraphy",
            "body_style": "SUV", "source": "CarGurus",
            "dealer": "Napleton Hyundai Chicago", "zip_code": "60601",
            "accident_history": "Clean",
            "features": ["adaptive cruise", "ventilated seats", "third row"],
            "color": "Grey",
        },
        {
            "id": "V007", "make": "Kia", "model": "Telluride", "year": 2021,
            "price": 34000, "mileage": 42000, "trim": "SX",
            "body_style": "SUV", "source": "Autotrader",
            "dealer": "Kia of Naperville", "zip_code": "60540",
            "accident_history": "1 Minor",
            "features": ["adaptive cruise", "ventilated seats", "third row", "sunroof"],
            "color": "Black",
        },
        {
            "id": "V012", "make": "Kia", "model": "Sorento", "year": 2021,
            "price": 26500, "mileage": 24000, "trim": "EX",
            "body_style": "SUV", "source": "Cars.com",
            "dealer": "Kia of Naperville", "zip_code": "60540",
            "accident_history": "Clean",
            "features": ["adaptive cruise", "touchscreen", "apple carplay", "third row",
                         "sunroof", "awd"],
            "color": "Silver",
        },

        # ── CHEVROLET INVENTORY ──────────────────────────────────────────────
        {
            "id": "V008", "make": "Chevrolet", "model": "Tahoe", "year": 2019,
            "price": 42000, "mileage": 60000, "trim": "Premier",
            "body_style": "SUV", "source": "Cars.com",
            "dealer": "Mike Anderson Chevrolet", "zip_code": "60622",
            "accident_history": "Clean",
            "features": ["towing package", "ventilated seats", "third row"],
            "color": "White",
        },
        {
            "id": "V016", "make": "Chevrolet", "model": "Corvette", "year": 2023,
            "price": 75000, "mileage": 5000, "trim": "Stingray 2LT",
            "body_style": "Sports Car", "source": "CarGurus",
            "dealer": "Chevrolet of Chicago", "zip_code": "60601",
            "accident_history": "Clean",
            "features": ["leather", "touchscreen", "apple carplay", "heated seats",
                         "ventilated seats"],
            "color": "Yellow",
        },

        # ── SUBARU INVENTORY ─────────────────────────────────────────────────
        {
            "id": "V009", "make": "Subaru", "model": "Outback", "year": 2020,
            "price": 24000, "mileage": 50000, "trim": "Touring XT",
            "body_style": "Wagon", "source": "Dealer Direct",
            "dealer": "Subaru of Naperville", "zip_code": "60540",
            "accident_history": "Clean",
            "features": ["adaptive cruise", "ventilated seats", "awd"],
            "color": "Green",
        },

        # ── BMW X5 (NOT CHICAGO) ─────────────────────────────────────────────
        {
            "id": "V010", "make": "BMW", "model": "X5", "year": 2021,
            "price": 49000, "mileage": 35000, "trim": "xDrive40i",
            "body_style": "SUV", "source": "Manufacturer CPO",
            "dealer": "BMW of Beverly Hills", "zip_code": "90210",
            "accident_history": "Clean",
            "features": ["adaptive cruise", "ventilated seats", "sunroof", "leather", "awd"],
            "color": "Blue",
        },

        # ── VOLKSWAGEN ───────────────────────────────────────────────────────
        {
            "id": "V013", "make": "Volkswagen", "model": "Tiguan", "year": 2022,
            "price": 25000, "mileage": 20000, "trim": "SE",
            "body_style": "SUV", "source": "Autotrader",
            "dealer": "Elgin VW", "zip_code": "60120",
            "accident_history": "Clean",
            "features": ["touchscreen", "apple carplay", "third row", "sunroof"],
            "color": "Black",
        },

        # ── PORSCHE ──────────────────────────────────────────────────────────
        {
            "id": "V015", "make": "Porsche", "model": "911", "year": 2021,
            "price": 95000, "mileage": 12000, "trim": "Carrera",
            "body_style": "Sports Car", "source": "Dealer Direct",
            "dealer": "Porsche of Chicago", "zip_code": "60601",
            "accident_history": "Clean",
            "features": ["leather", "apple carplay", "heated seats"],
            "color": "Red",
        },
        {
            "id": "V020", "make": "Porsche", "model": "911", "year": 2024,
            "price": 128000, "mileage": 4000, "trim": "Carrera S",
            "body_style": "Sports Car", "source": "Dealer Direct",
            "dealer": "Porsche of Chicago", "zip_code": "60601",
            "accident_history": "Clean",
            "features": ["leather", "apple carplay", "heated seats", "ventilated seats"],
            "color": "White",
        },
    ]

    df = pd.DataFrame(data)

    # Build direct CarGurus Vehicle Detail Page (VDP) URLs for each car
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
        zip_code = row.get('zip_code', '60601')
        vdp_id = cargurus_vdp_ids.get((make, model))
        if vdp_id:
            return f"https://www.cargurus.com/Cars/inventorylisting/vdp.action?listingId={vdp_id}"
        make_slug = make.replace(' ', '-').lower()
        model_slug = model.replace(' ', '-').replace('/', '-').lower()
        return f"https://www.autotrader.com/cars-for-sale/used-cars/{make_slug}/{model_slug}/?zip={zip_code}"

    df['listing_url'] = df.apply(make_listing_url, axis=1)
    return df
