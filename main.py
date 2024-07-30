import example
import subprocess

from itertools import product


def gen_comb(c1, c2):
    suits = ["c", "d", "h", "s"]
    combs = set()
    for s1 in suits:
        for s2 in suits:
            combs.add(f"{c1}{s1}{c2}{s2}")
    assert len(combs) == 16
    return list(combs)


# Define the arguments
myhand = "9hTs"
# board = ""
board = "4s5h2d9djh"
# exclude = ["3d6s"]
exclude = ["up10"]
# exclude = gen_comb(6,3) + gen_comb('A','A') + gen_comb('K','K') + gen_comb('Q','Q') + gen_comb('J','J') + gen_comb('T','T') + gen_comb('9','9') + gen_comb('8','8') + gen_comb('7','7') + gen_comb('6','6') + gen_comb('5','5') + gen_comb('4','4') + gen_comb('3','3') + gen_comb('2','2')

# Execute the C++ program
# print("Original")
# subprocess.run(["../../../build/bin/ps-eval", myhand, "--board", board])

# Call the C++ function
print("My")
result = example.equity(myhand, board, exclude)

print(f"Equity: {result}")
