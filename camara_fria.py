import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import time
import matplotlib.pyplot as plt
import paho.mqtt.client as mqtt
import sys
import json

is_ready_to_start = False #flag para a lógica fuzzy
global temperatura
global umidade
temperatura = 0
umidade = 0

def camara_fria(client_obj, temperatura, umidade):

    time.sleep(5)

    #cenários de temperatura e umidade
    for _ in range(10):
        #temperatura subindo e umidade baixando
        temperatura += 1
        umidade -= 2
        client_obj.publish("iot/temperatura/att", str(temperatura))
        client_obj.publish("iot/umidade/att", str(umidade))

        time.sleep(2) #mudar os dados de 2 em 2 segundos

    for _ in range(10):
        #temperatura subindo e umidade subindo
        temperatura += 3
        umidade += 1
        client_obj.publish("iot/temperatura/att", str(temperatura))
        client_obj.publish("iot/umidade/att", str(umidade))

        time.sleep(5) #mudar os dados de 5 em 5 segundos

    time.sleep(5) #manter a temperatura e umidade por 5 segundos

    for _ in range(10):
        #temperatura descendo e umidade baixando
        temperatura -= 1
        umidade -= 1
        client_obj.publish("iot/temperatura/att", str(temperatura))
        client_obj.publish("iot/umidade/att", str(umidade))

        time.sleep(2) #mudar os dados de 2 em 2 segundos

    for _ in range(10):
        #temperatura descendo e umidade subindo
        temperatura -= 2
        umidade += 2
        client_obj.publish("iot/temperatura/att", str(temperatura))
        client_obj.publish("iot/umidade/att", str(umidade))

        time.sleep(3) #mudar os dados de 3 em 3 segundos

#---------------MQTT-----------------#
BROKER = "test.mosquitto.org"
PORT = 1883
TOPIC_UMID = "iot/umidade/#"
TOPIC_TEMP = "iot/temperatura/#"

def on_connect(client_obj, userdata, flags, rc):
    print("Conectado com código:", rc)
    client_obj.subscribe(TOPIC_TEMP)
    client_obj.subscribe(TOPIC_UMID)

    #chamar função que envie temperaturas e umidades diferentes de tempo em tempo
    camara_fria(client_obj, temperatura= 0, umidade= 80) #umidade ideal: entre 85% e 90%; temp. ideal: -4°C e 0°C

def on_message(client_obj, userdata, msg):
    global is_ready_to_start
    print(f"[RECEBIDO] {msg.topic}: {msg.payload.decode()}")

    lista = msg.topic.split("/")
    mensagem = msg.payload.decode().split(";")
    print(mensagem)

    if(lista[1] == ("umidade") and lista[3] == ("alt")):
        try:
            #atualização da umidade
            print("humidity alteration")
            new_humidity = float(mensagem[0])
            umidade = new_humidity
            temperatura = temperatura
            print(f"[UPDATE] Temp Atual = {temperatura}")
            print(f"[UPDATE] Umidade Atual = {umidade}")

        except Exception as e:
            print("Erro ao atualizar umidade:", e)


    if(lista[1] == ("temperatura") and lista[3] == ("alt")):
        try:
            #atualização da temperatura
            print("temperature alteration")
            new_temp = float(mensagem[0])
            temperatura = new_temp
            umidade = umidade
            print(f"[UPDATE] Temp Atual = {temperatura}")
            print(f"[UPDATE] Umidade Atual = {umidade}")

        except Exception as e:
            print("Erro ao atualizar temperatura:", e)


# Inicializando conexão do cliente Mqtt
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect(BROKER, PORT, 60) 
except Exception:
    print("Não foi possivel conectar ao MQTT...")
    print("Encerrando...")
    sys.exit()    

# Iniciando Loop 
try:
    client.loop_start()

    while not is_ready_to_start:
        time.sleep(0.1) 

    try:
        camara_fria(client, temperatura, umidade)
    except KeyboardInterrupt:
        print("Encerrando...")
        client.loop_stop()

except KeyboardInterrupt:
    print("Encerrando...")
