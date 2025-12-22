from pydantic import BaseModel, computed_field, PrivateAttr, Field
from typing import List, Tuple, Iterator
from datetime import datetime
from itertools import cycle
import random

class Sensor(BaseModel):
    pos: Tuple[float, float, float]
    temp: float


class SerialModel(BaseModel):
    label: str = Field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))
    temperatures: List[Sensor] = Field(default_factory=list)
    voltage: float = 0.0
    amperage: float = 0.0

    def to_csv_row(self) -> list:
        """Convierte la instancia del modelo en una lista plana para una fila de CSV."""
        # Primero, los datos simples
        row_data = [self.label, self.voltage, self.amperage]
        
        # Luego, extrae solo la temperatura de cada sensor y la añade a la lista
        temp_data = [sensor.temp for sensor in self.temperatures]
        row_data.extend(temp_data)
        
        return row_data

    @classmethod
    def get_csv_header(cls, num_sensors: int) -> list[str]:
        """Genera la cabecera del CSV dinámicamente según el número de sensores."""
        header = ["label", "voltage", "amperage"]
        
        # Crea una columna para la temperatura de cada sensor (ej. temp_sensor_0, temp_sensor_1)
        temp_headers = [f"temp_sensor_{i}" for i in range(num_sensors)]
        header.extend(temp_headers)
        
        return header

class TestModel(BaseModel):
    initial_sensor_position: Tuple[Tuple[float, float, float], ...] = Field(exclude=True)
    n_temp_sensors: int = Field(exclude=True)
    temp_min: float = Field(exclude=True)
    temp_max: float = Field(exclude=True)
    _temperatures_iter: List[Iterator[float]] = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        n = 1000
        temp_segment = (self.temp_max - self.temp_min) / n
        
        self._temperatures_iter = [
            cycle(
                sorted([
                    random.uniform(
                        self.temp_max + i * temp_segment,
                        self.temp_min + (i + 1) * temp_segment
                    ) 
                for i in range(n)])
            ) 
            for _ in range(self.n_temp_sensors)
        ]

    @computed_field
    @property
    def label(self) -> str:
        return datetime.now().strftime("%H:%M:%S")

    @computed_field
    @property
    def voltage(self) -> int:
        return random.randint(0, 25)

    @computed_field
    @property
    def amperage(self) -> int:
        return random.randint(0, 10)

    @computed_field
    @property
    def temperatures(self) -> List[Sensor]:
        return [
            Sensor(
                pos=self.initial_sensor_position[i],
                temp=next(self._temperatures_iter[i])
            )
            for i in range(self.n_temp_sensors)
        ]