from datetime import date

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from member import Member

from enum import Enum

from sqlalchemy import Enum as SQLAlchemyEnum


class LoanStatus(str, Enum):
    BORROWED = "borrowed"
    RETURNED = "returned"


class Loan(Base):
    __tablename__ = "loans"

    __table_args__ = (
        CheckConstraint(
            "loan_status IN ('borrowed', 'returned')",
            name="ck_loans_status",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )
    member_id: Mapped[int] = mapped_column(
        ForeignKey("members.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    book_title: Mapped[str] = mapped_column(
        String(250),
        nullable=False,
    )
    subject: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    loan_status: Mapped[LoanStatus] = mapped_column(
        SQLAlchemyEnum(
            LoanStatus,
            name="loan_status",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        default=LoanStatus.BORROWED,
        nullable=False,
    )
    due_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    member: Mapped["Member"] = relationship(
        back_populates="loans",
    )
