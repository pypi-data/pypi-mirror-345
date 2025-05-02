from antelop.connection import import_schemas
from antelop.utils.os_utils import get_config
from antelop.utils.analysis_base import AnalysisBase
from antelop.utils.hash_utils import dfs_functions
import importlib
import pkgutil
import inspect
import types
import sys
from pathlib import Path
import json
import ast
import tempfile
import git
from git.exc import GitCommandError
from types import SimpleNamespace


class AntelopNamespace(SimpleNamespace):
    def __repr__(self, indent=0):
        """Pretty print nested AntelopNamespace with indentation"""
        items = []
        spacing = "  " * indent
        
        for k, v in self.__dict__.items():
            if isinstance(v, AntelopNamespace):
                nested = v.__repr__(indent + 1)
                items.append(f"{spacing}{k}:\n{nested}")
            elif isinstance(v, (list, tuple)):
                if any(isinstance(x, (AntelopNamespace, object)) for x in v):
                    items.append(f"{spacing}{k}:")
                    for item in v:
                        if isinstance(item, AntelopNamespace):
                            items.append(item.__repr__(indent + 1))
                        elif isinstance(item, object) and not isinstance(item, (str, int, float, bool)):
                            items.append(f"{spacing}  - {k}")
                        else:
                            items.append(f"{spacing}  {repr(item)}")
                else:
                    items.append(f"{spacing}{k}: {repr(v)}")
            elif isinstance(v, object) and not isinstance(v, (str, int, float, bool)):
                items.append(f"{spacing}- {k}")
            else:
                items.append(f"{spacing}{k}: {repr(v)}")
                
        return "\n".join(items)


def find_script_in_subfolders(folder):
    """
    Function searches a folder and its subfolders for python scripts
    to arbitrary depth and returns a nested dictionary of the folder
    """
    scripts = {}
    for path in Path(folder).rglob("*.py"):
        relative_path = path.relative_to(folder)
        parts = relative_path.parts
        current_level = scripts
        for part in parts[:-1]:
            if part not in current_level:
                current_level[part] = {".": []}
            current_level = current_level[part]
        if "." not in current_level:
            current_level["."] = []
        current_level["."].append(str(path))
    return scripts


def import_script(path):
    spec = importlib.util.spec_from_file_location("module_name", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["module_name"] = module
    spec.loader.exec_module(module)
    return module


def import_analysis(conn, tables):
    # built in analysis functions
    analysis = importlib.import_module("antelop.analysis")
    functions = []
    errors = []
    for _, name, _ in pkgutil.iter_modules(analysis.__path__):
        module = importlib.import_module(f"antelop.analysis.{name}")
        for _, cls in module.__dict__.items():
            if (
                inspect.isclass(cls)
                and issubclass(cls, AnalysisBase)
                and cls != AnalysisBase
            ):
                setattr(cls, "location", "stdlib")
                setattr(cls, "folder", name)
                functions.append(cls(conn))

    # user defined analysis functions
    config = get_config()
    if config.get("deployment", {}).get("deployment") == "apptainer" and "analysis" in config:
        user_analysis = config["analysis"]["folders"]
        for folder in user_analysis:
            scripts = find_script_in_subfolders(folder)

            def import_scripts(scripts, base_path=[]):
                for key, val in scripts.items():
                    if key == ".":
                        for script in val:
                            try:
                                module = import_script(Path(folder) / script)
                                for _, cls in module.__dict__.items():
                                    if (
                                        inspect.isclass(cls)
                                        and issubclass(cls, AnalysisBase)
                                        and cls != AnalysisBase
                                    ):
                                        setattr(cls, "location", "local")
                                        setattr(
                                            cls, "folder", base_path + [Path(script).stem]
                                        )
                                        functions.append(cls(conn))
                            except ImportError:
                                errors.append(("local", base_path, Path(script).stem))
                    else:
                        import_scripts(val, base_path + [key])

            import_scripts(scripts)

    # github analysis functions
    github_repos = get_config()["github"]
    for name, repo in github_repos.items():
        status = check_repo_access(repo)
        if status == 'success':
            try:
                tmp_path = Path(tempfile.gettempdir()) / "antelop_github"
                if not tmp_path.exists():
                    tmp_path.mkdir()
                repo_path = tmp_path / name
                if repo_path.exists():
                    repo = git.Repo(repo_path)
                    # Access the 'origin' remote explicitly
                    origin = repo.remotes["origin"] if "origin" in repo.remotes else None
                    if origin:
                        origin.pull()
                    else:
                        print(f"No 'origin' remote found for repository {name}")
                else:
                    repo = git.Repo.clone_from(repo, repo_path)
            except Exception as e:
                print(e)
                errors.append(("github", name, "Unknown error"))
                continue
        elif status == "private":
            errors.append(("github", name, "Repository private"))
            continue
        elif status == 'respository not found':
            errors.append(("github", name, "Repository not found"))
            continue
        else:
            errors.append(("github", name, "Unknown error"))
            continue

        scripts = find_script_in_subfolders(repo_path)

        def import_github_scripts(scripts, base_path=[]):
            for key, val in scripts.items():
                if key == ".":
                    for script in val:
                        try:
                            module = import_script(repo_path / script)
                            for _, cls in module.__dict__.items():
                                if (
                                    inspect.isclass(cls)
                                    and issubclass(cls, AnalysisBase)
                                    and cls != AnalysisBase
                                ):
                                    setattr(cls, "location", name)
                                    setattr(
                                        cls, "folder", base_path + [Path(script).stem]
                                    )
                                    functions.append(cls(conn))
                        except ImportError as e:
                            errors.append(("github", base_path, Path(script).stem))
                else:
                    import_github_scripts(val, base_path + [key])

        import_github_scripts(scripts)

    # add functions to functions
    new_functions = []
    for function in functions:
        new_functions.append(patch_functions(function, functions, tables))

    return new_functions, errors


def instantiate_from_db(key, tables):
    # pull function definition from database
    function, name = (tables["AnalysisFunction"] & key).fetch1(
        "function", "analysisfunction_name"
    )

    # deserialise and instantiate
    function = json.loads(function)
    parsed = ast.parse(function)
    for node in ast.walk(parsed):
        if isinstance(node, ast.ClassDef):
            class_name = node.name
    exec(function)
    function = locals()[class_name](tables["Experimenter"].connection)
    function.local = False
    return function


def patch_functions(self, functions, tables):
    """
    This function patches the functions to allow other functions and tables to be accessible in the run() method.
    Has to be separate from the decorator as functions haven't yet been initialised with connections when the decorator is called.
    """

    new_globals = self.run.__globals__.copy()

    # add tables that are defined in function
    new_tables = []
    if isinstance(self.query, str):
        new_tables.append(self.query)
    elif isinstance(self.query, list):
        new_tables = self.query
    if hasattr(self, "data"):
        if isinstance(self.data, str):
            new_tables.append(self.data)
        elif isinstance(self.data, list):
            new_tables += self.data
    for key in new_tables:
        new_globals[key] = tables[key]

    # add functions defined in calls
    if hasattr(self, "calls"):
        new_globals = {
            **new_globals,
            **subset_functions_to_namespace(functions, self.calls, self),
        }

    new_run = types.FunctionType(
        self.run.__code__,
        new_globals,
        self.run.__name__,
        self.run.__defaults__,
        self.run.__closure__,
    )
    self.run = new_run

    # compute all tables to hash for later
    hash = dfs_functions(self, functions)
    self.hash = hash

    return self


def split_trials(data, mask):
    """
    Split trials based on mask

    Inputs:
    mask: tuple of data, timestamps
    data: tuple of data, timestamps

    Returns:
    list of tuples of data, timestamps
    """

    mask_data, mask_time = mask
    data_data, data_time = data

    start_times = mask_time[mask_data == 1]
    stop_times = mask_time[mask_data == -1]

    mask = (data_time[:, None] >= start_times) & (data_time[:, None] <= stop_times)
    trials = [
        (data_data[mask[:, i]], data_time[mask[:, i]]) for i in range(mask.shape[1])
    ]

    return trials


def instantiate_function(key, tables):
    """
    Function loads an analysis function from the masks table and returns an instantiation of it
    """
    # pull function definition from database
    function, name = (tables["MaskFunction"] & key).fetch1(
        "mask_function", "maskfunction_name"
    )

    # deserialise and instantiate
    function = json.loads(function)
    exec(function)
    function = locals()[name](tables["Experimenter"].connection)

    # patch functions to function
    functions = import_analysis(tables["Experimenter"].connection, tables)
    for folder_name, outer_folder in functions.items():
        function = patch_functions(function, functions, tables)

    return function


def get_docstring(function_string, name):
    """
    Gets docstring from function string
    """

    exec(json.loads(function_string))
    function = locals()[name]
    docstring = function.__doc__
    return docstring


def check_repo_access(repo_url):
    """Test if repo exists and is accessible"""
    # TODO: this still asks for credentials if the repo isn't found
    try:
        # Try to do a ls-remote which doesn't require cloning
        git.cmd.Git().ls_remote(repo_url)
        return 'success'
    except GitCommandError as e:
        if "Authentication failed" in str(e):
            # Repo exists but is private
            return "private"
        elif "repository not found" in str(e):
            # Repo doesn't exist
            return 'respository not found'
        else:
            # Other git errors
            return False


def reload_analysis(conn, tables):
    """
    Reloads analysis functions and repatches them if the underlying script has changed
    """
    functions = []
    errors = []

    # built-in analysis functions
    analysis = importlib.import_module("antelop.analysis")
    for _, name, _ in pkgutil.iter_modules(analysis.__path__):
        module_name = f"antelop.analysis.{name}"
        if module_name in sys.modules:
            module = importlib.reload(sys.modules[module_name])
        else:
            module = importlib.import_module(module_name)
        for _, cls in module.__dict__.items():
            if (
                inspect.isclass(cls)
                and issubclass(cls, AnalysisBase)
                and cls != AnalysisBase
            ):
                setattr(cls, "location", "stdlib")
                setattr(cls, "folder", name)
                functions.append(cls(conn))

    # user-defined analysis functions
    config = get_config()
    deployment = config.get("deployment", {}).get("deployment")
    if deployment == "local" or (deployment == "apptainer" and "analysis" in config):
        user_analysis = config["analysis"]["folders"]
        for folder in user_analysis:
            scripts = find_script_in_subfolders(folder)

            def import_scripts(scripts, base_path=[]):
                for key, val in scripts.items():
                    if key == ".":
                        for script in val:
                            try:
                                module_name = Path(script).stem
                                if module_name in sys.modules:
                                    module = importlib.reload(sys.modules[module_name])
                                else:
                                    module = import_script(Path(folder) / script)
                                for _, cls in module.__dict__.items():
                                    if (
                                        inspect.isclass(cls)
                                        and issubclass(cls, AnalysisBase)
                                        and cls != AnalysisBase
                                    ):
                                        setattr(cls, "location", "local")
                                        setattr(
                                            cls, "folder", base_path + [Path(script).stem]
                                        )
                                        functions.append(cls(conn))
                            except ImportError:
                                errors.append(("local", base_path, Path(script).stem))
                    else:
                        import_scripts(val, base_path + [key])

            import_scripts(scripts)

    # github analysis functions
    github_repos = get_config()["github"]
    for name, repo in github_repos.items():
        status = check_repo_access(repo)
        if status == 'success':
            try:
                tmp_path = Path(tempfile.gettempdir()) / "antelop_github"
                if not tmp_path.exists():
                    tmp_path.mkdir()
                repo_path = tmp_path / name
                if repo_path.exists():
                    repo = git.Repo(repo_path)
                    # Access the 'origin' remote explicitly
                    origin = repo.remotes["origin"] if "origin" in repo.remotes else None
                    if origin:
                        origin.pull()
                    else:
                        print(f"No 'origin' remote found for repository {name}")
                else:
                    repo = git.Repo.clone_from(repo, repo_path)
            except Exception:
                errors.append(("github", name, "Unknown error"))
                continue
        elif status == "private":
            errors.append(("github", name, "Repository private"))
            continue
        elif status == 'respository not found':
            errors.append(("github", name, "Repository not found"))
            continue
        else:
            errors.append(("github", name, "Unknown error"))
            continue

        scripts = find_script_in_subfolders(repo_path)

        def import_github_scripts(scripts, base_path=[]):
            for key, val in scripts.items():
                if key == ".":
                    for script in val:
                        try:
                            module_name = Path(script).stem
                            if module_name in sys.modules:
                                module = importlib.reload(sys.modules[module_name])
                            else:
                                module = import_script(repo_path / script)
                            for _, cls in module.__dict__.items():
                                if (
                                    inspect.isclass(cls)
                                    and issubclass(cls, AnalysisBase)
                                    and cls != AnalysisBase
                                ):
                                    setattr(cls, "location", name)
                                    setattr(
                                        cls, "folder", base_path + [Path(script).stem]
                                    )
                                    functions.append(cls(conn))
                        except ImportError as e:
                            errors.append(("github", base_path, Path(script).stem))
                else:
                    import_github_scripts(val, base_path + [key])

        import_github_scripts(scripts)

    # add functions to new_functions with patched run method
    new_functions = []
    for function in functions:
        new_functions.append(patch_functions(function, functions, tables))

    return new_functions, errors


def functions_to_simplenamespace(functions):
    """
    Converts list of functions to nested AntelopNamespace objects
    """
    local = AntelopNamespace()
    stdlib = AntelopNamespace()
    github = {}

    for fct in functions:
        if fct.hidden:
            continue
        if fct.location == "local":
            if isinstance(fct.folder, str):
                if not hasattr(local, fct.folder):
                    setattr(local, fct.folder, AntelopNamespace())
                setattr(getattr(local, fct.folder), fct.name, fct)
            else:
                local_child = local
                for directory in fct.folder:
                    if not hasattr(local_child, directory):
                        setattr(local_child, directory, AntelopNamespace())
                    local_child = getattr(local_child, directory)
                setattr(local_child, fct.name, fct)

        elif fct.location == "stdlib":
            if isinstance(fct.folder, str):
                if not hasattr(stdlib, fct.folder):
                    setattr(stdlib, fct.folder, AntelopNamespace())
                setattr(getattr(stdlib, fct.folder), fct.name, fct)
            else:
                stdlib_child = stdlib
                for directory in fct.folder:
                    if not hasattr(stdlib_child, directory):
                        setattr(stdlib_child, directory, AntelopNamespace())
                    stdlib_child = getattr(stdlib_child, directory)
                setattr(stdlib_child, fct.name, fct)

        else:
            if fct.location not in github.keys():
                github[fct.location] = AntelopNamespace()
            github_child = github[fct.location]
            for directory in fct.folder:
                if not hasattr(github_child, directory):
                    setattr(github_child, directory, AntelopNamespace())
                github_child = getattr(github_child, directory)
            setattr(github_child, fct.name, fct)

    return local, stdlib, github


def subset_functions_to_namespace(functions, function_names, parent_function):
    """
    Converts list of functions to a single dictionary of nested AntelopNamespace objects.
    Only instantiates functions specified in function_names.
    """
    new_globals = {}

    def should_instantiate(fct):
        for name in function_names:
            if "." in name:
                location, folder, function = name.split(".")
                if (
                    fct.location == location
                    and fct.folder == folder
                    and fct.name == function
                ):
                    return True
            else:
                if (
                    parent_function.location == fct.location
                    and parent_function.folder == fct.folder
                    and fct.name == name
                ):
                    return True
        return False

    for fct in functions:
        if not should_instantiate(fct):
            continue

        if "." not in fct.name:
            new_globals[fct.name] = fct
            continue

        if fct.location == "local":
            if isinstance(fct.folder, str):
                if fct.folder not in new_globals:
                    new_globals[fct.folder] = AntelopNamespace()
                setattr(new_globals[fct.folder], fct.name, fct)
            else:
                local_child = new_globals
                for directory in fct.folder:
                    if directory not in local_child:
                        local_child[directory] = AntelopNamespace()
                    local_child = local_child[directory]
                setattr(local_child, fct.name, fct)

        elif fct.location == "stdlib":
            if isinstance(fct.folder, str):
                if fct.folder not in new_globals:
                    new_globals[fct.folder] = AntelopNamespace()
                setattr(new_globals[fct.folder], fct.name, fct)
            else:
                stdlib_child = new_globals
                for directory in fct.folder:
                    if directory not in stdlib_child:
                        stdlib_child[directory] = AntelopNamespace()
                    stdlib_child = stdlib_child[directory]
                setattr(stdlib_child, fct.name, fct)

        else:
            if fct.location not in new_globals:
                new_globals[fct.location] = AntelopNamespace()
            github_child = new_globals[fct.location]
            for directory in fct.folder:
                if directory not in github_child:
                    github_child[directory] = AntelopNamespace()
                github_child = github_child[directory]
            setattr(github_child, fct.name, fct)

    return new_globals


def functions_to_dict(functions):
    """
    Converts list of functions to a dictionary of nested dictionaries
    """
    functions_dict = {"local": {}, "stdlib": {}}

    for fct in functions:
        if fct.location == "local":
            if isinstance(fct.folder, str):
                if fct.folder not in functions_dict["local"]:
                    functions_dict["local"][fct.folder] = {}
                functions_dict["local"][fct.folder][fct.name] = fct
            else:
                local_child = functions_dict["local"]
                for directory in fct.folder:
                    if directory not in local_child:
                        local_child[directory] = {}
                    local_child = local_child[directory]
                local_child[fct.name] = fct

        elif fct.location == "stdlib":
            if isinstance(fct.folder, str):
                if fct.folder not in functions_dict["stdlib"]:
                    functions_dict["stdlib"][fct.folder] = {}
                functions_dict["stdlib"][fct.folder][fct.name] = fct
            else:
                stdlib_child = functions_dict["stdlib"]
                for directory in fct.folder:
                    if directory not in stdlib_child:
                        stdlib_child[directory] = {}
                    stdlib_child = stdlib_child[directory]
                stdlib_child[fct.name] = fct

        else:
            if fct.location not in functions_dict:
                functions_dict[fct.location] = {}
            github_child = functions_dict[fct.location]
            for directory in fct.folder:
                if directory not in github_child:
                    github_child[directory] = {}
                github_child = github_child[directory]
            github_child[fct.name] = fct

    return functions_dict


def find_function(functions, name, location, folder):
    """
    Function finds a function in a list of functions
    """
    for fct in functions:
        if fct.name == name and fct.location == location and fct.folder == folder:
            return fct
    return None