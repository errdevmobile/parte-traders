# El Parte de las 7

Parte bursátil diario para el grupo Traders. Se publica cada día laborable antes de las 7:00 (hora de Madrid).

- `data.json`: datos del día.
- `tools/build_parte.py`: genera `index.html` a partir de `data.json` (`python3 -I tools/build_parte.py data.json index.html`).
- `tools/scenes.py`: escenas originales de los memes (Velito). Cada día se elige una al azar según el tono (`mood`: g/a/r), sin repetir la del día anterior. Se puede fijar con `"scene"` en `meme`/`meme2`.

Campos opcionales de `data.json`:
- `title`, `subtitle`: para las alertas personales con el mismo diseño.
- `earnings`: resultados empresariales de la semana `[{"d","h","n","c","s","hot"}]` (`c` = país de la sede en ISO de 2 letras, se pinta con bandera; `h` = hora de España).
- `earningsNote`, `stocksNote`: notas bajo cada bloque.
- `stocks[].tag`: por qué está hoy el valor en el radar.

Contenido orientativo generado por una IA con datos públicos. No es asesoramiento financiero.
