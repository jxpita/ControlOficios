# Notas para Claude Code — ControlOficios

## Dependencias

- `cryptography` — **obligatoria** (cifrado de credenciales y oficios).
- `pymupdf` — opcional: visor de PDF integrado (`visor_pdf.py`). Sin ella la
  app funciona y ofrece abrir el PDF con el lector del sistema.
- `pillow` — opcional: logo del banco en cabecera/login y mayor nitidez del
  visor de PDF (sin ella el visor usa el modo PPM nativo de Tk).

Las dependencias opcionales se importan con `try/except ImportError` y tienen
alternativa; no rompas ese patrón al modificar el código.

## Grafo de conocimiento (graphify)

El proyecto mantiene un **grafo de conocimiento** generado con
[graphify](https://github.com/Graphify-Labs/graphify) en la carpeta
**`grafo/graphify-out/`** (subcarpeta `grafo/` del repo, versionada en git).

La salida se fija con la variable de entorno `GRAPHIFY_OUT=grafo/graphify-out`,
que **todos** los comandos de graphify respetan.

### IMPORTANTE: actualizar el grafo tras CADA cambio de código

Después de modificar código y **antes de hacer push**, regenera el grafo y
commitéalo junto con los cambios. Es 100 % local (AST con tree-sitter, sin
API key ni coste de LLM):

```bash
export GRAPHIFY_OUT=grafo/graphify-out
graphify update .                      # re-extrae solo lo que cambió (incremental)
graphify cluster-only . --no-label     # recalcula comunidades y regenera GRAPH_REPORT.md + graph.html
```

Si un refactor eliminó código o el grafo quedó inconsistente, haz una
reconstrucción limpia:

```bash
export GRAPHIFY_OUT=grafo/graphify-out
rm -rf grafo/graphify-out
graphify extract . --code-only --no-cluster
graphify cluster-only . --no-label
```

Se usa `--code-only` / `--no-label` para no requerir ninguna API key.

### Qué se versiona y qué no

Se versionan: `graph.json`, `graph.html`, `GRAPH_REPORT.md`, `manifest.json`,
`.graphify_analysis.json`.
Se ignoran (en `.gitignore`): `cache/`, `.graphify_root` (guarda una ruta
absoluta, no portable) y `cost.json`.

### Consultar el grafo

```bash
graphify query "<pregunta>" --graph grafo/graphify-out/graph.json
graphify path "AplicacionPrincipal" "descifrar()" --graph grafo/graphify-out/graph.json
graphify explain "SelectorFecha" --graph grafo/graphify-out/graph.json
```
