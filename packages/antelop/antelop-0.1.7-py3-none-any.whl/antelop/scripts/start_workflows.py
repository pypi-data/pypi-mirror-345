from antelop.connection import connect, import_schemas
from antelop.utils.os_utils import get_config
from antelop.utils.analysis_utils import import_analysis, functions_to_simplenamespace
import os
import types

config = get_config()
username = os.environ.get("DB_USER")
password = os.environ.get("DB_PASS")

if username is None or password is None:
    raise Exception("Please set the DB_USER and DB_PASS environment variables")

conn = connect.dbconnect(username, password)
tables = import_schemas.schema(conn)

for key, val in tables.items():
    globals()[key] = val

# import analysis functions
analysis_functions, import_errors = import_analysis(conn, tables)
local, stdlib, github = functions_to_simplenamespace(analysis_functions)
globals()["local"] = local
globals()["stdlib"] = stdlib
for key, val in github.items():
    globals()[key] = val


def print_errors(errors):
    """
    Function pretty prints errors
    """
    if len(errors) > 0:
        print("\n")
        print("Error importing the following analysis scripts:")
        for location, directories, script in errors:
            display_dirs = "/".join(directories)
            print(f"Script: {display_dirs}/{script}.py in {location}")
        print("\n")


print_errors(import_errors)
