# 🇳🇱 Dutch Fuel Prices - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub Release](https://img.shields.io/github/release/Ierlandfan/nl_fuel_price_tracker.svg)](https://github.com/Ierlandfan/nl_fuel_price_tracker/releases)
[![GitHub](https://img.shields.io/github/license/Ierlandfan/nl_fuel_price_tracker.svg)](LICENSE)

Get **real-time fuel prices** in the Netherlands with automatic **cheapest station notifications** based on your location and radius!

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Ierlandfan&repository=nl_fuel_price_tracker&category=integration)

---

## 🚀 Quick Start

1. **Click the badge above** to add to HACS (or add manually via HACS → Custom repositories)
2. Download the integration and **restart Home Assistant**
3. **Add Integration**: [![Add Integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=nl_fuel_prices)
4. Configure your location, fuel type, and daily notifications
5. Get cheapest fuel prices in your area! ⛽💰

**📖 Need help? See [INSTALLATION.md](INSTALLATION.md) for complete step-by-step guide**

---

## Features

⛽ **Multi-Fuel Support**
- Euro 95 (E10)
- Euro 98
- Diesel
- LPG
- AdBlue
- Configurable fuel type per sensor

📍 **Location-Based Search**
- **Search by Dutch postcode** (e.g., 1621AB, 3811AB, 6711AA)
- Automatic geocoding (postcode → exact coordinates)
- Configurable radius (1-50 km)
- Supports all Dutch postcodes (cities & villages)

💰 **Cheapest Station Alerts**
- Automatic notifications when cheapest station changes
- Price drop alerts (configurable threshold)
- Daily/weekly price summary reports

🗺️ **Map Integration**
- Show fuel stations on Home Assistant maps
- Distance from your location
- Opening hours display

📊 **Rich Data**
- Current price per liter
- Price history tracking
- Station brand, address, distance
- Opening hours
- Last updated timestamp

🔔 **Smart Notifications**
- "Cheapest station within 10km changed!"
- "Price dropped by €0.05 at Shell Ede!"
- "Your favorite station now cheapest!"

## Available APIs for Dutch Fuel Prices

### 1. **DirectLease API** (Recommended)
- **URL**: `https://tankservice.app-it-up.com`
- **Coverage**: Netherlands nationwide
- **Data**: Real-time prices, all major brands
- **Rate Limit**: Reasonable for HA usage
- **Auth**: API key required (free tier available)

### 2. **United Consumers**
- **URL**: `https://www.unitedconsumers.com/tanken/`
- **Coverage**: Netherlands
- **Data**: Community-reported prices
- **Note**: May require scraping or unofficial API

### 3. **Benzineprijs.nl**
- **Coverage**: Netherlands & Belgium
- **Data**: Real-time from major stations
- **Note**: May require scraping

### 4. **MyFuelManager / Flitsmeister**
- **Coverage**: Netherlands
- **Data**: User-reported prices
- **Note**: Mobile app data

## Implementation Plan

This integration will use **DirectLease API** (or fallback to others) with:
- Automatic location from Home Assistant zones
- Configurable radius and fuel types
- Price change detection
- Cheapest station tracking
- Notification system

## Installation

### HACS (Recommended)

**Click to add to HACS:**

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Ierlandfan&repository=nl_fuel_price_tracker&category=integration)

**Or manually:**

1. Open HACS in Home Assistant
2. Click the three dots (⋮) in the top right
3. Select **"Custom repositories"**
4. Add repository URL: `https://github.com/Ierlandfan/nl_fuel_price_tracker`
5. Category: **Integration**
6. Click **"Add"**
7. Find "Dutch Fuel Prices" in HACS
8. Click **"Download"**
9. Restart Home Assistant
10. Add integration via UI: [![Add Integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=nl_fuel_prices)

### Manual

1. Copy `custom_components/nl_fuel_prices` to your HA config
2. Restart Home Assistant
3. Add integration via UI

## Configuration

### Via UI (Recommended)

1. **Settings** → **Devices & Services** → **Add Integration**
2. Search for "Dutch Fuel Prices"
3. Configure:
   - **Location**: Select Home Assistant zone or enter coordinates
   - **Fuel Type**: Euro 95, Euro 98, Diesel, LPG, AdBlue
   - **Radius**: 1-50 km
   - **Update Interval**: 5-60 minutes
   - **Notifications**: Enable price alerts

### Multiple Locations

Add multiple instances for:
- Home location (5km radius)
- Work location (10km radius)
- Favorite route (along highway)

## Usage Examples

### Dashboard Card

```yaml
type: entities
title: Cheapest Fuel Nearby
entities:
  - entity: sensor.fuel_euro95_home
    name: Euro 95
  - entity: sensor.fuel_diesel_home
    name: Diesel
  - type: attribute
    entity: sensor.fuel_euro95_home
    attribute: station_name
    name: Station
  - type: attribute
    entity: sensor.fuel_euro95_home
    attribute: distance
    name: Distance
```

### Automation: Price Drop Alert

```yaml
alias: "Fuel Price Drop Alert"
trigger:
  - platform: state
    entity_id: sensor.fuel_euro95_home
condition:
  - condition: template
    value_template: >
      {{ (trigger.from_state.state | float - trigger.to_state.state | float) > 0.03 }}
action:
  - service: notify.mobile_app_phone
    data:
      title: "⛽ Fuel Price Drop!"
      message: >
        Euro 95 dropped €{{ '%.3f' | format(trigger.from_state.state | float - trigger.to_state.state | float) }}
        to €{{ trigger.to_state.state }}/L at 
        {{ state_attr('sensor.fuel_euro95_home', 'station_name') }}
```

### Automation: Cheapest Station Changed

```yaml
alias: "Cheapest Station Alert"
trigger:
  - platform: state
    entity_id: sensor.fuel_euro95_home
    attribute: station_id
action:
  - service: notify.mobile_app_phone
    data:
      title: "🏆 New Cheapest Station!"
      message: >
        {{ state_attr('sensor.fuel_euro95_home', 'station_name') }}
        is now cheapest: €{{ states('sensor.fuel_euro95_home') }}/L
        Distance: {{ state_attr('sensor.fuel_euro95_home', 'distance') }} km
```

## Sensor Attributes

```yaml
sensor.fuel_euro95_home:
  state: 1.859  # Price in EUR per liter
  attributes:
    fuel_type: "Euro 95 (E10)"
    station_name: "Shell Ede"
    station_brand: "Shell"
    station_address: "Hoofdstraat 123, Ede"
    distance: 2.3  # km from location
    latitude: 52.0409
    longitude: 5.6574
    opening_hours: "06:00-23:00"
    last_updated: "2024-11-30T10:15:00+01:00"
    price_yesterday: 1.879
    price_change_24h: -0.020
    rank: 1  # 1 = cheapest in radius
    total_stations: 15  # in radius
```

## Events

### `nl_fuel_prices_cheapest_changed`

Fired when the cheapest station changes.

```yaml
event_data:
  fuel_type: "Euro 95"
  location: "home"
  new_station: "Shell Ede"
  new_price: 1.859
  old_station: "BP Veenendaal"
  old_price: 1.879
  savings: 0.020
```

### `nl_fuel_prices_price_drop`

Fired when price drops significantly (configurable threshold).

```yaml
event_data:
  fuel_type: "Diesel"
  station: "Shell Ede"
  old_price: 1.659
  new_price: 1.599
  drop: 0.060
```

## API Notes

The integration will attempt to use multiple data sources:

1. **Primary**: DirectLease API (if available)
2. **Fallback**: United Consumers data
3. **Fallback**: Benzineprijs.nl scraping

You can configure API preference in integration options.

## Privacy

- Location data stays local in Home Assistant
- API calls use minimal data (lat/lng + radius) -- default is every hour
- No tracking or data collection
- All processing done locally


## License

MIT License - See LICENSE file

## Credits
Based on: https://github.com/pantherale0/ha-fuelprices
