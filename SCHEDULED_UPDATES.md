# ⏰ Scheduled Updates Guide

Configure price updates to run only at specific times instead of continuously.

---

## Why Use Scheduled Updates?

### **Continuous Updates** (Default)
- Updates every X minutes (e.g., every 15 minutes)
- Uses more API calls
- Good for: Real-time monitoring

### **Scheduled Updates** (Recommended)
- Updates only at specific times (e.g., 06:00, 12:00, 18:00)
- Uses fewer API calls
- Good for: Daily price checking

---

## How It Works

### Example Configuration

**Scheduled Updates**: ✅ Enabled  
**Update Times**: `06:00`, `12:00`, `18:00`

**Result**:
- **06:00** - Morning update (before commute)
- **12:00** - Midday update (lunch break)
- **18:00** - Evening update (after work)

No updates in between these times!

---

## Configuration

### Step 1: Enable Scheduled Updates

**Settings → Devices & Services → Dutch Fuel Prices → Configure**

```
Scheduled Updates: ✅ Enabled
```

### Step 2: Select Times

```
Update Times: 
  ✅ 06:00 (6 AM)
  ✅ 12:00 (Noon)
  ✅ 18:00 (6 PM)
```

**Available Times**:
- 00:00 (Midnight)
- 03:00 (3 AM)
- 06:00 (6 AM) ⭐
- 09:00 (9 AM)
- 12:00 (Noon) ⭐
- 15:00 (3 PM)
- 18:00 (6 PM) ⭐
- 21:00 (9 PM)

Select multiple times for more frequent updates.

### Step 3: Update Interval Still Matters

```
Update Interval: 60 minutes
```

**Why?** This is the fallback if scheduled updates fail or are disabled.

---

## Use Cases

### 1. **Commuter** (Morning & Evening)

```
Update Times:
  ✅ 06:00 (Before work)
  ✅ 18:00 (After work)
```

**Why**: Check prices when you're likely to fill up.

---

### 2. **Daily Shopper** (Three Times)

```
Update Times:
  ✅ 06:00 (Morning)
  ✅ 12:00 (Lunch)
  ✅ 18:00 (Evening)
```

**Why**: Catch price changes throughout the day.

---

### 3. **Weekend Warrior** (Mid-day Only)

```
Update Times:
  ✅ 12:00 (Noon)
```

**Why**: One daily update is enough for casual use.

---

### 4. **Night Owl** (Midnight Update)

```
Update Times:
  ✅ 00:00 (Midnight)
```

**Why**: Prepare for next day, low server load.

---

### 5. **Comprehensive** (Every 3 Hours)

```
Update Times:
  ✅ 00:00
  ✅ 03:00
  ✅ 06:00
  ✅ 09:00
  ✅ 12:00
  ✅ 15:00
  ✅ 18:00
  ✅ 21:00
```

**Why**: Maximum coverage without constant polling.

---

## Comparison

### Continuous Updates (15 min interval)

```
API Calls per Day: 96 (24 hours × 4 per hour)
Battery Impact: Higher (mobile app)
Network Usage: Higher
Best For: Real-time monitoring
```

### Scheduled Updates (3 times/day)

```
API Calls per Day: 3 (06:00, 12:00, 18:00)
Battery Impact: Lower
Network Usage: Lower
Best For: Daily price checks
```

**Savings**: 96 → 3 calls = **96% reduction!**

---

## How to Check It's Working

### 1. View Logs

**Settings → System → Logs**

Search for: `nl_fuel_prices`

You'll see:
```
INFO: Setting up scheduled updates at: ['06:00:00', '12:00:00', '18:00:00']
DEBUG: Scheduled update at 06:00:00
INFO: Running scheduled fuel price update at 06:00:00
DEBUG: Scheduled update completed successfully
```

### 2. Check Sensor Update Time

View sensor attributes:
```yaml
sensor.fuel_euro95_hoorn:
  attributes:
    last_updated: "2024-01-15T06:00:03"  # Updated at 06:00
```

Wait until next scheduled time, sensor updates!

---

## Combining with Daily Notifications

### Perfect Combo

**Scheduled Updates**:
```
Update Times: 06:00, 12:00, 18:00
```

**Daily Notification**:
```
Notification Time: 08:00
Days: Mon-Fri
```

**Flow**:
1. **06:00** - Prices update
2. **08:00** - You get notification with latest prices
3. **12:00** - Midday price check
4. **18:00** - Evening price check

You always have fresh data for your notification!

---

## Troubleshooting

### Updates Not Happening

**Problem**: No updates at scheduled times

**Solutions**:
1. Check **"Scheduled Updates"** is ✅ Enabled
2. Verify times are selected
3. Check logs for errors
4. Time uses Home Assistant timezone

### Still Using Continuous Updates

**Problem**: Updates every 15 minutes despite scheduled updates enabled

**Solution**: 
- When scheduled updates **enabled**, continuous updates **pause**
- If you see frequent updates, reload integration:
  - Settings → Devices & Services
  - Click ⋮ on Dutch Fuel Prices
  - Click "Reload"

### Times Not Showing

**Problem**: Dropdown shows no times

**Solution**: Clear browser cache (Ctrl+F5) and reload page

---

## Advanced: Custom Times

Want different times? You can request them via GitHub issue or use automations:

### Automation Example (Update at 07:30)

```yaml
automation:
  - alias: "Fuel Prices - Update at 7:30 AM"
    trigger:
      - platform: time
        at: "07:30:00"
    action:
      - service: homeassistant.update_entity
        target:
          entity_id: sensor.fuel_euro95_hoorn
```

---

## Best Practices

### 1. **Match Your Routine**
- Select times when you **actually need** prices
- Don't update while you're sleeping

### 2. **Start with 3 Times**
- Morning (06:00)
- Noon (12:00)
- Evening (18:00)

Adjust based on needs.

### 3. **Coordinate with Notifications**
- Update **before** daily notification time
- Example: Update 06:00, Notify 08:00

### 4. **Less is More**
- More updates = more API calls
- Fuel prices don't change every minute
- 2-3 times per day is usually enough

---

## FAQ

**Q: Can I use both scheduled AND continuous updates?**  
A: No, it's either/or. Scheduled updates disable continuous polling.

**Q: What if I disable scheduled updates?**  
A: It reverts to continuous updates using the interval you configured.

**Q: Do I need to restart Home Assistant?**  
A: No, just reload the integration.

**Q: Can times be customized beyond the list?**  
A: Currently limited to 3-hour intervals. Use automations for custom times.

**Q: What timezone is used?**  
A: Your Home Assistant timezone (Settings → System → General).

---

## Summary

| Feature | Continuous | Scheduled |
|---------|-----------|-----------|
| **Updates** | Every X minutes | At specific times |
| **API Calls** | ~96/day (15 min) | ~3/day (3 times) |
| **Efficiency** | Lower | Higher ⭐ |
| **Real-time** | Yes | No |
| **Recommended** | Monitoring | Daily use ⭐ |

**For most users: Use scheduled updates (06:00, 12:00, 18:00)** ✅

---

**Enjoy more efficient fuel price tracking!** ⏰⛽
