from fastmcp import FastMCP
from ytmusicapi import YTMusic
from ytmusicapi.exceptions import YTMusicError
from typing import Annotated
from pydantic import BaseModel, Field
from fastmcp.exceptions import ToolError

mcp = FastMCP(name="YouTube Music Finder", version="0.1.0")
yt = YTMusic()

class Song(BaseModel):
    title: str
    artists: list[str] | None
    album: str | None
    duration: str | None
    url: str

class Album(BaseModel):
    title: str
    artists: list[str] | None
    year: str | None
    url: str

@mcp.tool(title="Search Songs Through Youtube Music", 
          annotations={
              "openWorldHint" : True,
              "readOnlyHint" : True,
              })
def search_song(query: Annotated[str, Field(description="Busca canciones en YouTube Music por nombre de canción, artista o álbum.", min_length=1, pattern=r"^.+$")], limit: Annotated[int, Field(description="The maximum number of results to return. Default is 5.", ge=1, le=5)] = 5) -> list[Song]:
    """Busca canciones en YouTube Music por nombre de canción, artista o álbum."""
    if query.strip() == "":
        raise ToolError("La consulta que enviaste está vacía. Por favor, ingresa una consulta válida.")

    try:
        results = yt.search(query, filter="songs", limit=limit)[:limit]
    except YTMusicError as e:
        raise ToolError(f"Error al buscar canciones: {str(e)}")
    
    if not results:
        raise ToolError("La consulta que enviaste no retornó resultados. Prueba con otra consulta. Si el problema persiste, puede que la canción que buscas no esté disponible en YouTube Music.")
    
    return [
        Song(
            title=r["title"],
            artists=[a["name"] for a in r.get("artists", [])],
            album=(r.get("album") or {}).get("name"),
            duration=r.get("duration"),
            url=f"https://music.youtube.com/watch?v={r['videoId']}"
        )
        for r in results
    ]

@mcp.tool(title="Search Albums Through Youtube Music", 
          annotations={
              "openWorldHint" : True,
              "readOnlyHint" : True,
              })
def search_albums(query: Annotated[str, Field(description="Busca álbumes en YouTube Music por nombre de álbum o artista.", min_length=1, pattern=r"^.+$")], max_results: Annotated[int, Field(description="The maximum number of results to return. Default is 5.", ge=1, le=5)] = 5) -> list[Album]:
    """Busca álbumes en YouTube Music por nombre de álbum o artista."""
    if query.strip() == "":
        raise ToolError("La consulta que enviaste está vacía. Por favor, ingresa una consulta válida.")

    try:
        results = yt.search(query, filter="albums", limit=max_results)[:max_results]
    except YTMusicError as e:
        raise ToolError(f"Error al buscar álbumes: {str(e)}")

    if not results:
        raise ToolError("La consulta que enviaste no retornó resultados. Prueba con otra consulta. Si el problema persiste, puede que el álbum que buscas no esté disponible en YouTube Music.")
    return [
        Album(
            title=r["title"],
            artists=[a["name"] for a in r.get("artists", [])],
            year=r.get("year"),
            url=f"https://music.youtube.com/browse/{r['browseId']}"
        )
        for r in results
    ]

if __name__ == "__main__":
    mcp.run()