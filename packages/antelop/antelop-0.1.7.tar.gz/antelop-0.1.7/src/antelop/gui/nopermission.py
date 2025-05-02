import streamlit_antd_components as sac


def show(username, tables):
    sac.alert(
        label="Permission denied",
        description="You do not have admin privileges",
        color="red",
        icon=True,
    )
