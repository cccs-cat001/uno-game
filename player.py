import random
import time
import threading
from typing import List
from card import Card

from uno import Game

class Player:
    def __init__(self,game: Game,name: str,robot: bool=False,robot_delay: int=0):
        self.game: Game = game
        self.name: str = name.capitalize()
        self.id: int = None
        self.hand: List[Card] = []
        self.drawable: bool = False
        self.myturn: bool = False
        self.on_my_turn = lambda: None
        self.on_change = lambda: None
        self.on_uno = lambda: None
        self.buffer = []
        self.robot: bool = robot
        self.robot_delay: int = robot_delay
        self.score: int = 0

    @property
    def handscore(self):
        score = 0
        for c in self.hand:
            if not c.is_special:
                score += c.num
            elif c.color == 0:
                score += 40
            else:
                score += 20
        return score


    def robot_delay_thread(self):
        if self.robot_delay:
            th = threading.Thread(target=self.robot_auto)
            th.start()
        else:
            self.robot_auto()

    def robot_auto(self):
        time.sleep(self.robot_delay)
        self.autoplay()

    def on_turn(self):
        if self.robot:
            self.robot_delay_thread()
        else:
            self.on_my_turn()

    def drawone(self):
        if not self.myturn: return False
        if self.drawable:
            self.game.draw_to_player(self.id,1)
            self.drawable = False
            if not self.robot:
                self.on_my_turn()
            return True
        else:
            return False

    def play(self, index: int, user_color: str=None):
        if not self.game.playing: return False
        if not self.myturn: return False
        if index > len(self.hand) - 1: return False
        return self.game.play(self,self.hand[index],user_color)

    def autoplay(self):
        if not self.game.playing: return False
        if not self.myturn: return False
        playables = []
        # Pick out all playable cards
        for i in range(len(self.hand)):
            if self.game.playable(self.hand[i]):
                playables.append(i)
        if len(playables):
            return self.play(random.choice(playables))
        else:
            # No card is playable
            if self.drawone():
                return self.autoplay()
            elif self.pass_turn():
                return True
            else:
                return self.accept_punish()

    def accept_punish(self):
        if not self.myturn: return False
        return self.game.punish(self.id)

    def pass_turn(self):
        if not self.myturn: return False
        if self.drawable: return False
        if self.game.has_punishment: return False
        self.game.turn()
        return True

    def confirm(self):
        if not self.myturn: return False
        if self.drawable: return False
        if self.game.has_punishment: return False
        self.game.turn()
        return True

    def __repr__(self):
        return '{}:{}'.format(self.name,len(self.hand))

    def __str__(self):
        return self.name
