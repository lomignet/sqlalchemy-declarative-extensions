from typing import Optional

from sqlalchemy import bindparam, column, literal, table

from sqlalchemy_declarative_extensions.sqlalchemy import select


def make_sqlite_schema(schema: Optional[str] = None):
    tablename = "sqlite_schema"
    if schema:
        tablename = f"{schema}.{tablename}"

    return table(
        tablename,
        column("type"),
        column("name"),
        column("sql"),
    )


def views_query(schema: Optional[str] = None):
    sqlite_schema = make_sqlite_schema(schema)
    return select(
        literal(None),
        sqlite_schema.c.name.label("name"),
        sqlite_schema.c.sql.label("definition"),
    ).where(sqlite_schema.c.type == "view")


def table_exists_query(schema: Optional[str] = None):
    sqlite_schema = make_sqlite_schema(schema)
    return (
        select(sqlite_schema)
        .where(sqlite_schema.c.type == "table")
        .where(sqlite_schema.c.table_schema == bindparam("schema"))
        .where(sqlite_schema.c.name == bindparam("name"))
    )
