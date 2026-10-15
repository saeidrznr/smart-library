import asyncio
from datetime import date, timedelta

from sqlalchemy import select

from database.connection import SessionLocal
from database.models.member import Member
from database.models.loan import Loan
from database.models.loan import LoanStatus

MEMBERS = [
    ("علی رضایی", "LIB-1001"),
    ("سارا محمدی", "LIB-1002"),
    ("محمد کریمی", "LIB-1003"),
    ("فاطمه احمدی", "LIB-1004"),
    ("رضا حسینی", "LIB-1005"),
    ("نگار موسوی", "LIB-1006"),
    ("امیر جعفری", "LIB-1007"),
    ("مریم کاظمی", "LIB-1008"),
    ("حسین مرادی", "LIB-1009"),
    ("زهرا صادقی", "LIB-1010"),
]

# Membership number, book title, subject, days until due date, loan status
LOANS = [
    ("LIB-1001", "مبانی هوش مصنوعی", "هوش مصنوعی", -10, "borrowed"),
    ("LIB-1001", "یادگیری عمیق", "یادگیری ماشین", 5, "borrowed"),
    ("LIB-1001", "پایگاه داده", "مهندسی نرم‌افزار", -3, "borrowed"),
    ("LIB-1002", "پردازش زبان طبیعی", "هوش مصنوعی", 7, "borrowed"),
    ("LIB-1002", "پایتون پیشرفته", "برنامه‌نویسی", -5, "borrowed"),
    ("LIB-1002", "ساختمان داده", "برنامه‌نویسی", -20, "returned"),
    ("LIB-1003", "شبکه‌های کامپیوتری", "شبکه", 10, "borrowed"),
    ("LIB-1003", "سیستم‌عامل", "سیستم‌عامل", -8, "borrowed"),
    ("LIB-1003", "الگوریتم‌ها", "برنامه‌نویسی", -15, "returned"),
    ("LIB-1004", "یادگیری ماشین", "یادگیری ماشین", 4, "borrowed"),
    ("LIB-1004", "بینایی ماشین", "هوش مصنوعی", -2, "borrowed"),
    ("LIB-1005", "طراحی الگوریتم", "برنامه‌نویسی", 12, "borrowed"),
    ("LIB-1005", "مهندسی نرم‌افزار", "مهندسی نرم‌افزار", -12, "borrowed"),
    ("LIB-1006", "آمار و احتمال", "ریاضیات", 3, "borrowed"),
    ("LIB-1006", "جبر خطی", "ریاضیات", -6, "returned"),
    ("LIB-1007", "مدل‌های زبانی بزرگ", "هوش مصنوعی", 8, "borrowed"),
    ("LIB-1007", "یادگیری تقویتی", "یادگیری ماشین", -4, "borrowed"),
    ("LIB-1008", "برنامه‌نویسی شیءگرا", "برنامه‌نویسی", 6, "borrowed"),
    ("LIB-1008", "معماری کامپیوتر", "سخت‌افزار", -9, "returned"),
    ("LIB-1009", "امنیت شبکه", "شبکه", 2, "borrowed"),
    ("LIB-1009", "سیستم‌های توزیع‌شده", "سیستم‌عامل", -7, "borrowed"),
    ("LIB-1010", "داده‌کاوی", "هوش مصنوعی", 9, "borrowed"),
    ("LIB-1010", "تحلیل داده", "علم داده", -1, "borrowed"),
    ("LIB-1004", "مبانی برنامه‌نویسی", "برنامه‌نویسی", -25, "returned"),
    ("LIB-1005", "آشنایی با علم داده", "علم داده", 15, "borrowed"),
]


async def seed_database():
    today = date.today()

    async with SessionLocal() as session:
        async with session.begin():
            # Retrieve existing members
            result = await session.execute(select(Member))

            members_by_number = {
                member.membership_number: member
                for member in result.scalars().all()
            }

            # Add members that do not already exist
            for full_name, number in MEMBERS:
                if number not in members_by_number:
                    member = Member(
                        full_name=full_name,
                        membership_number=number,
                    )
                    session.add(member)
                    members_by_number[number] = member

            # Flush to assign IDs to newly added members
            await session.flush()

            # Identify existing loan records
            result = await session.execute(select(Loan))

            existing_loans = {
                (
                    loan.member_id,
                    loan.book_title,
                    loan.subject,
                    loan.due_date,
                    loan.loan_status,
                )
                for loan in result.scalars().all()
            }

            inserted = 0

            # Insert sample loans
            for number, title, subject, days, status in LOANS:
                member = members_by_number[number]
                due_date = today + timedelta(days=days)
                loan_status = LoanStatus(status)

                key = (
                    member.id,
                    title,
                    subject,
                    due_date,
                    loan_status,
                )

                if key in existing_loans:
                    continue

                loan = Loan(
                    member_id=member.id,
                    book_title=title,
                    subject=subject,
                    loan_status=loan_status,
                    due_date=due_date,
                )

                session.add(loan)
                existing_loans.add(key)
                inserted += 1

        print(f"Seed completed. Members in sample: {len(MEMBERS)}")
        print(f"New loans inserted: {inserted}")


if __name__ == "__main__":
    asyncio.run(seed_database())
