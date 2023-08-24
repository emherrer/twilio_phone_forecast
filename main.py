import os
from twilio.rest import Client
import requests
import pandas as pd
from tqdm import tqdm
import time

# 1. ARMAR URL Y EXPLORACION RESPUESTA API
city = "Constitucion"
api_key = os.environ.get("WEATHER_API_KEY")
url_clima = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={city}&days=1&aqi=no&alerts=no"

# Respuesta
response = requests.get(url_clima).json()
response.keys()

# N° registros
numero_reg = len(response.get("forecast").get(
    "forecastday")[0].get("hour"))  # 24 registros

# Exploracion para registro idx=0
# Obteniendo Fecha (año-mes-dia)
response.get("forecast").get("forecastday")[
    0].get("hour")[0].get("time").split()[0]

# Obteniendo Hora (0-24)
int(response.get("forecast").get("forecastday")[0].get(
    "hour")[0].get("time").split()[1].split(":")[0])

# Obteniendo condicion
response.get("forecast").get("forecastday")[0].get(
    "hour")[0].get("condition").get("text")

# Obteniendo temperatura °Celsius
response.get("forecast").get("forecastday")[0].get("hour")[0].get("temp_c")

# Lluvia (si=1, no=0)
response.get("forecast").get("forecastday")[
    0].get("hour")[0].get("will_it_rain")

# Probabilidad de lluevia
response.get("forecast").get("forecastday")[
    0].get("hour")[0].get("chance_of_rain")


# 2. CREANDO DATA-FRAME
def get_forecast(response, i):
    fecha = response.get("forecast").get("forecastday")[
        0].get("hour")[i].get("time").split()[0]
    hora = int(response.get("forecast").get("forecastday")[0].get(
        "hour")[i].get("time").split()[1].split(":")[0]) + int(1)
    condicion = response.get("forecast").get("forecastday")[
        0].get("hour")[i].get("condition").get("text")
    temp_c = response.get("forecast").get("forecastday")[
        0].get("hour")[i].get("temp_c")
    lluvia = response.get("forecast").get("forecastday")[
        0].get("hour")[i].get("will_it_rain")
    prob_lluvia = response.get("forecast").get("forecastday")[
        0].get("hour")[i].get("chance_of_rain")

    return fecha, hora, condicion, temp_c, lluvia, prob_lluvia

fecha = response.get("forecast").get("forecastday")[
        0].get("hour")[0].get("time").split()[0]

datos = []
for i in tqdm(range(numero_reg), colour="green"):
    datos.append(get_forecast(response=response, i=i))
    
df = pd.DataFrame(datos)

# - data wrangling
df_wrangled = df \
    .set_axis(
        ["fecha", "hora", "condicion", "temperatura_c", "lluvia", "prob_lluvia"],
        axis=1) \
    .assign(fecha = lambda x: pd.to_datetime(x["fecha"])) \
    .query(f"lluvia == 1") \
    .filter(regex="(hora)|(condicion)") \
    .set_index("hora") 
    

# 3. TEMPLATE
sms_message = f"\nHola! \n\n\n El pronóstico del tiempo hoy {fecha} en {city} es: \n\n\n {str(df_wrangled)}"


# 4. MENSAJE SMS DESDE TWILIO
time.sleep(1)
account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')

client = Client(account_sid, auth_token)

message = client.messages.create(from_='+16184486717',
                      to=os.environ.get("MY_PHONE_NUMBER"),
                      body=sms_message)

print(f"Mensaje enviado {message.sid}")