"""SQLAlchemy model for a network."""
from typing import Optional
from typing_extensions import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped, relationship
from bingefriend.shows.core.models.base import Base

if TYPE_CHECKING:
    from bingefriend.shows.core.models.show import Show
    from bingefriend.shows.core.models.season import Season


class Network(Base):
    """SQLAlchemy model for a network."""

    __tablename__ = "networks"

    # Attributes
    id: Mapped[int] = mapped_column(primary_key=True)
    maze_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(255))
    country_name: Mapped[Optional[str]] = mapped_column(String(255))
    country_code: Mapped[Optional[str]] = mapped_column(String(255))
    country_timezone: Mapped[Optional[str]] = mapped_column(String(255))

    # Relationships - referencing this model
    shows: Mapped[list["Show"]] = relationship(back_populates="network")
    seasons: Mapped[list["Season"]] = relationship(back_populates="network")
