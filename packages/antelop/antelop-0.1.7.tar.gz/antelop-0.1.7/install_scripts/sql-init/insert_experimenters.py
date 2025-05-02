from antelop.utils.os_utils import get_config
from antelop.connection.connect import dbconnect
from antelop.connection import import_schemas
import getpass
from pathlib import Path
import csv

config = get_config()
if config is None:
    print("\n")
    print("Config file not found.")
    print("Please run `antelop-config` to generate a configuration file.")
    exit()

# Form database connection
print("\n")
username = input("Please enter your username: ")
password = getpass.getpass("Please enter your password: ")
print("\n")
conn = dbconnect(username, password)
tables = import_schemas.schema(conn)

# Load csv file of experimenters
csv_file = Path(__file__).parent / "experimenters.csv"
if not csv_file.exists():
    raise FileNotFoundError(f"CSV file {csv_file} not found.")
with csv_file.open(mode='r') as file:
    reader = csv.DictReader(file)
    experimenters = [row for row in reader]

# Insert experimenters into the database
tables['Experimenter'].insert(experimenters, skip_duplicates=True)