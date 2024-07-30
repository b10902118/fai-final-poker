import game.visualize_utils as U
from game.players import BasePokerPlayer
from example import equity
from typing import List, Tuple, Dict
from time import sleep

# double equity(const string &myhand, const string &board, const vector<std::string> &exclude)


def parse_game_card(game_card: str):
    assert len(game_card) == 2
    return f"{game_card[1]}{game_card[0].lower()}"


MAX_ROUND = 20
BLIND = 10


def win(round, mystack, isbig):
    r = MAX_ROUND - round
    max_loss = r * 10 - 5 * (r // 2 + 1 if isbig and r % 2 == 1 else r // 2)
    return max_loss + 1000 + 1 - mystack


class ConsolePlayer(BasePokerPlayer):
    uuid: str

    bet: int
    hole_card: str  # don't want to parse every time

    history: List[List[Dict]]  # list of actions
    actions: List[Dict]

    # take on need
    # isbig: bool  # seats order
    # community_card: List[str]
    # round: int
    # pot: int  # main pot, side pot won't be lost
    # street: str  # preflop, flop, turn, river, showdown
    # stack: int
    # op_stack: int

    def init_round(self):
        self.bet = 0
        self.hole_card = ""
        self.actions = []

    def __init__(self, input_receiver=None):
        self.init_round()
        self.history = []
        self.actions = []
        # print(f"{input_receiver}")
        # self.input_receiver = (
        #    input_receiver if input_receiver else self.__gen_raw_input_wrapper()
        # )

    def parse_round_state(self, round_state: Dict):
        street = round_state.get("street")
        pot = round_state["pot"]["main"]["amount"]
        community_card = ""
        for c in round_state.get("community_card"):
            community_card += parse_game_card(c)
        round_count = round_state.get("round_count")

        big_pos = round_state.get("big_blind_pos")
        mystack, opstack = 0, 0
        for seat in round_state.get("seats"):
            if seat.get("uuid") == self.uuid:
                mystack = seat.get("stack")
                isbig = seat.get("position") == big_pos
            else:
                opstack = seat.get("stack")
        self.bet = BLIND if isbig else 5
        print(street, pot, community_card, round_count, isbig, mystack, opstack)
        return street, pot, community_card, round_count, isbig, mystack, opstack

    def declare_action(self, valid_actions, hole_card, round_state):
        print("declare action")
        street, pot, community_card, round_count, isbig, mystack, opstack = (
            self.parse_round_state(round_state)
        )
        myneed = win(round_count, mystack, isbig)

        print(self.hole_card, community_card)
        if myneed <= 0:
            return "fold", 0
        print(valid_actions)
        opneed = win(round_count, opstack, not isbig)
        print(f"{myneed=} {opneed=}")
        eq = equity(self.hole_card, community_card, [])
        print(f"equity = {eq}")

        amount = 0
        action = ""
        if eq < 0.5:  # call or fold
            ca = valid_actions[1]["amount"]
            c = 0 if ca == 0 else ca - self.bet
            ev = eq * pot - (1 - eq) * c
            print(f"{ev=} {pot=} {c=}")
            print(valid_actions)
            if ev > 0:  # may use dyn threshould
                action, amount = "call", min(mystack, ca)
            else:
                action, amount = "fold", 0
        else:
            rmin = valid_actions[2]["amount"]["min"]
            if street == "preflop":
                r = pot + max(rmin, 2 * BLIND)
            else:
                r = max(rmin, int((1 + eq) * pot))
            action, amount = "raise", min(mystack, r)

        assert action != ""
        amount = min(amount, mystack)  # need check
        self.bet = amount
        return action, amount

    def receive_game_start_message(self, game_info):  # fixed known info
        print(f"my uuid = {self.uuid}")
        self.__wait_until_input()

    def receive_round_start_message(self, round_count, hole_card, seats):
        print(f"{round_count=}")
        self.init_round()
        for h in hole_card:
            self.hole_card += parse_game_card(h)

        self.__wait_until_input()

    def receive_street_start_message(self, street, round_state):
        print(f"{street=}")
        self.__wait_until_input()

    def receive_game_update_message(self, new_action, round_state):  # from both player
        print(f"{new_action=}")
        street, pot, community_card, round_count, isbig, mystack, opstack = (
            self.parse_round_state(round_state)
        )
        # update opponent info
        if new_action["player_uuid"] != self.uuid:
            pass
            # append parsed action
            self.actions.append(new_action)

        self.__wait_until_input()

    def receive_round_result_message(self, winners, hand_info, round_state):
        print(f"{hand_info=}")
        self.history.append(self.actions)
        # `hand_info` is a list of dictionaries, each representing a player's hand. Each dictionary contains:
        # - `uuid`: A unique identifier for the player.
        # - `hand`: A dictionary with information about the player's hand. It contains two sub-dictionaries:
        #   - `hand`: Contains `strength` (the type of hand, e.g., 'ONEPAIR'), `high` (the highest card in the hand), and `low` (the lowest card in the hand).
        #   - `hole`: Contains `high` and `low`, representing the highest and lowest cards in the player's hole (private) cards.
        # [{'uuid': 'uethnhbyducbtbxhrzslyy', 'hand': {'hand': {'strength': 'ONEPAIR', 'high': 9, 'low': 0}, 'hole': {'high': 9, 'low': 2}}}, {'uuid': 'gluxjtrqkpuxezsrbdlwir', 'hand': {'hand': {'strength': 'ONEPAIR', 'high': 11, 'low': 0}, 'hole': {'high': 11, 'low': 11}}}]

        # `round_state` is a dictionary that represents the state of the current round. It contains:
        # - `street`: The current stage of the game (e.g., 'showdown').
        # - `pot`: A dictionary with information about the main pot and any side pots.
        # - `community_card`: A list of the community cards on the table.
        # - `dealer_btn`: The position of the dealer button.
        # - `next_player`: The position of the next player to act.
        # - `small_blind_pos` and `big_blind_pos`: The positions of the small and big blinds.
        # - `round_count`: The current round number.
        # - `small_blind_amount`: The amount of the small blind.
        # - `seats`: A list of dictionaries, each representing a player. Each dictionary contains the player's name, uuid, stack (amount of chips), and state (e.g., 'participating').
        # - `action_histories`: A dictionary with a list of actions that have occurred during each stage of the game. Each action is a dictionary that includes the action type (e.g., 'CALL'), the amount, the amount added to the pot, and the uuid of the player who took the action.
        # {'street': 'showdown', 'pot': {'main': {'amount': 20}, 'side': []}, 'community_card': [♣9, ♦8, ♠5, ♣7, ♦A], 'dealer_btn': 0, 'next_player': 1, 'small_blind_pos': 1, 'big_blind_pos': 0, 'round_count': 1, 'small_blind_amount': 5, 'seats': [{'name': 'p1', 'uuid': 'uethnhbyducbtbxhrzslyy', 'stack': 990, 'state': 'participating'}, {'name': 'me', 'uuid': 'gluxjtrqkpuxezsrbdlwir', 'stack': 1010, 'state': 'participating'}], 'action_histories': {'preflop': [{'action': 'SMALLBLIND', 'amount': 5, 'add_amount': 5, 'uuid': 'gluxjtrqkpuxezsrbdlwir'}, {'action': 'BIGBLIND', 'amount': 10, 'add_amount': 5, 'uuid': 'uethnhbyducbtbxhrzslyy'}, {'action': 'CALL', 'amount': 10, 'paid': 5, 'uuid': 'gluxjtrqkpuxezsrbdlwir'}, {'action': 'CALL', 'amount': 10, 'paid': 0, 'uuid': 'uethnhbyducbtbxhrzslyy'}], 'flop': [{'action': 'CALL', 'amount': 0, 'paid': 0, 'uuid': 'gluxjtrqkpuxezsrbdlwir'}, {'action': 'CALL', 'amount': 0, 'paid': 0, 'uuid': 'uethnhbyducbtbxhrzslyy'}], 'turn': [{'action': 'CALL', 'amount': 0, 'paid': 0, 'uuid': 'gluxjtrqkpuxezsrbdlwir'}, {'action': 'CALL', 'amount': 0, 'paid': 0, 'uuid': 'uethnhbyducbtbxhrzslyy'}], 'river': [{'action': 'CALL', 'amount': 0, 'paid': 0, 'uuid': 'gluxjtrqkpuxezsrbdlwir'}, {'action': 'CALL', 'amount': 0, 'paid': 0, 'uuid': 'uethnhbyducbtbxhrzslyy'}]}}
        # winner = [{'name': 'p1', 'uuid': 'aeeuqlixcwkgtwlerziqng', 'stack': 1010, 'state': 'participating'}]
        print(U.visualize_round_result(winners, hand_info, round_state, self.uuid))

        # summarize round information

        self.__wait_until_input()

    def __wait_until_input(self):
        pass
        # input("Enter some key to continue ...")

    def __gen_raw_input_wrapper(self):
        return lambda msg: input(msg)

    def __receive_action_from_console(self, valid_actions):
        flg = self.input_receiver("Enter f(fold), c(call), r(raise).\n >> ")
        if flg in self.__gen_valid_flg(valid_actions):
            if flg == "f":
                return valid_actions[0]["action"], valid_actions[0]["amount"]
            elif flg == "c":
                return valid_actions[1]["action"], valid_actions[1]["amount"]
            elif flg == "r":
                valid_amounts = valid_actions[2]["amount"]
                raise_amount = self.__receive_raise_amount_from_console(
                    valid_amounts["min"], valid_amounts["max"]
                )
                return valid_actions[2]["action"], raise_amount
        else:
            return self.__receive_action_from_console(valid_actions)

    def __gen_valid_flg(self, valid_actions):
        flgs = ["f", "c"]
        is_raise_possible = valid_actions[2]["amount"]["min"] != -1
        if is_raise_possible:
            flgs.append("r")
        return flgs

    def __receive_raise_amount_from_console(self, min_amount, max_amount):
        raw_amount = self.input_receiver(
            "valid raise range = [%d, %d]" % (min_amount, max_amount)
        )
        try:
            amount = int(raw_amount)
            if min_amount <= amount and amount <= max_amount:
                return amount
            else:
                print("Invalid raise amount %d. Try again.")
                return self.__receive_raise_amount_from_console(min_amount, max_amount)
        except:
            print("Invalid input received. Try again.")
            return self.__receive_raise_amount_from_console(min_amount, max_amount)


def setup_ai():
    return ConsolePlayer()
