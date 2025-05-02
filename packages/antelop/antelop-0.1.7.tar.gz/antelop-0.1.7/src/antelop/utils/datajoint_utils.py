"""
Utility functions for datajoint table manipulations

Author: Rory Bedfod
Date: 07/07/23
"""

import pandas as pd
import datajoint as dj
import numpy as np
import pathlib
from pathlib import Path
import os
import sys
from io import StringIO
import json
import datetime
import tempfile
from antelop.connection.connect_utils import thread_connect, thread_connect_admin
from antelop.connection.transaction import transaction_context
import zipfile


def delete_status(tablename, tables, query):
    """
    Function returns the delete status of a table
    Options include 'temp', 'perm', 'none', 'custom-behave'
    """

    from antelop.utils.antelop_utils import check_animals

    parent_tables = [
        i for i in tables.values() if i.full_table_name in tables[tablename].parents()
    ]

    table = tables[tablename]

    no_delete = ["Feature"]

    # can't delete part tables for concurrency
    if tablename in no_delete:
        return "none"

    # custom behaviour for self and world tables
    elif (
        tablename == "Self"
        and len(check_animals((tables["BehaviourRig"] & query).fetch1("rig_json"))) == 1
    ):
        return "custom-behave"

    # if there's a spare key, can temp delete
    elif check_spare_key(table, parent_tables):
        return "temp"

    # if there's no spare key, permanent delete
    else:
        return "perm"


def check_spare_key(table, parent_tables):
    """
    Function checks if there's a spare key in the table primary keys, not belonging to any parent
    """

    # construct join query of all parents
    counter = 0
    for parent in parent_tables:
        if counter == 0:
            parent_join = parent.proj()
            counter += 1
        else:
            parent_join = parent_join * parent.proj()

    # check if there's a key not defined in parents
    spare_key = False
    for key in table.primary_key:
        if key not in parent_join.heading.attributes.keys():
            spare_key = True
            break

    return spare_key


def insertable_tables(tables, subtables, username):
    """
    Returns the subdictionary of all tables the user can insert into
    """
    available_tables = dict()

    for tablename, table in subtables.items():
        # compute all parents of this table
        parent_tables = [
            i for i in tables.values() if i.full_table_name in table.parents()
        ]

        spare_key = check_spare_key(table, parent_tables)

        # if there's a spare key, and all parent have undeleted entries
        if spare_key:
            if len(parent_tables) > 0 and all(
                [len(i & {"experimenter": username}) > 0 for i in parent_tables]
            ):
                available_tables[tablename] = table

        # if there's no spare key, and there are remaining combinations of parent keys
        else:
            counter = 0
            for parent in parent_tables:
                if counter == 0:
                    parent_join = parent.proj()
                    counter += 1
                else:
                    parent_join = parent_join * parent.proj()

            # if there are any entries in the join query not already in the table
            if len(parent_join - table & {"experimenter": username}) > 0:
                available_tables[tablename] = table

    # can't insert into experimenter table
    if "Experimenter" in available_tables.keys():
        del available_tables["Experimenter"]

    return available_tables


def searchable_tables(tables, delete_mode):
    """
    Returns the subdictionary of tables the user is able to search
    """

    available_tables = dict()

    for tablename, table in tables.items():
        if table & delete_restriction(table, delete_mode):
            available_tables[tablename] = table

    return available_tables


def form_query(querystring, tables, admin=False):
    """
    Forms a valid datajoint query object from an input string
    Supports all the tables, operators, and restrictions
    Should return errors on any misformed queries (provides some protection against malignant SQL)
    Inputs: querystring: string representing datajoint query
    Returns: query: a valid datajoint query object
    """

    # first, move variables into local namespace
    if not admin:
        for tablename in tables.keys():
            locals()[tablename] = tables[tablename]
    else:
        for tablename in tables.keys():
            locals()[tablename] = tables[tablename]._admin()

    # convert text to actual query object
    query = eval(querystring)

    return query


def parent_primaries(table, tables, primary_only=False):
    """
    Finds the parent tables referenced by all foreign keys for a given table

    Inputs: table: the table to apply the operation to
            tables: a dictionary of all tables in the database
            primary_only: if True, only return for primary keys of the table

    Returns: a dictionary of attribute:table mappings for all foreign keys
    """

    # calculate all parents of table
    full_names = {val.full_table_name: key for key, val in tables.items()}
    if type(table) == dj.expression.QueryExpression:
        join_tables = table.support
        parents = []
        for join_table in join_tables:
            parents += join_table.parents()
        parents = list(set(parents))
    else:
        parents = table.parents()

    # dictionary with parent primary keys mapping to the parent tables for querying
    parent_tables = {}
    for par_table in tables.values():
        for parent in parents:
            if par_table.full_table_name == parent:
                for primary_key in par_table.primary_key:
                    parent_tables[primary_key] = par_table

    if primary_only:
        primary_keys = table.primary_key
        parent_tables = {
            key: val for key, val in parent_tables.items() if key in primary_keys
        }

    return parent_tables


def ancestor_primaries(table, tables):
    """
    Finds the earliest ancestor tables referenced by all foreign keys for a given table

    Inputs: table: the table to apply the operation to
            tables: a dictionary of all tables in the database

    Returns: a dictionary of attribute:table mappings for all foreign keys
    """

    # first return all parent tables for all foreign keys
    parent_tables = parent_primaries(table, tables)
    next_tables = parent_tables.copy()
    result = {}

    # loop as long as there are still upstream tables
    while next_tables:
        # now for all referenced tables, calculate all upstream tables
        next_tables = {}
        for key, tab in parent_tables.items():
            next_tables.update(parent_primaries(tab, tables, primary_only=True))

        # calculate tables that have finished
        result.update(
            {
                key: val
                for key, val in parent_tables.items()
                if key not in next_tables.keys()
            }
        )
        parent_tables = {
            key: val for key, val in next_tables.items() if key not in result.keys()
        }
        next_tables = dict(parent_tables)

    return result


def query_without_external(query, mode="Sequential Filter"):
    """
    Queries the database without downloading external attributes or displaying jsons

    Inputs: table: table to be queried
            restriction: optional dict of restrictions

    Outputs: dataframe of query with up to 30 items (with placeholders for external and json)
             length of full query
    """

    # calculate any external attributes to be removed (so it doesn't download)
    # also calculate any jsons to be removed (since they look messy)

    if mode == "Sequential Filter":
        df = query.display(show='name')
    elif mode == "Navigation":
        df = query.display(show='id')

    return df, len(query)


def download_data(
    querystring,
    download_path,
    mode="Sequential Filter",
    username=None,
    password=None,
    conn=None,
):
    """
    Downloads query as a numpy array as well as external data.
    Inputs: querystring: the query in string form (needs to be serialisble - queries themselves include connections)
            download_path: path to download data to
    """

    # function runs in different process so needs to establish its own connection
    conn, tables_download = thread_connect(conn, username, password)

    # form query
    query = form_query(querystring, tables_download)

    # append keys we want to keep
    projection = []
    for key in query.heading.attributes.keys():
        if mode == "Sequential Filter":
            continue
        elif key == f"""{query.table_name.replace("_", "")}_in_compute""":
            continue
        else:
            projection.append(key)

    # remove deleted attribute from query
    query = query.proj(*projection)

    # fetch results of query
    results = query.fetch(download_path=download_path)

    # loop through tables attributes to change external paths
    keys = list(query.heading.attributes.keys())
    for key in keys:
        # if attribute is an external file
        if query.heading.attributes[key].is_attachment:
            # convert to dataframe
            df = pd.DataFrame(results)

            # loop and change path to current directory
            for index, row in df.iterrows():
                # load path
                path = pathlib.Path(row[key])

                # update to just the filename
                row[key] = path.name

            # convert back to recarray
            results = df.to_records()

    # save array to disk
    np.save(str(download_path), results)


def check_session(tables, insert_dict):
    """
    function checks if directory has correct extension
    """

    # first, check the directory structure is correct
    # load config file
    resources = Path(os.path.abspath(__file__)).parent.parent / "resources"
    with open(resources / "ephys_extensions.json") as f:
        extensions = json.load(f)

    # query equipment type
    ephys_acquisition = insert_dict["ephys_acquisition"]

    # check if ephys acquisition is none
    if ephys_acquisition == "none":
        return False

    #  get list of extensions
    equip_ext = extensions[ephys_acquisition]
    checkls = []

    # check all files exist
    for ext in equip_ext:
        if ext == "dir":
            # check if the folder contains a directory
            status = any(item.is_dir() for item in insert_dict["recording"].iterdir())
        else:
            status = len(list(insert_dict["recording"].glob(f"*.{ext}"))) > 0
        checkls.append(status)

    # check channel mapping
    if 'device_channel_mapping' in insert_dict.keys():
        if not Path(insert_dict['device_channel_mapping']).exists():
            return False
        else:
            with open(insert_dict['device_channel_mapping']) as f:
                device_channel_mapping = json.load(f)
                if not type(device_channel_mapping) == list:
                    return False
                if not all([isinstance(i, int) for i in device_channel_mapping]):
                    return False

    # return true if all files exist
    return all(checkls)


def get_ephys_extensions():
    resources = Path(os.path.abspath(__file__)).parent.parent / "resources"
    with open(resources / "ephys_extensions.json") as f:
        extensions = json.load(f)
    return extensions


def upload(
    tablename, insert_dict, mode="insert", conn=None, username=None, password=None
):
    """
    Uploads data to database including external data
    Inputs: table: the table to insert to
            insert_dict: the content of the upload as a dictionary
    """

    # function runs in different process so needs to establish its own connection
    conn_upload, tables_upload = thread_connect(conn, username, password)

    # get table
    table_upload = tables_upload[tablename]

    # make dict mapping full_table_names to display table full_table_names
    full_names = {val.full_table_name: key for key, val in tables_upload.items()}

    # if it's a session, we need to zip the raw data first and update the path
    if tablename == "Recording":
        # extract dirpath
        dirpath = insert_dict["recording"]

        # create zipfile name from primary key
        recfile = Path(dirpath).with_suffix(".zip")

        # get files to zip
        extensions = get_ephys_extensions()
        ephys_acquisition = insert_dict["ephys_acquisition"]
        equip_ext = extensions[ephys_acquisition]
        files = []
        for ext in equip_ext:
            if ext == "dir":
                # add all directories
                files.extend([item for item in Path(dirpath).iterdir() if item.is_dir()])
            else:
                files.extend(list(Path(dirpath).glob(f"*.{ext}")))

        # create zipfile
        with zipfile.ZipFile(recfile, "w") as zipf:
            for file in files:
                if file.is_dir():
                    # Recursively add all files in the directory
                    for root, _, filenames in os.walk(file):
                        for filename in filenames:
                            filepath = Path(root) / filename
                            arcname = filepath.relative_to(dirpath)  # Preserve relative path
                            zipf.write(filepath, arcname=arcname)
                else:
                    # Add individual files
                    zipf.write(file, arcname=file.name)

        # update dirpath
        insert_dict["recording"] = str(recfile)

        if 'device_channel_mapping' in insert_dict.keys():
            with open(insert_dict['device_channel_mapping']) as f:
                device_channel_mapping = json.load(f)

                insert_dict['device_channel_mapping'] = device_channel_mapping

    # start insert transaction
    with transaction_context(table_upload.connection):
        # insert data
        if mode == "insert":
            table_upload.insert1(insert_dict)

        elif mode == "update":
            table_upload.update1(insert_dict)

        # after insertion, need to check the delete status of the upstream tables
        # as these could get safe deleted during the insert
        for parentname in table_upload.parents():
            # retrieve datajoint table from full name
            parent = tables_upload[full_names[parentname]]

            # check parent delete status
            if full_names[parentname] == "Experimenter":
                delete_status = "False"
            else:
                delete_status = len(parent & insert_dict) > 0

            # if any parents are deleted
            if delete_status == "True":
                # raise error so thread status checker works and transaction rolls back
                raise Exception("A parent table has been deleted during the upload.")


def safe_delete(querystring, username=None, password=None, conn=None):
    """
    Safely deletes data from the database (just changes the 'delete' attribute to True)
    These deletes cascade
    Inputs: tablename: the table to delete from
            restriction: the key to delete
    """
    conn_del, tables_del = thread_connect_admin(conn, username, password)

    # form query
    query = form_query(querystring, tables_del)

    update_dict = {}

    # make dict mapping full_table_names to display table full_table_names
    full_names = {val.full_table_name: key for key, val in tables_del.items()}

    # all updates in transaction
    with transaction_context(conn_del):
        # loop through all tables to be modified
        for tablename in query.descendants():
            # retrieve datajoint table from full name
            table = tables_del[full_names[tablename]]

            # main query
            full_query = table & (
                query.proj()
                & {f"""{query.table_name.replace("_", "")}_deleted""": "False"}
            )

            # fetch primary keys of rows to be deleted
            data = full_query.proj().fetch(as_dict=True)

            update_dict[tablename] = data

        # now loop again to perform modifications
        for tablename, data in update_dict.items():
            # retrieve datajoint table from full name
            table = tables_del[full_names[tablename]]

            for i in data:
                table.update1(
                    {**i, f"""{table.table_name.replace("_", "")}_deleted""": "True"}
                )


def restore(querystring, username=None, password=None, conn=None):
    """
    Restores deleted data from the database (just changes the 'delete' attribute to False)
    These restores cascade
    Inputs: querystring: the query to restore from
    """
    conn_res, tables_res = thread_connect(conn, username, password)

    # form query
    query = form_query(querystring, tables_res, admin=True)
    query = query & query.restriction
    query.restore()


def release_computation(
    tablename, restriction, username=None, password=None, conn=None
):
    """
    Releases data from computation(just changes the 'in_compute' attribute to False)
    Inputs: querystring: the query to release from
    """
    conn_rel, tables_rel = thread_connect(conn, username, password)

    # form datajoint querystring
    querystring = f"{tablename} & {str(restriction)}"

    # form query
    query = form_query(querystring, tables_rel)

    table = tables_rel[tablename]

    # all updates in transaction
    with transaction_context(conn_rel):
        if tablename == "SpikeSorting":
            # get data to update
            data = query.proj("manually_curated").fetch(as_dict=True)

            # loop through data and update or delete
            for i in data:
                if i["manually_curated"] == "True":
                    table.update1(
                        {
                            **i,
                            f"""{table.table_name.replace("_", "")}_in_compute""": "False",
                        }
                    )
                elif i["manually_curated"] == "False":
                    with SimulateEnterContext():
                        (table & i).delete(safemode=False)

        elif tablename == "LabelledFrames":
            data = query.proj().fetch(as_dict=True)
            for i in data:
                table.update1(
                    {
                        **i,
                        f"""{table.table_name.replace("_", "")}_in_compute""": "False",
                    }
                )


def names_to_ids(keys, tables):
    """
    Functions converts a list of keys with name columns to id columns
    input: keys: list of keys
    return: list of keys with id columns
    """
    table_names = {table.table_name.replace('#','').replace('_',''):table for table in tables.values()}
    new_keys = []
    for key in keys:
        new_key = {}
        for k, v in key.items():
            if "name" in k:
                id_col = k.replace("name", "id")
                table = table_names[k.replace("_name", "")]
                tmp_key = {**new_key, k: v}
                new_key[id_col] = (table & tmp_key).fetch1(k.replace("_name", "_id"))
            else:
                new_key[k] = v
        new_keys.append(new_key)
    return new_keys


def show_deletes(tables, query):
    """
    Function to show all the deletes that cascade
    """
    query = query.proj()

    # make dict mapping full_table_names to display table full_table_names
    full_names = {val.full_table_name: key for key, val in tables.items()}

    # initialise dataframe with number of deletes from each table
    descendant_dict = {"Table": [], "Number entries to be deleted": []}

    # cycle through descendants calculating number that will get deleted
    for descendant in query.descendants():

        table = tables[full_names[descendant]]
        # main new_query
        full_query = table & query

        number_entries = len(full_query)
        if number_entries > 0:
            descendant_dict["Table"].append(full_names[descendant])
            descendant_dict["Number entries to be deleted"].append(number_entries)

    return descendant_dict


def show_restores(tables, query):
    """
    Function to show all the restores that cascade
    """

    # make dict mapping full_table_names to display table full_table_names
    full_names = {val.full_table_name: key for key, val in tables.items()}

    # initialise dataframe with number of deletes from each table
    descendant_dict = {"Table": [], "Number entries to be restored": []}

    # cycle through descendants calculating number that will get deleted
    for descendant in query.descendants():
        table = tables[full_names[descendant]]

        # want entries that are deleted and join the query
        tmp_query = table * query.proj() & {
            f"""{table.table_name.replace("_", "")}_deleted""": "True"
        }

        # additionally, need to check the parents are either descendants of the query, or are undeleted
        if query.table_name not in descendant:  # skip if parent table
            for parentname in table.parents():
                if parentname not in query.descendants():
                    parent = tables[full_names[parentname]]

                    tmp_query = tmp_query & parent

        number_entries = len(tmp_query)
        if number_entries > 0:
            descendant_dict["Table"].append(full_names[descendant])
            descendant_dict["Number entries to be restored"].append(number_entries)

    return descendant_dict


def show_true_deletes(tables, query):
    """
    Function to show all the restores that cascade
    """

    # make dict mapping full_table_names to display table full_table_names
    full_names = {val.full_table_name: key for key, val in tables.items()}

    # initialise dataframe with number of deletes from each table
    descendant_dict = {"Table": [], "Number entries to be restored": []}

    # cycle through descendants calculating number that will get deleted
    for descendant in query.descendants():
        table = tables[full_names[descendant]]

        # want entries that are deleted and join the query
        tmp_query = table * query.proj() & {
            f"""{table.table_name.replace("_", "")}_deleted""": "True"
        }

        number_entries = len(tmp_query)
        if number_entries > 0:
            descendant_dict["Table"].append(full_names[descendant])
            descendant_dict["Number entries to be restored"].append(number_entries)

    return descendant_dict


def query_to_str(query):
    """
    Function makes an easily readable string from a datajoint query
    Used for file names and identifying queries
    """

    # extract SQL
    string = query.make_sql()

    # take table name
    string = string.split("FROM")[1]
    string = string.split(".")[1]
    string = string.split(" ")[0]

    # clean tablename
    string = (
        string.replace("`", "")
        .replace("#", "")
        .replace(".", "")
        .replace("_", "")
        .strip()
    )

    # final name
    name = (
        "antelop-"
        + string
        + "--"
        + datetime.datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
    )

    return name


def delete_restriction(query, delete_mode="False"):
    cols = list((query & False).fetch(format="frame").reset_index().columns)
    delete_dict = {}
    for col in cols:
        if "deleted" in col:
            delete_dict[col] = delete_mode
    return delete_dict


def delete_column(query):
    cols = list((query & False).fetch(format="frame").reset_index().columns)
    to_delete = []
    not_delete = []
    for col in cols:
        if "deleted" in col:
            to_delete.append(col)
        else:
            not_delete.append(col)
    return to_delete, not_delete


def get_tablename(query):
    cols = list((query & False).fetch(format="frame").reset_index().columns)
    for col in cols:
        if "name" in col and col != "full_name":
            return col


# some datajoint functions seem to be broken and require user input
class SimulateEnterContext:
    def __enter__(self):
        self.original_stdin = sys.stdin
        self.fake_input = StringIO("\n")  # '\n' simulates hitting Enter
        sys.stdin = self.fake_input
        self.original_stdout = sys.stdout
        sys.stdout = StringIO()

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdin = self.original_stdin
        self.fake_input.close()
        sys.stdout = self.original_stdout


def ids_to_names(cols):
    """
    Functions converts a list of table attributes with id columns to name columns
    """
    names = []
    for col in cols:
        if "id" in col:
            names.append(col.replace("id", "name"))
        else:
            names.append(col)
    return names