"""Constants for the Dutch Fuel Prices integration."""

DOMAIN = "nl_fuel_prices"

# Configuration
CONF_LOCATION_LAT = "latitude"
CONF_LOCATION_LON = "longitude"
CONF_RADIUS = "radius"
CONF_FUEL_TYPE = "fuel_type"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_NOTIFY_ON_CHANGE = "notify_on_change"
CONF_NOTIFY_SERVICES = "notify_services"
CONF_PRICE_DROP_THRESHOLD = "price_drop_threshold"
CONF_DAILY_NOTIFICATION = "daily_notification"
CONF_DAILY_NOTIFICATION_TIME = "daily_notification_time"
CONF_DAILY_NOTIFICATION_DAYS = "daily_notification_days"
CONF_SCHEDULED_UPDATES = "scheduled_updates"
CONF_SCHEDULED_UPDATE_TIMES = "scheduled_update_times"

# Fuel types
FUEL_EURO95 = "euro95"
FUEL_EURO98 = "euro98"
FUEL_DIESEL = "diesel"
FUEL_LPG = "lpg"
FUEL_ADBLUE = "adblue"

FUEL_TYPES = {
    FUEL_EURO95: "Euro 95 (E10)",
    FUEL_EURO98: "Euro 98",
    FUEL_DIESEL: "Diesel",
    FUEL_LPG: "LPG",
    FUEL_ADBLUE: "AdBlue",
}

# API endpoints
API_DIRECTLEASE = "https://tankservice.app-it-up.com/Tankservice/v1/places"
API_UNITED_CONSUMERS = "https://api.unitedconsumers.com/alg/tankstations/zoekomlat"

# Events
EVENT_CHEAPEST_CHANGED = f"{DOMAIN}_cheapest_changed"
EVENT_PRICE_DROP = f"{DOMAIN}_price_drop"
EVENT_DAILY_REPORT = f"{DOMAIN}_daily_report"

# Defaults
DEFAULT_RADIUS = 10  # km
DEFAULT_UPDATE_INTERVAL = 60  # minutes (1 hour)
DEFAULT_PRICE_DROP_THRESHOLD = 0.03  # EUR
DEFAULT_DAILY_TIME = "08:00:00"  # Morning notification
DEFAULT_DAILY_DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]  # Every day
DEFAULT_SCHEDULED_UPDATE_TIMES = ["06:00:00", "12:00:00", "18:00:00"]  # 6 AM, 12 PM, 6 PM

# Attributes
ATTR_STATION_NAME = "station_name"
ATTR_STATION_BRAND = "station_brand"
ATTR_STATION_ADDRESS = "station_address"
ATTR_DISTANCE = "distance"
ATTR_LATITUDE = "latitude"
ATTR_LONGITUDE = "longitude"
ATTR_OPENING_HOURS = "opening_hours"
ATTR_LAST_UPDATED = "last_updated"
ATTR_PRICE_YESTERDAY = "price_yesterday"
ATTR_PRICE_CHANGE_24H = "price_change_24h"
ATTR_RANK = "rank"
ATTR_TOTAL_STATIONS = "total_stations"
ATTR_STATION_ID = "station_id"
ATTR_PRICE_WEEK_AGO = "price_week_ago"
ATTR_PRICE_CHANGE_WEEK = "price_change_week"
ATTR_ALL_STATIONS = "all_stations"
