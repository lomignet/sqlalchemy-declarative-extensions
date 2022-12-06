from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy_declarative_extensions import Schemas, declarative_database

_Base = declarative_base()


@declarative_database
class Base(_Base):
    __abstract__ = True

    schemas = Schemas(ignore_unspecified=True).are("foo")
