from typing import List
from room import Room
from uno import Card, Player
from utils import name_prettify, set_timeout

class RoomPlayer:
    def __init__(self,room: Room, name: str):
        self.room: Room = room
        self.name: str = name
        self.display_name: str = name_prettify(self.name)
        self.sockets: List = []
        self.game_player: Player = None
        self.score: int = 0
        self.prev_score: int = None
        self.wins: int = 0
        self.played:int = 0
        self.is_ingame: bool = False
        self.timer = None

        self.on_disconnect_all = lambda is_turn: None

    @property
    def cards(self):
        if self.is_ingame:
            return len(self.game_player.hand)
        else:
            return 0

    @property
    def hand(self):
        if self.is_ingame:
            return self.game_player.hand
        else:
            return None

    @property
    def is_turn(self):
        if self.game_player and self.room.game:
            return self.game_player == self.room.game.current_player
        else:
            return None

    @property
    def is_online(self):
        return len(self.sockets)

    def autoplay(self):
        if self.room and self.room.game and self.game_player:
            self.game_player.autoplay()
    def drawone(self):
        if self.game_player:
            self.game_player.drawone()
    def accept_punish(self):
        if self.game_player:
            if self.game_player.accept_punish():
                self._user_action()
    def pass_turn(self):
        if self.game_player:
            if self.game_player.pass_turn():
                self._user_action()
    def play(self,card: Card,color=None):
        if self.game_player:
            if self.game_player.play(card,color):
                self._user_action()

    def _user_action(self):
        self.remove_timer()

    def set_timer(self, sec):
        self.remove_timer()
        self.timer = set_timeout(self.autoplay,sec)

    def remove_timer(self):
        if self.timer:
            self.timer.cancel()
            self.timer = None

    def _on_disconnect_all(self):
        self.room.new_pipe().player_left(self).boardcast()
        if self.is_turn: self.set_timer(5)
        self.on_disconnect_all(self.is_turn)
        # If all the player is disconnected,
        # over the game
        if not self.room.players_online:
            self.room.end()

    def send_message(self,action='ping',**message):
        message['action'] = action
        for ws in self.sockets:
            ws.send_json_message(message)

    def send_raw_message(self,message):
        for ws in self.sockets:
            ws.send_message(message)

    def connect(self,ws):
        self.sockets.append(ws)
        self.room.bc_player_join(self)
        self.room.new_pipe().scoreboard().messageto(self)

    def disconnect(self,ws):
        try:
            self.sockets.remove(ws)
        except:
            return False
        else:
            # autoplay when a player lost he's all connections
            if not self.is_online:
                self._on_disconnect_all()
            return True

    def bind_game_player(self,game_player):
        self.game_player = game_player
        self.game_player.on_my_turn = lambda: self.on_my_turn()
        self.game_player.on_change = lambda: self.on_change()
        self.is_ingame = True

    def add_score(self):
        if self.game_player:
            if self.game_player.score > 0:
                self.wins += 1
            self.played += 1
            self.score += self.game_player.score
            self.prev_score = self.game_player.score

    def clear_score(self):
        self.played = 0
        self.wins = 0
        self.score = 0
        self.prev_score = 0

    def on_change(self):
        self.room.new_pipe().hand(self).messageto(self)

    def on_others_turn(self):
        self.remove_timer()

    def on_my_turn(self):
        if not self.is_online:
            # If player is disconnected when it's his/her turn,
            # set an autoplay-timer for 5sec
            self.set_timer(5)
        else:
            # Set an autoplay-timer to limit player's turn time
            if self.room.options['turn_timeout'] > 0:
                self.set_timer(self.room.options['turn_timeout'])
            self.room.new_pipe().myturn(self).messageto(self)

    def on_gameover(self):
        self.is_ingame = False
        self.game_player = None
