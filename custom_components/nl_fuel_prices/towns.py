"""Dutch towns/cities with coordinates."""

DUTCH_TOWNS = {
    # Noord-Holland
    "Amsterdam": {"lat": 52.3676, "lon": 4.9041, "province": "Noord-Holland"},
    "Haarlem": {"lat": 52.3874, "lon": 4.6462, "province": "Noord-Holland"},
    "Hoorn": {"lat": 52.6425, "lon": 5.0597, "province": "Noord-Holland"},
    "Alkmaar": {"lat": 52.6318, "lon": 4.7516, "province": "Noord-Holland"},
    "Zaandam": {"lat": 52.4389, "lon": 4.8261, "province": "Noord-Holland"},
    "Purmerend": {"lat": 52.5050, "lon": 4.9592, "province": "Noord-Holland"},
    
    # Zuid-Holland
    "Rotterdam": {"lat": 51.9225, "lon": 4.4792, "province": "Zuid-Holland"},
    "Den Haag": {"lat": 52.0705, "lon": 4.3007, "province": "Zuid-Holland"},
    "Leiden": {"lat": 52.1601, "lon": 4.4970, "province": "Zuid-Holland"},
    "Delft": {"lat": 52.0116, "lon": 4.3571, "province": "Zuid-Holland"},
    "Dordrecht": {"lat": 51.8133, "lon": 4.6900, "province": "Zuid-Holland"},
    "Zoetermeer": {"lat": 52.0575, "lon": 4.4937, "province": "Zuid-Holland"},
    
    # Utrecht
    "Utrecht": {"lat": 52.0907, "lon": 5.1214, "province": "Utrecht"},
    "Amersfoort": {"lat": 52.1561, "lon": 5.3878, "province": "Utrecht"},
    "Nieuwegein": {"lat": 52.0293, "lon": 5.0939, "province": "Utrecht"},
    "Veenendaal": {"lat": 52.0283, "lon": 5.5553, "province": "Utrecht"},
    
    # Gelderland
    "Arnhem": {"lat": 51.9851, "lon": 5.8987, "province": "Gelderland"},
    "Nijmegen": {"lat": 51.8426, "lon": 5.8528, "province": "Gelderland"},
    "Apeldoorn": {"lat": 52.2112, "lon": 5.9699, "province": "Gelderland"},
    "Ede": {"lat": 52.0409, "lon": 5.6574, "province": "Gelderland"},
    "Wageningen": {"lat": 51.9692, "lon": 5.6654, "province": "Gelderland"},
    
    # Noord-Brabant
    "Eindhoven": {"lat": 51.4416, "lon": 5.4697, "province": "Noord-Brabant"},
    "Tilburg": {"lat": 51.5555, "lon": 5.0913, "province": "Noord-Brabant"},
    "'s-Hertogenbosch": {"lat": 51.6978, "lon": 5.3037, "province": "Noord-Brabant"},
    "Breda": {"lat": 51.5719, "lon": 4.7683, "province": "Noord-Brabant"},
    "Helmond": {"lat": 51.4814, "lon": 5.6559, "province": "Noord-Brabant"},
    
    # Limburg
    "Maastricht": {"lat": 50.8514, "lon": 5.6909, "province": "Limburg"},
    "Heerlen": {"lat": 50.8872, "lon": 5.9807, "province": "Limburg"},
    "Venlo": {"lat": 51.3704, "lon": 6.1724, "province": "Limburg"},
    "Roermond": {"lat": 51.1942, "lon": 5.9876, "province": "Limburg"},
    
    # Overijssel
    "Enschede": {"lat": 52.2215, "lon": 6.8937, "province": "Overijssel"},
    "Zwolle": {"lat": 52.5168, "lon": 6.0830, "province": "Overijssel"},
    "Almelo": {"lat": 52.3570, "lon": 6.6627, "province": "Overijssel"},
    "Deventer": {"lat": 52.2551, "lon": 6.1636, "province": "Overijssel"},
    
    # Flevoland
    "Almere": {"lat": 52.3508, "lon": 5.2647, "province": "Flevoland"},
    "Lelystad": {"lat": 52.5084, "lon": 5.4750, "province": "Flevoland"},
    
    # Groningen
    "Groningen": {"lat": 53.2194, "lon": 6.5665, "province": "Groningen"},
    
    # Friesland
    "Leeuwarden": {"lat": 53.2012, "lon": 5.7999, "province": "Friesland"},
    "Sneek": {"lat": 53.0333, "lon": 5.6583, "province": "Friesland"},
    
    # Drenthe
    "Assen": {"lat": 52.9961, "lon": 6.5624, "province": "Drenthe"},
    "Emmen": {"lat": 52.7891, "lon": 6.8970, "province": "Drenthe"},
    
    # Zeeland
    "Middelburg": {"lat": 51.4988, "lon": 3.6109, "province": "Zeeland"},
    "Vlissingen": {"lat": 51.4427, "lon": 3.5734, "province": "Zeeland"},
}


def get_town_options() -> list[dict[str, str]]:
    """Get sorted list of towns for selector."""
    towns = []
    for town, data in sorted(DUTCH_TOWNS.items()):
        towns.append({
            "value": town,
            "label": f"{town} ({data['province']})"
        })
    return towns


def get_town_coords(town: str) -> tuple[float, float] | None:
    """Get coordinates for a town."""
    if town in DUTCH_TOWNS:
        data = DUTCH_TOWNS[town]
        return (data["lat"], data["lon"])
    return None
