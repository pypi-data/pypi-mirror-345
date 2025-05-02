from contextlib import contextmanager
import datajoint as dj
from antelop.connection.permission import patch_table, patch_admin


@contextmanager
def schema_context_manager(admin=False):
    # Create new classes that inherit from the original classes
    original_classes = {
        "manual": patch_admin(type("Manual", (dj.Manual,), {})),
        "lookup": patch_admin(type("Lookup", (dj.Lookup,), {})),
        "imported": patch_admin(type("Imported", (dj.Imported,), {})),
        "computed": patch_admin(type("Computed", (dj.Computed,), {})),
    }

    # Create patched versions of the classes
    patched_classes = {
        "manual": patch_table(type("Manual", (dj.Manual,), {})),
        "lookup": patch_table(type("Lookup", (dj.Lookup,), {})),
        "imported": patch_table(type("Imported", (dj.Imported,), {})),
        "computed": patch_table(type("Computed", (dj.Computed,), {})),
    }

    if admin:
        yield original_classes
    else:
        yield patched_classes

class AntelopTables(dict):
    """
    Pretty prints all tables in the database
    """
    def __repr__(self):

        display_dict = {}
        for schema in ['metadata', 'ephys', 'behaviour']:
            display_dict[schema] = []
            for key, value in self.items():
                if schema in value.full_table_name:
                    display_dict[schema].append(key)

        display_str = ''
        for schema, tables in display_dict.items():
            display_str += f'\n{schema.capitalize()}:\n'
            for table in tables:
                display_str += f'  - {table}\n'

        return display_str