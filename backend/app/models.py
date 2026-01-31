"""define db models"""

from typing import Optional

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import ARRAY, TEXT
from sqlmodel import Field, Relationship, SQLModel


class Title(SQLModel, table=True):
    """titles"""

    __tablename__ = "titles"

    tconst: str = Field(primary_key=True)
    title_type: str
    primary_title: str
    original_title: Optional[str]
    is_adult: bool
    start_year: Optional[int]
    end_year: Optional[int]
    runtime_minutes: Optional[int]

    genres: Optional[list[str]] = Field(sa_column=Column(ARRAY(TEXT)))

    rating: Optional["TitleRating"] = Relationship(back_populates="title")
    episodes: list["Episode"] = Relationship(
        back_populates="parent",
        sa_relationship_kwargs={"foreign_keys": "[Episode.parent_tconst]"},
    )


class Person(SQLModel, table=True):
    """person people"""

    __tablename__ = "people"

    nconst: str = Field(primary_key=True)
    primary_name: Optional[str]
    birth_year: Optional[int]
    death_year: Optional[int]

    primary_professions: Optional[list[str]] = Field(sa_column=Column(ARRAY(TEXT)))

    known_for_titles: Optional[list[str]] = Field(sa_column=Column(ARRAY(TEXT)))


class TitleRating(SQLModel, table=True):
    """ratings of title"""

    __tablename__ = "title_ratings"

    tconst: str = Field(foreign_key="titles.tconst", primary_key=True)
    average_rating: float
    num_votes: int

    title: Optional[Title] = Relationship(back_populates="rating")


class Episode(SQLModel, table=True):
    """episode"""

    __tablename__ = "episodes"

    tconst: str = Field(foreign_key="titles.tconst", primary_key=True)
    parent_tconst: str = Field(foreign_key="titles.tconst")

    season_number: Optional[int]
    episode_number: Optional[int]

    parent: Optional[Title] = Relationship(
        back_populates="episodes",
        sa_relationship_kwargs={"foreign_keys": "[Episode.parent_tconst]"},
    )


class TitleAka(SQLModel, table=True):
    """title aka localized"""

    __tablename__ = "title_akas"

    title_id: str = Field(foreign_key="titles.tconst", primary_key=True)
    ordering: int = Field(primary_key=True)

    title: str
    region: Optional[str]
    language: Optional[str]

    types: Optional[list[str]] = Field(sa_column=Column(ARRAY(TEXT)))

    attributes: Optional[list[str]] = Field(sa_column=Column(ARRAY(TEXT)))

    is_original: Optional[bool]


class TitlePrincipal(SQLModel, table=True):
    """title user mapping"""

    __tablename__ = "title_principals"

    tconst: str = Field(foreign_key="titles.tconst", primary_key=True)
    ordering: int = Field(primary_key=True)

    nconst: str = Field(foreign_key="people.nconst")
    category: str
    job: Optional[str]
    characters: Optional[str]


class TitleDirector(SQLModel, table=True):
    """directors"""

    __tablename__ = "title_directors"

    tconst: str = Field(foreign_key="titles.tconst", primary_key=True)
    nconst: str = Field(foreign_key="people.nconst", primary_key=True)


class TitleWriter(SQLModel, table=True):
    """writers"""

    __tablename__ = "title_writers"

    tconst: str = Field(foreign_key="titles.tconst", primary_key=True)
    nconst: str = Field(foreign_key="people.nconst", primary_key=True)
