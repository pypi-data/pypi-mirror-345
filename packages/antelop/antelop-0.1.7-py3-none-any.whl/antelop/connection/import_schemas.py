"""
We apply significant patches to the underlying datajoint methods, including permissions checks, etc.
To do this we load all tables twice, with the original datajoint classes and the patched classes.
This means we can access the underlying datajoint functionality.
"""

from antelop.schemas import metadata, ephys, behaviour
from antelop.connection.permission import delete_patch
from antelop.connection.utils import schema_context_manager, AntelopTables


def schema(conn):
    # load both modified and datajoint tables
    with schema_context_manager(admin=True) as admin_classes:
        admin_metadata_tables, _ = metadata.schema(conn, admin_classes)
        admin_ephys_tables, _ = ephys.schema(conn, admin_classes)
        admin_behaviour_tables, _ = behaviour.schema(conn, admin_classes)
        admin_tables = {
            **admin_metadata_tables,
            **admin_ephys_tables,
            **admin_behaviour_tables,
        }

    with schema_context_manager(admin=False) as non_admin_classes:
        metadata_tables, _ = metadata.schema(conn, non_admin_classes)
        ephys_tables, _ = ephys.schema(conn, non_admin_classes)
        behaviour_tables, _ = behaviour.schema(conn, non_admin_classes)
        tables = AntelopTables(**metadata_tables, **ephys_tables, **behaviour_tables)

    for name, table in admin_tables.items():
        table.tables = admin_tables
        table.connection.tables = admin_tables
        admin_tables[name] = table

    for name, table in tables.items():
        tables[name] = delete_patch(table)
        tables[name]._admin = admin_tables[name]

    for name, table in tables.items():
        table.tables = tables
        table.connection.tables = tables
        tables[name] = table

    return tables
