import threading
import time
import asyncio
import datetime
import json
from .location_service import LocationService


class AsyncStaticLocationService(LocationService):
    """
    Location Servie that just provides an static position.

    Attributes
    ----------
    period : int
        Periodicity of the location update in ms.
    latitude : float
        Latitude of the static location.
    longitude : float
        Longitude of the static location.
    """

    def __init__(
        self,
        period: int = 1000,
        latitude: float = 41.387304,
        longitude: float = 2.112485,
    ) -> None:
        """
        Initialize the Static Location Service.
        period : int
            Periodicity of the location update in ms.
        static_location : dict
            The static location to provide. (In TPV format)
        """
        super().__init__()
        self.period = period
        self.latitude = latitude
        self.longitude = longitude

    async def start_async(self) -> None:
        # pylint: disable=duplicate-code
        """
        Start the Static Location Service.
        """
        while True:
            tt = datetime.datetime.fromtimestamp(time.time()).strftime(
                "%Y-%m-%dT%H:%M:%S.%f"
            )
            tt = tt[:-3]
            tt = tt + "Z"
            tt = tt.encode("utf-8")
            tpv_string = (
                b'{"class":"TPV","device":"/dev/ttyACM0","mode":3,"time":"'
                + tt
                + b'","ept":0.005,"lat":'
                + str(self.latitude).encode("utf-8")
                + b',"lon":'
                + str(self.longitude).encode("utf-8")
                + b',"alt":163.800,"epx":10.000,"epy":10.000,"epv":10.000,'
                + b'"track":0.0000,"speed":0.000,"climb":0.000,"eps":0.00}'
            )
            json_tpv = json.loads(tpv_string)
            self.send_to_callbacks(json_tpv)
            await asyncio.sleep(self.period / 1000)


class ThreadStaticLocationService(LocationService):
    """
    Location Servie that just provides an static position.

    Attributes
    ----------
    period : int
        Periodicity of the location update in ms.
    latitude : float
        Latitude of the static location.
    longitude : float
        Longitude of the static location.
    location_service_thread : threading.Thread
        The thread of the location service.
    """

    def __init__(
        self,
        period: int = 1000,
        latitude: float = 41.387304,
        longitude: float = 2.112485,
    ) -> None:
        """
        Initialize the Static Location Service.
        period : int
            Periodicity of the location update in ms.
        latitude : float
            Latitude of the static location.
        longitude : float
            Longitude of the static location.
        """
        super().__init__()
        self.period = period
        self.latitude = latitude
        self.longitude = longitude
        self.location_service_thread = threading.Thread(target=self.start, daemon=True)
        self.stop_event = threading.Event()
        self.location_service_thread.start()

    def start(self) -> None:
        # pylint: disable=duplicate-code
        """
        Start the Static Location Service.
        """
        while not self.stop_event.is_set():
            tt = datetime.datetime.fromtimestamp(time.time()).strftime(
                "%Y-%m-%dT%H:%M:%S.%f"
            )
            tt = tt[:-3]
            tt = tt + "Z"
            tt = tt.encode("utf-8")
            tpv_string = (
                b'{"class":"TPV","device":"/dev/ttyACM0","mode":3,"time":"'
                + tt
                + b'","ept":0.005,"lat":'
                + str(self.latitude).encode("utf-8")
                + b',"lon":'
                + str(self.longitude).encode("utf-8")
                + b',"alt":163.800,"epx":10.000,"epy":10.000,"epv":10.000,"track":0.0000,"speed":0.000,'
                + b'"climb":0.000,"eps":0.00}'
            )
            json_tpv = json.loads(tpv_string)
            self.send_to_callbacks(json_tpv)
            time.sleep(self.period / 1000)
