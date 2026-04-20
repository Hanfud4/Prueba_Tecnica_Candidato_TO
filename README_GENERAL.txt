PRUEBA TÉCNICA - INGENIERO DE MODELACIÓN

Estructura entregada
--------------------
parte_python/
  enunciado_python.pdf
  instancias/
    small.json
    medium.json
    large.json
    xlarge.json

parte_sql/
  enunciado_sql.pdf
  data/
    vehiculos.csv
    viajes.csv
    asignaciones.csv
    eventos_operacion.csv

Condiciones generales
---------------------
- Duración sugerida total: 3h30 a 4h.
- Puedes usar internet, PostgreSQL y librerías estándar de Python. También puedes usar pandas y numpy.
- La entrega debe consistir solo en código y archivos generados por código.
- No se requiere un informe en PDF o PowerPoint.
- Si alguna decisión de modelamiento no está especificada, documenta tu supuesto dentro del código (comentario o docstring) o en un README breve.

Entrega esperada
----------------
Se espera una carpeta final con esta estructura:

apellido_nombre/
  python/
    solve.py
    validator.py
    outputs/
      small_solution.json
      medium_solution.json
      large_solution.json
      xlarge_solution.json
    metrics.csv
  sql/
    create_tables.sql
    load_data.sql
    queries.sql
    outputs/
      q1.csv
      q2.csv
      q3.csv
      q4.csv
      q5.csv

Recomendaciones
---------------
- Prioriza correctitud y claridad antes que sofisticación.
- Tu código debe poder ejecutarse por separado para la parte Python y la parte SQL.
- Evita depender de rutas absolutas.
