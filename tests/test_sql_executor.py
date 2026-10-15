import pytest

from app.agents.sql_executor import validate_sql


@pytest.mark.parametrize(
    "query",
    [
        "SELECT * FROM members",
        "SELECT * FROM loans;",
        """
        SELECT m.full_name, l.book_title
        FROM members AS m
        JOIN loans AS l ON l.member_id = m.id
        """,
    ],
)
def test_validate_sql_accepts_select(query):
    validate_sql(query)


@pytest.mark.parametrize(
    "query",
    [
        "",
        "DELETE FROM members",
        "UPDATE members SET full_name = 'Test'",
        "SELECT * FROM members; DELETE FROM members",
    ],
)
def test_validate_sql_rejects_unsafe_queries(query):
    with pytest.raises(ValueError):
        validate_sql(query)
