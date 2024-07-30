import sys
from game.game import setup_config, start_poker
from agents.cur_player import setup_ai as console_ai
import os
import multiprocessing
from sys import argv
from baseline7 import setup_ai


def setup_game():
    config = setup_config(max_round=20, initial_stack=1000, small_blind_amount=5)
    config.register_player(name="p1", algorithm=setup_ai())
    config.register_player(name="me", algorithm=console_ai())
    return config


def test(config):
    while True:
        start_poker(config, verbose=1)


def main():
    config = setup_game()
    num_processes = multiprocessing.cpu_count()
    print(num_processes)
    with multiprocessing.Pool(num_processes) as pool:
        pool.map(test, [config] * num_processes)


if __name__ == "__main__":
    main()
