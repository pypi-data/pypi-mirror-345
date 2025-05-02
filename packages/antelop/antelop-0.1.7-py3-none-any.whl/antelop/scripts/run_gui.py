import os
from pathlib import Path
from antelop.utils.os_utils import cp_st_config
import runpy
import sys
import warnings
from contextlib import contextmanager, redirect_stdout, redirect_stderr
import argparse
from antelop.scripts.find_port import find_available_port


@contextmanager
def suppress_stdout(suppress=True):
    if suppress:
        with open(os.devnull, "w") as devnull:
            with redirect_stdout(devnull), redirect_stderr(devnull):
                yield
    else:
        yield


def run():
    parser = argparse.ArgumentParser(description="Run Antelop GUI")
    parser.add_argument("--debug", action="store_true", help="Run with debug output")
    args = parser.parse_args()

    try:
        import streamlit
    except ImportError:
        print(
            """
Antelop GUI is not installed. Please install using:

pip install antelop[gui]

Or run the command line version using:

antelop-python
            """
        )
    else:
        # copy streamlit config to home if it doesn't exist
        cp_st_config()

        app = Path(os.path.abspath(__file__)).parent / "app.py"
        debug_app = Path(os.path.abspath(__file__)).parent / "debug_app.py"

        port = find_available_port()

        print(f"""
Welcome to Antelop!

http://localhost:{port}
""")

        with suppress_stdout(not args.debug):
            if not args.debug:
                sys.argv = ["streamlit", "run", str(app), "--server.port", str(port)]
            else:
                sys.argv = ["streamlit", "run", str(debug_app), "--server.port", str(port)]
            runpy.run_module("streamlit", run_name="__main__")

if __name__ == '__main__':
    run()
