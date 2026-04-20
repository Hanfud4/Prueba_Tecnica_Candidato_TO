# Script para validar que las rutas generadas cumplen con las restricciones del problema

import numpy as np
import pandas as pd
import json
import math

from functions import preprocesar_datos, _haversine

VELOCIDAD_MEDIA = 20/60/60 # 20 km/h en km/s

def validacion_de_rutas(rutas: dict, data_viajes: dict, data_vehiculos:dict, verbose: bool = False):
    error = False
    for veh, ruta in rutas.items():
        if verbose: print(f"Vehículo {veh}: {ruta}")
        if ruta == []:
            if verbose: print(f"Vehículo {veh} no tiene viajes asignados.")
            continue
        
        vehiculo = data_vehiculos[data_vehiculos['id'] == veh].iloc[0]
        # === Checkeo de factiblidad de las rutas asignadas ===
        
        # Criterio 1: que cada viaje asignado a un vehículo cumpla con las restricciones de capacidad
        for idx, viaje_id in enumerate(ruta):
            viaje = data_viajes[data_viajes['id'] == viaje_id].iloc[0]
            if vehiculo.capacidad < viaje.num_pasajeros:
                error = True
                if verbose: print(f"Error: Vehículo {veh} no tiene capacidad para el viaje {viaje_id}")
            else:
                if verbose: print(f"Vehículo {veh} tiene capacidad {vehiculo.capacidad} para el viaje {viaje_id} con {viaje.num_pasajeros} pasajeros")
        
        # Criterio 2: sucesión de viajes --> fin viaje i + deadhead i,j <= hora presentación viaje j
            viaje_siguiente = data_viajes[data_viajes['id'] == ruta[idx+1]].iloc[0] if idx + 1 < len(ruta) else None
            if viaje_siguiente is not None:
                dh = _haversine(viaje.lat_destino, viaje.lon_destino, viaje_siguiente.lat_origen, viaje_siguiente.lon_origen)
                tiempo_llegada = dh / VELOCIDAD_MEDIA
                hora_llegada = viaje.hora_finalizacion + tiempo_llegada
                if not(hora_llegada <= viaje_siguiente.hora_presentacion):
                    error = True
                    if verbose: print(f"Error: Vehículo {veh} no llega a tiempo para el viaje {viaje_siguiente.id} después de completar el viaje {viaje_id}")
                else:
                    if verbose: print(f"Vehículo {veh} llega a tiempo para el viaje {viaje_siguiente.id} después de completar el viaje {viaje_id}")
        
        # Criterio 3: primer viaje i - deadhead depot,i despues de inicio de ventana operativa
        primer_viaje = data_viajes[data_viajes['id'] == ruta[0]].iloc[0]
        dh = _haversine(vehiculo.lat_inicio_jornada, vehiculo.lon_inicio_jornada, primer_viaje.lat_origen, primer_viaje.lon_origen)
        tiempo_llegada = dh / VELOCIDAD_MEDIA   

        hora_llegada = vehiculo.hora_inicio_jornada + tiempo_llegada
        if not(hora_llegada <= primer_viaje.hora_presentacion):
            error = True
            if verbose: print(f"Error: Vehículo {veh} no llega a tiempo para el primer viaje {primer_viaje.id} después de salir del depósito: {vehiculo.hora_inicio_jornada} + {tiempo_llegada} > {primer_viaje.hora_presentacion}")
        else:
            if verbose: print(f"Vehículo {veh} llega a tiempo para el primer viaje {primer_viaje.id} después de salir del depósito")
        # Criterio 4: fin viaje i + deadhead i, depot antes de fin de ventana operativa
        ultimo_viaje = data_viajes[data_viajes['id'] == ruta[-1]].iloc[0]
        dh = _haversine(ultimo_viaje.lat_destino, ultimo_viaje.lon_destino, vehiculo.lat_fin_jornada, vehiculo.lon_fin_jornada)
        tiempo_llegada = dh / VELOCIDAD_MEDIA   
        hora_llegada = ultimo_viaje.hora_finalizacion + tiempo_llegada
        if not(hora_llegada <= vehiculo.hora_fin_jornada):
            error = True
            if verbose: print(f"Error: Vehículo {veh} no llega a tiempo al depósito después de completar el último viaje {ultimo_viaje.id}: {ultimo_viaje.hora_finalizacion} + {tiempo_llegada} > {vehiculo.hora_fin_jornada}")
        else:
            if verbose: print(f"Vehículo {veh} llega a tiempo para el ultimo viaje {ultimo_viaje.id} después de salir del depósito")
    
    return not error

if __name__ == "__main__":
    paths = ['parte_python/instancias/small.json', 'parte_python/instancias/medium.json', 'parte_python/instancias/large.json', 'parte_python/instancias/muy_large.json']
    for path in paths:
        data_viajes, data_vehiculos = preprocesar_datos(path)
        instance_name = path.split("/")[-1].split(".")[0]
        solucion = json.load(open(f'parte_python/outputs/{instance_name}_solution.json'))
        rutas_generadas = solucion['assigned_trips']
        validez = validacion_de_rutas(rutas_generadas, data_viajes, data_vehiculos, verbose=False)
        if validez:
            print(f"Solución para {instance_name} es válida.")
        else:
            print(f"Solución para {instance_name} es inválida.")