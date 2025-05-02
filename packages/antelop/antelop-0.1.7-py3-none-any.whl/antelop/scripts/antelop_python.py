from antelop.connection.connect import dbconnect
from antelop.connection import import_schemas
from antelop.utils.os_utils import get_config
from antelop.utils.analysis_utils import (
    import_analysis,
    reload_analysis,
    functions_to_simplenamespace,
)
from IPython import embed
import getpass
import antelop.scripts.hold_conn as hold


def print_errors(errors):
    """
    Function pretty prints errors
    """
    if len(errors) > 0:
        print("\n")
        print("Error importing the following analysis scripts:")
        for location, directories, script in errors:
            display_dirs = "/".join(directories) if isinstance(directories, list) else directories
            print(f"Script: {display_dirs}/{script}.py in {location}")
        print("\n")

class Functions:
    def __init__(self, stdlib, local, github):
        self.stdlib = stdlib
        self.local = local
        self.github = github
    def __repr__(self):
        functions = "\n"
        functions += "Antelop analysis functions\n"
        functions += "--------------------------\n"
        functions += "\nstdlib:\n"
        for line in str(self.stdlib).splitlines():
            functions += f"  {line}\n"
        functions += "\nlocal:\n"
        for line in str(self.local).splitlines():
            functions += f"  {line}\n"
        for name, repo in self.github.items():
            functions += f"\n{name}:\n"
            for line in str(repo).splitlines():
                functions += f"  {line}\n"

        return functions


def run():
    # first check config file exists
    config = get_config()
    if config is None:
        print("\n")
        print("Config file not found.")
        print("Please run `antelop-config` to generate a configuration file.")
        exit()

    # connect to database
    print("\n")
    username = input("Please enter your username: ")
    password = getpass.getpass("Please enter your password: ")
    print("\n")

    global conn
    conn = dbconnect(username, password)
    global tables
    tables = import_schemas.schema(conn)

    if hold.conn is None:
        hold.conn = conn
    if hold.tables is None:
        hold.tables = tables

    for key, val in tables.items():
        globals()[key] = val

    # import analysis functions
    analysis_functions, import_errors = import_analysis(conn, tables)
    local, stdlib, github = functions_to_simplenamespace(analysis_functions)
    globals()["local"] = local
    globals()["stdlib"] = stdlib
    for key, val in github.items():
        globals()[key] = val
    globals()["functions"] = Functions(stdlib, local, github)
    print_errors(import_errors)
    def reload():
        """
        Global function to relaod all analysis functions interactively
        """
        analysis_functions, import_errors = reload_analysis(conn, tables)
        local, stdlib, github = functions_to_simplenamespace(analysis_functions)
        globals()["local"] = local
        globals()["stdlib"] = stdlib
        for key, val in github.items():
            globals()[key] = val
        print_errors(import_errors)
        globals()["functions"] = Functions(stdlib, local, github)

    # start ipython session
    embed()
