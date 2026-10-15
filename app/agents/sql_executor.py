import re

from sqlalchemy import text

from database.connection import SessionLocal


FORBIDDEN_KEYWORDS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|"
    r"CREATE|GRANT|REVOKE|CALL|COPY|DO|EXECUTE|"
    r"MERGE|VACUUM|SET|RESET)\b",
    re.IGNORECASE,
)


def validate_sql(query: str) -> None:
    """Validate that the query is a single read-only SELECT statement."""

    normalized_query = query.strip()

    if not normalized_query:
        raise ValueError("SQL query cannot be empty.")

    # Allow at most one trailing semicolon.
    if normalized_query.endswith(";"):
        normalized_query = normalized_query[:-1].rstrip()

    # Reject multiple statements.
    if ";" in normalized_query:
        raise ValueError("Multiple SQL statements are not allowed.")

    if not re.match(r"^SELECT\b", normalized_query, re.IGNORECASE):
        raise ValueError("Only SELECT queries are allowed.")

    if FORBIDDEN_KEYWORDS.search(normalized_query):
        raise ValueError("The query contains a forbidden SQL keyword.")


async def execute_sql(query: str) -> list[dict]:
    """Execute a validated read-only query and return its rows."""

    validate_sql(query)

    async with SessionLocal() as session:
        # Use a read-only transaction as an additional safeguard.
        async with session.begin():
            await session.execute(text("SET TRANSACTION READ ONLY"))

            result = await session.execute(text(query))
            rows = result.mappings().all()

            return [dict(row) for row in rows]