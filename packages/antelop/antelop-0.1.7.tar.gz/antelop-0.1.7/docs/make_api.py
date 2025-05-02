"""
Run custom script to generate api docs
Sphinx tools were too restrictive for our needs here
"""
import os
import importlib
import inspect
import pkgutil


def generate_rst_for_module(module_name, output_filename='docs/source/api/analysis.rst'):
    """
    Generates an .rst file with Sphinx documentation for all classes that are part of the 'antelop.utils.analysis_base' module
    in the specified module and its submodules, documenting only the class docstring and the attributes 'Query', 'Returns', and 'Calls'.
    
    :param module_name: The name of the module (e.g., 'antelop.analysis').
    :param output_filename: The filename to write the generated documentation to.
    """
    print(f"Starting documentation for module: {module_name}")

    # Initialize the output file
    with open(output_filename, 'w') as rst_file:
        # Add the module header with the new title "Analysis"
        rst_file.write(f"Analysis\n")
        rst_file.write("=" * len("Analysis") + "\n\n")

        # Import the module
        try:
            print(f"Importing module: {module_name}")
            module = importlib.import_module(module_name)
        except ImportError:
            print(f"Error: Unable to import module '{module_name}'. Please check if the module is in sys.path.")
            return
        
        # Write the module docstring, if available
        module_doc = inspect.getdoc(module)
        if module_doc:
            rst_file.write(f"{module_doc}\n\n")  # Write the docstring of the module
        
        # Discover all submodules in the module
        print(f"Discovering submodules for {module_name}...")
        submodules = []
        for _, submodule_name, _ in pkgutil.iter_modules(module.__path__):
            submodule_full_name = f"{module_name}.{submodule_name}"
            submodules.append(submodule_full_name)
            print(f"Found submodule: {submodule_full_name}")
        
        # Include the main module itself in the list of modules to inspect
        submodules.append(module_name)
        
        # Group classes by their submodule
        submodule_classes = {}
        print(f"Inspecting submodules for classes part of 'antelop.utils.analysis_base'...")

        # Now find classes that belong to 'antelop.utils.analysis_base' in each submodule
        for submodule in submodules:
            print(f"Inspecting submodule: {submodule}")
            try:
                submodule_obj = importlib.import_module(submodule)
            except ImportError:
                print(f"Error: Unable to import submodule '{submodule}'. Skipping.")
                continue

            # Inspect for classes that belong to 'antelop.utils.analysis_base'
            for name, obj in inspect.getmembers(submodule_obj):
                if inspect.isclass(obj):
                    # Check if the class is part of 'antelop.utils.analysis_base'
                    if obj.__module__ == 'antelop.utils.analysis_base':
                        print(f"Found class: {name} in {submodule} that belongs to 'antelop.utils.analysis_base'")
                        if submodule not in submodule_classes:
                            submodule_classes[submodule] = []
                        submodule_classes[submodule].append(obj)

        if not submodule_classes:
            print(f"No classes found that belong to 'antelop.utils.analysis_base' in any submodule of {module_name}.")
            return
        
        # For each submodule, write its own section in the .rst file
        for submodule, classes in submodule_classes.items():
            submodule_name = submodule.split('.')[-1]  # Get the submodule name (last part of the full module path)
            print(f"Writing documentation for submodule: {submodule_name}")
            rst_file.write(f"\n{submodule_name.capitalize()}\n")
            rst_file.write("-" * len(submodule_name) + "\n\n")
            
            # Write the docstring of the submodule, if available
            submodule_doc = inspect.getdoc(importlib.import_module(submodule))
            if submodule_doc:
                rst_file.write(f"{submodule_doc}\n\n")

            # Iterate over the classes
            for cls in classes:
                # Use the class's 'name' attribute (without the full module path)
                class_name = getattr(cls, 'name', cls.__name__)  # Use 'name' attribute as the class name
                class_doc = inspect.getdoc(cls)

                # Write the class documentation using .. class:: directive
                rst_file.write(f".. class:: {class_name}\n")
                rst_file.write("   :noindex:\n\n")

                # Indent the class docstring and replace every \n with \n\n (double line breaks)
                if class_doc:
                    class_doc = class_doc.replace("\n", "\n\n")  # Double the line breaks
                    # Modify the docstring for "Arguments" to be bold if it exists
                    class_doc = class_doc.replace("Arguments", "**Arguments**")
                    for line in class_doc.splitlines():
                        rst_file.write(f"   {line}\n")
                    rst_file.write("\n")

                # Add an additional line break between the docstring and attributes
                rst_file.write("\n")

                # Only document the 'Query', 'Returns', and 'Calls' attributes
                class_attributes = {attr: getattr(cls, attr, None) for attr in ['query', 'returns', 'calls']}

                # Check if 'Arguments' is in the docstring
                if "Arguments" not in class_doc:
                    # Add 'Arguments' as the first attribute if it's not already in the docstring
                    arguments = getattr(cls, 'arguments', None)
                    if arguments is not None:
                        rst_file.write(f"   **Arguments**: {arguments}\n\n")

                # Indent the attributes and write them directly under the class docstring
                for attr, value in class_attributes.items():
                    if value is not None:
                        rst_file.write(f"   **{attr.capitalize()}**: {value}\n\n")  # Bold attribute names

                # Add a dropdown for the 'run' method's code if it exists
                run_method = getattr(cls, 'run', None)
                if run_method and callable(run_method):
                    rst_file.write(f"   .. dropdown:: See Code\n\n")
                    rst_file.write(f"      .. code-block:: python\n\n")
                    run_code = inspect.getsource(run_method)
                    for line in run_code.splitlines():
                        rst_file.write(f"         {line}\n")
                    rst_file.write("\n")

                # Add a line break between classes for better readability
                rst_file.write("\n")

        print(f"Documentation has been written to '{output_filename}'.")

if __name__ == '__main__':

    # Set the hardcoded module and output file path
    module_name = 'antelop.analysis'  # The module to document
    generate_rst_for_module(module_name)
    with open("docs/source/api/analysis.rst", "r") as f:
        lines = f.readlines()    

    lines[0] = "Analysis standard library\n"
    lines[1] = "=========================\n"

    with open("docs/source/python/stlib.rst", "w") as f:
        f.writelines(lines)

    
