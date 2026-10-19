# mcp-poc

Prueba de concepto para investigar y experimentar cómo funciona el **Model Context Protocol (MCP)**: cómo se construye un servidor MCP en Python, cómo expone herramientas (*tools*) y cómo se conecta a distintos clientes de IA (VS Code + Copilot, Claude Desktop, Claude Code).

> Este proyecto es experimental y con fines de aprendizaje. No está pensado para uso en producción.

## ¿Qué es MCP?

[MCP](https://modelcontextprotocol.io/) es un protocolo abierto que estandariza cómo una aplicación de IA (el **cliente**) se comunica con programas externos (los **servidores**) que le ofrecen herramientas, recursos y prompts.

```
┌──────────────────────┐      JSON-RPC       ┌────────────────────────┐
│ Cliente MCP          │ ◀─────────────────▶ │ Servidor MCP           │
│ (Copilot, Claude...) │   stdio  o  HTTP    │ (este proyecto)        │
└──────────────────────┘                     └────────────────────────┘
        │                                               │
        │ 1. initialize                                 │
        │ 2. tools/list   → descubre las herramientas   │
        │ 3. tools/call   → el modelo decide usar una   │
        ▼                                               ▼
   El modelo de IA                              Tu código Python
```

El modelo nunca ejecuta tu código directamente: el cliente le muestra la lista de herramientas (nombre, descripción y parámetros), el modelo decide cuál llamar y con qué argumentos, y el cliente envía esa llamada al servidor.

**Transportes** que se exploran aquí:

| Transporte | Cómo funciona | Cuándo usarlo |
|---|---|---|
| `stdio` | El cliente lanza el servidor como subproceso y se comunican por stdin/stdout | Servidores locales; el cliente gestiona su ciclo de vida |
| `http` | El servidor corre por su cuenta y el cliente se conecta a una URL | Servidores remotos o compartidos |

## Servidores incluidos

Ambos están construidos con [FastMCP](https://gofastmcp.com/), que convierte funciones de Python decoradas con `@mcp.tool()` en herramientas MCP. Los *type hints* y el *docstring* de cada función son lo que el modelo ve para decidir cómo usarla.

### 🧮 Calculadora — `src/fastmcp-calculator.py`

Servidor mínimo para entender lo básico del protocolo.

| Herramienta | Parámetros | Descripción |
|---|---|---|
| `multiply` | `a`, `b` | Multiplica dos números |
| `add` | `x`, `y` | Suma dos números (ejemplo de `name`, `description` y `tags` personalizados) |
| `subtract` | `a`, `b` | Resta dos números |
| `divide` | `a`, `b` | Divide dos números; lanza un error si `b` es 0 |

### 🎵 YouTube Music Finder — `src/ytmusic-finder.py`

Servidor que consulta datos reales usando [ytmusicapi](https://ytmusicapi.readthedocs.io/). Busca por nombre de canción, álbum o artista, sin necesidad de cuenta ni API key.

| Herramienta | Parámetros | Descripción |
|---|---|---|
| `search_song` | `query`, `limit` | Busca canciones; devuelve título, artistas, álbum, duración y URL |
| `search_albums` | `query`, `max_results` | Busca álbumes; devuelve título, artistas, año y URL |

> `ytmusicapi` es una librería no oficial: puede dejar de funcionar si YouTube Music cambia su web.

## Estructura del proyecto

```
mcp-poc/
├── src/
│   ├── fastmcp-calculator.py   # Servidor MCP: calculadora
│   ├── ytmusic-finder.py       # Servidor MCP: búsqueda en YouTube Music
│   └── mcp_poc/                # Paquete del proyecto (placeholder)
├── .vscode/
│   └── mcp.json                # Configuración de los servidores para VS Code
├── pyproject.toml              # Dependencias y metadatos
└── uv.lock                     # Versiones exactas de las dependencias
```

## Instalación local

### Requisitos

- **Python 3.14** o superior
- **[uv](https://docs.astral.sh/uv/)**, el gestor de paquetes y entornos usado en el proyecto

Si no tienes `uv`:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Pasos

```bash
git clone <url-del-repositorio>
cd mcp-poc
uv sync
```

`uv sync` crea el entorno virtual `.venv/` e instala todas las dependencias con las versiones exactas de `uv.lock`. Si no tienes Python 3.14, `uv` lo descarga automáticamente.

### Comprobar que funciona

Sin conectar ningún cliente, puedes listar y llamar herramientas desde la terminal con la CLI de FastMCP:

```bash
# Ver las herramientas de un servidor
uv run fastmcp list src/fastmcp-calculator.py

# Llamar a una herramienta
uv run fastmcp call src/fastmcp-calculator.py multiply a=10 b=10
# → { "result": 100.0 }

uv run fastmcp call src/ytmusic-finder.py search_albums query="Soda Stereo" max_results=2
```

Para explorarlos con una interfaz web, usa el **MCP Inspector** (requiere Node.js):

```bash
uv run fastmcp dev inspector src/ytmusic-finder.py
```

## Ejecutar los servidores

**Modo stdio** (el que usan los clientes de escritorio; normalmente no lo lanzas tú, lo lanza el cliente):

```bash
uv run fastmcp run src/fastmcp-calculator.py -t stdio
uv run fastmcp run src/ytmusic-finder.py -t stdio
```

**Modo HTTP** (la calculadora lo trae configurado en su `__main__`):

```bash
uv run src/fastmcp-calculator.py
# Escuchando en http://localhost:8003/mcp
```

## Conectar un cliente

### VS Code + GitHub Copilot

El repositorio ya incluye [.vscode/mcp.json](.vscode/mcp.json) con los dos servidores (`calc-mcp-stdio` y `ytmusic-finder`).

1. Abre la carpeta del proyecto en VS Code y ejecuta `uv sync` si no lo has hecho.
2. Abre `.vscode/mcp.json` y pulsa **Start** sobre el servidor que quieras (o `Ctrl+Shift+P` → **MCP: List Servers**).
3. Abre el chat de Copilot en modo **Agent**; las herramientas aparecen en el selector de herramientas.
4. Prueba: *"Busca álbumes de Soda Stereo en YouTube Music"*.

Si algo falla: **MCP: List Servers** → servidor → **Show Output**.

### Claude Desktop

Edita el archivo de configuración de Claude Desktop:

| Sistema | Ruta |
|---|---|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

Añade el servidor dentro de `mcpServers`, sustituyendo las rutas por las tuyas:

```json
{
  "mcpServers": {
    "ytmusic-finder": {
      "command": "/ruta/absoluta/a/uv",
      "args": [
        "run", "--directory", "/ruta/absoluta/a/mcp-poc",
        "fastmcp", "run", "src/ytmusic-finder.py", "-t", "stdio", "--no-banner"
      ]
    }
  }
}
```

- Usa la **ruta absoluta** de `uv` (obtenla con `which uv`): Claude Desktop no hereda el `PATH` de tu terminal.
- Cierra Claude Desktop por completo y vuelve a abrirlo; la configuración solo se lee al arrancar.
- Los logs del servidor están en la carpeta `logs/` junto al archivo de configuración (`mcp-server-ytmusic-finder.log`).

### Claude Code

Desde la raíz del proyecto:

```bash
claude mcp add ytmusic-finder -- uv run --directory "$(pwd)" fastmcp run src/ytmusic-finder.py -t stdio --no-banner
```

Abre una sesión nueva de Claude Code y comprueba con `/mcp` que el servidor aparece como conectado.

## Problemas conocidos

| Síntoma | Causa y solución |
|---|---|
| `TypeError: Server.__init__() takes 2 positional arguments but 3 were given` | Algunas librerías construidas sobre el SDK de MCP (como `fastapi-mcp` 0.4) no son compatibles con `mcp` 2.x. Por eso `pyproject.toml` fija `mcp<2`, que además es lo que exige `fastmcp` 3.x. |
| El cliente no encuentra `uv` | Usa la ruta absoluta del ejecutable en la configuración del cliente. |
| El servidor arranca pero el cliente no ve herramientas | En stdio, cualquier `print()` a stdout corrompe el protocolo. Usa `--no-banner` y escribe los logs en stderr. |

## Recursos

- [Especificación de MCP](https://modelcontextprotocol.io/)
- [Documentación de FastMCP](https://gofastmcp.com/)
- [Documentación de ytmusicapi](https://ytmusicapi.readthedocs.io/)
- [MCP en VS Code](https://code.visualstudio.com/docs/copilot/chat/mcp-servers)
- [Python Course sobre MCP con freecodeCamp](https://www.youtube.com/watch?v=DosHnyq78xY)
