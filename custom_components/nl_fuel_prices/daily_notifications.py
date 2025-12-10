"""Daily notification manager for fuel prices."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, time as dt_time
from typing import Any

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_change
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    EVENT_DAILY_REPORT,
    CONF_DAILY_NOTIFICATION,
    CONF_DAILY_NOTIFICATION_TIME,
    CONF_DAILY_NOTIFICATION_DAYS,
    CONF_NOTIFY_SERVICES,
    DEFAULT_DAILY_TIME,
    DEFAULT_DAILY_DAYS,
)

_LOGGER = logging.getLogger(__name__)


class DailyNotificationManager:
    """Manage daily fuel price notifications."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize notification manager."""
        self.hass = hass
        self._price_history: dict[str, list[dict[str, Any]]] = {}
        self._cancel_trackers: dict[str, Any] = {}  # Track cancellers per entry

    async def setup(self, config_entry) -> None:
        """Set up daily notifications."""
        entry_id = config_entry.entry_id
        
        if not config_entry.data.get(CONF_DAILY_NOTIFICATION, False):
            _LOGGER.info(f"Daily notifications disabled for entry {entry_id}")
            return

        # Cancel existing tracker for this entry if it exists (for reload scenarios)
        if entry_id in self._cancel_trackers:
            _LOGGER.info(f"Cancelling existing notification tracker for entry {entry_id}")
            self._cancel_trackers[entry_id]()
            del self._cancel_trackers[entry_id]

        notification_time = config_entry.data.get(
            CONF_DAILY_NOTIFICATION_TIME, DEFAULT_DAILY_TIME
        )
        
        # Parse time string (HH:MM:SS)
        try:
            hour, minute, second = map(int, notification_time.split(":"))
        except ValueError:
            _LOGGER.error(f"Invalid notification time: {notification_time}")
            return

        # Schedule daily notification
        cancel_tracker = async_track_time_change(
            self.hass,
            self._send_daily_notification,
            hour=hour,
            minute=minute,
            second=second,
        )
        
        self._cancel_trackers[entry_id] = cancel_tracker
        
        _LOGGER.info(f"Daily fuel price notification scheduled for {notification_time} (entry: {entry_id})")

    async def _send_daily_notification(self, now: datetime) -> None:
        """Send daily fuel price report."""
        _LOGGER.info(f"Daily notification triggered at {now}")
        
        # Check if today is in configured days
        day_names = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        current_day = day_names[now.weekday()]
        _LOGGER.debug(f"Current day: {current_day}")
        
        # Get all fuel price coordinators (skip manager entries)
        coordinators = self.hass.data.get(DOMAIN, {})
        
        for entry_id, coordinator in coordinators.items():
            # Skip non-coordinator entries (managers, scheduled, etc.)
            if not hasattr(coordinator, 'entry'):
                continue
                
            config_entry = coordinator.entry
            
            # Skip if daily notification not enabled
            if not config_entry.data.get(CONF_DAILY_NOTIFICATION, False):
                _LOGGER.debug(f"Daily notification not enabled for {entry_id}")
                continue
            
            # Check if notification should be sent today
            notify_days = config_entry.data.get(
                CONF_DAILY_NOTIFICATION_DAYS, DEFAULT_DAILY_DAYS
            )
            _LOGGER.debug(f"Notify days: {notify_days}, Current day: {current_day}")
            if current_day not in notify_days:
                _LOGGER.info(f"Skipping notification for {entry_id} - not scheduled for {current_day}")
                continue
            
            # Get current data
            data = coordinator.data
            if not data:
                _LOGGER.warning(f"No data available for {entry_id}")
                continue
            
            cheapest = data.get("cheapest")
            if not cheapest:
                _LOGGER.warning(f"No cheapest station found for {entry_id}")
                continue
            
            _LOGGER.info(f"Preparing daily notification for {entry_id}")
            
            # Get historical data
            price_week_ago = await self._get_price_week_ago(entry_id, cheapest)
            
            # Build notification message
            message = await self._build_daily_message(
                cheapest, price_week_ago, data.get("stations", []), config_entry
            )
            
            # Send notification
            notify_services = config_entry.data.get(CONF_NOTIFY_SERVICES, [])
            stations = data.get("stations", [])
            _LOGGER.info(f"Notify services configured: {notify_services}")
            
            if notify_services:
                _LOGGER.info(f"Sending daily notification to {len(notify_services)} service(s)")
                await self._send_notifications(
                    notify_services, 
                    "⛽ Daily Fuel Report", 
                    message,
                    cheapest,
                    stations[:3] if len(stations) > 0 else []
                )
            
            # Fire event
            await self._fire_daily_report_event(cheapest, price_week_ago, data, config_entry)

    async def _build_daily_message(
        self,
        cheapest: dict[str, Any],
        price_week_ago: float | None,
        all_stations: list[dict[str, Any]],
        config_entry,
    ) -> str:
        """Build daily notification message."""
        fuel_type = config_entry.data.get("fuel_type", "euro95")
        location_name = config_entry.data.get("location_name", "Unknown")
        radius = config_entry.data.get("radius", 10)
        
        # Header
        message = f"📍 {location_name} ({radius}km radius)\n\n"
        
        # Cheapest station
        message += f"🏆 Cheapest Station:\n"
        message += f"{cheapest.get('name')} - €{cheapest.get('price'):.3f}/L\n"
        message += f"📍 {cheapest.get('distance')}km away\n"
        message += f"📮 {cheapest.get('address', 'N/A')}\n"
        
        # Station type and services
        is_unmanned = cheapest.get('is_unmanned', False)
        has_shop = cheapest.get('has_shop', False)
        
        if is_unmanned:
            message += f"🤖 Unmanned station\n"
        else:
            message += f"👤 Manned station\n"
        
        if has_shop:
            message += f"🏪 Shop available\n"
            shop_hours = cheapest.get('shop_hours')
            if shop_hours:
                # Show today's shop hours
                from datetime import datetime
                day_names = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
                today = day_names[datetime.now().weekday()]
                if today in shop_hours:
                    hours = shop_hours[today]
                    start = self._format_time(hours[0])
                    end = self._format_time(hours[1])
                    message += f"🕐 Shop hours today: {start} - {end}\n"
        
        message += "\n"
        
        # Week comparison
        if price_week_ago is not None:
            price_change = cheapest.get('price') - price_week_ago
            if abs(price_change) < 0.001:
                change_text = "No change"
                emoji = "➡️"
            elif price_change > 0:
                change_text = f"+€{price_change:.3f}"
                emoji = "📈"
            else:
                change_text = f"€{price_change:.3f}"
                emoji = "📉"
            
            message += f"{emoji} vs Last Week: {change_text}\n"
            message += f"   (was €{price_week_ago:.3f}/L)\n\n"
        
        # Top 3 cheapest stations
        if len(all_stations) > 1:
            message += "💰 Top 3 Cheapest:\n"
            for idx, station in enumerate(all_stations[:3], 1):
                message += f"{idx}. {station.get('name')} - €{station.get('price'):.3f} ({station.get('distance')}km)\n"
            message += "\n"
        
        # Price range
        if len(all_stations) > 1:
            most_expensive = max(all_stations, key=lambda x: x.get('price', 0))
            price_diff = most_expensive.get('price') - cheapest.get('price')
            message += f"💸 Price Range: €{price_diff:.3f} difference\n"
            message += f"   Cheapest: €{cheapest.get('price'):.3f}\n"
            message += f"   Most expensive: €{most_expensive.get('price'):.3f}\n"
        
        return message

    async def _get_price_week_ago(self, entry_id: str, current_station: dict[str, Any]) -> float | None:
        """Get price from a week ago for comparison."""
        # Initialize history if needed
        if entry_id not in self._price_history:
            self._price_history[entry_id] = []
        
        history = self._price_history[entry_id]
        
        # Add current price to history
        now = dt_util.now()
        history.append({
            "timestamp": now,
            "price": current_station.get("price"),
            "station_id": current_station.get("id"),
        })
        
        # Keep only last 30 days of history
        cutoff = now - timedelta(days=30)
        self._price_history[entry_id] = [
            h for h in history if h["timestamp"] > cutoff
        ]
        
        # Find price from approximately a week ago
        week_ago = now - timedelta(days=7)
        
        # Find closest entry to a week ago
        closest_entry = None
        min_diff = timedelta(days=999)
        
        for entry in history:
            diff = abs(entry["timestamp"] - week_ago)
            if diff < min_diff and diff < timedelta(days=2):  # Within 2 days of target
                min_diff = diff
                closest_entry = entry
        
        if closest_entry:
            return closest_entry.get("price")
        
        return None

    async def _send_notifications(
        self,
        services: list[str],
        title: str,
        message: str,
        cheapest_station: dict[str, Any] | None = None,
        top_stations: list[dict[str, Any]] | None = None,
    ) -> None:
        """Send notification to all configured services with Telegram enhancements."""
        for service in services:
            try:
                # Check if using telegram_bot service (direct) or notify service
                if service == "telegram_bot" or service.startswith("telegram_bot."):
                    await self._send_telegram_bot_notification(
                        title, message, cheapest_station, top_stations
                    )
                elif "telegram" in service.lower():
                    # Support both 'notify.telegram' and 'telegram' formats
                    if not service.startswith("notify."):
                        service = f"notify.{service}"
                    await self._send_telegram_notify_notification(
                        service, title, message, cheapest_station, top_stations
                    )
                else:
                    # Standard notify service (mobile_app, etc.)
                    if not service.startswith("notify."):
                        service = f"notify.{service}"
                    
                    notification_data = {
                        "title": title,
                        "message": message,
                        "data": {
                            "priority": "normal",
                            "notification_icon": "mdi:gas-station",
                        },
                    }
                    
                    await self.hass.services.async_call(
                        "notify",
                        service.replace("notify.", ""),
                        notification_data,
                    )
                    _LOGGER.info(f"Sent daily report via {service}")
            except Exception as err:
                _LOGGER.error(f"Failed to send notification via {service}: {err}")
    
    async def _send_telegram_bot_notification(
        self,
        title: str,
        message: str,
        cheapest_station: dict[str, Any] | None = None,
        top_stations: list[dict[str, Any]] | None = None,
    ) -> None:
        """Send notification using telegram_bot.send_message service."""
        # Format message with HTML
        formatted_message = message
        if cheapest_station:
            formatted_message = self._format_html_daily_message(
                message, cheapest_station, top_stations
            )
        
        # Build inline keyboard
        inline_keyboard = None
        if cheapest_station:
            lat = cheapest_station.get("latitude")
            lon = cheapest_station.get("longitude")
            if lat and lon:
                inline_keyboard = [
                    [["🗺️ Open in Google Maps", f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"]],
                    [["🧭 Navigate (Google)", f"https://www.google.com/maps/dir/?api=1&destination={lat},{lon}"]],
                    [["🚗 Navigate (Waze)", f"https://waze.com/ul?ll={lat},{lon}&navigate=yes"]]
                ]
        
        # Send main message
        telegram_data = {
            "message": f"<b>{title}</b>\n\n{formatted_message}",
            "parse_mode": "html",
        }
        
        if inline_keyboard:
            telegram_data["inline_keyboard"] = inline_keyboard
        
        await self.hass.services.async_call(
            "telegram_bot",
            "send_message",
            telegram_data,
            blocking=False,
        )
        
        # Send location separately for better map display
        if cheapest_station:
            lat = cheapest_station.get("latitude")
            lon = cheapest_station.get("longitude")
            if lat and lon:
                await self.hass.services.async_call(
                    "telegram_bot",
                    "send_location",
                    {
                        "latitude": lat,
                        "longitude": lon,
                    },
                    blocking=False,
                )
        
        _LOGGER.info("Sent daily report via telegram_bot")
    
    async def _send_telegram_notify_notification(
        self,
        service: str,
        title: str,
        message: str,
        cheapest_station: dict[str, Any] | None = None,
        top_stations: list[dict[str, Any]] | None = None,
    ) -> None:
        """Send notification using notify.telegram service."""
        notification_data = {
            "title": title,
            "message": message,
            "data": {
                "priority": "normal",
                "notification_icon": "mdi:gas-station",
            },
        }
        
        # Format message with HTML
        if cheapest_station:
            notification_data["message"] = self._format_html_daily_message(
                message, cheapest_station, top_stations
            )
        
        # Add location and inline keyboard if available
        if cheapest_station:
            lat = cheapest_station.get("latitude")
            lon = cheapest_station.get("longitude")
            if lat and lon:
                # Send location as separate message
                await self.hass.services.async_call(
                    "notify",
                    service.replace("notify.", ""),
                    {
                        "message": "⛽ Fuel Price Update",
                        "data": {
                            "location": {
                                "latitude": lat,
                                "longitude": lon,
                            }
                        }
                    },
                    blocking=False,
                )
                
                # Add inline keyboard with navigation
                notification_data["data"]["inline_keyboard"] = [
                    [
                        {
                            "text": "🗺️ Open in Google Maps",
                            "url": f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
                        }
                    ],
                    [
                        {
                            "text": "🧭 Navigate (Google)",
                            "url": f"https://www.google.com/maps/dir/?api=1&destination={lat},{lon}"
                        }
                    ],
                    [
                        {
                            "text": "🚗 Navigate (Waze)",
                            "url": f"https://waze.com/ul?ll={lat},{lon}&navigate=yes"
                        }
                    ]
                ]
        
        await self.hass.services.async_call(
            "notify",
            service.replace("notify.", ""),
            notification_data,
            blocking=False,
        )
        _LOGGER.info(f"Sent daily report via {service}")
    
    def _format_html_daily_message(
        self,
        message: str,
        cheapest_station: dict[str, Any],
        top_stations: list[dict[str, Any]] | None,
    ) -> str:
        """Format daily message with HTML for Telegram."""
        lines = message.split('\n')
        html_msg = ""
        
        for line in lines:
            if line.startswith("🏆"):
                html_msg += f"<b>{line}</b>\n"
            elif line.startswith("💰 Top 3"):
                html_msg += f"\n<b>{line}</b>\n"
            elif "€" in line and any(str(i) + "." in line for i in range(1, 4)):
                # Top 3 stations - make price bold
                parts = line.split(" - €")
                if len(parts) == 2:
                    html_msg += f"{parts[0]} - <b>€{parts[1]}</b>\n"
                else:
                    html_msg += f"{line}\n"
            elif line.startswith("📍") or line.startswith("📮"):
                html_msg += f"<i>{line}</i>\n"
            elif "Cheapest Station:" in line or "Price Range:" in line:
                html_msg += f"<b>{line}</b>\n"
            else:
                html_msg += f"{line}\n"
        
        return html_msg

    async def _fire_daily_report_event(
        self,
        cheapest: dict[str, Any],
        price_week_ago: float | None,
        data: dict[str, Any],
        config_entry,
    ) -> None:
        """Fire daily report event for automation triggers."""
        event_data = {
            "fuel_type": config_entry.data.get("fuel_type"),
            "location": config_entry.data.get("location_name"),
            "cheapest_station": cheapest.get("name"),
            "cheapest_price": cheapest.get("price"),
            "cheapest_distance": cheapest.get("distance"),
            "total_stations": data.get("total_stations", 0),
        }
        
        if price_week_ago is not None:
            event_data["price_week_ago"] = price_week_ago
            event_data["price_change_week"] = cheapest.get("price") - price_week_ago
        
        # Add top 3 stations
        stations = data.get("stations", [])
        if stations:
            event_data["top_3"] = [
                {
                    "name": s.get("name"),
                    "price": s.get("price"),
                    "distance": s.get("distance"),
                }
                for s in stations[:3]
            ]
        
        self.hass.bus.async_fire(EVENT_DAILY_REPORT, event_data)
    
    def _format_time(self, time_int: int) -> str:
        """Format time from API format (e.g., 600 -> '06:00', 1630 -> '16:30')."""
        if time_int == 0:
            return "00:00"
        if time_int == 2400:
            return "24:00"
        
        hours = time_int // 100
        minutes = time_int % 100
        return f"{hours:02d}:{minutes:02d}"

    async def store_current_price(self, entry_id: str, station: dict[str, Any]) -> None:
        """Store current price for historical tracking."""
        if entry_id not in self._price_history:
            self._price_history[entry_id] = []
        
        # Don't duplicate if we just added this
        now = dt_util.now()
        history = self._price_history[entry_id]
        
        # Only add if last entry was more than 1 hour ago
        if history:
            last_entry = history[-1]
            if (now - last_entry["timestamp"]).total_seconds() < 3600:
                return
        
        history.append({
            "timestamp": now,
            "price": station.get("price"),
            "station_id": station.get("id"),
        })

    def shutdown(self) -> None:
        """Clean up resources."""
        for entry_id, cancel_tracker in self._cancel_trackers.items():
            cancel_tracker()
        self._cancel_trackers.clear()
