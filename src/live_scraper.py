"""
Live Car Search Scraper
Queries CarGurus with the correct location zip code and returns real listings.
Also builds pre-filtered search URLs for Autotrader and Cars.com.
"""
import re
import gzip
import urllib.request
import urllib.parse


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

# CarGurus model entity IDs — needed for model-level filtering
CARGURUS_ENTITY_IDS = {
    "X5": "d393", "X3": "d390", "3 Series": "d371", "5 Series": "d376",
    "Highlander": "d298", "RAV4": "d306", "Camry": "d167", "Sienna": "d295",
    "4Runner": "d303", "Tacoma": "d292", "Tundra": "d286",
    "CR-V": "d589", "Pilot": "d599", "Odyssey": "d597", "Accord": "d660", "Civic": "d663",
    "F-150": "d337", "Explorer": "d681", "Mustang": "d2", "Escape": "d682", "Bronco": "d3100",
    "Model 3": "d2475", "Model Y": "d2576", "Model S": "d1703", "Model X": "d1704",
    "Palisade": "d2847", "Tucson": "d2010", "Santa Fe": "d658", "Sonata": "d641",
    "Telluride": "d2757", "Sorento": "d620", "Sportage": "d2010",
    "Tahoe": "d637", "Corvette": "d1", "Equinox": "d680", "Traverse": "d938",
    "Silverado": "d634", "Colorado": "d636",
    "Outback": "d380", "Forester": "d383", "Crosstrek": "d1752", "WRX": "d1750",
    "Tiguan": "d1028", "Atlas": "d2310", "Jetta": "d1027", "Passat": "d1026",
    "911": "d404", "Cayenne": "d1180", "Macan": "d1963",
    "RX": "d429", "NX": "d2281",
    "GLE": "d1558", "C-Class": "d531", "E-Class": "d530",
    "Q5": "d474", "A4": "d470",
}

DEAL_RATING_MAP = {
    "GREAT_PRICE": "🟢 Great Price",
    "GOOD_PRICE": "🔵 Good Price",
    "FAIR_PRICE": "🟡 Fair Price",
    "HIGH_PRICE": "🟠 High Price",
    "OVERPRICED": "🔴 Overpriced",
}


def _fetch(url, timeout=12):
    """Fetches URL, handles gzip decompression. Returns HTML string or None."""
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
        try:
            return gzip.decompress(raw).decode("utf-8", errors="replace")
        except Exception:
            return raw.decode("utf-8", errors="replace")
    except Exception as e:
        print(f"[LiveSearch] HTTP error: {e}")
        return None


def _extract_features(text):
    """Extracts known feature keywords from a description or title string."""
    features = []
    tl = text.lower()
    checks = {
        "leather": ["leather", "leatherette"],
        "sunroof": ["sunroof", "moonroof", "panoramic"],
        "adaptive cruise": ["adaptive cruise", "active cruise"],
        "apple carplay": ["carplay", "apple carplay"],
        "heated seats": ["heated seat"],
        "ventilated seats": ["ventilated seat", "cooled seat"],
        "awd": ["awd", "all-wheel", "xdrive", "x-drive", "4matic", "quattro"],
        "touchscreen": ["touchscreen", "navigation", "infotainment"],
    }
    for feat, kws in checks.items():
        if any(kw in tl for kw in kws):
            features.append(feat)
    return features


def _parse_cargurus_html(html, make, model, zip_code):
    """
    Parses CarGurus search HTML by splitting on listingId boundaries so each
    chunk contains exactly one listing's fields — correctly aligned.
    """
    if not html:
        return []

    # Split HTML on each listing boundary
    chunks = re.split(r'(?="listingId":\d{8,10})', html)
    listings = []

    for chunk in chunks:
        lid_m = re.search(r'"listingId":(\d{8,10})', chunk)
        if not lid_m:
            continue
        lid = lid_m.group(1)

        def field(pat, default=""):
            m = re.search(pat, chunk)
            return m.group(1) if m else default

        car_year    = int(field(r'"year":(\d{4})', "0") or 0)
        car_make    = field(r'"make":"([^"]+)"', make)
        car_model   = field(r'"model":"([^"]+)"', model)
        car_price   = int(field(r'"price":(\d{4,6})', "0") or 0)
        car_mileage = int(field(r'"mileage":(\d+)', "0") or 0)
        car_trim    = field(r'"trim":"([^"]+)"')
        car_city    = field(r'"cityRegion":"([^"]+)"')
        car_color   = field(r'"exteriorColor":"([^"]+)"')
        car_image   = field(r'"imageUrl":"(https://static\.cargurus\.com/[^"]+)"')
        car_rating  = field(r'"dealFinderRating":"([^"]+)"')
        car_title   = field(r'"listingTitle":"([^"]+)"')

        if not car_year or not car_price:
            continue

        vdp_url  = f"https://www.cargurus.com/Cars/inventorylisting/vdp.action?listingId={lid}"
        features = _extract_features(f"{car_trim} {car_title}")

        listings.append({
            "id":               f"CG_{lid}",
            "make":             car_make,
            "model":            car_model,
            "year":             car_year,
            "price":            car_price,
            "mileage":          car_mileage,
            "trim":             car_trim,
            "body_style":       "SUV",
            "source":           "CarGurus",
            "dealer":           car_city,
            "zip_code":         zip_code,
            "accident_history": "Unknown",
            "features":         features,
            "color":            car_color,
            "image_url":        car_image,
            "listing_url":      vdp_url,
            "deal_badge":       DEAL_RATING_MAP.get(car_rating, ""),
        })

    return listings


def search_cargurus(params):
    """
    Builds CarGurus URL and fetches live listings for the given params.
    Returns (list_of_cars, search_url).
    """
    make     = params.get("make", "")
    model    = params.get("model", "")
    zip_code = params.get("zip_code") or "10001"
    min_year = params.get("min_year")
    max_year = params.get("max_year")
    mileage  = params.get("mileage")
    budget   = params.get("budget")

    entity_id  = CARGURUS_ENTITY_IDS.get(model, "")
    make_slug  = make.replace(" ", "-")
    model_slug = model.replace(" ", "-").replace("/", "-")

    if entity_id and make and model:
        base_path = f"/Cars/l-Used-{make_slug}-{model_slug}-{entity_id}"
    elif make:
        base_path = f"/Cars/l-Used-{make_slug}"
    else:
        base_path = "/Cars/l-Used-Cars"

    qp = {"zip": zip_code, "distance": "50", "sortType": "PRICE", "sortDir": "ASC", "showNegotiable": "false"}
    if min_year:  qp["startYear"]  = str(min_year)
    if max_year:  qp["endYear"]    = str(max_year)
    if mileage:   qp["maxMileage"] = str(mileage)
    if budget:    qp["maxPrice"]   = str(budget)
    if entity_id: qp["entitySelectingHelper.selectedEntity"] = entity_id

    url = f"https://www.cargurus.com{base_path}?{urllib.parse.urlencode(qp)}"
    print(f"[CarGurus] GET {url[:120]}")

    html     = _fetch(url)
    listings = _parse_cargurus_html(html, make, model, zip_code) if html else []

    # Client-side year/mileage/budget guard
    if min_year: listings = [r for r in listings if not r["year"] or r["year"] >= min_year]
    if max_year: listings = [r for r in listings if not r["year"] or r["year"] <= max_year]
    if mileage:  listings = [r for r in listings if not r["mileage"] or r["mileage"] <= mileage]
    if budget:   listings = [r for r in listings if not r["price"]   or r["price"]   <= budget]

    print(f"[CarGurus] {len(listings)} listings returned for zip={zip_code}")
    return listings[:8], url


def _autotrader_url(params):
    make  = params.get("make", ""); model = params.get("model", "")
    zip_  = params.get("zip_code") or "10001"
    qp    = {"zip": zip_, "searchRadius": "50"}
    if params.get("min_year"): qp["startYear"]  = str(params["min_year"])
    if params.get("max_year"): qp["endYear"]    = str(params["max_year"])
    if params.get("mileage"):  qp["maxMileage"] = str(params["mileage"])
    if params.get("budget"):   qp["maxPrice"]   = str(params["budget"])
    mk = make.lower().replace(" ", "-"); md = model.lower().replace(" ", "-").replace("/","")
    path = f"/cars-for-sale/used-cars/{mk}/{md}/" if make and model else f"/cars-for-sale/used-cars/{mk}/" if make else "/cars-for-sale/used-cars/"
    return f"https://www.autotrader.com{path}?{urllib.parse.urlencode(qp)}"


def _cars_com_url(params):
    make  = params.get("make", ""); model = params.get("model", "")
    zip_  = params.get("zip_code") or "10001"
    qp    = {"stock_type": "used", "zip": zip_, "maximum_distance": "50"}
    if params.get("min_year"): qp["year_min"]    = str(params["min_year"])
    if params.get("max_year"): qp["year_max"]    = str(params["max_year"])
    if params.get("mileage"):  qp["mileage_max"] = str(params["mileage"])
    if params.get("budget"):   qp["price_max"]   = str(params["budget"])
    mk = make.lower().replace(" ", "-"); md = model.lower().replace(" ", "-").replace("/","")
    if make and model:
        return f"https://www.cars.com/shopping/{mk}-{md}/?{urllib.parse.urlencode(qp)}"
    return f"https://www.cars.com/shopping/results/?{urllib.parse.urlencode(qp)}"


def live_search(params):
    """
    Entry point: runs a live CarGurus search for the given parsed params.
    Returns:
        {
          "listings":       list of car dicts (real, from CarGurus),
          "platform_links": [(label, url), ...] for click-through,
          "cargurus_url":   str  (the exact search URL used)
        }
    """
    listings, cg_url = search_cargurus(params)

    platform_links = [
        ("🔍 CarGurus Live Search ↗", cg_url),
        ("🔍 Autotrader Live Search ↗", _autotrader_url(params)),
        ("🔍 Cars.com Live Search ↗",  _cars_com_url(params)),
    ]

    return {
        "listings":       listings,
        "platform_links": platform_links,
        "cargurus_url":   cg_url,
    }
