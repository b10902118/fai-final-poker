import os
import glob
import numpy as np


def deserialize(serialized):
    string1, string2, boolean = serialized.split("|")
    return string1, string2, bool(int(boolean))


"""
def read_and_deserialize_files():
    results = []
    for filename in glob.glob("results/**/*.txt", recursive=True):
        with open(filename, "r") as f:
            for line in f:
                results.append(deserialize(line.strip()))
    return results
"""
import concurrent.futures


def read_and_deserialize_file(filename):
    results = []
    with open(filename, "r") as f:
        for line in f:
            results.append(deserialize(line.strip()))
    return results


def read_and_deserialize_files():
    files = glob.glob("results/**/*.txt", recursive=True)
    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_file = {
            executor.submit(read_and_deserialize_file, filename): filename
            for filename in files
        }
        for future in concurrent.futures.as_completed(future_to_file):
            results.extend(future.result())
    return results


def parse_card(game_card: str):
    suits = ["C", "D", "H", "S"]
    ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]

    # Extract suits and ranks from game_card
    # print(game_card)
    suit1, rank1, suit2, rank2 = (
        game_card[0],
        ranks.index(game_card[1]),
        game_card[2],
        ranks.index(game_card[3]),
    )

    # Check if suits are the same
    if suit1 == suit2:
        suited = True
    else:
        suited = False

    # Check if rank1 is greater than rank2
    if rank1 > rank2:
        rank1, rank2 = rank2, rank1
    return (rank1, rank2) if suited else (rank2, rank1)


# Create a 4D array with dimensions 13x13x13x13
mytotal = np.zeros(
    (
        13,
        13,
    ),
    dtype=np.int32,
)
optotal = np.zeros(
    (
        13,
        13,
    ),
    dtype=np.int32,
)
mywin = np.zeros(
    (
        13,
        13,
    ),
    dtype=np.int32,
)
opwin = np.zeros(
    (
        13,
        13,
    ),
    dtype=np.int32,
)


def print_cpp_2d_array(np_array, name):
    print("double", f"{name}[13][13]", "= {")
    for i in range(np_array.shape[0]):
        print("{", end="")
        for j in range(np_array.shape[1]):
            print(f"{np_array[i, j]:.3f}", end="")
            if j != np_array.shape[1] - 1:
                print(", ", end="")
        print("}", end="")
        if i != np_array.shape[0] - 1:
            print(",\n", end="")
    print("};")


import matplotlib.pyplot as plt


def visualize_array(array, title):
    plt.figure()
    plt.imshow(array, cmap="hot", interpolation="nearest")
    plt.colorbar(label="Value")
    plt.title(title)
    plt.savefig(title + ".png")
    plt.close()  # Close the figure


# Usage
deserialized_results = read_and_deserialize_files()
print("done")
for result in deserialized_results:
    op = parse_card(result[0])
    my = parse_card(result[1])
    optotal[op[0], op[1]] += 1
    mytotal[my[0], my[1]] += 1
    if result[2]:
        mywin[my[0], my[1]] += 1
    else:
        opwin[op[0], op[1]] += 1
# print(mytotal)
# print(mywin)
myeq = mywin / mytotal
opeq = opwin / optotal


# print_cpp_2d_array(myeq, "mypreflop")
# print_cpp_2d_array(opeq, "oppreflop")
visualize_array(myeq, "mypreflop")
visualize_array(opeq, "oppreflop")
