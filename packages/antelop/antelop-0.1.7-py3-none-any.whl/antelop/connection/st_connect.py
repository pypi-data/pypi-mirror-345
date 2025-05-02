import streamlit as st
from antelop.connection.connect import dbconnect


def validate_connection(conn):
    """
    Load connection, validate, and return connection.
    """
    try:
        conn.ping()
        return True
    except Exception:
        print("Connection lost, reconnecting...")
        return False


@st.cache_resource(validate=validate_connection)
def connect():
    """
    Function used by streamlit to connect to database and effectively
    cache the connection.
    """

    conn = dbconnect(st.session_state.username, st.session_state.password)
    return conn


# check credentials and return connection
def check_credentials():
    try:
        conn = dbconnect(st.session_state.username, st.session_state.password)
        return True

    except Exception:
        return False
