# Views

Views definition and registration can be performed exactly as it is done with other object
types, by defining the set of views on the `MetaData` or declarative base, like so:

```python
from sqlalchemy_declarative_extensions.sqlalchemy import declarative_base
from sqlalchemy_declarative_extensions import declarative_database, View, Views

_Base = declarative_base()


@declarative_database
class Base(_Base):
    __abstract__ = True

    views = Views().are(
        View("foo", "select * from bar where id > 10", schema="baz"),
    )
```

And if you want to define views using raw strings, or otherwise not reference the tables
produced off the `MetaData`, then this is absolutely a valid way to organize.

## The `view` decorator

However views differ from most of the other object types, in that they are convenient to
define **in terms of** the tables they reference (i.e. your existing set of models/tables).
In fact personally, all of my views are produced from [select](sqlalchemy.sql.expression.select) expressions
referencing the underlying [Table](sqlalchemy.schema.Table) object.

This commonly introduce a circular reference problem wherein your tables/models are defined
through subclassing the declarative base, which means your declarative base cannot then
have the views statically defined **on** the base (while simultaneously referencing those models).

```{note}
There are ways of working around this in SQLAlchemy-land. For example by creating a ``MetaData``
ahead of time and defining all models in terms of their underlying ``Table``.

Or perhaps by using SQLAlchemy's mapper apis such that you're not subclassing the declarative base
for models.

In any case, these options are more complex and probably atypical. As such, we cannot assume
you will adopt them.
```

For everyone else, the [view](sqlalchemy_declarative_extensions.view) decorator is meant to be the
solution to that problem.

This strategy allows one to organize their views alongside the models/tables those
views happen to be referencing, without requiring the view be importable at MetaData/model base
definition time.

```python
from sqlalchemy import Column, types, select
from sqlalchemy_declarative_extensions.sqlalchemy import declarative_base
from sqlalchemy_declarative_extensions import view

Base = declarative_base()


class Foo(Base):
    __tablename__ = 'foo'

    id = Column(types.Integer, primary_key=True)


@view(Base)
class Bar:
    __tablename__ = 'bar'
    __view__ = select(Foo.__table__).where(Foo.__table__.id > 10)

    id = Column(types.Integer, primary_key=True)
```

The protocol this class is following provides an interface that is intentionally similar to the one
given by a normal sqlalchemy model. From the perspective of code, your `Bar` class will be usable
by SQLAlchemy in the same way as a normal table, i.e. `session.query(Bar1).all()`.

Alternatively, if you dont **care** about being able to programmatically make use of the model-like
ORM interface, you can omit the model-style declaration of columns. That at least allows you to
avoid duplicating the list of columns unnecessarily.

Finally, you can directly call `register_view` to imperitively register a normal [View](sqlalchemy_declarative_extensions.View)
object, if the class interface doesn't float your boat.

## Materialized views

Materialized views can be created by adding the `materialized=True` kwarg to the `@view` decorator,
or else by supplying the same kwarg directly to the `View` constructor.

Note that in order to refresh materialized views concurrently, the Postgres requires the view to
have a unique constraint. The constraint can be applied in the same way that it would be on a
normal table (i.e. `__table_args__`):

```python
@view(Base, materialized=True)
class Bar:
    __tablename__ = 'bar'
    __view__ = select(Foo.__table__).where(Foo.__table__.id > 10)
    __table_args__ = (Index('uq_bar', 'id', unique=True))
```

There is a caveat (at least currently), that the `UniqueConstraint` convenience class provided by
SQLAlchemy does not appear to function in the same way as `Index` in a way that makes it incompatible
with the mechanisms used by this library at the time of writing. As such, we ignore `__table_args__`
constraints which are not `Index`.
