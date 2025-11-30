# 📅 Daily Notifications Guide - Dutch Fuel Prices

## Overview

Get **daily fuel price reports** with:
- ⏰ Configurable time and days
- 💰 Cheapest station in your radius
- 📊 Week-over-week price comparison
- 🏆 Top 3 cheapest stations
- 💸 Price range in your area

---

## Configuration (via UI)

### Initial Setup

1. **Settings** → **Devices & Services** → **Add Integration** → **Dutch Fuel Prices**
2. Configure daily notifications:

| Setting | Description | Example |
|---------|-------------|---------|
| **Enable Daily Notifications** | Turn on/off daily reports | ✅ Enabled |
| **Daily Notification Time** | When to send report | `08:00:00` (8 AM) |
| **Days for Notifications** | Which days to send | Mon-Fri (weekdays only) |
| **Notification Services** | Where to send | `mobile_app_phone` |

### Edit Existing

1. **Settings** → **Devices & Services** → **Dutch Fuel Prices**
2. Click **CONFIGURE** on your fuel price integration
3. Adjust notification settings

---

## Notification Examples

### Daily Report (Weekday Morning)

```
⛽ Daily Fuel Report

📍 Home (10km radius)

🏆 Cheapest Station:
Tango Wageningen - €1.839/L
📍 2.1km away
📮 Stationsstraat 67, 6701 AM Wageningen

📉 vs Last Week: -€0.020
   (was €1.859/L)

💰 Top 3 Cheapest:
1. Tango Wageningen - €1.839 (2.1km)
2. Shell Ede Centrum - €1.859 (2.3km)
3. Esso Ede Noord - €1.869 (3.5km)

💸 Price Range: €0.050 difference
   Cheapest: €1.839
   Most expensive: €1.889
```

### Price Increase Alert

```
⛽ Daily Fuel Report

📍 Home (10km radius)

🏆 Cheapest Station:
Shell Ede Centrum - €1.889/L
📍 2.3km away
📮 Hoofdstraat 123, 6711 AA Ede

📈 vs Last Week: +€0.030
   (was €1.859/L)

💰 Top 3 Cheapest:
1. Shell Ede Centrum - €1.889 (2.3km)
2. BP Veenendaal - €1.899 (4.2km)
3. Esso Ede Noord - €1.909 (3.5km)

💸 Price Range: €0.040 difference
   Cheapest: €1.889
   Most expensive: €1.929
```

---

## Use Cases

### 1. Weekday Commuter

**Configuration**:
- Time: `07:00:00` (7 AM)
- Days: Monday, Tuesday, Wednesday, Thursday, Friday
- Radius: 10 km

**Why**: Get fuel report before leaving for work, plan fill-ups on best days.

### 2. Weekend Fill-Up

**Configuration**:
- Time: `09:00:00` (9 AM)
- Days: Saturday, Sunday
- Radius: 15 km

**Why**: Know where to fill up for weekend trips.

### 3. Cost-Conscious Every Day

**Configuration**:
- Time: `20:00:00` (8 PM)
- Days: All 7 days
- Radius: 20 km

**Why**: Evening notification to plan next day's fill-up.

### 4. Multiple Locations

Add 2 integrations:
1. **Home** - 10km radius, weekday 7 AM
2. **Work** - 5km radius, weekday 5 PM

Get reports for both locations!

---

## Event Trigger

For advanced automations, use the `nl_fuel_prices_daily_report` event:

### Event Data

```yaml
event_type: nl_fuel_prices_daily_report
data:
  fuel_type: "euro95"
  location: "Home"
  cheapest_station: "Tango Wageningen"
  cheapest_price: 1.839
  cheapest_distance: 2.1
  total_stations: 5
  price_week_ago: 1.859
  price_change_week: -0.020
  top_3:
    - name: "Tango Wageningen"
      price: 1.839
      distance: 2.1
    - name: "Shell Ede Centrum"
      price: 1.859
      distance: 2.3
    - name: "Esso Ede Noord"
      price: 1.869
      distance: 3.5
```

---

## Example Automations

### 1. Only Notify on Price Drops

```yaml
alias: "Daily Fuel Report - Price Drops Only"
trigger:
  - platform: event
    event_type: nl_fuel_prices_daily_report
condition:
  - condition: template
    value_template: "{{ trigger.event.data.price_change_week < 0 }}"
action:
  - service: notify.mobile_app_phone
    data:
      title: "💰 Fuel Price Dropped!"
      message: >
        {{ trigger.event.data.cheapest_station }} now 
        €{{ trigger.event.data.cheapest_price }}/L
        (down €{{ -trigger.event.data.price_change_week | round(3) }} from last week!)
```

### 2. TTS Announcement at Home

```yaml
alias: "Announce Cheapest Fuel Price"
trigger:
  - platform: event
    event_type: nl_fuel_prices_daily_report
condition:
  - condition: state
    entity_id: person.john
    state: "home"
action:
  - service: tts.google_say
    target:
      entity_id: media_player.living_room
    data:
      message: >
        Good morning! The cheapest fuel today is at 
        {{ trigger.event.data.cheapest_station }}, 
        {{ trigger.event.data.cheapest_distance | round(1) }} kilometers away, 
        for {{ trigger.event.data.cheapest_price }} euros per liter.
```

### 3. Persistent Notification on Dashboard

```yaml
alias: "Daily Fuel - Persistent Notification"
trigger:
  - platform: event
    event_type: nl_fuel_prices_daily_report
action:
  - service: persistent_notification.create
    data:
      title: "⛽ Today's Cheapest Fuel"
      message: >
        **{{ trigger.event.data.cheapest_station }}**
        €{{ trigger.event.data.cheapest_price }}/L
        {{ trigger.event.data.cheapest_distance }}km away
        
        {% if trigger.event.data.price_change_week < 0 %}
        📉 Down €{{ -trigger.event.data.price_change_week | round(3) }} from last week
        {% elif trigger.event.data.price_change_week > 0 %}
        📈 Up €{{ trigger.event.data.price_change_week | round(3) }} from last week
        {% else %}
        ➡️ No change from last week
        {% endif %}
      notification_id: "daily_fuel_report"
```

### 4. Email Report (Detailed)

```yaml
alias: "Email Daily Fuel Report"
trigger:
  - platform: event
    event_type: nl_fuel_prices_daily_report
action:
  - service: notify.email
    data:
      title: "Daily Fuel Price Report - {{ now().strftime('%A, %B %d') }}"
      message: |
        Location: {{ trigger.event.data.location }}
        Fuel Type: {{ trigger.event.data.fuel_type }}
        
        CHEAPEST STATION
        {{ trigger.event.data.cheapest_station }}
        Price: €{{ trigger.event.data.cheapest_price }}/L
        Distance: {{ trigger.event.data.cheapest_distance }}km
        
        WEEKLY COMPARISON
        Last Week: €{{ trigger.event.data.price_week_ago }}/L
        Change: €{{ trigger.event.data.price_change_week | round(3) }}
        
        TOP 3 STATIONS
        {% for station in trigger.event.data.top_3 %}
        {{ loop.index }}. {{ station.name }} - €{{ station.price }}/L ({{ station.distance }}km)
        {% endfor %}
        
        Total stations found: {{ trigger.event.data.total_stations }}
```

### 5. Conditional Notification (Only Big Changes)

```yaml
alias: "Fuel Alert - Significant Changes Only"
trigger:
  - platform: event
    event_type: nl_fuel_prices_daily_report
condition:
  - condition: template
    value_template: >
      {{ trigger.event.data.price_week_ago is not none and
         (trigger.event.data.price_change_week | abs) > 0.05 }}
action:
  - service: notify.mobile_app_phone
    data:
      title: "⚠️ Significant Fuel Price Change!"
      message: >
        {% if trigger.event.data.price_change_week < 0 %}
        Price dropped €{{ -trigger.event.data.price_change_week | round(3) }}! 
        Now €{{ trigger.event.data.cheapest_price }}/L at 
        {{ trigger.event.data.cheapest_station }}
        {% else %}
        Price increased €{{ trigger.event.data.price_change_week | round(3) }}! 
        Now €{{ trigger.event.data.cheapest_price }}/L at 
        {{ trigger.event.data.cheapest_station }}
        {% endif %}
      data:
        priority: high
```

---

## Dashboard Card

Show last daily report info:

```yaml
type: markdown
title: Latest Fuel Report
content: |
  {% set sensor = 'sensor.fuel_euro95_home' %}
  {% if states(sensor) != 'unknown' %}
  ### 🏆 Cheapest Station
  **{{ state_attr(sensor, 'station_name') }}**
  **€{{ states(sensor) }}/L**
  📍 {{ state_attr(sensor, 'distance') }}km away
  
  {% if state_attr(sensor, 'price_week_ago') %}
  ### 📊 vs Last Week
  {% set change = states(sensor) | float - state_attr(sensor, 'price_week_ago') | float %}
  {% if change < 0 %}
  📉 Down €{{ -change | round(3) }}
  {% elif change > 0 %}
  📈 Up €{{ change | round(3) }}
  {% else %}
  ➡️ No change
  {% endif %}
  {% endif %}
  
  **{{ state_attr(sensor, 'total_stations') }}** stations in radius
  {% else %}
  No data available
  {% endif %}
```

---

## Tips

1. **Test First**: Set notification time to a few minutes from now to test
2. **Multiple Services**: Add multiple notification services (phone + email)
3. **Weekday Only**: Save money by checking weekdays only (commute days)
4. **Evening Notifications**: Get report night before to plan morning fill-up
5. **Large Radius**: Use larger radius (20-30km) for comprehensive price comparison

---

## Troubleshooting

### Not Receiving Daily Notifications

**Check**:
1. ✅ Daily notifications enabled in config
2. ✅ Notification service configured and working
3. ✅ Today is in selected days
4. ✅ Time is correct (uses HA timezone)
5. ✅ Check Home Assistant logs for errors

**Test**: 
- Set time to 2 minutes from now
- Check if notification arrives

### Wrong Time

- Integration uses **Home Assistant's timezone**
- Check HA timezone: Settings → System → General
- Notification time is in 24-hour format (HH:MM:SS)

### Missing Week Comparison

- Needs at least 1 week of data
- Data collected automatically over time
- After first week, comparisons will appear

---

## Summary

| Feature | Description |
|---------|-------------|
| **Scheduling** | Configurable time + days |
| **Report Content** | Cheapest station, top 3, price range |
| **History** | Week-over-week comparison |
| **Delivery** | Any HA notification service |
| **Events** | Full automation support |
| **Multi-Location** | Add multiple integrations |

**Never miss the cheapest fuel again!** ⛽💰
