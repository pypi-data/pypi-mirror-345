import inspect
import pandas as pd
from pathlib import Path
from antelop.utils.hash_utils import hash_tables, list_to_datajoint, code_hash
import json
import pprint
import numpy as np
from matplotlib.figure import Figure


def antelop_analysis(cls):
    """
    This is a class decorator used to reduce boilerplate code in analysis functions.
    """

    # initialise with connection
    def __init__(self, conn):
        super(cls, self).__init__(conn)

    cls.__init__ = __init__

    # inherit from AnalysisBase
    class Child(cls, AnalysisBase):
        __doc__ = cls.__doc__
        pass

    return Child


class AnalysisBase:
    name: str
    query: str
    returns: dict
    args: dict
    hidden: bool = False

    def __init__(self, conn):
        self.conn = conn
        self.tables = conn.tables

    def run(self, *args):
        raise NotImplementedError

    def get_directory(self):
        for i in self.__class__.__bases__:
            if i.__name__ != "AnalysisBase":
                return i.__module__.split(".")[-1]

    def __repr__(self):
        folder = self.folder if isinstance(self.folder, str) else "/".join(self.folder)
        args = pprint.pformat(self.args) if hasattr(self, "args") else "None"
        docs = self.__doc__.strip() if hasattr(self, "__doc__") else "None"

        fct_name = self.location
        if isinstance(self.folder, str):
            fct_name += "." + self.folder
        elif isinstance(self.folder, list):
            fct_name += "." + ".".join(self.folder)
        fct_name += "." + self.name

        string = (
            "Antelop analysis\n"
            f"Function: {self.name}\n"
            "\n"
            "Parameters:\n"
            f"  - location={self.location},\n"
            f"  - folder={folder},\n"
            f"  - query={pprint.pformat(self.query)},\n"
            f"  - returns={pprint.pformat(self.returns)},\n"
            f"  - args={args}\n"
            f"\n"
            f"{docs}"
            "\n\n"
        )

        methods = (
            "Methods:\n"
            f"  - {fct_name}(restriction, *args): Run the function with the given restriction and arguments.\n"
            f"  - {fct_name}.save_result(filepath='./result', format='pkl', restriction={{}}, *args): Run the function and save the result to disk.\n"
            f"  - {fct_name}.rerun(json_path): Load a reproducibility json and rerun the function with the same arguments.\n"
            f"  - {fct_name}.check_hash(json_path): Load a reproducibility json and check the data and code hash.\n"
            f"  - {fct_name}.reproduce(json_path, result_path, format='pkl'): Load a reproducibility json and run the function with the same arguments.\n"
        )

        string += methods
        return string

    def help(self):
        print(self.__repr__())

    def __call__(self, restriction={}, *args, **kwargs):
        # first, check everything initialized
        if not all([self.name, self.query, self.returns]):
            raise TypeError("Function not properly defined")

        # append built-in restriction
        if hasattr(self, "key"):
            restriction = {**restriction, **self.key}

        # get primary keys from restriction
        if isinstance(self.query, str):
            table = self.tables[self.query].proj()
        elif isinstance(self.query, list):
            table = self.tables[self.query[0]]
            for q in self.query[1:]:
                table = table * self.tables[q].proj()
        dataset = (table & restriction).proj().fetch(as_dict=True)

        # loop through primary keys and run function
        results = []
        for primary_key in dataset:
            result = self.run(primary_key, *args, **kwargs)
            answer = primary_key.copy()
            for i, key in enumerate(self.returns.keys()):
                if len(self.returns.keys()) == 1:
                    answer[key] = result
                else:
                    answer[key] = result[i]
            results.append(answer)

        if len(results) == 1:
            return results[0]
        else:
            return results

    def save_reproducibility(self, filepath, restriction, *args, **kwargs):
        """
        Saves the reproducibility json to disk.
        """

        # make restriction json serializable
        for key, val in restriction.items():
            if isinstance(val, np.integer):
                restriction[key] = int(val)

        # get argument dictionary
        full_args = get_full_args_dict(self, *args, **kwargs)

        tables = list_to_datajoint(self.tables, self.hash)

        # hash tables
        data_hash = hash_tables(tables, restriction)
        codehash = code_hash(self)

        # save reproducibility
        reproducibility = {
            "name": self.name,
            "location": self.location,
            "folder": self.folder,
            "restriction": restriction,
            "arguments": full_args,
            "data_hash": data_hash,
            "code_hash": codehash,
        }

        with open(filepath, "w") as f:
            json.dump(reproducibility, f, indent=4)

    def save_result(self, filepath="./result", format="pkl", restriction={}, *args, **kwargs):
        """
        Runs the function, and saves the pickled result to disk along with the reproducibility json.
        """

        # run function
        result = self(restriction, *args, **kwargs)
        if isinstance(result, dict):
            result = [result]
        result = pd.DataFrame(result)

        # ensure filepath has the correct extension
        filepath = Path(filepath).with_suffix(f".{format}")

        # save reproducibility
        self.save_reproducibility(filepath.with_suffix(".json"), restriction, *args, **kwargs)

        # save result
        save_result(result, filepath, format, self.returns)


    def rerun(self, json_path):
        """
        Loads a reproducibility json and reruns the function with the same arguments.
        """

        with open(json_path, "r") as f:
            reproducibility = json.load(f)

        tables = list_to_datajoint(self.tables, self.hash)

        # hash tables
        data_hash = hash_tables(tables, reproducibility["restriction"])
        codehash = code_hash(self)

        # assert everything is the same
        if not reproducibility["name"] == self.name:
            print("Warning: Function name has changed.")
        if not reproducibility["location"] == self.location:
            print("Warning: Function location has changed.")
        if not reproducibility["folder"] == self.folder:
            print("Warning: Function folder has changed.")
        assert reproducibility["data_hash"] == data_hash, (
            "Data has changed since last function run."
        )
        assert reproducibility["code_hash"] == codehash, (
            "Code has changed since last function run."
        )
        print("Reproducibility checks passed.")
        print("Running function...")

        # run function
        results = self(reproducibility["restriction"], **reproducibility["arguments"])

        if len(results) == 1:
            return results[0]
        else:
            return results

    def reproduce(self, json_path, result_path, format="pkl"):
        """
        Loads a reproducibility json and runs the function with the same arguments,
        checking the data hash and code hash, then saves the result to disk.
        """

        result = self.rerun(json_path)
        if len(result) == 1:
            result = result[0]

        # ensure result_path has the correct extension
        if format == "pkl":
            result_path = Path(result_path).with_suffix(".pkl")
        elif format == "csv":
            result_path = Path(result_path).with_suffix(".csv")

        # save result
        result = pd.DataFrame(result)
        save_result(result, result_path, format, self.returns)

    def check_hash(self, json_path):
        """
        Loads a reproducibility json and runs the function with the same arguments,
        checking the data hash and code hash.
        """

        with open(json_path, "r") as f:
            reproducibility = json.load(f)

        # tables to hash
        tables = list_to_datajoint(self.tables, self.hash)

        # hash tables
        data_hash = hash_tables(tables, reproducibility["restriction"])
        codehash = code_hash(self)

        # check conditions
        if not reproducibility["data_hash"] == data_hash:
            return "Data has changed since last function run."
        elif not reproducibility["code_hash"] == codehash:
            return "Code has changed since last function run."
        else:
            return "Reproducibility checks passed."



def get_full_args_dict(func, *args, **kwargs):
    # Get the signature of the function
    sig = inspect.signature(func.run)

    # Create a dictionary of the default values
    defaults = {
        k: v.default
        for k, v in sig.parameters.items()
        if v.default is not inspect.Parameter.empty and k != "restriction"
    }

    # Get the names of all parameters
    param_names = [k for k in sig.parameters.keys() if k != "key"]

    # Update the defaults dictionary with provided args
    args_dict = dict(zip(param_names, args))

    # Combine the defaults, provided args, and provided kwargs
    full_args = {**defaults, **args_dict, **kwargs}

    return full_args


def save_result(result, filepath, format, returns):
    """
    Function saves the result to disk.
    If there are matplotlib figures in the DataFrame, it will make a directory and
    save the figures as pngs.
    """
    key_cols = [col for col in result.columns 
                if col not in returns.keys() 
                and (len(result) == 1 or result[col].nunique() > 1)]

    # save figs
    for key, val in returns.items():
        if val == Figure:
            dirname = filepath.stem + '_' + key
            directory = Path(filepath).parent / dirname
            directory.mkdir(parents=True, exist_ok=True)
            for i, row in result.iterrows():
                rowdict = row.to_dict()
                name = "_".join([f"{k}_{v}" for k, v in rowdict.items() if k in key_cols])
                fig = row[key]
                figpath = directory / f"{name}.png"
                fig.savefig(figpath)
                result.at[i, key] = str(dirname) + "/" + f"{name}.png"
        
    # save result
    if format == "pkl":
        result.to_pickle(filepath)
    elif format == "csv":
        result.to_csv(filepath)