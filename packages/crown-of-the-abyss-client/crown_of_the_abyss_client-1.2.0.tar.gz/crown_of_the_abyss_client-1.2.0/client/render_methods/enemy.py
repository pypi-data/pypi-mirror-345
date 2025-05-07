from ..main import Player, Enemy, ActionBar
from typing import Any
import pygame

def enemy(state: dict, screen: pygame.Surface, player: Player, other_players: dict[int, Player], 
          map: dict[int, Any]={}, enemies: dict[int, Enemy]={}, action_bar: ActionBar=None, key: str=""):

    w = screen.get_width()
    h = screen.get_height()
   
    # Move players to enemy location
    player.start_transition((w // 4) - player.width, (h // 2) - player.height, other_players, w, h) 
    for p in other_players:
        p_width = other_players[p].width
        p_height = other_players[p].height
        other_players[p].start_transition((w // 4) - p_width, (h // 2) - p_height, other_players, w, h)

    # Move enemies to enemy location
    for id, enemy in enemies.items():
        other_enemies = dict(enemies)
        del other_enemies[id]
        enemy.start_transition((w // 1.5) - enemy.width, (h // 2) - enemy.height, other_enemies, w, h)

    # Enable action bar if the current turn is the main player
    current_turn = state["turns"][0]
    id = int(current_turn[2:]) # Remove the [P | E]# from the front and grab the id
    type_of_turn = current_turn[0]

    if (type_of_turn == "E"):
            action_bar.set_enabled(False)
            # Skip enemy turns for now
            player.update_state({"enemy": True})
    else:
        # Since the main player id is -1 on the client, then if the
        # current turn id is not a player id, its the main player
        isMainPlayer = True
        if (player.get_id() == id): isMainPlayer = False 
        for p in other_players:
            if (p == id): isMainPlayer = False

        if (isMainPlayer):
            # Set up action bar for the main player
            # 4 moves for a player
            action_bar.set_enabled(True)

            moves = player.get_state()["moves"]
            if (id != -1):
                for p in other_players:
                    if (other_players[p].get_id() == -1):
                        moves = other_players[p].get_state()["moves"]
                        break

            for i in range(len(action_bar.buttons)):
                action_bar.set_button_properties(i, text=moves[i])
        else:
            action_bar.set_enabled(False)
            # 'Perform' the temates turn 
            player.update_state({"enemy": True})


        # Get the buttons of the action bar and check if
        # The first one is pressed, change later
        for i in range(len(action_bar.buttons)):
            if (action_bar.buttons[i]["state"] == "pressed"):
                # State that the turn is finished
                action_bar.set_enabled(False)
                player.update_state({"enemy": True, "move_made": f"{i}#{player.get_target()}"})
                break

