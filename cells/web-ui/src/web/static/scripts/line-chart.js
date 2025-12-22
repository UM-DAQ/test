const MAX_DATA_POINTS = 50;
const SENSOR_COLORS = [
    '#FF6384', // Rosa
    '#36A2EB', // Azul
    '#FFCE56', // Amarillo
    '#4BC0C0', // Turquesa
    '#9966FF', // Morado
    '#FF9F40'  // Naranja
];

let lineChart;
const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
   animation: {
        duration: 250 // Animación suave
    },
    scales: {
        x: {
            display: false,
        },
        y: {
            ticks: { color: '#E0E0E0' },
            grid: { color: '#444444' },
            beginAtZero: true,
            title: {
                display: true,
                text: 'Temperatura (°C)',
                color: '#E0E0E0'
            },
            
            min: 0,   // Fija el mínimo del eje Y
            max: 100  // Fija el máximo del eje Y
        }
    },
    plugins: {
        title: {
            display: true,
            text: 'Temperature Curve',
            color: '#F5F5F5',
            font: { size: 16 }
        },
        legend: {
            position: 'top',
            labels: {
                color: '#F5F5F5'
            }
        }
    },
    elements: {
        line: {
            tension: 0.3 // Líneas ligeramente curvas
        },
        point: {
            radius: 1 // Puntos pequeños
        }
    }
};

/**
 * Inicializa el gráfico de líneas de sensores.
 */
function initializeLineChart() {
    const ctx = document.getElementById('line-chart-sensors').getContext('2d');

    // Asumimos 6 sensores basados en tu contexto previo
    const datasets = [];
    for (let i = 0; i < 6; i++) {
        datasets.push({
            label: `Sensor ${i}`,
            data: [],
            borderColor: SENSOR_COLORS[i],
            backgroundColor: SENSOR_COLORS[i] + '33', // Color con opacidad
            borderWidth: 2,
            fill: false
        });
    }

    lineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: datasets
        },
        options: chartOptions
    });
}

/**
 * Actualiza el gráfico con nuevos datos recibidos del WebSocket.
 * @param {string} newLabel - La nueva etiqueta del eje X (ej. tiempo).
 * @param {number[]} newTemperatures - Un array de 6 valores de temperatura.
 */
window.updateLineChartSensors = (newLabel, newTemperatures) => {
    if (!lineChart) {
        console.error("El gráfico de líneas no está inicializado.");
        return;
    }

    try {
        // Añadir nueva etiqueta de tiempo/paso
        lineChart.data.labels.push(newLabel);

        // Añadir nuevos datos de temperatura a cada dataset
        newTemperatures.forEach((sensor, index) => {
            if (lineChart.data.datasets[index]) {
                lineChart.data.datasets[index].data.push(sensor.temp);
            }
        });

        // Limitar el historial de datos para evitar sobrecarga
        if (lineChart.data.labels.length > MAX_DATA_POINTS) {
            lineChart.data.labels.shift(); // Quita la etiqueta más antigua
            lineChart.data.datasets.forEach(dataset => {
                dataset.data.shift(); // Quita el dato más antiguo
            });
        }

        // Actualizar el gráfico sin una animación completa
        lineChart.update('none');

    } catch (error) {
        console.error("Error actualizando el gráfico de líneas:", error);
    }
};

// Inicializar el gráfico cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', initializeLineChart);

