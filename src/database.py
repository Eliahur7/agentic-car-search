import pandas as pd
import random

def get_inventory():
    """
    Returns a simulated inventory of vehicles from multiple sources.
    """
    data = [
        {
            "id": "V001",
            "make": "Toyota",
            "model": "Highlander",
            "year": 2021,
            "price": 27500,
            "mileage": 38000,
            "trim": "XLE",
            "body_style": "SUV",
            "source": "CarGurus",
            "accident_history": "Clean",
            "features": ["adaptive cruise", "touchscreen", "heated seats", "third row seating"],
            "color": "Silver",
            "image_url": "https://images.unsplash.com/photo-1619682817481-e994891cd1f5?auto=format&fit=crop&w=400&q=80"
        },
        {
            "id": "V002",
            "make": "Honda",
            "model": "CR-V",
            "year": 2022,
            "price": 26000,
            "mileage": 25000,
            "trim": "EX-L",
            "body_style": "SUV",
            "source": "Autotrader",
            "accident_history": "Clean",
            "features": ["adaptive cruise", "touchscreen", "leather seats", "apple carplay"],
            "color": "White",
            "image_url": "https://images.unsplash.com/photo-1563720223185-11003d516935?auto=format&fit=crop&w=400&q=80"
        },
        {
            "id": "V003",
            "make": "Ford",
            "model": "F-150",
            "year": 2020,
            "price": 35000,
            "mileage": 45000,
            "trim": "Lariat",
            "body_style": "Truck",
            "source": "Cars.com",
            "accident_history": "1 Minor",
            "features": ["towing package", "ventilated seats", "touchscreen", "backup camera"],
            "color": "Black",
            "image_url": "https://images.unsplash.com/photo-1559416523-140ddc3d238c?auto=format&fit=crop&w=400&q=80"
        },
        {
            "id": "V004",
            "make": "Toyota",
            "model": "RAV4",
            "year": 2023,
            "price": 31000,
            "mileage": 12000,
            "trim": "Limited",
            "body_style": "SUV",
            "source": "Dealer Direct",
            "accident_history": "Clean",
            "features": ["adaptive cruise", "ventilated seats", "panoramic sunroof", "premium audio"],
            "color": "Blue",
            "image_url": "https://images.unsplash.com/photo-1621007947382-bb3c3994e3fd?auto=format&fit=crop&w=400&q=80"
        },
        {
            "id": "V005",
            "make": "Tesla",
            "model": "Model 3",
            "year": 2021,
            "price": 33000,
            "mileage": 30000,
            "trim": "Long Range",
            "body_style": "Sedan",
            "source": "Manufacturer CPO",
            "accident_history": "Clean",
            "features": ["autopilot", "touchscreen", "heated seats", "premium audio"],
            "color": "Red",
            "image_url": "https://images.unsplash.com/photo-1560958089-b8a1929cea89?auto=format&fit=crop&w=400&q=80"
        },
        {
            "id": "V006",
            "make": "Hyundai",
            "model": "Palisade",
            "year": 2022,
            "price": 38000,
            "mileage": 20000,
            "trim": "Calligraphy",
            "body_style": "SUV",
            "source": "CarGurus",
            "accident_history": "Clean",
            "features": ["adaptive cruise", "ventilated seats", "third row seating", "head-up display"],
            "color": "Grey",
            "image_url": "https://images.unsplash.com/photo-1633507421376-71d3ce880629?auto=format&fit=crop&w=400&q=80"
        },
        {
            "id": "V007",
            "make": "Kia",
            "model": "Telluride",
            "year": 2021,
            "price": 34000,
            "mileage": 42000,
            "trim": "SX",
            "body_style": "SUV",
            "source": "Autotrader",
            "accident_history": "1 Minor",
            "features": ["adaptive cruise", "ventilated seats", "third row seating", "sunroof"],
            "color": "Black",
            "image_url": "https://images.unsplash.com/photo-1609521263047-f8f205293f24?auto=format&fit=crop&w=400&q=80"
        },
        {
            "id": "V008",
            "make": "Chevrolet",
            "model": "Tahoe",
            "year": 2019,
            "price": 42000,
            "mileage": 60000,
            "trim": "Premier",
            "body_style": "SUV",
            "source": "Cars.com",
            "accident_history": "Clean",
            "features": ["towing package", "ventilated seats", "third row seating", "rear entertainment"],
            "color": "White",
            "image_url": "https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?auto=format&fit=crop&w=400&q=80"
        },
        {
            "id": "V009",
            "make": "Subaru",
            "model": "Outback",
            "year": 2020,
            "price": 24000,
            "mileage": 50000,
            "trim": "Touring XT",
            "body_style": "Wagon",
            "source": "Dealer Direct",
            "accident_history": "Clean",
            "features": ["adaptive cruise", "ventilated seats", "awd", "roof rails"],
            "color": "Green",
            "image_url": "https://images.unsplash.com/photo-1590362891991-f776e747a588?auto=format&fit=crop&w=400&q=80"
        },
        {
            "id": "V010",
            "make": "BMW",
            "model": "X5",
            "year": 2021,
            "price": 49000,
            "mileage": 35000,
            "trim": "xDrive40i",
            "body_style": "SUV",
            "source": "Manufacturer CPO",
            "accident_history": "Clean",
            "features": ["adaptive cruise", "ventilated seats", "panoramic sunroof", "premium audio", "awd"],
            "color": "Blue",
            "image_url": "https://images.unsplash.com/photo-1555215695-3004980ad54e?auto=format&fit=crop&w=400&q=80"
        },
        {
            "id": "V011",
            "make": "Honda",
            "model": "Pilot",
            "year": 2020,
            "price": 27000,
            "mileage": 28000,
            "trim": "EX-L",
            "body_style": "SUV",
            "source": "CarGurus",
            "accident_history": "Clean",
            "features": ["adaptive cruise", "touchscreen", "leather", "apple carplay", "third row", "sunroof"],
            "color": "Blue",
            "image_url": "https://images.unsplash.com/photo-1511527661048-7fe73d85e9a4?auto=format&fit=crop&w=400&q=80"
        },
        {
            "id": "V012",
            "make": "Kia",
            "model": "Sorento",
            "year": 2021,
            "price": 26500,
            "mileage": 24000,
            "trim": "EX",
            "body_style": "SUV",
            "source": "Cars.com",
            "accident_history": "Clean",
            "features": ["adaptive cruise", "touchscreen", "apple carplay", "third row", "sunroof", "awd"],
            "color": "Silver",
            "image_url": "https://images.unsplash.com/photo-1609521263047-f8f205293f24?auto=format&fit=crop&w=400&q=80"
        },
        {
            "id": "V013",
            "make": "Volkswagen",
            "model": "Tiguan",
            "year": 2022,
            "price": 25000,
            "mileage": 20000,
            "trim": "SE",
            "body_style": "SUV",
            "source": "Autotrader",
            "accident_history": "Clean",
            "features": ["touchscreen", "apple carplay", "third row", "sunroof"],
            "color": "Black",
            "image_url": "https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?auto=format&fit=crop&w=400&q=80"
        },
        {
            "id": "V014",
            "make": "Toyota",
            "model": "Highlander",
            "year": 2019,
            "price": 27500,
            "mileage": 29000,
            "trim": "XLE",
            "body_style": "SUV",
            "source": "Dealer Direct",
            "accident_history": "1 Minor",
            "features": ["touchscreen", "leather", "apple carplay", "third row", "sunroof", "awd"],
            "color": "White",
            "image_url": "https://images.unsplash.com/photo-1619682817481-e994891cd1f5?auto=format&fit=crop&w=400&q=80"
        },
        {
            "id": "V015",
            "make": "Porsche",
            "model": "911",
            "year": 2021,
            "price": 95000,
            "mileage": 12000,
            "trim": "Carrera",
            "body_style": "Sports Car",
            "source": "Dealer Direct",
            "accident_history": "Clean",
            "features": ["leather", "apple carplay", "heated seats"],
            "color": "Red",
            "image_url": "https://images.unsplash.com/photo-1503376712351-1f2a33503b87?auto=format&fit=crop&w=400&q=80"
        },
        {
            "id": "V016",
            "make": "Chevrolet",
            "model": "Corvette",
            "year": 2023,
            "price": 75000,
            "mileage": 5000,
            "trim": "Stingray 2LT",
            "body_style": "Sports Car",
            "source": "CarGurus",
            "accident_history": "Clean",
            "features": ["leather", "touchscreen", "apple carplay", "heated seats", "ventilated seats"],
            "color": "Yellow",
            "image_url": "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?auto=format&fit=crop&w=400&q=80"
        },
        {
            "id": "V017",
            "make": "Ford",
            "model": "Mustang",
            "year": 2020,
            "price": 35000,
            "mileage": 22000,
            "trim": "GT Premium",
            "body_style": "Sports Car",
            "source": "Cars.com",
            "accident_history": "1 Minor",
            "features": ["leather", "apple carplay", "touchscreen"],
            "color": "Black",
            "image_url": "https://images.unsplash.com/photo-1494976388531-d1058494cdd8?auto=format&fit=crop&w=400&q=80"
        }
    ]
    df = pd.DataFrame(data)
    
    # Generate a precise, deep-search listing URL per car based on its source
    def make_listing_url(row):
        make = row['make'].lower()
        # Normalize model: lowercase, replace spaces and slashes with hyphens
        model = row['model'].lower().replace(' ', '-').replace('/', '-').replace('.', '')
        year = row['year']
        price = row['price']
        mileage = row['mileage']
        source = row['source']

        if source == "CarGurus":
            # CarGurus search URL - filters by year, make, model, price, mileage
            return (
                f"https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action"
                f"?zip=&showNegotiable=false&sortDir=ASC&distance=200&sortType=PRICE"
                f"&startYear={year}&endYear={year}&maxPrice={price}&maxMileage={mileage}"
                f"&automotive_score_filter=0&make={row['make']}&model={row['model']}"
            )
        elif source == "Autotrader":
            return (
                f"https://www.autotrader.com/cars-for-sale/used-cars/{make}/{model}/"
                f"?startYear={year}&endYear={year}&maxMileage={mileage}&maxPrice={price}&numRecords=25"
            )
        elif source == "Cars.com":
            return (
                f"https://www.cars.com/shopping/{make}-{model}/"
                f"?maximum_mileage={mileage}&price_max={price}&year_max={year}&year_min={year}"
            )
        elif source == "Dealer Direct":
            # Route to Autotrader which has the clearest URL format
            return (
                f"https://www.autotrader.com/cars-for-sale/used-cars/{make}/{model}/"
                f"?startYear={year}&endYear={year}&maxMileage={mileage}&maxPrice={price}&numRecords=25"
            )
        elif source == "Manufacturer CPO":
            return (
                f"https://www.autotrader.com/cars-for-sale/certified-used-cars/{make}/{model}/"
                f"?startYear={year}&endYear={year}&maxMileage={mileage}&maxPrice={price}"
            )
        else:
            return (
                f"https://www.autotrader.com/cars-for-sale/used-cars/{make}/{model}/"
                f"?startYear={year}&endYear={year}&maxMileage={mileage}&maxPrice={price}"
            )
    
    df['listing_url'] = df.apply(make_listing_url, axis=1)
    return df
