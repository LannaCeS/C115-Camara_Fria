import random
import time
from flask import Flask, render_template, request, Response
import paho.mqtt.client as mqtt
from conversor import Conversor
import json
 
TOKEN_BLYNK = "hlvSU6KeHmNWj_xSqaY6rAtSOpxYkWM0"
BROKER = "blynk.cloud"
PORT = 1883
USERNAME = "device"
CLIENT_ID = ""
 
TEMP = "Temperatura"
UMI = "Umidade"
ALARM = "Alarme"
AUTH = "Autenticar"
 
 
client = mqtt.Client(client_id=CLIENT_ID)
def connect_mqtt():
    client.username_pw_set(USERNAME, TOKEN_BLYNK)
    client.connect(BROKER, PORT, 60)
    client.loop_start()
    client.subscribe( f"ds/{TEMP}")
    client.subscribe( f"ds/{UMI}")
    client.subscribe( f"ds/{ALARM}")
    client.subscribe( f"ds/{AUTH}")
 
def send_to_blynk(ds_name, value):
    topic = f"ds/{ds_name}"
    print(f"MQTT → {topic}: {value}")
    client.publish(topic, str(value))
 
app = Flask(__name__)
 
cenario = None
resistencia_atual = None
 
resistencia_ambiente = Conversor.callendar_van_dusen(25)
resistencia_congelados = Conversor.callendar_van_dusen(-23)
resistencia_refrigerados = Conversor.callendar_van_dusen(2)
 
def enviar_leituras(resistencia_pt100, umidade):
    temperatura = Conversor.pt100_para_celsius(resistencia_pt100)
 
    alarme = 1 if temperatura > 5 else 0
 
    send_to_blynk(TEMP, round(temperatura, 2))
    send_to_blynk(UMI, round(umidade, 2))
    send_to_blynk(ALARM, alarme)
 
def gerar_medidas():
    global cenario, resistencia_atual
 
    while True:
        if cenario is None:
            yield "data: {}\n\n"
            time.sleep(2)
            continue
 
        if cenario == "congelados":
            resistencia_pt100 = resistencia_congelados + random.uniform(-0.4, 0.4)
            umidade = random.uniform(35, 45)
 
        elif cenario == "resfriados":
            resistencia_pt100 = resistencia_refrigerados + random.uniform(-0.4, 0.4)
            umidade = random.uniform(70, 85)
 
        elif cenario == "congelados_porta":
            if resistencia_atual is None:
                resistencia_atual = resistencia_congelados
 
            resistencia_atual += 0.3
            if resistencia_atual > resistencia_ambiente:
                resistencia_atual = resistencia_ambiente
 
            resistencia_pt100 = resistencia_atual
            umidade = random.uniform(60, 70)
 
        elif cenario == "resfriados_porta":
            if resistencia_atual is None:
                resistencia_atual = resistencia_refrigerados
 
            resistencia_atual += 0.3
            if resistencia_atual > resistencia_ambiente:
                resistencia_atual = resistencia_ambiente
 
            resistencia_pt100 = resistencia_atual
            umidade = random.uniform(90, 95)
 
        enviar_leituras(resistencia_pt100, umidade)

        dados = {
            "temperatura": round(Conversor.pt100_para_celsius(resistencia_pt100), 2),
            "resistencia": round(resistencia_pt100, 3),
            "umidade": round(umidade, 2)
        }

        yield f"data: {json.dumps(dados)}\n\n"


        time.sleep(2)
 
 
@app.route("/")
def index():
    return render_template("index.html")
 
@app.route("/set_cenario", methods=["POST"])
def set_cenario():
    global cenario, resistencia_atual
 
    cenario = request.form["cenario"]
    resistencia_atual = None
 
    return ("", 204)
 
 
@app.route("/stream")
def stream():
    return Response(gerar_medidas(), mimetype="text/event-stream")
 
 
if __name__ == "__main__":
    connect_mqtt()
    app.run(debug=True, threaded=True)