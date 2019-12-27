# Treasures of the Abandoned Labyrinth

## Basic Version

| Command | Description |
|---|---|
|`./setup` | Download required dependencies for the game. Do this if you get any `<module> not found` errors. |
|`./new_game` | Starts a new game |
|`./new_game_omniscient` | Starts a new game in omniscient mode |
|`./list_saved_games` | Lists all saved game ids |
|`./restore_game <game_id>` | Restores a game from its game id |
|`./restore_game_omniscient <game_id>` | Restores a game from its game id in omniscient mode |
|`./delete_game <game_id>` | Deletes a saved game |
|`./delete_all_games` | Deletes all saved games |


### Players

Recommended: 3-5 players

### Objective

Explore to discover each player and tile on the game master’s map, find the treasure, and successfully exit the labyrinth with the treasure without being injured.

### Game Map

This program generates the game board by placing the following types of tiles on a 
rectangular grid. By default, the board is hidden from all adventurers for the entirety of the game. 
(You may override this function by running the program in "omniscient" mode.)

Tile Types:
* Safe - Default: 34 tiles
* Shop - Default: 1 tile
* Hospital - Default: 1 tile
* Marsh - Default: 8 tiles
* River - Default: 12 tiles
    * The river will begin and end on a labyrinth wall, cannot fork, and can only move in one direction.
* Fake Portal - Default: 1 tile
* AB (2-way) portal - Default: 1 set (2 portal tiles (1 A, 1 B))
* ABC (3-way) portals - Default: 1 set (3 portal tiles (1 A, 1 B, 1 C))
* Treasure - Default: 2 tiles

Border Types (does not take up any space, exists between tiles):
* Outer wall - Default: 30 border spaces
* Exit - Default: 2 border spaces
    * A break between outer walls
* Inner wall - Default: 20 border spaces

#### Starting positions

After the map is set up, the game master (this program or an omniscient human) spawns each player on a randomly chosen safe tile and randomly decides the 
order of their turns. Important: The game master will NEVER give away the location of anyone in the game except when a 
player is found by another player. Each player also starts with an empty gun (this does not take up an item space). 


During the game adventurers may freely talk, share information, discuss map arrangements, or even lie to each other. 
The game master will give away any information that has not been directly discovered by an adventurer. If any 
adventurer wants to look at the game master's logs to verify a previously uncovered observation, all adventurers must 
unanimously agree, otherwise the information will not be revealed. After each turn, the game master will ask the 
adventurers if they want to peek at the board. If there is ever a discrepancy, a non-player party may peek to make 
sure the game state is playable and consistent.

### Moves

Each player takes turns in the order decided by the game master. On each turn, each player must make one and only one 
movement, but may take any number of actions.

1. **Action: Use an item (Optional)**

    * If you use or drop an item you lose it irreversibly, you may not pick it up again.
    * Rusty bullet
        * Choose a direction to shoot one player up to 3 spaces away (not including the shooter's current space).
            * Game Master: If there is no player up to 3 spaces away from the shooter in that direction or if a wall 
            blocks the bullet, announce that the shooter has missed, but do not give away anything else. Otherwise the 
            bullet injures the first person within 3 spaces. The shooter loses his/her bullet.
    * First aid kit
        * Use the first aid kit to heal yourself instantly.
    * Pile of junk
        * If you are not in the thrift shop you may throw away your useless junk.

1. **Action: Attack (Optional)**

    * If you occupy the same tile as another adventurer (except for the hospital) and you are not injured you 
    may choose to attack the other player (if they are also not injured). See the "Battle" section.

1. **Movement: Move once (Mandatory)**
   (The game master will tell you one of the following responses if you encounter any of the following tiles)

    * A Wall
        * "`player` cannot move `direction`. Blocked by wall."
            * The adventurer may continue asking to move until they do not hit a wall
            * Game Master: Do NOT give away where the wall is on the map.
            * Does not take up space on the map, just marks a border that stops adventurer movement.
    * A Labyrinth Exit
        * "`player` has exited the maze with the treasure and won the game." OR "`player` has found an exit, but has no treasure."
            * If the adventurer has treasure, they win the game.
            * If not, the adventurer stays in place, but now knows that border is an exit on the labyrinth.
            * Does not take up space on the map, marks a labyrinth exit.
    * An Empty Tile
        * If the empty tile is no occupied by another adventurer:
            * "`player` walks into a SAFE clearing."
        * If another adventurer is on the same tile:
            * "Fight `other_player`" (See Battle section) or end your turn.
            * Remember: If you do not attack, the other player may choose to attack you at the start of their next turn 
            (Any non-injured adventurer can attack another non-injured adventurer)
    * A Shop
        * "Buy a randomly chosen item from the shop."
            * If the adventurer is not already holding an item, they may role the dice to pick between the 3 items. A 1 or 2 gives the rusty bullet, a 3 or 4 gives the first aid kit, a 5 or 6 gives the useless junk.
            * Rusty Bullet - Your gun can now be used to shoot one player up to 3 spaces away if no walls separate you two.
            * First aid kit - Sacrifice one turn at any time to heal yourself
            * A Pile of Junk - Useless.
    * A Hospital
        * "`player` enters a HOSPITAL."
            * Heal at the expense of your next turn.
    * A Marsh
        * "`player` sinks into a MARSH."
            * Lose your next turn.
    * A River Tile
        * Do NOT give away the direction that the player has been flushed
        * The player will end up moving 2 tiles this turn unless the river pushes them into a wall (once for the move they requested, and once from the river pushing them downstream 1 tile). 
        * If the next tile downstream of the river is a wall (the 2nd tile of the 2 tile move):
            * "The river tries to flush `player`, but a wall prevents him/her from moving."
        * Otherwise:
            * "`player` is flushed by the river one tile."
    * A Portal
        * Any portal: "`player` enters and exits a portal."
            * On the master board, move the adventurer marker according to what type of portal the portal is. Do NOT give away the portal type to the adventurer.
            * For the Game Master ONLY:
                * Fake
                    * Adventurer enters portal F and exits portal F in the same spot
                * AB (2-way)
                    * If the adventurer enters portal A, they exit on the portal B tile. If the adventurer enters portal B, they exit on the portal A tile.
                * ABC (3-way)
                    * If the adventurer enters portal 1, they exit on the portal 2 tile. If the adventurer enters portal 2, they exit on the portal 3 tile. If the adventurer enters portal 3, they exit on the portal 1 tile.
    * A Tile containing Treasure
        * "`player` also stumbles across a pile of TREASURE"
            * The player can pick up the treasure only if he/she is not injured.
            * You can only hold one treasure at a time

### Player conditions

Healthy - If the player has not been shot by another player or lost a battle with another player they are considered healthy and are able to collect treasure freely.
Injured - If a player is shot by another player with a gun and rusty bullet, or loses a battle with another adventurer, they become injured, drop any treasure they are holding, and are unable to pick up any more treasure unless they are healed with a first aid kit or by traveling to a hospital. Their movement is not otherwise affected in any way.

### Battle

When two non-injured players occupy the same tile, the adventurer whose turn it is may choose to attack the other non-injured adventurer. During a battle, the attacker and defender each take turns rolling the die once. Whichever adventurer rolls a lower number becomes injured, drops any treasure they are holding, and becomes unable to pick up any more treasure unless they are healed with a first aid kit or at a hospital. If there is a tie with the dice roll, the attacking adventurer wins the battle.

If the attacking adventurer owns a gun and a rusty bullet, they choose whether or not to use the bullet to automatically win the battle, subsequently losing the bullet. However, if the defending adventurer owns a gun they cannot not use it at all during the battle.

### Game Over

When the first adventurer finds a treasure and successfully exits the labyrinth with the treasure wins. After they exit the labyrinth crumbles behind them, burying the rest of the adventurers, ending the game.


## Upcoming Versions

* Software tested game equilibrium
    * Run thousands of simulations, add rules to even out win distribution.
* EXPANSION PACKS:
    * More Actions: Trading.
    * New Tiles: Stairs/elevators to multiple labyrinth levels, donation center
    * New Treasure: Pure, Fools, Booby Trapped
    * New Items: Treasure scanner, broken flashlight + battery (combine items for them to work, reveal more of the map), dynamite (blows up walls), shield, etc.
    * New Monsters: Bear, dog, zombie, etc.
    * New Themes: Haunted house, Cursed Forest, Psych Ward, Pirate Ship, etc.

