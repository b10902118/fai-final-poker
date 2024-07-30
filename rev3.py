import importlib
import inspect


def inspect_cython_function(func):
    print(f"Name: {func.__name__}")
    print(f"Type: {type(func)}")
    print(f"Docstring: {func.__doc__}")
    print(f"Module: {func.__module__}")
    if hasattr(func, "__annotations__"):
        print(f"Annotations: {func.__annotations__}")
    if hasattr(func, "__defaults__"):
        print(f"Defaults: {func.__defaults__}")
    if hasattr(func, "__kwdefaults__"):
        print(f"Keyword Defaults: {func.__kwdefaults__}")
    if hasattr(func, "__code__"):
        code = func.__code__
        print(f"Code object: {code}")
        print(f"Filename: {code.co_filename}")
        print(f"First line number: {code.co_firstlineno}")
        print(f"Number of lines: {code.co_lnotab}")


# Loop through the modules and inspect setup_ai
for i in range(8):  # Loop from 0 to 7
    module_name = f"baseline{i}"
    try:
        module = importlib.import_module(module_name)
        if hasattr(module, "setup_ai"):
            setup_ai = module.setup_ai
            print(f"\nInspecting setup_ai in {module_name}:\n")
            inspect_cython_function(setup_ai)
    except ModuleNotFoundError:
        print(f"Module {module_name} not found.")
