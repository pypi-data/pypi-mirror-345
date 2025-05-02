from antelop.utils.datajoint_utils import delete_restriction, delete_column
import re
from tabulate import tabulate
import functools
from pathlib import Path
from antelop.connection.transaction import operation_context, transaction_context


def delete_patch(table):
    # don't show deleted entries
    restriction = delete_restriction(table, "False")
    table = table & restriction
    _, projection = delete_column(table)
    table = table.proj(*projection)

    return table


def check_admin(query):
    username = query.connection.get_user().split("@")[0]
    admin = (query.tables["Experimenter"] & {"experimenter": username}).fetch1("admin")
    return admin


def safe_delete(query):
    with transaction_context(query.connection):
        data = (query._admin() & query.restriction).proj()
        restriction = delete_restriction(query._admin(), "True")
        for i in data:
            query._admin().update1({**i, **restriction})


def check_username(query):
    username = query.connection.get_user().split("@")[0]
    status = len(query - {"experimenter": username}) == 0
    return status


def full_names(tables):
    return {val.full_table_name: key for key, val in tables.items()}


def display(self, format='str', show='name'):
    """
    Performs a fetch but shows parent names rather than keys.

    Parameters:
    ----------
    format : str, optional
        The format in which to display the fetched data. 
        Options are 'str' for a string representation (default) or 'frame' for a pandas DataFrame.
    show : str, optional
        Determines whether to show parent names or IDs. 
        Options are 'name' to show parent names (default) or 'id' to show parent IDs.

    Returns:
    -------
    str or pandas.DataFrame
        If format is 'str', returns a string representation of the fetched data.
        If format is 'frame', returns a pandas DataFrame of the fetched data.

    Raises:
    ------
    ValueError
        If the 'show' parameter is not 'name' or 'id'.

    Notes:
    -----
    - When show='name', the function fetches data and replaces parent keys with parent names.
    - The function uses the `tabulate` library to format the output when format='str'.
    - The function handles external attributes, JSON fields, and blob fields separately.

    Example:
    -------
    >>> table.display(format='str', show='name')
    +----+-------------+-------------+
    | ID | Parent Name | Other Field |
    +----+-------------+-------------+
    | 1  | Parent1     | Value1      |
    | 2  | Parent2     | Value2      |
    +----+-------------+-------------+

    >>> table.display(format='frame', show='id')
        ID  Parent_ID  Other_Field
    0   1          1       Value1
    1   2          2       Value2
    """
    if show == 'name':
        parents = self.ancestors()
        query = self
        parent_keys_to_names = []  # list of tuples (parent_key, parent_name)
        for parent_full_name in parents:
            if parent_full_name == self.full_table_name:
                continue
            parent_table = self.tables[full_names(self.tables)[parent_full_name]]
            parent_name_col = parent_table.table_name.replace('#', '').replace('_', '') + "_name"
            parent_id_col = parent_table.table_name.replace('#', '').replace('_', '') + "_id"
            if parent_name_col not in parent_table.heading.names:
                continue
            if parent_id_col not in query.heading.names:
                continue
            query = query * parent_table.proj(parent_name_col)
            parent_keys_to_names.append((parent_id_col, parent_name_col))
    elif show == 'id':
        query = self
    else:
        raise ValueError("show must be 'name' or 'id'")

    projection = []
    external = []
    jsons = []
    blobs = []
    for key, val in query.heading.attributes.items():
        if val.is_attachment:
            external.append(key)
        elif val.json:
            jsons.append(key)
        elif val.is_blob:
            blobs.append(key)
        else:
            projection.append(key)

    # remove external attributes and deleted
    query = query.proj(*projection)

    total = len(query)

    # fetch query
    df = query.fetch(format="frame", limit=30)

    # reset index (so we can hide it later)
    df = df.reset_index()

    # replace json entries
    for i in jsons:
        df[i] = len(df.index) * ["json"]

    # replace blobs entries
    for i in blobs:
        df[i] = len(df.index) * ["blob"]

    # add blank external entries for display
    for i in external:
        df[i] = len(df.index) * ["external"]
    
    if show == 'name':
        for parent_key, parent_name in parent_keys_to_names:
            df[parent_key] = df[parent_name]
            df = df.drop(parent_name, axis=1)
            df = df.rename(columns={parent_key: parent_name})

    if format == 'str':
        display = tabulate(df, headers='keys', tablefmt='grid', showindex=False)
        display += f"\n\nNumber entries: {total}"
        return display
    elif format == 'frame':
        return df


def patch_table(table):
    """
    This is applied directly on the dj.Table objects
    """

    for method in ["insert", "delete", "update1", "delete_quick", "insert1"]:
        setattr(table, method, None)

    def help(self):
        print("Antelop table:")

        pattern = r'`[^`]+_([^`]+)`.`([^`]+)`'  # Only capture after _ and table name
        match = re.search(pattern, self.full_table_name)
        schema, table = match.groups()
        schema = schema.capitalize()
        table = ''.join([word.capitalize() for word in table.replace('#','_').split('_')])

        print(f"Schema: {schema}")
        print(f"Table: {table}")
        print("\n")

        print(self.original_heading)

        print("\n")
        print("Methods:")
        print("  - fetch()")
        print("  - fetch1()")
        print("  - delete()")
        print("  - insert()")
        print("  - insert1()")
        print("  - update1()")
        print("\n")
        
    setattr(table, "help", help)

    setattr(table, "display", functools.partialmethod(display, format='frame'))
    setattr(table, "__repr__", functools.partialmethod(display, format='str', show='name'))


    def proj_with_names(self):
        """
        Datajoint projection with column names, joining with ancestors to include their name attributes.
        """
        tables = self.tables
        table_name = self.table_name
        full_name_dict = full_names(tables)
        projection = list(self.heading.names)
        parents = self.ancestors()
        for parent_full_name in parents:
            parent_table = tables[full_name_dict[parent_full_name]]
            if parent_table.table_name == table_name:
                continue
            parent_name_col = parent_table.table_name.replace('#', '').replace('_', '') + "_name"
            parent_id_col = parent_table.table_name.replace('#', '').replace('_', '') + "_id"
            if parent_name_col in parent_table.heading.names:
                self = self * parent_table.proj(parent_name_col)
                projection.append(parent_name_col)
        return self.proj(*projection)

    setattr(table, "proj_with_names", proj_with_names)


    def delete(self, safemode=True, force=False):
        admin = check_admin(self)

        with operation_context(self.connection):
            if not admin:
                if not safemode and force:
                    query = self._admin() & self.restriction
                    query.delete(safemode=False)
                elif not safemode:
                    raise PermissionError(
                        "You do not have permission to perform permanent deletes"
                    )
                elif safemode:
                    safe_delete(self)

            else:
                if check_username(self):
                    if safemode:
                        safe_delete(self)
                    else:
                        query = self._admin() & self.restriction
                        query.delete(safemode=False)
                else:
                    raise PermissionError(
                        "You do not have permission to delete entries for other users"
                    )

    setattr(table, "delete", delete)

    def insert(self, *args, **kwargs):
        admin = check_admin(self)

        with operation_context(self.connection):
            if not admin:
                if not check_username(self):
                    raise PermissionError(
                        "You do not have permission to insert entries for other users"
                    )
                else:
                    self._admin().insert(*args, **kwargs)
            else:
                self._admin().insert(*args, **kwargs)

    setattr(table, "insert", insert)

    def insert1(self, *args, **kwargs):
        admin = check_admin(self)

        with operation_context(self.connection):
            if not admin:
                if not check_username(self):
                    raise PermissionError(
                        "You do not have permission to insert entries for other users"
                    )
                else:
                    self._admin().insert1(*args, **kwargs)
            else:
                self._admin().insert1(*args, **kwargs)

    setattr(table, "insert1", insert1)

    def update1(self, *args, **kwargs):
        admin = check_admin(self)

        with operation_context(self.connection):
            if not admin:
                if not check_username(self):
                    raise PermissionError(
                        "You do not have permission to update entries for other users"
                    )
                else:
                    self._admin().update1(*args, **kwargs)
            else:
                self._admin().update1(*args, **kwargs)

    setattr(table, "update1", update1)

    return table


def full_restore(query):
    """
    Function performs a full restore on the deleted objects and all its deleted children
    Since tables can have multiple parents, it needs to additionally check there are no remaining
    deleted parents
    """
    update_dict = {}

    with operation_context(query.connection):
        # what to update
        for tablename in query.descendants():
            table = query.tables[full_names(query.tables)[tablename]]
            table = query.tables[full_names(query.tables)[tablename]]
            child_query = table & query.proj() & delete_restriction(table, "True")
            for parentname in table.parents():
                if parentname not in query.tables:
                    parent = query.tables[full_names(query.tables)[parentname]]
                    col, _ = delete_column(parent)
                    child_query = child_query & (
                        parent.proj(*col) & delete_restriction(parent, "False")
                    )
            update_dict[tablename] = child_query.proj().fetch(as_dict=True)

        # update
        for tablename, data in update_dict.items():
            for i in data:
                deleted = delete_restriction(
                    query.tables[full_names(query.tables)[tablename]], "False"
                )
                query.tables[full_names(query.tables)[tablename]].update1(
                    {**i, **deleted}
                )


def patch_admin(table):
    """
    We also add restore functionality to the admin tables
    """

    def restore(self):
        """
        Applied on the admin table query object
        """

        admin = check_admin(self)

        if not admin:
            raise PermissionError("You do not have permission to restore entries")

        else:
            print("Restoring data")
            full_restore(self)

    setattr(table, "restore", restore)
    setattr(table, "display", functools.partialmethod(display, format='frame'))
    setattr(table, "__repr__", functools.partialmethod(display, format='str', show='name'))

    return table
