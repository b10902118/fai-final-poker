import sys
from termcolor import colored

from game.game import setup_config, start_poker

# from agents.call_player import setup_ai as call_ai
# from agents.random_player import setup_ai as random_ai
from agents.cur_player import setup_ai as console_ai

from multiprocessing import Process, Manager
import importlib
import os

from sys import argv

n = int(argv[1]) if len(argv) == 2 else 10


def test(baseline_module, results_dict):
    sys.stdout = open(os.devnull, "w")
    # sys.stderr = open(os.devnull, "w")
    baseline = importlib.import_module(baseline_module)
    setup_ai = getattr(baseline, "setup_ai")
    results = []
    config = setup_config(max_round=20, initial_stack=1000, small_blind_amount=5)
    config.register_player(name="p1", algorithm=setup_ai())
    config.register_player(name="me", algorithm=console_ai())
    for _ in range(n):
        game_result = start_poker(config, verbose=1)
        p1_stack = None
        me_stack = None
        for player in game_result["players"]:
            if player["name"] == "p1":
                p1_stack = player["stack"]
            elif player["name"] == "me":
                me_stack = player["stack"]

        # Check and print if p1's stack is greater than me's stack
        if p1_stack is not None and me_stack is not None:
            if p1_stack > me_stack:
                result = "LOSE"
                color = "red"
            else:
                result = "WIN"
                color = "green"

            output = f"{result} {me_stack} {p1_stack}"
            results.append(output)
        else:
            print("Failed to find both player stacks", file=sys.stderr)
            sys.exit(1)
        # Check if key exists in dictionary
        if baseline_module not in results_dict:
            # If key does not exist, create it
            results_dict[baseline_module] = results
        else:
            # If key exists, add to it
            results_dict[baseline_module] += results


if __name__ == "__main__":
    baseline_modules = [
        "baseline4",
        "baseline5",
        "baseline6",
        "baseline7",
    ] * 10
    with Manager() as manager:
        results_dict = manager.dict()
        processes = []

        for baseline_module in baseline_modules:
            p = Process(target=test, args=(baseline_module, results_dict))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

        win_rate_dict = {}
        for baseline_module in sorted(results_dict.keys()):
            print(baseline_module)
            total = len(results_dict[baseline_module])
            win = 0
            for result in results_dict[baseline_module]:
                result_parts = result.split()
                if result_parts[0] == "WIN":
                    color = "green"
                    win += 1
                else:
                    color = "red"
                print(colored(result, color))
                win_rate = win / total  # Calculate win rate
                win_rate_dict[baseline_module] = (
                    win_rate  # Store win rate in dictionary
                )

        # Print all win rates together
        for baseline_module, win_rate in sorted(win_rate_dict.items()):
            print(f"{baseline_module}: Win rate: {win_rate}")
