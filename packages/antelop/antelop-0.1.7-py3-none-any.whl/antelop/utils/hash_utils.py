import hashlib
import json
import numpy as np
import inspect
from pathlib import Path


def hash_list(data_list):
    # Serialize the list to a JSON string
    json_string = json.dumps(data_list)

    # Encode the JSON string to bytes
    json_bytes = json_string.encode("utf-8")

    # Create a SHA-256 hash object
    sha256 = hashlib.sha256()

    # Update the hash object with the byte representation
    sha256.update(json_bytes)

    # Get the hexadecimal representation of the hash
    hash_hex = sha256.hexdigest()

    return hash_hex


def hash_query(query):
    """
    Function produces a reproducible hash of a query.
    It uses the MD5 algorithm on the database side and is therefore quite fast.
    """

    hashtable = query.proj(
        row_hash=f"MD5(CONCAT_WS('|',{', '.join(f'HEX(`{k}`)' for k in query.heading)}))"
    ).fetch("row_hash")

    return hashtable


def hash_tables(tables, key):
    """
    Function hashes the data across several tables belonging to a given key.
    This can be used to check if data is consistent fo a given key across the database.

    Arguments:
    tables: list of tables to hash
    key: dict giving a datajoint restriction
    """

    table_hashes = []
    tables.sort(key=lambda x: x.full_table_name)
    for table in tables:
        query = table & key
        row_hashes = hash_query(query)
        row_hashes = list(np.sort(row_hashes))
        table_hashes.append(hash_list(row_hashes))

    hash = hash_list(table_hashes)
    return hash


def code_hash(function):
    """
    Function hashes the code of a function.
    """

    code = inspect.getsource(function.run)
    code = code.encode("utf-8")
    sha256 = hashlib.sha256()
    sha256.update(code)
    hash = sha256.hexdigest()
    return hash


def list_to_datajoint(tables, tablenames):
    """
    Function to convert a list of tablenames to a list of datajoint tables.
    """

    table_list = []
    for table in tablenames:
        table_list.append(tables[table])
    return table_list


def dfs_functions(self, functions):
    """
    Does a depth first search to find the graph of all functions that are called recursively.
    Assumes functions are called in a tree. Could be modified if loops are allowed later.
    """

    # base case - return tables
    if not hasattr(self, "calls"):
        tables = []
        if isinstance(self.query, str):
            tables.append(self.query)
        elif isinstance(self.query, list):
            tables = self.query
        if hasattr(self, "data"):
            if isinstance(self.data, str):
                tables.append(self.data)
            elif isinstance(self.data, list):
                tables += self.data
        return tables

    # otherwise recurse
    else:
        tables = []
        # loop through all recursed functions
        for function in self.calls:
            # actually instantiate function from string
            if "." in function:
                location, folder, function = function.split(".")
                for f in functions:
                    if (
                        f.name == function
                        and f.folder == folder
                        and f.location == location
                    ):
                        function_inst = f
            else:
                folder = Path(inspect.getsourcefile(self.__class__.__bases__[0])).stem
                for f in functions:
                    if f.name == function and f.folder == folder:
                        function_inst = f

            # recurse, accumulating children tables
            tables.extend(dfs_functions(function_inst, functions))

        # append self's tables
        if isinstance(self.query, str):
            tables.append(self.query)
        elif isinstance(self.query, list):
            tables.extend(self.query)
        if hasattr(self, "data"):
            if isinstance(self.data, str):
                tables.append(self.data)
            elif isinstance(self.data, list):
                tables.extend(self.data)
        tables = list(set(tables))

        return tables
