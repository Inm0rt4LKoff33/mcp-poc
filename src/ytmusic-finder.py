from fastmcp import FastMCP
from ytmusicapi import YTMusic

mcp = FastMCP(name="YouTube Music Finder", version="0.1.0")
yt = YTMusic()

@mcp.tool()
def search_song(query: str, limit: int = 5) -> list:
    """Search for songs on YouTube Music.

    args: query (str): The search query.
          limit (int): The maximum number of results to return. Default is 5.

    returns: list: A list of search results.
    """
    results = yt.search(query, filter="songs", limit=limit)
    return [
        {
            "title": r["title"],
            "artists": [a["name"] for a in r.get("artists", [])],
            "album": (r.get("album") or {}).get("name"),
            "duration": r.get("duration"),
            "url": f"https://music.youtube.com/watch?v={r['videoId']}",
        }
        for r in results
    ]

@mcp.tool()
def search_albums(query: str, max_results: int = 5) -> list[dict]:
    """Busca álbumes en YouTube Music por nombre de álbum o artista."""
    results = yt.search(query, filter="albums", limit=max_results)[:max_results]
    return [
        {
            "title": r["title"],
            "artists": [a["name"] for a in r.get("artists", [])],
            "year": r.get("year"),
            "url": f"https://music.youtube.com/browse/{r['browseId']}",
        }
        for r in results
    ]

if __name__ == "__main__":
    mcp.run()