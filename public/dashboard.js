// Conecta ao Socket.IO
const socket = io();

// Elementos de interface
const currentTempEl = document.getElementById('current-temp');
const currentHumEl = document.getElementById('current-hum');
const lastUpdateEl = document.getElementById('last-update');

// Limite de pontos no gráfico
const MAX_DATA_POINTS = 30;

// --- Gráfico: Temperatura ---
const tempData = {
    labels: [],
    datasets: [{
        label: 'Temperatura (°C)',
        data: [],
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1,
        fill: false
    }]
};

const tempCtx = document.getElementById('tempChart').getContext('2d');
const tempChart = new Chart(tempCtx, {
    type: 'line',
    data: tempData,
    options: {
        responsive: true,
        scales: {
            y: { title: { display: true, text: 'Temperatura (°C)' } }
        }
    }
});

// --- Gráfico: Umidade ---
const humData = {
    labels: [],
    datasets: [{
        label: 'Umidade (%)',
        data: [],
        borderColor: 'rgb(255, 159, 64)',
        tension: 0.1,
        fill: false
    }]
};

const humCtx = document.getElementById('humChart').getContext('2d');
const humChart = new Chart(humCtx, {
    type: 'line',
    data: humData,
    options: {
        responsive: true,
        scales: {
            y: { title: { display: true, text: 'Umidade (%)' } }
        }
    }
});

// --- Recebe dados MQTT (via Node.js) ---
socket.on('mqttData', (data) => {
    const timestamp = data.timestamp;

    // Atualiza cards
    currentTempEl.textContent = data.temperatura;
    currentHumEl.textContent = data.umidade;
    lastUpdateEl.textContent = timestamp;

    // Atualiza gráficos
    tempChart.data.labels.push(timestamp);
    tempChart.data.datasets[0].data.push(data.temperatura);

    humChart.data.labels.push(timestamp);
    humChart.data.datasets[0].data.push(data.umidade);

    // Limita os dados
    if (tempChart.data.labels.length > MAX_DATA_POINTS) {
        tempChart.data.labels.shift();
        tempChart.data.datasets[0].data.shift();
    }

    if (humChart.data.labels.length > MAX_DATA_POINTS) {
        humChart.data.labels.shift();
        humChart.data.datasets[0].data.shift();
    }

    tempChart.update();
    humChart.update();
});