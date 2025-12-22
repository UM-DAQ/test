from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from src.tools.models import create_battery_pack_mesh, calculate_surface_temps
from src.tools.serial_reader import SerialReader
import pyvista as pv
import asyncio
import json
import os


PATH = os.path.dirname(os.path.abspath(__file__))
TEMP_GLB_PATH = os.path.join(PATH, "static/temp_battery_pack.glb")
IN_TEST = True
WRITE = True
SENSORS_NUMBER = 6
TEMP_SCALE = (20, 100)
INITIAL_SENSOR_POSITIONS = (
    (-12.2, 0.0, 5.0),
    (-4.9, 1.5, 8.0),
    (2.4, 0.0, 2.0),
    (12.7, -1.5, 5.0),
    (4.7, -1.5, 5.0),
    (3.7, -1.5, 5.0)
)

# --- Constantes de configuración ---
CELL_RADIUS = 1.5
CELL_HEIGHT = 10.0
CELL_SPACING = 0.1
NUM_CELLS = 4

# --- Lógica para calcular centros de las celdas (para referencia) ---
total_width = NUM_CELLS * (CELL_RADIUS * 2 + CELL_SPACING) - CELL_SPACING
start_x = -total_width / 2.0 + CELL_RADIUS
cell_centers_x = [
    start_x + i * (CELL_RADIUS * 2 + CELL_SPACING) for i in range(NUM_CELLS)
]

# --- REEMPLAZA TU TUPLA CON ESTA ---
INITIAL_SENSOR_POSITIONS = (
    # Sensor 1: En la primera celda (x=-4.65), al frente, a media altura
    (cell_centers_x[0], CELL_RADIUS, CELL_HEIGHT / 2),
    # Sensor 2: En la primera celda (x=-4.65), arriba, en la parte de atrás
    (cell_centers_x[0], -CELL_RADIUS, CELL_HEIGHT * 0.9),
    # Sensor 3: En la segunda celda (x=-1.55), al frente, en la parte baja
    (cell_centers_x[1], CELL_RADIUS, CELL_HEIGHT * 0.2),
    # Sensor 4: En la tercera celda (x=1.55), en la parte de atrás, a media altura
    (cell_centers_x[2], -CELL_RADIUS, CELL_HEIGHT / 2),
    # Sensor 5: En la cuarta celda (x=4.65), al frente, arriba
    (cell_centers_x[3], CELL_RADIUS, CELL_HEIGHT * 0.9),
    # Sensor 6: En la cuarta celda (x=4.65), en la parte de atrás, abajo
    (cell_centers_x[3], -CELL_RADIUS, CELL_HEIGHT * 0.2),
)


app = FastAPI()
app.mount("/static", StaticFiles(directory=os.path.join(PATH, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(PATH, "templates"))


# --- Endpoints ---
@app.get("/", response_class=HTMLResponse)
async def get_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    base_mesh = create_battery_pack_mesh(num_cells=4)
    serial_reader = SerialReader(
        INITIAL_SENSOR_POSITIONS,
        SENSORS_NUMBER,
        device="/dev/ttyUSB1",
        baud_rate=115200,
        writing=WRITE,
        path=PATH,
        in_test=IN_TEST,
    )

    try:
        while True:
            current_mesh = base_mesh.copy()
            temps = serial_reader.data_model.temperatures
            mesh_temps = calculate_surface_temps(temps, current_mesh)
            plotter = pv.Plotter(off_screen=True, lighting='light_kit')

            # 1. Añadir la malla principal USANDO EL PARÁMETRO 'name'
            plotter.add_mesh(
                current_mesh,
                scalars=mesh_temps,
                cmap='jet',
                clim=TEMP_SCALE,
                show_scalar_bar=False,
                name='battery_pack' # <-- Forma correcta de nombrar el objeto
            )

            # 2. Añadir cada sensor USANDO EL PARÁMETRO 'name'
            for i, sensor in enumerate(INITIAL_SENSOR_POSITIONS):
                sensor_marker = pv.Sphere(radius=0.8, center=sensor) 

                plotter.add_mesh(
                    sensor_marker, 
                    color='black', 
                    name=f'sensor_{i}'
                )

            plotter.export_gltf(TEMP_GLB_PATH)
            plotter.close()

            await websocket.send_text(json.dumps({
                'type': 'update_model', 
                'model_url': f"/static/{os.path.basename(TEMP_GLB_PATH)}",
                'mesh_temps': mesh_temps,
                'data': serial_reader.data_model.model_dump()
            }))
            await asyncio.sleep(1)
    except Exception as e:
        print(f"WebSocket desconectado: {e}")
    finally:
        await websocket.close()
