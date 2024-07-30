import matplotlib.pyplot as plt


def visualize_array(array, title):
    plt.figure()
    plt.imshow(array, cmap="hot", interpolation="nearest")
    plt.colorbar(label="Value")
    plt.title(title)
    plt.savefig(title + ".png")
    plt.close()  # Close the figure


import numpy as np


def cpp_to_numpy_2d_array(filename):
    with open(filename, "r") as file:
        content = file.read()

    # Extract the array content between the braces
    start = content.find("{")
    end = content.rfind("}") + 1
    array_content = content[start:end]

    # Remove unwanted characters
    array_content = (
        array_content.replace("{", "").replace("}", "").replace(";", "").strip()
    )

    # Split the content into individual numbers
    number_strings = array_content.split(",")
    numbers = [float(num) for num in number_strings]

    # Determine the dimensions of the array
    dim_x = 13  # Based on the provided array dimensions in the example
    dim_y = 13  # Based on the provided array dimensions in the example

    # Reshape the list of numbers into a 2D NumPy array
    np_array = np.array(numbers).reshape((dim_x, dim_y))

    return np_array


# Example usage:
# Assuming 'array.txt' contains the provided C++ array
filename = "array.txt"
numpy_array = cpp_to_numpy_2d_array(filename)
print(numpy_array)


# Usage
visualize_array(numpy_array, "origpreflop")
