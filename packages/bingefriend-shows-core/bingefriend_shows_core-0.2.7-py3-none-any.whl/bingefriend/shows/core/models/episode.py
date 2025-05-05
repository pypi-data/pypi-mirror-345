"""SQLAlchemy model for an episode."""

import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import ForeignKey, Integer, String, Date, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from bingefriend.shows.core.models.base import Base

if TYPE_CHECKING:
    from bingefriend.shows.core.models.season import Season
    from bingefriend.shows.core.models.show import Show


class Episode(Base):
    """SQLAlchemy model for an episode."""

    __tablename__ = "episodes"

    # Attributes
    id: Mapped[int] = mapped_column(primary_key=True)
    maze_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(Text)
    number: Mapped[Optional[int]] = mapped_column(Integer)
    type: Mapped[Optional[str]] = mapped_column(String(50))
    airdate: Mapped[Optional[datetime.date]] = mapped_column(Date)
    airtime: Mapped[Optional[str]] = mapped_column(String(10))
    airstamp: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    runtime: Mapped[Optional[int]] = mapped_column(Integer)
    image_medium: Mapped[Optional[str]] = mapped_column(String(255))
    image_original: Mapped[Optional[str]] = mapped_column(String(255))
    summary: Mapped[Optional[str]] = mapped_column(Text)
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id"), nullable=False)
    show_id: Mapped[int] = mapped_column(ForeignKey("shows.id"), nullable=False)

    # Relationships - referenced in this model
    season: Mapped["Season"] = relationship(back_populates="episodes")
    show: Mapped["Show"] = relationship(back_populates="episodes")
