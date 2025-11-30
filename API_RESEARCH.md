# 🔍 Fuel Price API Research - Netherlands

## Available APIs & Data Sources

### 1. **DirectLease Tankservice API** ⭐ **RECOMMENDED**

**Endpoint**: `https://tankservice.app-it-up.com/`

**Status**: Active, requires authentication

**Coverage**: 
- Netherlands nationwide
- All major fuel brands (Shell, BP, Esso, Texaco, Tango, etc.)
- Real-time price updates

**Data Available**:
- Fuel prices (Euro 95, 98, Diesel, LPG)
- Station location (lat/lng)
- Opening hours
- Station facilities
- Brand information

**Request Example**:
```
GET /Tankservice/v1/places?latitude=52.0907&longitude=5.1214&radius=10000
Headers:
  Authorization: Bearer {API_KEY}
```

**Response Format**: JSON
```json
{
  "places": [
    {
      "id": "12345",
      "name": "Shell Ede",
      "brand": "Shell",
      "address": {...},
      "location": {"lat": 52.04, "lng": 5.66},
      "fuels": [
        {"type": "E95", "price": 1.859},
        {"type": "diesel", "price": 1.659}
      ],
      "openingHours": {...}
    }
  ]
}
```

**How to Get API Key**:
1. Register at DirectLease developer portal
2. Request free tier access
3. API key provided via email
4. Free tier: ~1000 requests/day

---

### 2. **United Consumers (Tankservice.app)**

**Website**: `https://www.unitedconsumers.com/tanken/`

**Status**: Public website, no official API

**Coverage**:
- Netherlands nationwide
- Community-reported prices
- Major and independent stations

**Access Methods**:
- **Option A**: Web scraping (legal gray area)
- **Option B**: Mobile app reverse engineering
- **Option C**: Contact for partnership/API access

**Data Available**:
- Current fuel prices
- Station addresses
- User ratings
- Price history
- Opening hours

**Scraping Example** (if legal):
```python
# Search URL pattern
https://www.unitedconsumers.com/tanken/zoeken/{postcode}
https://www.unitedconsumers.com/tanken/informatie/tankstation/{id}
```

---

### 3. **Benzineprijs.nl**

**Website**: `https://www.benzineprijs.nl/`

**Status**: Public website

**Coverage**:
- Netherlands & Belgium
- Major fuel stations

**Access**: Web scraping required

**URL Patterns**:
```
https://www.benzineprijs.nl/tankstations/{city}
https://www.benzineprijs.nl/api/v1/prices?lat=52.09&lon=5.12&radius=10
```

---

### 4. **ANWB Onderweg (Roadside Assistance)**

**Website**: `https://www.anwb.nl/op-de-weg/tankstations`

**Status**: Members-only data

**Coverage**: Netherlands

**Access**: 
- Requires ANWB membership
- Mobile app data
- No public API

---

### 5. **MyFuelManager / Flitsmeister**

**Apps**: iOS/Android

**Status**: Mobile apps with user-reported prices

**Coverage**: Netherlands, user-driven

**Access**:
- Mobile app required
- Reverse engineering possible but ToS violation
- No official API

---

### 6. **European Union - Fuel Price Portal**

**Website**: `https://ec.europa.eu/energy/observatory/reports/`

**Status**: Official EU data

**Coverage**: All EU countries including NL

**Data**: Weekly averages, not real-time station data

**Not suitable** for real-time station finder

---

## Recommended Implementation Strategy

### Phase 1: MVP with Mock Data ✅
- Create integration structure
- Use mock data for 5 stations
- Test all features (sensors, notifications, events)
- UI configuration flow
- **Timeline**: Complete now

### Phase 2: DirectLease API Integration 🎯
- Register for API key
- Implement authentication
- Add real API calls
- Handle rate limits
- Error handling & fallbacks
- **Timeline**: 1-2 weeks

### Phase 3: Fallback Sources
- Add United Consumers scraping (if legally possible)
- Add Benzineprijs.nl as backup
- Merge data from multiple sources
- **Timeline**: 2-4 weeks

### Phase 4: Advanced Features
- Price history tracking
- Trend analysis
- Route optimization
- Multi-location support
- **Timeline**: 1-2 months

---

## Legal Considerations

### ✅ ALLOWED:
- Using official APIs with proper authentication
- Scraping publicly available data (check robots.txt)
- Caching data locally for reasonable time
- Personal/non-commercial use

### ⚠️ GRAY AREA:
- Web scraping commercial websites
- Reverse engineering mobile apps
- Automated data collection at scale

### ❌ NOT ALLOWED:
- Violating Terms of Service
- Redistributing proprietary data commercially
- Creating excessive server load
- Bypassing authentication/paywalls

---

## API Registration Process

### DirectLease API (Recommended Path)

1. **Visit**: https://tankservice.app-it-up.com/
2. **Contact**: developers@directlease.nl or support@app-it-up.com
3. **Request**: API access for Home Assistant integration
4. **Provide**:
   - Project description (non-commercial, open source)
   - Expected request volume (<100/day per user)
   - Use case (personal fuel price tracking)
5. **Receive**: API key + documentation
6. **Implement**: Add to integration

**Email Template**:
```
Subject: API Access Request - Home Assistant Integration

Hello,

I'm developing an open-source Home Assistant integration for Dutch fuel 
price tracking. The integration will help users find cheapest fuel prices 
near their location.

Project Details:
- Open source (MIT license)
- Non-commercial, personal use
- Expected volume: <100 API calls/day per user
- Purpose: Fuel price monitoring for smart home automation

Could you provide API access for this integration?

Thank you!
```

---

## Alternative: Community Data Sources

If API access is difficult, we can use:

1. **Crowdsourced Data**
   - Users manually report prices
   - Integration stores locally
   - Share anonymously if user opts in

2. **Home Assistant Community**
   - Other HA users share data
   - Decentralized approach
   - Privacy-friendly

3. **Manual Entry**
   - Users input their favorite stations
   - Integration tracks price changes
   - Manual updates when refueling

---

## Current Implementation (v0.1.0)

**Uses**: Mock data with 5 fictional stations

**Stations**:
1. Shell Ede Centrum - €1.859
2. BP Veenendaal - €1.879
3. Tango Wageningen - €1.839 (cheapest)
4. Esso Ede Noord - €1.869
5. Texaco Veenendaal West - €1.889

**Features Working**:
- ✅ Distance calculation
- ✅ Radius filtering
- ✅ Price sorting (cheapest first)
- ✅ Rank assignment
- ✅ All sensor attributes
- ✅ Ready for real API integration

**Next Step**: Register for DirectLease API key!

---

## Notes for Users

When you install this integration:

1. **Currently**: Uses demo data (5 fake stations)
2. **Why**: Real APIs require authentication
3. **Future**: Will automatically use real data once API key is added
4. **Help**: Contact developers if you have API access

**You can help** by:
- Reporting if you find working APIs
- Sharing API keys (if license allows)
- Contributing to API integration code

---

## Summary

| Source | Status | Real-time | Coverage | Difficulty |
|--------|--------|-----------|----------|------------|
| DirectLease API | 🟢 Best | ✅ Yes | Excellent | Medium (needs key) |
| United Consumers | 🟡 OK | ⚠️ Varies | Good | Hard (scraping) |
| Benzineprijs.nl | 🟡 OK | ⚠️ Varies | Good | Hard (scraping) |
| ANWB | 🔴 Limited | ✅ Yes | Good | Very Hard (members only) |
| Flitsmeister | 🔴 Limited | ✅ Yes | OK | Very Hard (app only) |

**Recommendation**: Use DirectLease API as primary source, mock data as demo.
