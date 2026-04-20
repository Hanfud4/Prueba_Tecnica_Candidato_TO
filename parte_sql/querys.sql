-- Construir una consulta que entregue, por fecha: viajes_totales, pasajeros_totales, viajes_asignados y viajes_no_asignados.

COPY(
    SELECT v.fecha,
    COUNT(v.viaje_id) AS viajes_totales,
    SUM(v.num_pasajeros) AS pasajeros_totales,
    COUNT(a.viaje_id) AS viajes_asignados,
    COUNT(v.viaje_id) - COUNT(a.viaje_id) AS viajes_no_asignados
    FROM viajes v
    LEFT JOIN asignaciones a ON v.viaje_id = a.viaje_id
    GROUP BY v.fecha
    ) 
TO 'C:/Users/pato2/Desktop/Codigos/Prueba/Prueba_Tecnica_Candidato/parte_sql/outputs/q1.csv' CSV HEADER;

-- Construir una consulta que entregue, por vehículo: viajes_asignados, pasajeros_transportados, primera_salida_programada y última_llegada_programada.


COPY(
SELECT veh.vehiculo_id,
    sum(res.num_pasajeros) AS pasajeros_transportados,
    min(res.inicio_programado) AS primera_salida_programada,
    max(res.fin_programado) AS ultima_llegada_programada
FROM vehiculos veh
LEFT JOIN (SELECT 
    a.vehiculo_id,
    via.viaje_id,
    via.num_pasajeros,
    via.inicio_programado,
    via.fin_programado
    FROM viajes via
    LEFT JOIN asignaciones a ON via.viaje_id = a.viaje_id) res 
ON res.vehiculo_id = veh.vehiculo_id
GROUP BY veh.vehiculo_id)
TO 'C:/Users/pato2/Desktop/Codigos/Prueba/Prueba_Tecnica_Candidato/parte_sql/outputs/q2.csv' CSV HEADER;

-- Construir una consulta que liste todos los viajes no asignados, ordenados por fecha e inicio_programado.
COPY(
SELECT v.viaje_id,
 v.fecha,
 v.inicio_programado
FROM viajes v
LEFT JOIN asignaciones a ON v.viaje_id = a.viaje_id
WHERE a.viaje_id IS NULL
ORDER BY v.fecha, v.inicio_programado
) TO 'C:/Users/pato2/Desktop/Codigos/Prueba/Prueba_Tecnica_Candidato/parte_sql/outputs/q3.csv' CSV HEADER;

-- Q4. Construir una consulta que detecte conflictos temporales consecutivos dentro de una misma ruta de un vehículo. Para este punto, considera conflicto cuando el fin_programado de un viaje es posterior al inicio_programado del siguiente viaje según orden_en_ruta. Se espera uso de funciones de ventana o una lógica equivalente.

COPY(
SELECT 
    v.inicio_programado,
    v.fin_programado,
    a.vehiculo_id,
    a.orden_en_ruta,
    LEAD(v.inicio_programado) OVER (PARTITION BY a.vehiculo_id ORDER BY a.orden_en_ruta) AS inicio_programado_siguiente,
    CASE
        WHEN v.fin_programado <= LEAD(v.inicio_programado) OVER (PARTITION BY a.vehiculo_id ORDER BY a.orden_en_ruta) THEN 'No conflicto'    
        ELSE 'Conflicto'
    END AS diagnostico
FROM viajes v
LEFT JOIN asignaciones a ON a.viaje_id = v.viaje_id
ORDER BY v.viaje_id
) TO 'C:/Users/pato2/Desktop/Codigos/Prueba/Prueba_Tecnica_Candidato/parte_sql/outputs/q4.csv' CSV HEADER;


-- Q5. Usando la tabla eventos_operacion, construir una consulta que entregue por fecha el porcentaje de viajes asignados cuyo inicio_real ocurrió con más de 10 minutos de atraso respecto de inicio_programado.
