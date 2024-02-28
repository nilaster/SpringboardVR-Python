import datetime
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .client import SpringboardVR


class SessionAPI(object):
    def __init__(self, springboardvr_client: SpringboardVR) -> None:
        """
        Initializes the SessionAPI class with a `Client` object.

        Args:
            client: The `Client` object used for interacting with the Springboard VR API.
        """
        self._springboardvr_client = springboardvr_client

    def create_session(
        self,
        location_id: str,
        experience_id: str,
        station_id: str,
        experience_start_time: datetime.datetime,
        duration: int,
        title: str,
    ) -> tuple[str, str]:
        """
        Creates a new booking session on Springboard VR.

        Args:
            location_id: The ID of the Springboard VR location.
            experience_id: The ID of the experience to be booked.
            station_id: The ID of the station where the experience will take place.
            experience_start_time: The start time of the experience.
            duration: The duration of the experience in minutes.

        Returns:
            A tuple containing the ID of the booking and the ID of the booking station session.

        Raises:
            Exception: If there are errors in the Springboard VR API response.
        """
        experience_end_time = experience_start_time + datetime.timedelta(
            minutes=duration
        )
        payload = {
            "query": """
                mutation storeBooking ($booking: BookingInput) {
                    storeBooking(booking: $booking) {
                        id
                        startTime
                        bookingStationTimes {
                            id
                        }
                    }
                }
            """,
            "variables": {
                "booking": {
                    "bookingStationTimes": [
                        {
                            "amountDue": 0,
                            "amountPaid": 0,
                            "coupon": {},
                            "discount": {},
                            "experience": {
                                "id": experience_id,
                            },
                            "startedAt": None,
                            "station": {
                                "id": station_id,
                            },
                            "endTime": experience_end_time.isoformat(),
                            "tier": {
                                "id": "custom",
                                "length": duration,
                                "price": 0,
                            },
                        }
                    ],
                    "host": {
                        "firstName": None,
                        "lastName": None,
                        "email": None,
                        "phone": None,
                    },
                    "location": {
                        "id": location_id,
                    },
                    "notifyHost": False,
                    "numPlayers": 1,
                    "startTime": experience_start_time.isoformat(),
                    "title": title,
                },
            },
        }

        res = self._springboardvr_client._client.post(
            "https://api.springboardvr.com/graphql", json=payload
        )
        json = res.json()

        if "errors" in json:
            raise Exception(json["errors"])  # TODO: Improve this exception

        data = json["data"]["storeBooking"]
        return (data["id"], data["bookingStationTimes"][0]["id"])

    def update_session(
        self,
        booking_id: str,
        station_session_id: str,
        experience_start_time: datetime.datetime,
        duration: int,
    ):
        """
        Updates an existing booking session on Springboard VR.

        Args:
            booking_id: The ID of the booking session to update.
            station_session_id: The ID of the station session to update.
            experience_start_time: The new start time of the experience.
            duration: The new duration of the experience in minutes.

        Raises:
            Exception: If there are errors in the Springboard VR API response.
        """
        experience_end_time = experience_start_time + datetime.timedelta(
            minutes=duration
        )
        payload = {
            "query": """
                mutation storeBooking ($booking: BookingInput) {
                    storeBooking (booking: $booking) {
                        id
                    }
                }
            """,
            "variables": {
                "booking": {
                    "id": booking_id,
                    "startTime": experience_start_time.isoformat(),
                    "bookingStationTimes": [
                        {
                            "id": station_session_id,
                            "endTime": experience_end_time.isoformat(),
                        }
                    ],
                },
            },
        }
        res = self._springboardvr_client._client.post(
            "https://api.springboardvr.com/graphql", json=payload
        )

        json = res.json()
        if "errors" in json:
            raise Exception(json["errors"])

    def delete_session(self, booking_id: str) -> None:
        """
        Deletes a booking session on Springboard VR.

        Args:
            booking_id: The ID of the booking session to delete.

        Raises:
            Exception: If there are errors in the Springboard VR API response.
        """
        payload = {
            "query": """
                mutation deleteBooking ($booking: BookingInput) {
                    deleteBooking (booking: $booking) {
                        id
                    }
                }
            """,
            "variables": {
                "booking": {
                    "id": booking_id,
                }
            },
        }
        res = self._springboardvr_client._client.post(
            "https://api.springboardvr.com/graphql", json=payload
        )

        json = res.json()
        if "errors" in json:
            raise Exception(json["errors"])

    def start_session(
        self,
        booking_id: str,
        station_id: str,
        station_session_id: str,
        experience_start_time: datetime.datetime,
        duration: int,
    ) -> tuple[datetime.datetime, datetime.datetime]:
        """
        Starts a booking session on Springboard VR.

        Args:
            booking_id: The ID of the booking session to start.
            station_id: The ID of the station where the experience will take place.
            station_session_id: The ID of the station session.
            experience_start_time: The booked start time of the experience.
            duration: The duration of the experience in minutes.

        Returns:
            A tuple containing the actual start time and end time of the session.

        Raises:
            Exception: If there are errors in the Springboard VR API response.
        """
        now = datetime.datetime.now()
        if now < experience_start_time:
            start_time = now
            end_time = start_time + datetime.timedelta(minutes=duration)
        elif now > experience_start_time:
            start_time = now
            timedelta = now - start_time
            end_time = start_time + (datetime.timedelta(minutes=duration) - timedelta)
        else:
            start_time = experience_start_time
            end_time = start_time + datetime.timedelta(minutes=duration)

        payload = {
            "query": """
                mutation storeBooking ($booking: BookingInput) {
                    storeBooking (booking: $booking) {
                        id
                    }
                }
            """,
            "variables": {
                "booking": {
                    "id": booking_id,
                    "checkedInAt": start_time.isoformat(),
                }
            },
        }
        res = self._springboardvr_client._client.post(
            "https://api.springboardvr.com/graphql", json=payload
        )

        json = res.json()
        if "errors" in json:
            raise Exception(json["errors"])

        payload = {
            "query": """
                mutation storeBookingStationTime ($bookingStationTime: BookingStationTimeInput) {
                    storeBookingStationTime (bookingStationTime: $bookingStationTime) {
                        id
                    }
                }
            """,
            "variables": {
                "bookingStationTime": {
                    "id": station_session_id,
                    "startedAt": start_time.isoformat(),
                    "endTime": end_time.isoformat(),
                    "station": {
                        "id": station_id,
                    },
                }
            },
        }
        res = self._springboardvr_client._client.post(
            "https://api.springboardvr.com/graphql", json=payload
        )

        json = res.json()
        if "errors" in json:
            raise Exception(json["errors"])

        return start_time, end_time

    def pause_session(
        self,
        station_session_id: str,
        pause_duration: int,
    ):
        """
        Pauses a booking session on Springboard VR.

        Args:
            station_session_id: The ID of the station session to pause.
            pause_duration: The duration of the pause in minutes.

        Raises:
            Exception: If there are errors in the Springboard VR API response.
        """
        now = datetime.datetime.now()

        payload = {
            "query": """
                mutation storeBookingStationTime ($bookingStationTime: BookingStationTimeInput) {
                    storeBookingStationTime (bookingStationTime: $bookingStationTime) {
                        id
                    }
                }
            """,
            "variables": {
                "bookingStationTime": {
                    "id": station_session_id,
                    "pausedAt": now.isoformat(),
                    "pausedDuration": pause_duration,
                }
            },
        }
        res = self._springboardvr_client._client.post(
            "https://api.springboardvr.com/graphql", json=payload
        )

        json = res.json()
        if "errors" in json:
            raise Exception(json["errors"])

    def unpause_session(self, station_station_id: str, end_time: datetime.datetime):
        """
        Unpauses a booking session on Springboard VR.

        Args:
            station_station_id: The ID of the station session to unpause (should be the same as `station_session_id` used in `pause_session`).
            end_time: The new end time of the session after unpausing.

        Raises:
            Exception: If there are errors in the Springboard VR API response.
        """
        payload = {
            "query": """
                mutation storeBookingStationTime ($bookingStationTime: BookingStationTimeInput) {
                    storeBookingStationTime (bookingStationTime: $bookingStationTime) {
                        id
                    }
                }
            """,
            "variables": {
                "bookingStationTime": {
                    "id": station_station_id,
                    "endTime": end_time.isoformat(),
                    "pausedAt": None,
                    "pausedDuration": None,
                }
            },
        }
        res = self._springboardvr_client._client.post(
            "https://api.springboardvr.com/graphql", json=payload
        )

        json = res.json()
        if "errors" in json:
            raise Exception(json["errors"])

    def modify_station_session_end_time(
        self, station_station_id: str, end_time: datetime.datetime
    ):
        """
        Modifies the end time of a booking session on Springboard VR.

        Args:
            station_station_id: The ID of the station session to modify.
            end_time: The new end time of the session.

        Raises:
            Exception: If there are errors in the Springboard VR API response.
        """
        payload = {
            "query": """
                mutation storeBookingStationTime ($bookingStationTime: BookingStationTimeInput) {
                    storeBookingStationTime (bookingStationTime: $bookingStationTime) {
                        id
                    }
                }
            """,
            "variables": {
                "bookingStationTime": {
                    "id": station_station_id,
                    "endTime": end_time.isoformat(),
                    "amountPaid": 0,
                    "amountDue": 0,
                    "customerCard": None,
                }
            },
        }
        res = self._springboardvr_client._client.post(
            "https://api.springboardvr.com/graphql", json=payload
        )

        json = res.json()
        if "errors" in json:
            raise Exception(json["errors"])
