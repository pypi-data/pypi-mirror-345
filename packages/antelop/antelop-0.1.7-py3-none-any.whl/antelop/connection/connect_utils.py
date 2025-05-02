from antelop.connection.connect import dbconnect
import antelop.connection.import_schemas as import_schemas


def thread_connect(conn=None, username=None, password=None):
    """
    Function checks if you're in the streamlit main thread or worker thread
    and returns the connection
    """
    if conn is None:
        conn = dbconnect(username, password)
        tables = import_schemas.schema(conn)
    else:
        tables = import_schemas.schema(conn)

    return conn, tables


def thread_connect_admin(conn=None, username=None, password=None):
    """
    Function checks if you're in the streamlit main thread or worker thread
    and returns the connection
    """
    if conn is None:
        conn = dbconnect(username, password)
        user_tables = import_schemas.schema(conn)
        tables = user_tables["Experimenter"].tables
    else:
        user_tables = import_schemas.schema(conn)
        tables = user_tables["Experimenter"].tables

    return conn, tables


def connect(username=None, password=None):
    """
    Function checks if you're in IPython, streamlit, or a script and returns the connection and tables
    """
    if check_streamlit():
        conn = dbconnect(username, password)
        tables = import_schemas.schema(conn)
    elif hasattr(sys, "ps1") or sys.flags.interactive:
        import antelop.scripts.hold_conn as hold

        conn = hold.conn
        tables = hold.tables
    else:
        import antelop.load_connection as db

        conn = getattr(db, "conn")
        tables = {}
        for table in dir(db):
            if not table.startswith("_"):
                tables[table] = getattr(db, table)

    return conn, tables


def check_streamlit():
    """
    Function to check whether python code is run within streamlit

    Returns
    -------
    use_streamlit : boolean
        True if code is run within streamlit, else False
    """
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        if not get_script_run_ctx():
            use_streamlit = False
        else:
            use_streamlit = True
    except ModuleNotFoundError:
        use_streamlit = False
    return use_streamlit
