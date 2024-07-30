from agents.console_player import setup_ai as console_ai

import baseline0 as b0
from baseline0 import setup_ai as baseline0_ai

print(dir(b0))
exit()

config = setup_config(max_round=20, initial_stack=1000, small_blind_amount=5)
config.register_player(name="p1", algorithm=baseline0_ai())
# config.register_player(name="p2", algorithm=random_ai())

## Play in interactive mode if uncomment
config.register_player(name="me", algorithm=console_ai())
game_result = start_poker(config, verbose=1)
