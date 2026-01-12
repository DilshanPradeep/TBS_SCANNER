# Timer Synchronization Feature

## Overview
The timer feature is now synchronized across all devices that are logged into the same IP address. When you enable or disable the timer from one device, it will automatically update on all other devices within 2 seconds.

## How It Works

### Server-Side Storage
- Timer state is stored in `timer_state.json` on the server
- This file contains:
  - `timer_enabled`: Boolean indicating if timer is enabled
  - `last_updated`: Timestamp of last update

### API Endpoints
1. **GET /api/get_timer_state**
   - Returns the current timer state from the server
   - Used by all devices to check the current state

2. **POST /api/set_timer_state**
   - Updates the timer state on the server
   - Called when admin toggles the timer
   - Body: `{"timer_enabled": true/false}`

### Client-Side Synchronization
1. **On Page Load**
   - Each device loads the current timer state from the server
   - Timer is started automatically if enabled

2. **Polling (Every 2 seconds)**
   - Each device checks the server for timer state changes
   - If a change is detected, the local state is updated automatically
   - Timer is started/stopped based on the new state

3. **When Admin Changes Timer**
   - New state is immediately saved to the server
   - All other devices detect the change within 2 seconds

## Usage

1. **Enable Timer**
   - Click the admin button (⚙️) in the top right
   - Login with credentials (TBS / TBS123)
   - Toggle "Enable Timer" switch ON
   - All devices will show the timer within 2 seconds

2. **Disable Timer**
   - Follow same steps as above
   - Toggle "Enable Timer" switch OFF
   - All devices will hide the timer within 2 seconds

## Benefits
- ✅ Consistent experience across all devices
- ✅ No need to enable timer separately on each device
- ✅ Real-time synchronization (2-second delay)
- ✅ Works for all devices on the same network/IP
- ✅ State persists even after server restart

## Technical Details
- Polling interval: 2 seconds
- Storage: JSON file (`timer_state.json`)
- Synchronization method: HTTP polling
- No database required
