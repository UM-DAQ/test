window.onload = () => {
    console.log("Starting...");

    const ws = new WebSocket("ws://localhost:8000/ws");
    ws.onmessage = function (event) {
        const payload = JSON.parse(event.data);
        const { model_url, mesh_temps, data } = payload;

        window.update3dGraph(model_url, mesh_temps, data.temperatures);
        window.updateStackedAreaChart(data.label, data.voltage, data.amperage);
        window.updateLineChartSensors(data.label, data.temperatures);
    };
};