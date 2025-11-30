# 🚀 Installation Guide - Dutch Fuel Prices

Complete step-by-step guide to install and configure the Dutch Fuel Prices integration in Home Assistant.

---

## 📋 Prerequisites

- Home Assistant **2024.11.0** or newer
- HACS (Home Assistant Community Store) installed
- Internet connection

---

## 🎯 Quick Install (Recommended)

### One-Click Installation

**Click this button** to add the repository to HACS:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Ierlandfan&repository=nl_fuel_price_tracker&category=integration)

**What happens**:
1. Opens your Home Assistant
2. Opens HACS
3. Pre-fills repository details
4. Click "Download" → Done!

---

## 📖 Manual Installation

### Method 1: HACS (Recommended)

#### Step 1: Add Custom Repository

1. Open **Home Assistant**
2. Go to **HACS** (in sidebar)
3. Click **Integrations** (bottom menu)
4. Click **⋮** (three dots, top right)
5. Select **"Custom repositories"**

#### Step 2: Enter Repository Details

```
Repository: https://github.com/Ierlandfan/nl_fuel_price_tracker
Category: Integration
```

6. Click **"Add"**
7. Close the dialog

#### Step 3: Install Integration

8. Search for **"Dutch Fuel Prices"** in HACS
9. Click on it
10. Click **"Download"**
11. Select latest version
12. Click **"Download"** again
13. Wait for download to complete

#### Step 4: Restart Home Assistant

14. Go to **Settings** → **System**
15. Click **"Restart"** (top right)
16. Click **"Restart Home Assistant"**
17. Wait 1-2 minutes for restart

---

### Method 2: Manual File Copy

#### Step 1: Download Files

1. Visit: https://github.com/Ierlandfan/nl_fuel_price_tracker
2. Click **"Code"** → **"Download ZIP"**
3. Extract the ZIP file

#### Step 2: Copy to Home Assistant

4. Locate your Home Assistant **config** folder:
   - Typical path: `/config/` or `\\homeassistant\config\`
   - SSH/Terminal: `/config/`
   - Samba share: `\\YOUR_HA_IP\config\`

5. Create folder (if doesn't exist):
   ```
   /config/custom_components/
   ```

6. Copy the integration folder:
   ```
   From: extracted_zip/custom_components/nl_fuel_prices/
   To:   /config/custom_components/nl_fuel_prices/
   ```

#### Step 3: Verify Structure

Your folder should look like:
```
/config/
  └── custom_components/
      └── nl_fuel_prices/
          ├── __init__.py
          ├── api.py
          ├── config_flow.py
          ├── const.py
          ├── daily_notifications.py
          ├── manifest.json
          ├── sensor.py
          ├── strings.json
          └── towns.py
```

#### Step 4: Restart Home Assistant

7. **Settings** → **System** → **Restart**

---

## ⚙️ Configuration

### Add Integration (UI)

**One-Click Add**:

[![Add Integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=nl_fuel_prices)

**Or manually**:

1. Go to **Settings** → **Devices & Services**
2. Click **"+ Add Integration"** (bottom right)
3. Search for **"Dutch Fuel Prices"**
4. Click on it

### Configuration Steps

#### Step 1: Location Selection

**Option A: Use Town Selector** (Recommended)
```
Use Town Selector: ✅ Enabled
Town: 1621 - Hoorn (Noord-Holland)
Radius: 10 km
```

**Option B: Manual Coordinates**
```
Use Town Selector: ❌ Disabled
Location Name: Home
Latitude: 52.6425
Longitude: 5.0597
Radius: 10 km
```

#### Step 2: Fuel Type

```
Fuel Type: Euro 95 (E10)
```

Options:
- Euro 95 (E10)
- Euro 98
- Diesel
- LPG
- AdBlue

#### Step 3: Update Settings

```
Update Interval: 15 minutes
```

Range: 5-60 minutes

#### Step 4: Daily Notifications (Optional)

```
Enable Daily Notifications: ✅ Enabled
Notification Time: 08:00:00
Days: Mon, Tue, Wed, Thu, Fri
Notification Services: mobile_app_phone
```

#### Step 5: Submit

Click **"Submit"** → Integration added! ✅

---

## 📊 Verify Installation

### Check Sensor

1. Go to **Settings** → **Devices & Services**
2. Find **"Dutch Fuel Prices"**
3. Click on it
4. You should see:
   - **Device**: Your location (e.g., "Hoorn")
   - **Sensor**: `sensor.fuel_euro95_hoorn`

### View Sensor Data

5. Click on the sensor
6. You should see:
   ```
   State: 1.839  (cheapest price)
   Attributes:
     - station_name: "Tango Wageningen"
     - distance: 2.1 km
     - location_postcode: "1621"
     - total_stations: 5
   ```

### Add to Dashboard

7. Go to your **Dashboard**
8. Click **Edit** (top right)
9. Click **"+ Add Card"**
10. Select **"Entity"**
11. Choose: `sensor.fuel_euro95_hoorn`
12. Click **"Save"**

---

## 🎨 Example Dashboard Card

### Simple Entity Card

```yaml
type: entities
title: Cheapest Fuel
entities:
  - entity: sensor.fuel_euro95_hoorn
    name: Euro 95
    secondary_info: last-changed
```

### Detailed Card

```yaml
type: entities
title: ⛽ Fuel Prices - Hoorn
entities:
  - entity: sensor.fuel_euro95_hoorn
    name: Cheapest Price
  - type: attribute
    entity: sensor.fuel_euro95_hoorn
    attribute: station_name
    name: Station
  - type: attribute
    entity: sensor.fuel_euro95_hoorn
    attribute: distance
    name: Distance
    suffix: km
  - type: attribute
    entity: sensor.fuel_euro95_hoorn
    attribute: total_stations
    name: Stations Found
```

### Markdown Card with Icon

```yaml
type: markdown
title: 🏆 Cheapest Fuel
content: |
  {% set sensor = 'sensor.fuel_euro95_hoorn' %}
  
  ### {{ state_attr(sensor, 'station_name') }}
  
  **€{{ states(sensor) }}/L**
  
  📍 {{ state_attr(sensor, 'distance') }}km away
  
  📮 {{ state_attr(sensor, 'location_postcode') }} - {{ state_attr(sensor, 'location_province') }}
  
  🔍 {{ state_attr(sensor, 'total_stations') }} stations in {{ state_attr(sensor, 'radius', 10) }}km radius
```

---

## 🔔 Setup Notifications

### Find Notification Service

1. Go to **Developer Tools** → **Services**
2. Type: `notify.`
3. You'll see services like:
   - `notify.mobile_app_phone`
   - `notify.mobile_app_iphone`
   - `notify.persistent_notification`

### Configure in Integration

4. **Settings** → **Devices & Services**
5. Click **"Configure"** on Dutch Fuel Prices
6. Enable **Daily Notification**
7. Select **Notification Services** from dropdown
8. Click **"Submit"**

---

## 🔧 Troubleshooting

### Integration Not Found

**Problem**: Can't find "Dutch Fuel Prices" in Add Integration

**Solution**:
1. Clear browser cache (Ctrl+F5)
2. Restart Home Assistant
3. Check `/config/custom_components/nl_fuel_prices/` exists
4. Check logs: **Settings** → **System** → **Logs**

### No Data Showing

**Problem**: Sensor shows "Unknown" or "Unavailable"

**Solution**:
1. Check integration is **loaded**
2. Wait 15 minutes (first update)
3. Check logs for errors
4. Verify internet connection

**Current Status**: Using demo/mock data (5 fake stations)
- Real data requires API key (see `API_RESEARCH.md`)

### Daily Notifications Not Working

**Problem**: Not receiving daily fuel reports

**Solution**:
1. Check notification service is **correct**
   - Go to **Developer Tools** → **Services**
   - Test: `notify.mobile_app_phone`
2. Verify **time** is correct (uses HA timezone)
3. Check **today** is in selected days
4. Test with time set to 2 minutes from now

### Postcode/Town Not Found

**Problem**: Can't find your town

**Solution**:
1. Check `POSTCODE_GUIDE.md` for full list
2. Use nearest major city
3. Or disable town selector and enter manual coordinates

---

## 📚 Additional Configuration

### Multiple Locations

Add integration **multiple times** for different locations:

1. **Home**: `1621 - Hoorn` (10km)
2. **Work**: `1012 - Amsterdam` (5km)
3. **Parents**: `3511 - Utrecht` (15km)

Each gets its own sensor!

### Different Fuel Types

Add same location with different fuel types:

1. **Euro 95**: `sensor.fuel_euro95_hoorn`
2. **Diesel**: `sensor.fuel_diesel_hoorn`

Compare prices for different fuels!

---

## 🎯 Quick Start Checklist

- [ ] HACS installed
- [ ] Repository added to HACS
- [ ] Integration downloaded
- [ ] Home Assistant restarted
- [ ] Integration added via UI
- [ ] Location configured (town or coordinates)
- [ ] Fuel type selected
- [ ] Sensor appears in entities
- [ ] Data visible (may be demo data)
- [ ] Added to dashboard
- [ ] (Optional) Daily notifications configured
- [ ] (Optional) Automations created

---

## 🆘 Getting Help

### Check Logs

**Settings** → **System** → **Logs**

Look for entries with: `nl_fuel_prices`

### GitHub Issues

Report problems: https://github.com/Ierlandfan/nl_fuel_price_tracker/issues

Include:
- Home Assistant version
- Integration version
- Error logs
- Configuration (remove sensitive data)

### Documentation

- `README.md` - Main documentation
- `POSTCODE_GUIDE.md` - Town/postcode lookup
- `DAILY_NOTIFICATIONS.md` - Notification guide
- `API_RESEARCH.md` - Real data API info

---

## ✅ Success!

You should now have:
- ⛽ Fuel price sensor working
- 📍 Location-based price tracking
- 💰 Cheapest station finder
- 📅 (Optional) Daily price reports
- 📊 Dashboard cards showing data

**Enjoy finding the cheapest fuel in the Netherlands!** 🇳🇱

---

**Note**: Integration currently uses demo data. For real fuel prices, see `API_RESEARCH.md` for API setup.
