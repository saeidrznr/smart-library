from datetime import date

from sqlalchemy import CheckConstraint, Date, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from loan import Loan


class Member(Base):
    __tablename__ = "members"

    __table_args__ = (
        CheckConstraint(
            "length(trim(full_name)) > 0",
            name="ck_members_full_name_not_empty",
        ),
        CheckConstraint(
            "length(trim(membership_number)) > 0",
            name="ck_membership_number_not_empty",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )
    full_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    membership_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )
    membership_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        default=date.today
    )

    loans: Mapped[list["Loan"]] = relationship(
        back_populates="member",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
