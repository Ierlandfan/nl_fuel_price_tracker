"""Price change notification manager for Dutch Fuel Prices."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import (
    DOMAIN,
    CONF_NOTIFY_ON_CHANGE,
    CONF_NOTIFY_SERVICES,
    CONF_PRICE_DROP_THRESHOLD,
    CONF_PRICE_INCREASE_THRESHOLD,
    FUEL_TYPES,
)

_LOGGER = logging.getLogger(__name__)


class PriceChangeNotificationManager:
    """Manage price change notifications."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the price change notification manager."""
        self.hass = hass
        self._previous_prices: dict[str, float] = {}

    async def check_and_notify(
        self,
        entry: ConfigEntry,
        current_price: float,
        station_data: dict[str, Any],
    ) -> None:
        """Check for price changes and send notifications if thresholds are exceeded."""
        if not entry.data.get(CONF_NOTIFY_ON_CHANGE, False):
            return

        notify_services = entry.data.get(CONF_NOTIFY_SERVICES, [])
        if not notify_services:
            return

        entry_id = entry.entry_id
        previous_price = self._previous_prices.get(entry_id)

        if previous_price is None:
            self._previous_prices[entry_id] = current_price
            return

        price_change = current_price - previous_price

        drop_threshold = entry.data.get(CONF_PRICE_DROP_THRESHOLD, 0.03)
        increase_threshold = entry.data.get(CONF_PRICE_INCREASE_THRESHOLD, 0.03)

        fuel_type = entry.data.get("fuel_type", "euro95")
        fuel_name = FUEL_TYPES.get(fuel_type, fuel_type)
        location_name = entry.data.get("location_name", "Unknown")
        station_name = station_data.get("name", "Unknown")

        if price_change <= -drop_threshold:
            await self._send_notification(
                notify_services,
                "💚 Fuel Price Drop",
                f"{fuel_name} at {station_name} has dropped by €{abs(price_change):.3f}/L! "
                f"Now €{current_price:.3f}/L (was €{previous_price:.3f}/L). "
                f"Location: {location_name}",
                station_data,
            )
            _LOGGER.info(
                "Price dropped from €%.3f to €%.3f for %s",
                previous_price,
                current_price,
                entry_id,
            )

        elif price_change >= increase_threshold:
            await self._send_notification(
                notify_services,
                "📈 Fuel Price Increase",
                f"{fuel_name} at {station_name} has increased by €{price_change:.3f}/L. "
                f"Now €{current_price:.3f}/L (was €{previous_price:.3f}/L). "
                f"Location: {location_name}",
                station_data,
            )
            _LOGGER.info(
                "Price increased from €%.3f to €%.3f for %s",
                previous_price,
                current_price,
                entry_id,
            )

        self._previous_prices[entry_id] = current_price

    async def _send_notification(
        self,
        services: list[str],
        title: str,
        message: str,
        station_data: dict[str, Any] | None = None,
    ) -> None:
        """Send notification to all configured services with Telegram enhancements."""
        for service in services:
            try:
                # Check if using telegram_bot service (direct) or notify service
                if service == "telegram_bot" or service.startswith("telegram_bot."):
                    await self._send_telegram_bot_notification(
                        title, message, station_data
                    )
                elif "telegram" in service.lower():
                    # Support both 'notify.telegram' and 'telegram' formats
                    if not service.startswith("notify."):
                        service = f"notify.{service}"
                    await self._send_telegram_notify_notification(
                        service, title, message, station_data
                    )
                else:
                    # Standard notify service (mobile_app, etc.)
                    if not service.startswith("notify."):
                        service = f"notify.{service}"
                    
                    notification_data = {
                        "title": title,
                        "message": message,
                    }
                    
                    await self.hass.services.async_call(
                        "notify",
                        service.replace("notify.", ""),
                        notification_data,
                        blocking=False,
                    )
            except Exception as err:
                _LOGGER.error("Failed to send notification to %s: %s", service, err)
    
    async def _send_telegram_bot_notification(
        self,
        title: str,
        message: str,
        station_data: dict[str, Any] | None = None,
    ) -> None:
        """Send notification using telegram_bot.send_message service."""
        # Format message with HTML
        formatted_message = self._format_html_message(message, station_data)
        
        # Build inline keyboard
        inline_keyboard = None
        if station_data:
            lat = station_data.get("latitude")
            lon = station_data.get("longitude")
            if lat and lon:
                inline_keyboard = [
                    [["🗺️ Open in Google Maps", f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"]],
                    [["🧭 Navigate", f"https://www.google.com/maps/dir/?api=1&destination={lat},{lon}"]]
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
        if station_data:
            lat = station_data.get("latitude")
            lon = station_data.get("longitude")
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
    
    async def _send_telegram_notify_notification(
        self,
        service: str,
        title: str,
        message: str,
        station_data: dict[str, Any] | None = None,
    ) -> None:
        """Send notification using notify.telegram service."""
        notification_data = {
            "title": title,
            "message": self._format_html_message(message, station_data),
            "data": {
                "parse_mode": "HTML",
            },
        }
        
        # Add location and inline keyboard if available
        if station_data:
            lat = station_data.get("latitude")
            lon = station_data.get("longitude")
            if lat and lon:
                # Send location separately for better map display
                await self.hass.services.async_call(
                    "notify",
                    service.replace("notify.", ""),
                    {
                        "message": "📍 Station Location",
                        "data": {
                            "location": {
                                "latitude": lat,
                                "longitude": lon,
                            }
                        }
                    },
                    blocking=False,
                )
                
                # Add inline keyboard with navigation buttons
                notification_data["data"]["inline_keyboard"] = [
                    [
                        {
                            "text": "🗺️ Open in Google Maps",
                            "url": f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
                        }
                    ],
                    [
                        {
                            "text": "🧭 Navigate",
                            "url": f"https://www.google.com/maps/dir/?api=1&destination={lat},{lon}"
                        }
                    ]
                ]
        
        await self.hass.services.async_call(
            "notify",
            service.replace("notify.", ""),
            notification_data,
            blocking=False,
        )

    def _format_html_message(self, message: str, station_data: dict[str, Any] | None) -> str:
        """Format message with HTML for Telegram."""
        if not station_data:
            return message
        
        station_name = station_data.get("name", "Unknown")
        price = station_data.get("price", 0)
        distance = station_data.get("distance", 0)
        address = station_data.get("address", "")
        
        # HTML formatted message
        html_msg = f"<b>{message.split('at')[0]}</b>\n\n"
        html_msg += f"⛽ <b>{station_name}</b>\n"
        html_msg += f"💰 <b>€{price:.3f}/L</b>\n"
        html_msg += f"📍 {distance}km away\n"
        if address:
            html_msg += f"🏠 {address}\n"
        
        return html_msg

    def clear_price(self, entry_id: str) -> None:
        """Clear stored price for an entry."""
        self._previous_prices.pop(entry_id, None)
