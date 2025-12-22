const stackedCtx = document.getElementById('stacked-area').getContext('2d');
const stackedAreaChart = new Chart(stackedCtx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Voltage',
            data: [],
            backgroundColor: 'rgba(54, 162, 235, 0.5)',
            borderColor: 'rgba(54, 162, 235, 1)',
            fill: true,
            tension: 0.3
        }, {
            label: 'Amperage',
            data: [],
            backgroundColor: 'rgba(255, 99, 132, 0.5)',
            borderColor: 'rgba(255, 99, 132, 1)',
            fill: true,
            tension: 0.3
        }]
    },
    options: {
        animation: {
            duration: 250 // Ideal para gráficos en tiempo real
        },
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                title: {
                    display: true,
                    text: 'Valor',
                    color: '#A3A3A3'
                },
                beginAtZero: true,
                ticks: { color: '#A3A3A3' },
                grid: { color: '#404040' }
            },
            x: {
                display: false
            }
        },
        plugins: {
            title: {
                display: true,
                text: 'Voltage & Amperage',
                color: '#F5F5F5',
                font: { size: 16 }
            },
            legend: {
                position: 'top',
                labels: {
                    color: '#F5F5F5'
                }
            }
        }
    }
});

const maxValues = 20; // Limitar a 20 puntos en el gráfico de línea
const voltageEl = document.getElementById("voltage");
const amperageEl = document.getElementById("amperage");

// Función global para actualizar el gráfico de línea
window.updateStackedAreaChart = (label, voltageData, amperageData) => {
    const chartData = stackedAreaChart.data;

    // Añadir nueva etiqueta (tiempo)
    if (chartData.labels.length >= maxValues) {
        chartData.labels.shift(); // Eliminar la más antigua
    }
    chartData.labels.push(label);

    // Añadir nuevo dato de voltaje
    if (chartData.datasets[0].data.length >= maxValues) {
        chartData.datasets[0].data.shift();
    }
    chartData.datasets[0].data.push(voltageData);

    // Añadir nuevo dato de amperaje
    if (chartData.datasets[1].data.length >= maxValues) {
        chartData.datasets[1].data.shift();
    }
    chartData.datasets[1].data.push(amperageData);

    // Actualizar los textos
    voltageEl.innerText = `${voltageData.toFixed(2)}`;
    amperageEl.innerText = `${amperageData.toFixed(2)}`;

    // Actualizar el gráfico
    stackedAreaChart.update();
};
