# Create GitHub Release for v1.4.1

Since GitHub CLI is not available, please create the release manually:

## Steps:

1. Go to: https://github.com/Ierlandfan/nl_fuel_price_tracker/releases/new

2. Fill in the form:
   - **Tag**: Select `v1.4.1` from dropdown
   - **Release title**: `v1.4.1 - Fix Config Flow 500 Error`
   - **Description**: Copy the content below

---

## 🐛 Bug Fix Release

### Fixed
- **Config Flow 500 Error**: Resolved "Server got itself in trouble" error when trying to edit integration configuration
  - Added proper error handling for notification services loading
  - Added early return check for `self.hass` existence
  - Config flow now works reliably even if notification services can't be loaded

### Technical Details
- Improved `_get_notify_services()` method in both `FuelPricesConfigFlow` and `FuelPricesOptionsFlow`
- Added fallback to default notification services on any exception
- Enhanced error handling in `async_step_init()` method

### Upgrade Notes
- Simply update via HACS to get this fix
- No configuration changes needed
- Fixes the inability to edit existing integrations

---

**Full Changelog**: https://github.com/Ierlandfan/nl_fuel_price_tracker/compare/v1.4.0...v1.4.1

---

3. Click **"Publish release"**

Once published, HACS will show v1.4.1 as available for update.
