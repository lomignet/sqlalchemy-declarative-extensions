from sqlalchemy_declarative_extensions import declarative_database
from sqlalchemy_declarative_extensions.sqlalchemy import declarative_base

_Base = declarative_base()


@declarative_database
class Base(_Base):
    __abstract__ = True

    schemas = ["foo", "bar"]
