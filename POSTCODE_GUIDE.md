# 📮 Postcode & Town Lookup Guide

## Dutch Postcode System

Dutch postcodes (postcodes) consist of **4 digits + 2 letters** (e.g., `1621 AB`).

For this integration, we use the **first 4 digits** to identify towns/cities.

---

## How to Find Your Postcode

### Option 1: You Know Your Postcode
If you know your postcode (e.g., `1621`), just select it from the dropdown:
- Dropdown shows: **"1621 - Hoorn (Noord-Holland)"**
- Coordinates automatically filled
- Radius set (e.g., 10 km)

### Option 2: You Know Your Town
Search by town name:
- Type: "Hoorn"
- Shows: **"1621 - Hoorn (Noord-Holland)"**
- Select and configure radius

### Option 3: Look Up Your Postcode

**Online:**
1. Visit: https://www.postcode.nl/
2. Enter your address
3. Get your postcode (e.g., `1621 AB`)
4. Use first 4 digits: `1621`

**Google Maps:**
1. Search your address in Google Maps
2. Your postcode appears in the address
3. Use first 4 digits

---

## Available Towns & Postcodes

### Noord-Holland
- **1012** - Amsterdam
- **2011** - Haarlem
- **1621** - Hoorn ✅
- **1811** - Alkmaar
- **1506** - Zaandam
- **1441** - Purmerend

### Zuid-Holland
- **3011** - Rotterdam
- **2511** - Den Haag
- **2311** - Leiden
- **2611** - Delft
- **3311** - Dordrecht
- **2711** - Zoetermeer

### Utrecht
- **3511** - Utrecht
- **3811** - Amersfoort
- **3431** - Nieuwegein
- **3901** - Veenendaal

### Gelderland
- **6811** - Arnhem
- **6511** - Nijmegen
- **7311** - Apeldoorn
- **6711** - Ede
- **6701** - Wageningen

### Noord-Brabant
- **5611** - Eindhoven
- **5011** - Tilburg
- **5211** - 's-Hertogenbosch
- **4811** - Breda
- **5701** - Helmond

### Limburg
- **6211** - Maastricht
- **6411** - Heerlen
- **5911** - Venlo
- **6041** - Roermond

### Overijssel
- **7511** - Enschede
- **8011** - Zwolle
- **7601** - Almelo
- **7411** - Deventer

### Flevoland
- **1311** - Almere
- **8232** - Lelystad

### Groningen
- **9711** - Groningen

### Friesland
- **8911** - Leeuwarden
- **8601** - Sneek

### Drenthe
- **9401** - Assen
- **7811** - Emmen

### Zeeland
- **4331** - Middelburg
- **4381** - Vlissingen

---

## Example: Setting Up for Hoorn

### Configuration
```yaml
Use Town Selector: ✅ Enabled
Town: 1621 - Hoorn (Noord-Holland)
Radius: 10 km
Fuel Type: Euro 95
```

### What Gets Stored
```yaml
location_name: "Hoorn"
latitude: 52.6425
longitude: 5.0597
town_postcode: "1621"
town_province: "Noord-Holland"
radius: 10
```

### Sensor Attributes
```yaml
sensor.fuel_euro95_hoorn:
  state: 1.839  # Cheapest price
  attributes:
    station_name: "Tango Hoorn"
    distance: 2.3
    location_postcode: "1621"  # Your search postcode
    location_province: "Noord-Holland"
```

---

## Why Postcodes?

### Easier for Dutch Users
- Everyone knows their postcode
- No need to look up coordinates
- More familiar than lat/lon

### Quick Search
- Type postcode: `1621` → Find Hoorn
- Type town: `Hoorn` → Find 1621
- Both work!

### Display Benefits
- Shows where you're searching
- Postcode visible in sensor attributes
- Province information included

---

## What If My Town Isn't Listed?

### Use Manual Coordinates
1. Toggle **"Use Town Selector"** to ❌ Off
2. Enter your coordinates manually
3. Find coordinates at: https://www.latlong.net/

### Or Use Nearest Town
1. Find nearest major town from the list
2. Adjust radius to include your area
3. Example: Live near Hoorn? Use `1621` with 15km radius

---

## Sensor Information Display

When viewing your sensor, you'll see:

```yaml
Fuel Euro 95 - Hoorn
State: €1.839/L
Attributes:
  - station_name: "Tango Hoorn"
  - station_address: "Stationsstraat 67, 1621 AB Hoorn"
  - distance: 2.3 km
  - location_postcode: "1621"
  - location_province: "Noord-Holland"
  - total_stations: 8
```

---

## Tips

1. **Radius Matters**: 
   - Small town? Use 15-20 km radius
   - Big city? 5-10 km sufficient

2. **Postcode Search**:
   - Dropdown shows: `postcode - town (province)`
   - Easy to scan and find

3. **Your Exact Address Not Needed**:
   - Town postcode is enough
   - Radius handles nearby areas

4. **Multiple Locations**:
   - Add separate integration for each location
   - Home: `1621 - Hoorn`
   - Work: `1012 - Amsterdam`

---

## Summary

| Format | Example | Result |
|--------|---------|--------|
| Postcode | `1621` | Hoorn (Noord-Holland) |
| Town Name | `Hoorn` | 1621 - Hoorn (Noord-Holland) |
| Province | `Noord-Holland` | Lists all towns in province |

**No coordinate lookup needed - just select your town or postcode!** 📮
