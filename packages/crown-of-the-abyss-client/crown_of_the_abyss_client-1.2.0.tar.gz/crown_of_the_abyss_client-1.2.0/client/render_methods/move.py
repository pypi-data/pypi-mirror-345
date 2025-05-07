from ..main import Player, Enemy
from typing import Any
import pygame

def move(state: dict, screen: pygame.Surface, player: Player , other_players: dict[int, Player], map: dict[int, Any]={}, enemies: dict[Any, Enemy]={}, key: str=""):

        w = screen.get_width()
        h = screen.get_height()

        if (player.get_id() == -1) and (not player.is_transitioning):

            # The main player is in the right spot, bring everyone to them
            for p in other_players:
                other_players[p].start_transition((player.x), (player.y), other_players, w, h)

            playersTransitioning = False
            for p in other_players:
                if other_players[p].is_transitioning:
                    print(f"Found player {other_players[p].get_id()} transitioning")
                    playersTransitioning = True

            print(playersTransitioning)

            # Tell server that we all moved
            if not playersTransitioning:
                # Move player to middle
                player.start_transition((w - player.width) // 2, (h - player.height) // 2, other_players, w, h)
                player.update_state({"move": True})
