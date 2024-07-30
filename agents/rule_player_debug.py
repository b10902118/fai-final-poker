import game.visualize_utils as U
from game.players import BasePokerPlayer
from example import equity
from typing import List, Tuple, Dict
from time import sleep
import random
from sys import stderr

# double equity(const string &myhand, const string &board, const vector<std::string> &exclude)


def parse_game_card(game_card: str):
    assert len(game_card) == 2, f"invalid card {game_card}"
    return f"{game_card[1]}{game_card[0].lower()}"


MAX_ROUND = 20
BLIND = 10


def win(round, mystack, opstack, isbig, pot):
    r = MAX_ROUND - round
    # print(f"{r=}")
    max_loss = r * 10 - 5 * (r // 2 + 1 if isbig and r % 2 == 1 else r // 2)
    # print(f"{max_loss=}")
    return max_loss + opstack + pot - (mystack - max_loss)


class History:
    cnt: int
    eq: float

    def __init__(self):
        self.cnt = 1
        self.eq = 0.5

    def update(self, eq):
        self.eq = (self.eq * self.cnt + eq) / (self.cnt + 1)
        self.cnt += 1

    def freq(self, total):
        return self.cnt / total


class ConsolePlayer(BasePokerPlayer):
    uuid: str

    bet: int
    hole_card: str  # don't want to parse every time

    # history: List[List[Dict]]  # list of actions
    actions: List[Dict]

    my_target: int
    op_target: int

    op_exclude: List[str]
    big_param: Dict[str, List]  # [preflop:,flop:, turn:, river:]
    small_param: Dict[str, List]
    op_opening: bool

    op_check: History
    op_call_raise: History
    op_fold_n: int

    total_act: int
    op_rc_cnt: int

    # take on need
    # isbig: bool  # seats order
    # community_card: List[str]
    # round: int
    # pot: int  # main pot, side pot won't be lost
    # street: str  # preflop, flop, turn, river, showdown
    # stack: int
    # op_stack: int

    def init_round(self):
        self.cur_bet = 0
        self.pre_bet = 0
        self.hole_card = ""
        self.actions = []
        self.op_opening = True
        self.opening = True
        self.op_exclude = []
        self.op_rc_cnt = 0

    def __init__(self, input_receiver=None):
        self.init_round()
        self.history = []
        self.op_check = History()
        self.op_call_raise = History()
        self.op_fold_n = 0
        self.total_act = 0

    def parse_round_state(self, round_state: Dict, print_=True):
        street = round_state.get("street")
        pot = round_state["pot"]["main"]["amount"]
        community_card = ""
        for c in round_state.get("community_card"):
            community_card += parse_game_card(c)
        round_count = round_state.get("round_count")

        big_pos = round_state.get("big_blind_pos")
        # print(f"{big_pos}")
        seats = round_state.get("seats")
        # print(f"{round_state.get('seats')}")
        mystack, opstack = 0, 0
        for pos, seat in enumerate(seats):
            if seat.get("uuid") == self.uuid:
                mystack = seat.get("stack")
                isbig = pos == big_pos
            else:
                opstack = seat.get("stack")
        if print_:
            print(street, pot, community_card, round_count, isbig, mystack, opstack)
        return street, pot, community_card, round_count, isbig, mystack, opstack

    def declare_action(self, valid_actions, hole_card, round_state):

        print("declare action")
        street, pot, community_card, round_count, isbig, mystack, opstack = (
            self.parse_round_state(round_state)
        )

        if win(round_count, mystack, opstack, isbig, pot) < 0:
            return "fold", 0

        eq = equity(self.hole_card, community_card, self.op_exclude)
        if not isbig and self.opening:
            last_act = None
        else:
            last_act = self.actions[-1]
        ischeck = last_act and last_act["action"] == "call"
        # print(f"{last_act=}")

        action, amount = "", 0
        rmin = valid_actions[2]["amount"]["min"]
        rmax = valid_actions[2]["amount"]["max"]
        ca = valid_actions[1]["amount"]
        c = 0 if ca == 0 else ca - self.cur_bet

        op_need = self.op_target - self.pre_bet
        my_need = self.my_target - self.pre_bet

        def can_fold():
            if round_count == 20:
                return win(round_count, opstack, mystack, not isbig, -pot) > 0
            return win(round_count, opstack, mystack, not isbig, -pot) >= 0

        def allin():
            action = "raise"
            if rmin == -1:
                action, amount = "call", ca
            elif my_need > rmin:
                amount = my_need
            elif rmin <= op_need:
                amount = rmin
            else:
                amount = rmax
            return action, amount

        def last_resort():
            if can_fold():
                return "fold", 0
            return allin()

        def bluff_raise():
            if ischeck:
                amount = self.cur_bet + 3 * BLIND
            else:
                amount = self.cur_bet + 2.25 * BLIND
            if amount < rmin:
                return "call", ca
            return "raise", amount

        def bait_raise():
            action = "raise"
            if street == "preflop":
                amount = (1 / 2 + 1 / 2) * pot - self.pre_bet
            elif street == "flop":
                amount = random.choices(
                    [(1 / 2 + 1 / 3) * pot - self.pre_bet, my_need], [0.7, 0.3], k=1
                )[0]
            elif street == "turn":
                amount = random.choices(
                    [(1 / 2 + 1 / 4) * pot - self.pre_bet, my_need], [0.5, 0.5], k=1
                )[0]
            else:  # street == "river":
                amount = my_need
            return action, amount

        def agg_raise():
            agg_amount = (0.5 + eq) * pot - self.pre_bet
            if street == "preflop":
                amount = agg_amount
            elif street == "flop":
                amount = random.choices([agg_amount, my_need], [0.7, 0.3], k=1)[0]
            elif street == "turn":
                amount = random.choices([agg_amount, my_need], [0.5, 0.5], k=1)[0]
            elif street == "river":
                amount = my_need
            return "raise", amount

        def rand_act(acts, probs):
            ch = random.choices(acts, weights=probs, k=1)[0]
            if isinstance(ch, str):
                if ch == "fold":
                    return "fold", 0
                elif ch == "call":
                    return "call", ca
                elif ch == "allin":
                    return allin()
                elif ch == "bluff":
                    return bluff_raise()
                else:
                    raise ValueError(f"unknown action {ch}")
            elif isinstance(ch, tuple):
                if ch[0] == "raise":
                    return "raise", ch[1]
                else:
                    raise ValueError(f"unknown action {ch}")
            else:
                raise print(f"unknown action {ch}")

        total_bet = self.pre_bet + self.cur_bet
        threat_rate = min(
            ca + self.pre_bet / (self.op_target if self.op_target > 0 else 1), 1
        )
        total_target = self.my_target + self.op_target
        if total_target == 0:
            margin = 1
            # print(
            #    f"{round_count} {mystack} {opstack} {self.my_target} {self.op_target}",
            #    file=stderr,
            # )
            # total_target = max(self.my_target, self.op_target)
        else:
            margin = self.op_target / total_target
        margin_rate = (max(margin - 1 / 2, 0)) * 2
        baseline_eq = 0.39 + 0.16 * margin_rate
        threshold_eq = 0.55 * threat_rate + min(0.03 * self.op_rc_cnt, 0.15)

        pot_odds = c / (pot + c)
        print(f"{self.hole_card} {community_card}")
        print(f"{eq=} {pot_odds=} {baseline_eq=} {threshold_eq=}")
        # print(valid_actions)

        if eq < pot_odds:
            action, amount = last_resort()
            print(f"eq < pot_odds, last_resort {action=} {amount=}")
        elif street == "preflop" and eq < baseline_eq:
            action, amount = last_resort()
            print(f"eq < baseline_eq, last_resort {action=} {amount=}")
        elif threat_rate > random.random() and eq < threshold_eq:
            action, amount = last_resort()
            print(f"eq < threshold_eq, last_resort {action=} {amount=}")
        else:
            if eq < 0.45:
                action, amount = "call", ca
                print(f"eq < 0.45, {action=} {amount=}")
            elif eq < 0.55:
                action, amount = rand_act(["call", "bluff"], [1 - eq, eq])
                print(f"eq < 0.55, rand_act {action=} {amount=}")
            else:  # >= 0.55
                action, amount = (
                    bait_raise() if ischeck or self.opening else agg_raise()
                )
                print(
                    f"eq > 0.55, {'bait' if ischeck or self.opening else 'agg'} {action=} {amount=}"
                )

        # clamping
        if action == "raise":
            total_amount = amount + self.pre_bet
            total_ca = ca + self.pre_bet

            if rmin == -1:
                # print("cannot raise", file=stderr)
                action, amount = "call", ca
            else:
                if (
                    self.op_target < total_amount <= self.my_target
                    and street == "river"
                ):
                    if eq < 0.5 and total_ca <= self.op_target:
                        if rmin <= op_need:
                            amount = op_need - 1
                        else:
                            action, amount = "call", ca
                    else:
                        amount = min(my_need, rmax)
                elif (
                    self.my_target < self.op_target
                    and total_ca <= self.op_target
                    and total_amount > self.op_target
                ):
                    if total_ca <= self.my_target:
                        amount = my_need + 1
                    else:
                        action, amount = "call", ca

                if action == "raise":
                    if amount > rmax:
                        amount = rmax
                    elif amount < rmin:
                        amount = rmin

        self.cur_bet = amount
        assert action in ["fold", "call", "raise"], f"unknown action {action}"
        self.opening = False
        # if action == "call":
        #    print(valid_actions)
        #    print(f"{amount=} {ca=}")
        return action, amount

    def receive_game_start_message(self, game_info):  # fixed known info
        print(f"my uuid = {self.uuid}")

    def receive_round_start_message(self, round_count, hole_card, seats):
        print(f"{round_count=}")
        self.init_round()
        for h in hole_card:
            self.hole_card += parse_game_card(h)

    def receive_street_start_message(self, street, round_state):
        def calc_target(round_count, mystack, opstack, isbig):
            my_blind = BLIND if isbig else 5
            op_blind = 15 - my_blind
            max_loss = win(round_count, 0, 0, isbig, 0) / 2
            target = (opstack + op_blind - (mystack + my_blind) + max_loss * 2) / 2
            # print(f"{isbig=}")
            # print(f"{max_loss=}")
            return target if target > 0 else 0

        print(f"{street=}")
        self.op_opening = True
        self.opening = True
        self.pre_bet += self.cur_bet
        self.cur_bet = 0
        # print(f"{round_state}")

        if street == "preflop":
            street, pot, community_card, round_count, isbig, mystack, opstack = (
                self.parse_round_state(round_state, False)
            )
            self.cur_bet = BLIND if isbig else 5
            self.my_target = calc_target(
                round_count, mystack, opstack, isbig
            )  # + 0.1  # exceed
            self.op_target = calc_target(
                round_count, opstack, mystack, not isbig
            )  # - 0.1
            # print(f"{self.my_target=} {self.op_target=} {mystack=} {opstack=}")

    def receive_game_update_message(self, new_action, round_state):  # from both player
        print(f"{new_action=}")
        street, pot, community_card, round_count, isbig, mystack, opstack = (
            self.parse_round_state(round_state, False)
        )
        # update opponent info
        if new_action["player_uuid"] != self.uuid:
            if street == "preflop" and self.op_opening:
                if new_action["action"] == "call" and new_action["amount"] <= 5:
                    self.op_exclude.append("up10")
                elif new_action["action"] == "raise":
                    self.op_exclude.append("down10")

            elif street == "flop" and self.op_opening:
                if new_action["action"] == "call" and new_action["amount"] == 0:
                    for c in community_card:
                        self.op_exclude.append(c[0])

            if new_action["action"] == "raise" or (
                new_action["action"] == "call" and new_action["amount"] > 5
            ):
                self.op_rc_cnt += 1

            new_action["community_card"] = community_card
            self.actions.append(new_action)

            self.op_opening = False

    def receive_round_result_message(self, winners, hand_info, round_state):
        def i2r(idx):
            if idx == 10:
                return "T"
            elif idx == 11:
                return "J"
            elif idx == 12:
                return "Q"
            elif idx == 13:
                return "K"
            elif idx == 14:
                return "A"
            else:
                return str(idx)

        if hand_info != []:
            # print(hand_info)
            for h in hand_info:
                if h["uuid"] != self.uuid:
                    print(h)
                    op_hole = f"{i2r(h['hand']['hole']['high'])}c{i2r(h['hand']['hole']['low'])}d"  # assume suit club and diamond
                    print(f"{op_hole=}")
                    break
            for a in self.actions:
                self.total_act += 1
                print(f"{op_hole=} {a['community_card']}")
                eq = equity(op_hole, a["community_card"], [])
                if a["action"] == "call" and a["amount"] == 0:
                    self.op_check.update(eq)
                elif a["action"] == "call" or a["action"] == "raise":
                    self.op_call_raise.update(eq)
        else:
            for a in self.actions:
                self.total_act += 1
                if a["action"] == "call" and a["amount"] == 0:
                    self.op_check.cnt += 1
                elif a["action"] == "call" or a["action"] == "raise":
                    self.op_call_raise.cnt += 1
                elif a["action"] == "fold":
                    self.op_fold_n += 1

        print(U.visualize_round_result(winners, hand_info, round_state, self.uuid))


def setup_ai():
    return ConsolePlayer()
