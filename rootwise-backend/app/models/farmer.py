
from datetime import datetime

from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Farmer(Base):
    __tablename__ = "farmers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Reference to the user's Supabase Auth ID.
    auth_user_id: Mapped[str | None] = mapped_column(
        String(100), unique=True, index=True
    )

    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(25))
    preferred_language: Mapped[str] = mapped_column(
        String(50), default="English"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    fields: Mapped[list["Field"]] = relationship(back_populates="farmer")
    scenarios: Mapped[list["Scenario"]] = relationship(
        back_populates="farmer"
    )
