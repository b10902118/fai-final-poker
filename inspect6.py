import inspect
import baseline6

# Define a function to inspect classes
def inspect_class(cls):
    print(f"Inspecting class: {cls.__name__}")
    print(f"Type: {type(cls)}")
    print(f"Module: {cls.__module__}")
    print(f"Docstring:\n{cls.__doc__}")
    print(f"Class methods and attributes:\n{inspect.getmembers(cls)}")

# Inspect the HE class
inspect_class(baseline6.HE)

# Inspect the ME class
inspect_class(baseline6.ME)

