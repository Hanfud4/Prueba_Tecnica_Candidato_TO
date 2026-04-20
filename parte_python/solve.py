# Heurística de generación de viajes

import numpy as np
import pandas as pd
import json
import math

VELOCIDAD_MEDIA = 20/60/60 # 20 km/h en km/s

def _haversine(lat1, lon1, lat2, lon2):

      R = 3959.87433 # this is in miles.  For Earth radius in kilometers use 6372.8 km

      dLat = math.radians(lat2 - lat1)
      dLon = math.radians(lon2 - lon1)
      lat1 = math.radians(lat1)
      lat2 = math.radians(lat2)

      a = math.sin(dLat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dLon/2)**2
      c = 2*math.asin(math.sqrt(a))
      return R * c


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

def heuristica_solucion(data_viajes, data_vehiculos, verbose = False):
    ids_veh = data_vehiculos['id']
    # early_veh = {row['id']: row['hora_inicio_jornada'] for _, row in data_vehiculos.iterrows()}
    # late_veh = {row['id']: row['hora_fin_jornada'] for _, row in data_vehiculos.iterrows()}
    cap_veh = {row['id']: row['capacidad'] for _, row in data_vehiculos.iterrows()}
    # Inicializo hora libre de cada vehículo con su hora de inicio de jornada
    hora_libre = {vehiculo.id: vehiculo.hora_inicio_jornada for vehiculo in data_vehiculos.itertuples()}
    ubicacion_libre = {row['id']: (row['lat_inicio_jornada'], row['lon_inicio_jornada']) for _, row in data_vehiculos.iterrows()}

    sorted_viajes = data_viajes.sort_values(by='hora_presentacion')

    viajes_no_asignados = []
    rutas = {vehiculo.id: [] for vehiculo in data_vehiculos.itertuples()}
    for viaje in sorted_viajes.itertuples():
        sin_asignar = True
        
        # Revisar si hay algún vehículo disponible en la ubicación del viaje a la hora de presentación

        # Asignar el viaje al vehículo más temprano disponible
        candidatos = []
        for vehiculo in data_vehiculos.itertuples():

            # Checkeo -1: hora de presentación mayor a inicio de ventana operativa
            if not(vehiculo.hora_inicio_jornada <= viaje.hora_presentacion):
                if verbose: print("Hora de presentacion previa al inicio de la jornada")
                continue
            # Checkeo 0: que el vehículo tenga capacidad para la cantidad de pasajeros del viaje
            if not(cap_veh[vehiculo.id] >= viaje.num_pasajeros):
                if verbose: print(f"El vehículo {vehiculo.id} no tiene capacidad para el viaje {viaje.id} \n{vehiculo.capacidad} < {viaje.num_pasajeros}")
                continue
                
            # Checkeo 1: que llegue a la hora de presentacion
            dh = _haversine(ubicacion_libre[vehiculo.id][0], ubicacion_libre[vehiculo.id][1], viaje.lat_origen, viaje.lon_origen)
            tiempo_llegada = dh / VELOCIDAD_MEDIA
            hora_minima_llegada = hora_libre[vehiculo.id] + tiempo_llegada #type:ignore
            if not(hora_minima_llegada <= viaje.hora_presentacion): # type:ignore
                if verbose: print(f"El vehículo {vehiculo.id} no llega a la hora de presentacion de {viaje.id}: {hora_libre[vehiculo.id]} + {tiempo_llegada} > {viaje.hora_presentacion}")
                continue
            
            # Checkeo 2: que el viaje + su retorno termine antes de la hora de fin de jornada del vehículo    
            hl = viaje.hora_presentacion + viaje.tiempo_en_ruta # type:ignore
            dh_retorno = _haversine(viaje.lat_destino, viaje.lon_destino, vehiculo.lat_fin_jornada, vehiculo.lon_fin_jornada) 
            tiempo_viaje = dh_retorno / VELOCIDAD_MEDIA
            if not(hora_libre[vehiculo.id] + tiempo_llegada + tiempo_viaje <= vehiculo.hora_fin_jornada): # type:ignore
                continue
            
            espera = viaje.hora_presentacion - hora_minima_llegada
            candidatos.append((vehiculo.id, espera))
        if verbose: print(viaje.id, candidatos)
        sorted_candidatos = sorted(candidatos, key=lambda x: x[1])
        vehiculo_asignado = sorted_candidatos[0][0] if len(sorted_candidatos) > 0 else None
        if verbose: print(f"Viaje {viaje.id} asignado a vehículo {vehiculo_asignado}")

        # Actualizar hora libre y ubicación libre del vehículo asignado
        if vehiculo_asignado is not None:
            hora_libre[vehiculo_asignado] = viaje.hora_finalizacion # type:ignore
            ubicacion_libre[vehiculo_asignado] = (viaje.lat_destino, viaje.lon_destino)
            rutas[vehiculo_asignado].append(viaje.id)
        else:
            if verbose: print(f"Viaje {viaje.id} no pudo ser asignado a ningún vehículo.")
            viajes_no_asignados.append(viaje.id)
        
    if verbose: print()
    print("Viajes no asignados:", viajes_no_asignados)
    print("Rutas asignadas a vehículos:", rutas)
    return rutas, viajes_no_asignados

def metricas_solucion(path, rutas_generadas, viajes_no_asignados, data_viajes, data_vehiculos):
    #  instance_name, total_trips, assigned_trips, unassigned_trips, vehicles_used, total_deadhead_km.
    instance_name = path.split('/')[-1].split('.')[0]
    assigned_trips = sum([len(r) for r in rutas_generadas.values()])
    unassigned_trips = len(viajes_no_asignados)
    vehicles_used = sum([1 for r in rutas_generadas.values() if len(r) > 0])
    total_deadhead_km = 0
    for veh, ruta in rutas_generadas.items():
        if len(ruta) == 0:
            continue
        # Desde el depósito al primer viaje
        primer_viaje = data_viajes[data_viajes['id'] == ruta[0]].iloc[0]
        vehiculo = data_vehiculos[data_vehiculos['id'] == veh].iloc[0]
        dh = _haversine(vehiculo.lat_inicio_jornada, vehiculo.lon_inicio_jornada, primer_viaje.lat_origen, primer_viaje.lon_origen)
        total_deadhead_km += dh
        
        # Entre viajes sucesivos
        for idx in range(len(ruta)-1):
            viaje_i = data_viajes[data_viajes['id'] == ruta[idx]].iloc[0]
            viaje_j = data_viajes[data_viajes['id'] == ruta[idx+1]].iloc[0]
            dh = _haversine(viaje_i.lat_destino, viaje_i.lon_destino, viaje_j.lat_origen, viaje_j.lon_origen)
            total_deadhead_km += dh
        
        # Desde el último viaje al depósito
        ultimo_viaje = data_viajes[data_viajes['id'] == ruta[-1]].iloc[0]
        dh = _haversine(ultimo_viaje.lat_destino, ultimo_viaje.lon_destino, vehiculo.lat_fin_jornada, vehiculo.lon_fin_jornada)
        total_deadhead_km += dh
        
    print(f"{instance_name}, {len(data_viajes)}, {assigned_trips}, {unassigned_trips}, {vehicles_used}, {total_deadhead_km}")
    return instance_name, len(data_viajes), assigned_trips, unassigned_trips, vehicles_used, total_deadhead_km

def solucion_a_json(path, rutas_generadas, viajes_no_asignados, metricas_solucion):
    output = {}

    instance_name = path.split('/')[-1].split('.')[0]
    output["instance_name"] = instance_name

    assigned_trips = {}
    for veh, ruta in rutas_generadas.items():
        assigned_trips[veh] = ruta
    output["assigned_trips"] = assigned_trips

    unassigned_trips = [{"viaje_id": viaje_id} for viaje_id in viajes_no_asignados]
    output["unassigned_trips"] = unassigned_trips

    output["summary"] = {"vehicles_used": metricas_solucion[4], "total_deadhead_km": metricas_solucion[5]}
    
    path_json = f'parte_python/outputs/{instance_name}_solution.json'
    with open(path_json, 'w') as f:
        json.dump(output, f, indent=4)


def main(paths):
    # Crear file metrics.csv con header
    pd.DataFrame(columns=['instance_name', 'total_trips', 'assigned_trips', 'unassigned_trips', 'vehicles_used', 'total_deadhead_km']).to_csv('parte_python/metrics.csv', index=False)
    
    for path in paths:
        data_viajes, data_vehiculos = preprocesar_datos(path)
        rutas_generadas, viajes_no_asignados = heuristica_solucion(data_viajes, data_vehiculos, verbose=False)
        metricas = metricas_solucion(path, rutas_generadas, viajes_no_asignados, data_viajes, data_vehiculos)
        # Guardar métricas en metrics.csv
        pd.DataFrame([metricas], columns=['instance_name', 'total_trips', 'assigned_trips', 'unassigned_trips', 'vehicles_used', 'total_deadhead_km']).to_csv('parte_python/metrics.csv', mode='a', header=False, index=False)  
        solucion_a_json(path, rutas_generadas, viajes_no_asignados, metricas)

if __name__ == "__main__":
    paths = ['parte_python/instancias/small.json', 'parte_python/instancias/medium.json', 'parte_python/instancias/large.json', 'parte_python/instancias/muy_large.json']
    main(paths)
    