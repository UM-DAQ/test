from src.models import Sensor
from typing import List
import pyvista as pv
import numpy as np

def create_battery_pack_mesh(
        num_cells: int = 8, 
        cell_radius: float = 1.5, 
        cell_height: float = 10.0, 
        spacing: float = 0.1
    ) -> pv.PolyData:

    single_cell = pv.Cylinder(radius=cell_radius, height=cell_height, direction=(0, 0, 1))
    meshes = []
    total_width = num_cells * (cell_radius * 2 + spacing) - spacing
    start_x = -total_width / 2.0 + cell_radius

    for i in range(num_cells):
        x_offset = start_x + i * (cell_radius * 2 + spacing)
        cell_instance = single_cell.translate((x_offset, 0, cell_height / 2), inplace=False)
        meshes.append(cell_instance)
    return pv.merge(meshes)


def calculate_surface_temps(sensor_data: List[Sensor], mesh_to_color: pv.PolyData) -> List[float]:
    temperature_values = []
    power = 4
    mesh_points = mesh_to_color.points
    for vx, vy, vz in mesh_points:
        weighted_temps_sum, weights_sum = 0, 0
        is_at_sensor = False
        for sensor in sensor_data:
            dist = np.sqrt((vx - sensor.pos[0])**2 + (vy - sensor.pos[1])**2 + (vz - sensor.pos[2])**2)
            if dist < 0.01: final_temp = sensor.temp; is_at_sensor = True; break
            weight = 1.0 / (dist ** power)
            weighted_temps_sum += sensor.temp * weight
            weights_sum += weight
        if not is_at_sensor: final_temp = weighted_temps_sum / weights_sum if weights_sum > 0 else 0
        final_temp = max(20.0, min(final_temp, 100.0))
        temperature_values.append(float(final_temp))
    return temperature_values