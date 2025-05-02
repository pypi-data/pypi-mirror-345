import datetime
from typing import List


class EQEvent:
    """ Clase que representa un evento sísmico con atributos de tiempo, localización y magnitud."""

    events: List['EQEvent'] = []

    def __init__(self, time: datetime.datetime, latitude: float, longitude: float, magnitude: float):
        """
        Constructor del evento.
        :param time: fecha/hora del sismo
        :param latitude: latitud
        :param longitude: longitud
        :param magnitude: magnitud
        """
        # Índice correspondiente en la lista events
        self.eventIndex: int = -1
        # Fecha y hora
        self.time: datetime.datetime = time
        # Coordenadas
        self.latitude: float = latitude
        self.longitude: float = longitude
        # Magnitud
        self.magnitude: float = magnitude

    @classmethod
    def setEvents(cls, events: List['EQEvent']) -> None:
        """ Asigna la lista estática de eventos en la clase."""
        cls.events = events

    @classmethod
    def getEvent(cls, eventIndex: int) -> 'EQEvent':
        """ Devuelve el evento correspondiente al índice dado, usando la lista estática. """
        return cls.events[eventIndex]

    def getEventIndex(self) -> int:
        return self.eventIndex

    def getTime(self) -> datetime.datetime:
        return self.time

    def setTime(self, time: datetime.datetime) -> None:
        self.time = time

    def getLatitude(self) -> float:
        return self.latitude

    def setLatitude(self, latitude: float) -> None:
        self.latitude = latitude

    def getLongitude(self) -> float:
        return self.longitude

    def setLongitude(self, longitude: float) -> None:
        self.longitude = longitude

    def getMagnitude(self) -> float:
        return self.magnitude

    def setMagnitude(self, magnitude: float) -> None:
        self.magnitude = magnitude

    def difference(self, event: 'EQEvent') -> float:
        """
        Calcula la diferencia de tiempo en días entre este evento y otro.
        :param event: otro EQEvent
        :return: diferencia en días (float)
        """
        delta = self.time - event.time  # timedelta
        return delta.total_seconds() / (3600.0 * 24.0)

    def getTimeToString(self) -> str:
        """ Devuelve la fecha/hora como cadena. """
        # Ajusta el formato de fecha según necesites:
        return self.time.strftime("%Y-%m-%d %H:%M:%S")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EQEvent):
            return False
        return (
            self.time == other.time
            and abs(self.latitude - other.latitude) < 1e-7
            and abs(self.longitude - other.longitude) < 1e-7
            and abs(self.magnitude - other.magnitude) < 1e-7
        )

    def __hash__(self) -> int:
        return hash((self.time, round(self.latitude, 7), round(self.longitude, 7), round(self.magnitude, 7)))

    # Ordenar por fecha/tiempo
    def __lt__(self, other: 'EQEvent') -> bool:
        return self.time < other.time

    def __str__(self) -> str:
        time_str = self.time.strftime("%Y-%m-%d %H:%M:%S")
        return f"EQEvent{{time={time_str}, latitude={self.latitude}, longitude={self.longitude}, magnitude={self.magnitude}}}"