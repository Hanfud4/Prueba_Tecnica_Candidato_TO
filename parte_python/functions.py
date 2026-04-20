import json
import math
import pandas as pd
import numpy as np


VELOCIDAD_MEDIA = 20/60/60 # 20 km/h en km/s

def preprocesar_datos(path):
    data = json.load(open(path))
    data_vehiculos = pd.DataFrame(data['vehiculos'])
    
    data_vehiculos['hora_inicio_jornada'] = data_vehiculos['inicio_jornada'].apply(lambda x: x['hora'])
    data_vehiculos['lat_inicio_jornada'] = data_vehiculos['inicio_jornada'].apply(lambda x: x['lat'])
    data_vehiculos['lon_inicio_jornada'] = data_vehiculos['inicio_jornada'].apply(lambda x: x['lon'])

    data_vehiculos['hora_fin_jornada'] = data_vehiculos['fin_jornada'].apply(lambda x: x['hora'])
    data_vehiculos['lat_fin_jornada'] = data_vehiculos['fin_jornada'].apply(lambda x: x['lat'])
    data_vehiculos['lon_fin_jornada'] = data_vehiculos['fin_jornada'].apply(lambda x: x['lon'])

    data_vehiculos.drop(columns=['inicio_jornada', 'fin_jornada'], inplace=True)

    data_viajes = pd.DataFrame(data['viajes'])
    data_viajes['lat_origen'] = data_viajes['origen'].apply(lambda x: x['lat'])
    data_viajes['lon_origen'] = data_viajes['origen'].apply(lambda x: x['lon'])

    data_viajes['lat_destino'] = data_viajes['destino'].apply(lambda x: x['lat'])
    data_viajes['lon_destino'] = data_viajes['destino'].apply(lambda x: x['lon'])

    data_viajes.drop(columns=['origen', 'destino'], inplace=True)
    data_viajes['tiempo_en_ruta'] = data_viajes.apply(lambda x: _haversine(x['lat_origen'], x['lon_origen'], x['lat_destino'], x['lon_destino']) / VELOCIDAD_MEDIA, axis=1)
    data_viajes['hora_finalizacion'] = data_viajes['hora_presentacion'] + data_viajes['tiempo_en_ruta']
    
    return data_viajes, data_vehiculos

def _haversine(lat1, lon1, lat2, lon2):

      R = 3959.87433 # this is in miles.  For Earth radius in kilometers use 6372.8 km

      dLat = math.radians(lat2 - lat1)
      dLon = math.radians(lon2 - lon1)
      lat1 = math.radians(lat1)
      lat2 = math.radians(lat2)

      a = math.sin(dLat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dLon/2)**2
      c = 2*math.asin(math.sqrt(a))
      return R * c
