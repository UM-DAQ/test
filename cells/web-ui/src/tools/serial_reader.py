from serial import Serial
from threading import Thread
from src.models import SerialModel, TestModel, Sensor
from typing import Tuple, Optional
import os
import csv
import subprocess
import signal
import sys


class SerialReader(Thread):
    def __clear_serial_port(self, port):
        """
        Busca y termina cualquier proceso que esté usando el puerto serial especificado.
        Funciona solo en sistemas Linux.
        """
        if not sys.platform.startswith("linux"):
            print(
                "Advertencia: La limpieza automática del puerto solo es compatible con Linux. Omitiendo."
            )
            return

        print(f"Buscando procesos que estén usando el puerto {port}...")
        try:
            # El comando 'lsof -t {port}' devuelve solo los PIDs (IDs de Proceso)
            command = ["lsof", "-t", port]
            result = subprocess.run(command, capture_output=True, text=True, check=False)

            # Si el comando tuvo éxito y devolvió PIDs
            if result.returncode == 0 and result.stdout:
                pids = result.stdout.strip().split("\n")
                print(f"Procesos encontrados con PIDs: {', '.join(pids)}. Terminando...")

                for pid_str in pids:
                    if pid_str:
                        try:
                            pid = int(pid_str)
                            os.kill(
                                pid, signal.SIGKILL
                            )  # SIGKILL es una terminación forzosa (kill -9)
                            print(f"Proceso {pid} terminado exitosamente.")
                        except (PermissionError, ProcessLookupError) as e:
                            print(
                                f"No se pudo terminar el proceso {pid}: {e}. Intenta ejecutar con 'sudo'."
                            )
                        except ValueError:
                            pass  # Ignorar si el PID no es un número válido
            else:
                print(
                    "No se encontraron procesos activos en el puerto. ¡Listo para iniciar!"
                )

        except FileNotFoundError:
            print(
                "Advertencia: No se encontró el comando 'lsof'. No se puede limpiar el puerto."
            )

    def __init__(
        self, 
        initial_sensor_position: Tuple[Tuple[float, float, float], ...], 
        n_temp_sensors: int = 6,
        device: str = "/dev/ttyACM0",
        baud_rate:int = 9600, 
        temp_min: int = 15,
        temp_max: int = 80,
        writing: bool = False,
        path: Optional[str] = None,
        in_test: bool = True
    ):
        if writing and not path:
            raise ValueError("Writing mode active but path no given")
        if len(initial_sensor_position) < n_temp_sensors:
            raise ValueError("The Sensors position given is less than number of sensors")

        self.__frame_data = ["0"] * (n_temp_sensors + 2)
        self.__sensors_positions = initial_sensor_position
        self.__in_test = in_test
        self.__writing = writing
        self.__path = path

        if not in_test:
            self.__clear_serial_port(device)

            try:
                ser = Serial(device, baud_rate)
                self.__serial = ser

            except Exception as e:
                raise IOError(
                    f"Error fatal al abrir el puerto serial después de limpiarlo: {e}"
                )

            super().__init__()
            self.start()

        else:
            self.__data_model = TestModel(
                initial_sensor_position=initial_sensor_position, 
                n_temp_sensors=n_temp_sensors,
                temp_min=temp_min,
                temp_max=temp_max
            )

    def run(self):
        while True:
            try:
                frame_data = self.__serial.readline().decode().strip().split(",")
                if len(frame_data) == len(self.__sensors_positions) + 1:
                    self.__frame_data = frame_data

            except UnicodeDecodeError:
                ...
    @property
    def data_model(self):

        if self.__in_test:
            return self.__data_model

        # "t1,t2,t3,t4,t5,t6,t7,v,a"
        data = self.__frame_data

        for i in range(len(data)):
            try:
                data[i] =float(data[i])
            except ValueError:
                data[i] = "0.0"
        
        *temps, voltage = data
        amperage = voltage / 0.7
        temps = [Sensor(pos=pos, temp=temp) for pos, temp in zip(self.__sensors_positions, temps)]

        data_model = SerialModel(
            temperatures= temps, 
            voltage=voltage, 
            amperage=amperage
        )

        if self.__writing:
            file_path = os.path.join(self.__path, "serial-data.csv") # type: ignore
            file_exists = os.path.isfile(file_path)

            with open(file_path, "a", newline="") as f:
                writer = csv.writer(f)

                if not file_exists:
                    num_sensors = len(data_model.temperatures)
                    header = SerialModel.get_csv_header(num_sensors)
                    writer.writerow(header)

                row = data_model.to_csv_row()
                writer.writerow(row)
        return data_model
