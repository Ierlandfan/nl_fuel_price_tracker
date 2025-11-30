"""Dutch towns/cities with coordinates and postcodes."""

DUTCH_TOWNS = {
    # Noord-Holland
    "Amsterdam": {"lat": 52.3676, "lon": 4.9041, "province": "Noord-Holland", "postcode": "1012"},
    "Haarlem": {"lat": 52.3874, "lon": 4.6462, "province": "Noord-Holland", "postcode": "2011"},
    "Hoorn": {"lat": 52.6425, "lon": 5.0597, "province": "Noord-Holland", "postcode": "1621"},
    "Alkmaar": {"lat": 52.6318, "lon": 4.7516, "province": "Noord-Holland", "postcode": "1811"},
    "Zaandam": {"lat": 52.4389, "lon": 4.8261, "province": "Noord-Holland", "postcode": "1506"},
    "Purmerend": {"lat": 52.5050, "lon": 4.9592, "province": "Noord-Holland", "postcode": "1441"},
    
    # Zuid-Holland
    "Rotterdam": {"lat": 51.9225, "lon": 4.4792, "province": "Zuid-Holland", "postcode": "3011"},
    "Den Haag": {"lat": 52.0705, "lon": 4.3007, "province": "Zuid-Holland", "postcode": "2511"},
    "Leiden": {"lat": 52.1601, "lon": 4.4970, "province": "Zuid-Holland", "postcode": "2311"},
    "Delft": {"lat": 52.0116, "lon": 4.3571, "province": "Zuid-Holland", "postcode": "2611"},
    "Dordrecht": {"lat": 51.8133, "lon": 4.6900, "province": "Zuid-Holland", "postcode": "3311"},
    "Zoetermeer": {"lat": 52.0575, "lon": 4.4937, "province": "Zuid-Holland", "postcode": "2711"},
    
    # Utrecht
    "Utrecht": {"lat": 52.0907, "lon": 5.1214, "province": "Utrecht", "postcode": "3511"},
    "Amersfoort": {"lat": 52.1561, "lon": 5.3878, "province": "Utrecht", "postcode": "3811"},
    "Nieuwegein": {"lat": 52.0293, "lon": 5.0939, "province": "Utrecht", "postcode": "3431"},
    "Veenendaal": {"lat": 52.0283, "lon": 5.5553, "province": "Utrecht", "postcode": "3901"},
    
    # Gelderland
    "Arnhem": {"lat": 51.9851, "lon": 5.8987, "province": "Gelderland", "postcode": "6811"},
    "Nijmegen": {"lat": 51.8426, "lon": 5.8528, "province": "Gelderland", "postcode": "6511"},
    "Apeldoorn": {"lat": 52.2112, "lon": 5.9699, "province": "Gelderland", "postcode": "7311"},
    "Ede": {"lat": 52.0409, "lon": 5.6574, "province": "Gelderland", "postcode": "6711"},
    "Wageningen": {"lat": 51.9692, "lon": 5.6654, "province": "Gelderland", "postcode": "6701"},
    
    # Noord-Brabant
    "Eindhoven": {"lat": 51.4416, "lon": 5.4697, "province": "Noord-Brabant", "postcode": "5611"},
    "Tilburg": {"lat": 51.5555, "lon": 5.0913, "province": "Noord-Brabant", "postcode": "5011"},
    "'s-Hertogenbosch": {"lat": 51.6978, "lon": 5.3037, "province": "Noord-Brabant", "postcode": "5211"},
    "Breda": {"lat": 51.5719, "lon": 4.7683, "province": "Noord-Brabant", "postcode": "4811"},
    "Helmond": {"lat": 51.4814, "lon": 5.6559, "province": "Noord-Brabant", "postcode": "5701"},
    
    # Limburg
    "Maastricht": {"lat": 50.8514, "lon": 5.6909, "province": "Limburg", "postcode": "6211"},
    "Heerlen": {"lat": 50.8872, "lon": 5.9807, "province": "Limburg", "postcode": "6411"},
    "Venlo": {"lat": 51.3704, "lon": 6.1724, "province": "Limburg", "postcode": "5911"},
    "Roermond": {"lat": 51.1942, "lon": 5.9876, "province": "Limburg", "postcode": "6041"},
    
    # Overijssel
    "Enschede": {"lat": 52.2215, "lon": 6.8937, "province": "Overijssel", "postcode": "7511"},
    "Zwolle": {"lat": 52.5168, "lon": 6.0830, "province": "Overijssel", "postcode": "8011"},
    "Almelo": {"lat": 52.3570, "lon": 6.6627, "province": "Overijssel", "postcode": "7601"},
    "Deventer": {"lat": 52.2551, "lon": 6.1636, "province": "Overijssel", "postcode": "7411"},
    
    # Flevoland
    "Almere": {"lat": 52.3508, "lon": 5.2647, "province": "Flevoland", "postcode": "1311"},
    "Lelystad": {"lat": 52.5084, "lon": 5.4750, "province": "Flevoland", "postcode": "8232"},
    
    # Groningen
    "Groningen": {"lat": 53.2194, "lon": 6.5665, "province": "Groningen", "postcode": "9711"},
    
    # Friesland
    "Leeuwarden": {"lat": 53.2012, "lon": 5.7999, "province": "Friesland", "postcode": "8911"},
    "Sneek": {"lat": 53.0333, "lon": 5.6583, "province": "Friesland", "postcode": "8601"},
    
    # Drenthe
    "Assen": {"lat": 52.9961, "lon": 6.5624, "province": "Drenthe", "postcode": "9401"},
    "Emmen": {"lat": 52.7891, "lon": 6.8970, "province": "Drenthe", "postcode": "7811"},
    
    # Zeeland
    "Middelburg": {"lat": 51.4988, "lon": 3.6109, "province": "Zeeland", "postcode": "4331"},
    "Vlissingen": {"lat": 51.4427, "lon": 3.5734, "province": "Zeeland", "postcode": "4381"},
}

# Postcode to town mapping (for reverse lookup)
POSTCODE_TO_TOWN = {}
for town, data in DUTCH_TOWNS.items():
    postcode = data["postcode"]
    POSTCODE_TO_TOWN[postcode] = town
    # Also add without last digit for broader matching
    POSTCODE_TO_TOWN[postcode[:3]] = town


def get_town_options() -> list[dict[str, str]]:
    """Get sorted list of towns for selector with postcode."""
    towns = []
    for town, data in sorted(DUTCH_TOWNS.items()):
        towns.append({
            "value": town,
            "label": f"{data['postcode']} - {town} ({data['province']})"
        })
    return towns


def get_town_coords(town: str) -> tuple[float, float] | None:
    """Get coordinates for a town."""
    if town in DUTCH_TOWNS:
        data = DUTCH_TOWNS[town]
        return (data["lat"], data["lon"])
    return None


def get_town_by_postcode(postcode: str) -> str | None:
    """Get town name by postcode (4-digit format like 1621)."""
    # Try exact match first
    postcode_clean = postcode.strip().replace(" ", "")[:4]
    
    if postcode_clean in POSTCODE_TO_TOWN:
        return POSTCODE_TO_TOWN[postcode_clean]
    
    # Try 3-digit match
    if len(postcode_clean) >= 3:
        postcode_3 = postcode_clean[:3]
        if postcode_3 in POSTCODE_TO_TOWN:
            return POSTCODE_TO_TOWN[postcode_3]
    
    return None


def search_town_or_postcode(query: str) -> list[dict[str, str]]:
    """Search towns by name or postcode."""
    query_lower = query.lower().strip()
    results = []
    
    for town, data in DUTCH_TOWNS.items():
        # Match by town name
        if query_lower in town.lower():
            results.append({
                "value": town,
                "label": f"{data['postcode']} - {town} ({data['province']})",
                "match": "name"
            })
        # Match by postcode
        elif query_lower in data["postcode"].lower():
            results.append({
                "value": town,
                "label": f"{data['postcode']} - {town} ({data['province']})",
                "match": "postcode"
            })
        # Match by province
        elif query_lower in data["province"].lower():
            results.append({
                "value": town,
                "label": f"{data['postcode']} - {town} ({data['province']})",
                "match": "province"
            })
    
    return results[:20]  # Limit to 20 results


def get_town_info(town: str) -> dict[str, any] | None:
    """Get full info for a town."""
    if town in DUTCH_TOWNS:
        data = DUTCH_TOWNS[town]
        return {
            "town": town,
            "postcode": data["postcode"],
            "province": data["province"],
            "latitude": data["lat"],
            "longitude": data["lon"],
        }
    return None
