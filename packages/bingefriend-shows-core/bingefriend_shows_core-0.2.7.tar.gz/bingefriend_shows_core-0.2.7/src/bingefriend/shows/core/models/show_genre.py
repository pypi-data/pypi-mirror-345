"""SQLAlchemy model for a show-genre association."""

from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from bingefriend.shows.core.models.base import Base

if TYPE_CHECKING:
    from bingefriend.shows.core.models.genre import Genre
    from bingefriend.shows.core.models.show import Show


class ShowGenre(Base):
    __tablename__ = "show_genre"

    # Attributes
    id: Mapped[int] = mapped_column(primary_key=True)
    show_id: Mapped[int] = mapped_column(ForeignKey("shows.id"), nullable=False)
    genre_id: Mapped[int] = mapped_column(ForeignKey("genres.id"), nullable=False)

    # Relationships - referenced in this model
    show: Mapped["Show"] = relationship(back_populates="show_genres")
    genre: Mapped["Genre"] = relationship(back_populates="show_genres")
