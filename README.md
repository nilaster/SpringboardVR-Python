# springboardvr: Python library for interacting with Springboard VR API

This library provides Python functions to interact with the Springboard VR API for managing sessions and other functionalities.

| IMPORTANT: In its current state, this package can only manage sessions. See [Usage](#usage) below.

## Requirements

- Python 3.9+

## Installation

```Bash
pip install springboardvr
```

## Usage

### Import the library:

```python
import springboardvr
```

### Create a client object:

```python
client = springboardvr.SpringboardVR(account_email="your_email@example.com", account_password="your_password")
```

### Create a new booking session:

```python
location_id = "1234"  # Replace with your location ID
experience_id = "5678"  # Replace with your experience ID
station_id = "9012"  # Replace with your station ID
experience_start_time = datetime.datetime(2024, 3, 1, 10, 0)  # Replace with your start time
duration = 60  # Duration in minutes

booking_id, station_session_id = client.sessions.create_session(
    location_id, experience_id, station_id, experience_start_time, duration
)

print(f"Booking ID: {booking_id}")
print(f"Station Session ID: {station_session_id}")
```

### Update an existing booking session:

```python
booking_id = "your_booking_id"
station_session_id = "your_station_session_id"
new_start_time = datetime.datetime(2024, 3, 2, 11, 0)
new_duration = 30

client.sessions.update_session(booking_id, station_session_id, new_start_time, new_duration)
```

### Delete a booking session:

```python
booking_id = "your_booking_id"

client.sessions.delete_session(booking_id)
```

### Start a booking session:

```python
booking_id = "your_booking_id"
station_id = "your_station_id"
station_session_id = "your_station_session_id"
experience_start_time = datetime.datetime(2024, 3, 1, 10, 0)
duration = 60

start_time, end_time = client.sessions.start_session(
    booking_id, station_id, station_session_id, experience_start_time, duration
)

print(f"Session started at: {start_time}")
print(f"Session ends at: {end_time}")
```
