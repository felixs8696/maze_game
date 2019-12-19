import random

from abc import ABC, abstractmethod

from move import Move
from utils import get_yes_or_no_response, response_is_yes
from datatypes import Direction, MoveType


class Action(Move):

    def __init__(self, is_mandatory=False):
        super().__init__(is_mandatory)
        self.move_type = MoveType.ACTION

    @abstractmethod
    def description(self):
        pass


class BuyItem(Action):

    def __init__(self, items, is_mandatory=False):
        super().__init__(is_mandatory)
        self.items = items

    def affect_player(self, player, **kwargs):
        if not player.can_acquire_item():
            print(f"You already have an item ({player.item}) and you cannot hold multiple items.")

        prompt = "Would you like to acquire an item from the shop? (y/n)"
        choose_to_act = get_yes_or_no_response(prompt)

        if response_is_yes(choose_to_act):
            chosen_item = random.choice(kwargs['items'])
            player.acquire_item(chosen_item)
        else:
            player.do_nothing()

    def description(self):
        return f"Buy a randomly chosen item from the shop."


class Teleport(Action):

    def __init__(self, exit_location, is_mandatory=False):
        super().__init__(is_mandatory)
        self.exit_location = exit_location

    def affect_player(self, player, **kwargs):
        player.teleport_to(self.exit_location)

    def description(self):
        return f"You have been teleported by a portal."


class Flush(Action):

    def __init__(self, direction: Direction, is_mandatory=False):
        super().__init__(is_mandatory)
        self.direction = direction

    def affect_player(self, player, **kwargs):
        player.flush_one_tile(self.direction)

    def description(self):
        return f"You have been flushed by the river."


class Heal(Action):

    def affect_player(self, player, **kwargs):
        if not player.is_injured():
            print(f"You are already healthy.")

        prompt = "Would you like to heal? (y/n)"
        choose_to_heal = get_yes_or_no_response(prompt)

        if response_is_yes(choose_to_heal):
            player.lose_turn()
            player.heal()
        else:
            player.do_nothing()

    def description(self):
        return f"You may heal at the cost of one turn."


class DropItem(Action):

    def affect_player(self, player, **kwargs):
        player.drop_item()

    def description(self):
        return f"You drop your item."


class AcquireTreasure(Action):

    def affect_player(self, player, **kwargs):
        player.acquire_treasure()

    def description(self):
        return f"You drop your treasure."


class DropTreasure(Action):

    def affect_player(self, player, **kwargs):
        player.drop_treasure()

    def description(self):
        return f"You drop your treasure."


class LoseTurn(Action):

    def affect_player(self, player, **kwargs):
        player.lose_turn()

    def description(self):
        return f"You lose your next turn."


class ShootBullet(Action):

    def __init__(self, direction: Direction, is_mandatory=False):
        super().__init__(is_mandatory)
        self.direction = direction

    def affect_player(self, player, **kwargs):
        board = kwargs['board']
        player.drop_item()

    def description(self):
        return f"Shoot up to 3 spaces in the {self.direction} direction."


class Fight(Action):

    def __init__(self, other_player, is_mandatory=False):
        super().__init__(is_mandatory)
        self.other_player = other_player

    def affect_player(self, player, **kwargs):
        player.fight(self.other_player)

    def description(self):
        return f"Fight {self.other_player.name}."


class EndTurn(Action):

    def __init__(self):
        super().__init__(is_mandatory=False)
        self.move_type = MoveType.END_TURN

    def affect_player(self, player, **kwargs):
        player.end_turn()

    def description(self):
        return f"You end your turn."


class DoNothing(Action):

    def affect_player(self, player, **kwargs):
        player.do_nothing()

    def description(self):
        return f"You do nothing."


class AnnounceSafety(Action):

    def affect_player(self, player, **kwargs):
        player.announce_safety()

    def description(self):
        return f"You are safe."


def ask_for_options(actions):
    actions_options = ""
    range_of_actions = range(len(actions))
    for i in range_of_actions:
        actions_options += f"({i}) {actions[i].description()}\n"
    print(f"{actions_options}")
