from alembic.autogenerate.api import AutogenContext
from alembic.autogenerate.compare import comparators
from alembic.autogenerate.render import renderers

from sqlalchemy_declarative_extensions.view.compare import (
    CreateViewOp,
    DropViewOp,
    compare_views,
)


@comparators.dispatch_for("schema")
def _compare_views(autogen_context, upgrade_ops, _):
    views = autogen_context.metadata.info.get("views")
    if not views:
        return

    result = compare_views(autogen_context.connection, views)
    upgrade_ops.ops.extend(result)


@renderers.dispatch_for(CreateViewOp)
def render_create_view(autogen_context: AutogenContext, op: CreateViewOp):
    assert autogen_context.connection
    dialect = autogen_context.connection.dialect
    commands = op.to_sql(dialect)

    return [f'op.execute("""{command}""")' for command in commands]


@renderers.dispatch_for(DropViewOp)
def render_drop_view(autogen_context: AutogenContext, op: DropViewOp):
    assert autogen_context.connection
    dialect = autogen_context.connection.dialect
    commands = op.to_sql(dialect)

    return [f'op.execute("""{command}""")' for command in commands]
