from datetime import date
from typing import List, Optional, cast
import numpy as np
from numpy.typing import NDArray
from sqlalchemy import (
    Table,
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Date,
    Text,
    ForeignKey,
)
from sqlalchemy.orm import sessionmaker, relationship
from pgvector.sqlalchemy import Vector  # type: ignore
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from model.genre import Genre
from model.manga import Manga


# Definir um tipo personalizado para o embedding
NpFloat32Array = NDArray[np.float32]


class Base(DeclarativeBase):
    pass


# Tabela de associação muitos-para-muitos
manga_genre_association = Table(
    "manga_genres",
    Base.metadata,
    Column("manga_id", Integer, ForeignKey("mangas.id"), primary_key=True),
    Column("genre_id", Integer, ForeignKey("genres.id"), primary_key=True),
)


class GenreDB(Base):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    # Relação com mangas (opcional, para acesso bidirecional)
    mangas: Mapped[List["MangaDB"]] = relationship(
        "MangaDB", secondary=manga_genre_association, back_populates="genres"
    )

    def to_genre(self) -> Genre:
        """Converte GenreDB para o Enum Genre"""
        try:
            # Encontra o membro do Enum que corresponde ao name
            return next(genre for genre in Genre if genre.value == self.name)
        except StopIteration:
            raise ValueError(f"Gênero {self.name} não encontrado no Enum Genre")

    @classmethod
    def from_genre(cls, genre: Genre) -> "GenreDB":
        """Cria um GenreDB a partir do Enum Genre"""
        return cls(name=genre.value)

    @classmethod
    def get_or_create(cls, session, genre: Genre) -> "GenreDB":
        """Obtém ou cria um GenreDB a partir do Enum"""
        genre_db = session.query(cls).filter_by(name=genre.value).first()
        if not genre_db:
            genre_db = cls.from_genre(genre)
            session.add(genre_db)
            session.commit()
        return genre_db


class MangaDB(Base):
    __tablename__ = "mangas"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    url: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    synopsis: Mapped[str] = mapped_column(Text)
    cover: Mapped[str] = mapped_column(String(512))
    language: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50))
    rating: Mapped[float] = mapped_column(Float)
    last_chapter: Mapped[float] = mapped_column(Float)
    release_date: Mapped[date] = mapped_column(Date)
    last_update: Mapped[date] = mapped_column(Date)
    author: Mapped[str] = mapped_column(String(255))
    artists: Mapped[str] = mapped_column(String(255))
    serialization: Mapped[str] = mapped_column(String(255))
    embedding: Mapped[NpFloat32Array] = mapped_column(Vector(384))

    # Relação com gêneros
    genres: Mapped[List["GenreDB"]] = relationship(
        "GenreDB", secondary=manga_genre_association, back_populates="mangas"
    )

    @classmethod
    def from_manga(cls, manga: Manga) -> "MangaDB":
        """Cria um MangaDB a partir de um objeto Manga"""
        return cls(
            title=manga.title,
            url=manga.url,
            synopsis=manga.synopsis,
            cover=manga.cover,
            language=manga.language,
            status=manga.status,
            rating=manga.rating,
            last_chapter=manga.last_chapter,
            release_date=manga.release_date,
            last_update=manga.last_update,
            author=manga.author,
            artists=manga.artists,
            serialization=manga.serialization,
            embedding=np.asarray(manga.embedding, dtype=np.float32),
            genres=[GenreDB(name=genre.value) for genre in manga.genres],
        )

    def to_manga(self) -> Manga:
        """Converte para o objeto de domínio Manga"""
        return Manga(
            title=self.title,
            url=self.url,
            synopsis=self.synopsis,
            cover=self.cover,
            language=self.language,
            status=self.status,
            rating=self.rating,
            last_chapter=self.last_chapter,
            release_date=self.release_date.strftime("%Y-%m-%d"),
            last_update=self.last_update.strftime("%Y-%m-%d"),
            author=self.author,
            artists=self.artists,
            serialization=self.serialization,
            embedding=np.asarray(self.embedding, dtype=np.float32),
            genres=[Genre(genre.name) for genre in self.genres],
        )


class MangaRepository:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def add_manga(self, manga: Manga):
        session = self.Session()

        # Converter strings de data para objetos date
        release_date = manga.release_date
        last_update = manga.last_update

        # Obter ou criar gêneros
        genre_dbs = [GenreDB.get_or_create(session, genre) for genre in manga.genres]

        manga_db = MangaDB(
            title=manga.title,
            url=manga.url,
            synopsis=manga.synopsis,
            cover=manga.cover,
            language=manga.language,
            status=manga.status,
            rating=manga.rating,
            last_chapter=manga.last_chapter,
            release_date=release_date,
            last_update=last_update,
            author=manga.author,
            artists=manga.artists,
            serialization=manga.serialization,
            embedding=np.asarray(manga.embedding, dtype=np.float32),
            genres=genre_dbs,
        )

        session.add(manga_db)
        session.commit()
        session.close()

    def get_manga_by_id(self, manga_id: int) -> Optional[Manga]:
        session = self.Session()
        manga_db = cast(Optional[MangaDB], session.query(MangaDB).get(manga_id))
        result = manga_db.to_manga() if manga_db else None
        session.close()
        return result
