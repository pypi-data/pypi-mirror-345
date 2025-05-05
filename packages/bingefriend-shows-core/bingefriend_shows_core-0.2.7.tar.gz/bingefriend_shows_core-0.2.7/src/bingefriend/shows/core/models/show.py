"""SQLAlchemy model for a show."""

import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, Date, ForeignKey, Text
from sqlalchemy.orm import mapped_column, Mapped, relationship
from bingefriend.shows.core.models.base import Base

if TYPE_CHECKING:
    from bingefriend.shows.core.models.episode import Episode
    from bingefriend.shows.core.models.network import Network
    from bingefriend.shows.core.models.season import Season
    from bingefriend.shows.core.models.show_genre import ShowGenre
    from bingefriend.shows.core.models.web_channel import WebChannel


class Show(Base):
    """SQLAlchemy model for a show."""

    __tablename__ = "shows"

    # Attributes
    id: Mapped[int] = mapped_column(primary_key=True)
    maze_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(String(255), nullable=False)
    language: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[Optional[str]] = mapped_column(String(255))
    runtime: Mapped[Optional[int]] = mapped_column(Integer)
    averageRuntime: Mapped[Optional[int]] = mapped_column(Integer)
    premiered: Mapped[Optional[datetime.date]] = mapped_column(Date)
    ended: Mapped[Optional[datetime.date]] = mapped_column(Date)
    schedule_time: Mapped[Optional[str]] = mapped_column(String(255))
    schedule_days: Mapped[Optional[str]] = mapped_column(String(255))
    network_id: Mapped[Optional[int]] = mapped_column(ForeignKey("networks.id"))
    webChannel_id: Mapped[Optional[int]] = mapped_column(ForeignKey("web_channel.id"))
    externals_imdb: Mapped[Optional[str]] = mapped_column(String(255))
    image_medium: Mapped[Optional[str]] = mapped_column(String(255))
    image_original: Mapped[Optional[str]] = mapped_column(String(255))
    summary: Mapped[Optional[str]] = mapped_column(Text)
    updated: Mapped[Optional[int]] = mapped_column(Integer)

    # Relationships - referenced in this model
    network: Mapped["Network"] = relationship(back_populates="shows")
    web_channel: Mapped[Optional["WebChannel"]] = relationship(back_populates="shows")

    # Relationships - referencing this model
    show_genres: Mapped[list["ShowGenre"]] = relationship(back_populates="show")
    seasons: Mapped["Season"] = relationship(back_populates="show", cascade="all, delete-orphan")
    episodes: Mapped["Episode"] = relationship(back_populates="show", cascade="all, delete-orphan")
