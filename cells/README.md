# 🔋 Battery Discharge Test System

### Octubre 2025

Este proyecto ha sido diseñado para gestionar, visualizar y analizar las pruebas de descarga de celdas de batería. El sistema integra una interfaz web en tiempo real y con visualización 3D, control de hardware mediante microcontroladores y herramientas de análisis de datos.

---

## 🛠️ Stack Tecnológico

* **Backend:** [FastAPI](https://fastapi.tiangolo.com/)
* **Frontend/Templating:** [Jinja2](https://jinja.palletsprojects.com/)
* **Visualización 3D:** [PyVista](https://docs.pyvista.org/) (Modelado y renderizado 3D de celdas/pruebas)
* **Análisis de Datos:** Jupyter Notebooks, Pandas, Matplotlib.

---

## 📂 Estructura del Proyecto

El repositorio está organizado en tres pilares principales:

| Carpeta | Descripción |
| --- | --- |
| `web-ui/` | Interfaz de usuario para monitoreo en tiempo real. |
| `protoboard/` | Código del microcontrolador y diagramas de conexión. |
| `analysis/` | Notebooks de Jupyter y caracterización de sensores. |

---

## 🌐 Interfaz Web (`web-ui`)

Contiene el dashboard de visualización. Permite monitorear las métricas de descarga conforme ocurren.

### 🚀 Instalación y Ejecución

1. **Instalar dependencias:**
```bash
cd web-ui
pip install -r requirements.txt

```


2. **Iniciar el servidor:**
```bash
uvicorn src.web.main:app --reload

```


3. **Acceso:** Abre tu navegador en `http://127.0.0.1:8000`.

### ⚙️ Configuración y Modos

En el archivo `src/web/main.py` puedes ajustar las variables principales. La más importante es:

* **`IN_TEST`**:
* `True`: Modo de prueba (datos simulados).
* `False`: Modo normal (lectura de datos reales).



---

## 🛠️ Hardware y Conexiones (`protoboard`)

En esta sección encontrarás todo lo necesario para la implementación física del proyecto:

* **Código Fuente:** Firmware que debe ser cargado en el microcontrolador.
* **Diagramas:** Esquemas de conexión detallados para el montaje de la placa de prueba.

---

## 📊 Análisis de Datos (`analysis`)

Este módulo está dedicado al post-procesamiento y validación de la información:

Para poder ejecutar todos los análisis de manera correcta es necesario instalar las dependencias

```bash
cd analysis
pip install -r requirements.txt
```

* **Caracterización:** Notebooks con las pruebas realizadas a cada sensor para asegurar su precisión.
* **Visualización:** Análisis estadísticos de las curvas de descarga obtenidas.
* **Almacenamiento:** Repositorio central de datos recolectados durante las sesiones de prueba.

---

## 👥 Equipo de Desarrollo

* **Uriel Cruz Luis Ramirez** – *Líder de DAQ*
* **Hernandez Villarreal Juan Manuel**
* **Cabrera Islas Jessica Fernanda**
* **Gurrión Aquino Carlos**

---