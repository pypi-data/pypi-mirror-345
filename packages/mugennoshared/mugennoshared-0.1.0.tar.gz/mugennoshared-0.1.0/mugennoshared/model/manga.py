from datetime import datetime
import numpy as np  # type: ignore
from numpy.typing import NDArray
from model.genre import Genre
from model.interfaces import IManga


class Manga(IManga):
    def __init__(
        self,
        title: str,
        url: str,
        synopsis: str,
        cover: str,
        language: str,
        status: str,
        rating: float,
        last_chapter: float,
        release_date: str,  # "YYYY-MM-DD"
        last_update: str,  # "YYYY-MM-DD"
        author: str,
        artists: str,
        serialization: str,
        genres: list[Genre],
        embedding: NDArray[np.float32],
    ):
        self.title = title
        self.url = url
        self.synopsis = synopsis
        self.cover = cover
        self.language = language
        self.status = status
        self.rating = rating
        self.last_chapter = last_chapter
        self.release_date = datetime.strptime(release_date, "%Y-%m-%d").date()
        self.last_update = datetime.strptime(last_update, "%Y-%m-%d").date()
        self.author = author
        self.artists = artists
        self.serialization = serialization
        self.genres = genres
        self.embedding = embedding

    def __str__(self) -> str:
        return f"""
📖 {self.title.upper()}
{'=' * (len(self.title) + 2)}

🔗 URL: {self.url}
✍️ Autor(es): {self.author}
🎨 Artista(s): {self.artists}
📰 Serialização: {self.serialization}
📌 Status: {self.status}
⭐ Nota: {self.rating}
📜 Último Capítulo: {self.last_chapter}
🏷️ Gêneros: {', '.join(genre.value for genre in self.genres)}

📝 Sinopse:
{self.synopsis}

🗓️ Data de Lançamento: {self.release_date}
🔄 Última Atualização: {self.last_update}
"""
