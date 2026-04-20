CREATE TABLE asignaciones (
    asignacion_id VARCHAR(5) PRIMARY KEY,
    vehiculo_id VARCHAR(6),
    viaje_id VARCHAR(5),
    orden_en_ruta INT
);

CREATE TABLE eventos_operacion (
    evento_id VARCHAR(6) PRIMARY KEY,
    vehiculo_id VARCHAR(6),
    viaje_id VARCHAR(5),
    timestamp_evento TIMESTAMP,
    tipo_evento VARCHAR(20),
    detalle TEXT
);

CREATE TABLE viajes (
    viaje_id VARCHAR(5) PRIMARY KEY,
    fecha DATE,
    inicio_programado TIMESTAMP,
    fin_programado TIMESTAMP,
    origen_comuna TEXT,
    destino_comuna TEXT,
    num_pasajeros INT
);

CREATE TABLE vehiculos (
    vehiculo_id VARCHAR(6) PRIMARY KEY,
    capacidad INT,
    base_id VARCHAR(6),
    hora_inicio_jornada TIME,
    hora_fin_jornada TIME
);


