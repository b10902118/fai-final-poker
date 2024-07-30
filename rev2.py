import importlib
import inspect

for i in range(8):  # Loop from 0 to 7
    module_name = f"baseline{i}"
    try:
        # Import the module dynamically
        module = importlib.import_module(module_name)
        print(f"\nMembers of {module_name}:\n")

        # Get and print all members of the module
        members = inspect.getmembers(module)

        for name, member in members:
            print(f"Name: {name}")
            print(f"Type: {type(member)}")
            if inspect.isfunction(member):
                print("This is a function.")
            elif inspect.isclass(member):
                print("This is a class.")
            print()
    except ModuleNotFoundError:
        print(f"Module {module_name} not found.")
