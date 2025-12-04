// server.js ajustado conforme solicitado
const express = require('express');
const http = require('http');
const socketio = require('socket.io');
const mqtt = require('mqtt');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = socketio(server);

// ---- CONFIGURAÇÕES MQTT ----
const BROKER_URL = 'mqtt://test.mosquitto.org';
const TOPIC_TEMP = "iot/temperatura/#";  // Recebe temperatura;erro;potencia do Python
const TOPIC_ALERT = "iot/alerta/#";      // Caso envie alertas
const TOPIC_SETPOINT_REQUEST = "iot/setpoint"; // Envia do dashboard -> Python

const client = mqtt.connect(BROKER_URL);

client.on('connect', () => {
    console.log('Conectado ao Broker MQTT');
    client.subscribe([TOPIC_TEMP, TOPIC_ALERT], (err) => {
        if (!err) {
            console.log('Inscrito nos tópicos (temperatura, alertas).');
        }
    });
});

client.on('message', (topic, message) => {
    const payload = message.toString();
    console.log(`[MQTT] Tópico: ${topic} | Payload: ${payload}`);

    if (topic.startsWith("iot/temperatura")) {
        const [tempStr, erroStr, potenciaStr] = payload.split(';');
        const data = {
            timestamp: new Date().toLocaleTimeString(),
            temperatura: parseFloat(tempStr),
            erro: parseFloat(erroStr),
            potencia: parseFloat(potenciaStr)
        };
        io.sockets.emit('mqttData', data);
    }

    if (topic.startsWith("iot/alerta")) {
        io.sockets.emit('mqttAlert', payload);
    }
});

// ---- SERVIDOR WEB ----
app.use(express.static(path.join(__dirname, 'public')));
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// ---- SOCKET.IO FRONT-END ----
io.on('connection', (socket) => {
    console.log('Cliente conectado ao dashboard');

    socket.on('sendSetpoint', (newSetpoint) => {
        console.log(`[SOCKET] Novo setpoint recebido: ${newSetpoint}`);

        client.publish(TOPIC_SETPOINT_REQUEST, newSetpoint.toString(), { qos: 1 }, (error) => {
            if (error) {
                console.error('Erro ao publicar setpoint MQTT:', error);
            } else {
                console.log('Setpoint enviado ao Python com sucesso.');
            }
        });
    });

    socket.on('disconnect', () => {
        console.log('Cliente dashboard desconectado');
    });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`Servidor rodando em http://localhost:${PORT}`);
});
