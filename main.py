import pygame as pg
import sys
from menu_ab import Menu
from game import Game
from map import Map
from path_ab import Path
from combat import Combat
from states import States
from levelup_ab import LevelUp
from simulator import Simulator

#Control and States class state machine code from
#https://python-forum.io/thread-336.html 

class Control:
    def __init__(self, **settings):
        pg.init()
        self.__dict__.update(settings)
        self.done = False
        self.screen = pg.display.set_mode(self.size)
        self.clock = pg.time.Clock()
    def setup_states(self, state_dict, start_state):
        self.state_dict = state_dict
        self.state_name = start_state
        self.state = self.state_dict[self.state_name]
    def flip_state(self):
        self.state.done = False
        previous,self.state_name = self.state_name, self.state.next
        self.state.cleanup()
        self.state = self.state_dict[self.state_name]
        self.state.startup()
        self.state.previous = previous
    def update(self, dt):
        if self.state.quit:
            self.done = True
        elif self.state.done:
            self.flip_state()
        self.state.update(self.screen, dt)
    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True       
            self.state.get_event(event)
    def main_game_loop(self):
        while not self.done:
            delta_time = self.clock.tick(self.fps)/1000.0
            self.event_loop()
            self.update(delta_time)
            pg.display.update()
 
settings = {
    'size':(1920,1080),
    'fps' :60
}

app = Control(**settings)
state_dict = {
    'menu': Menu(),
    'game': Game(),
    'map': Map(),
    'path': Path(),
    'combat': Combat(),
    'levelup': LevelUp(),
    'simulator': Simulator()
}
app.setup_states(state_dict, 'menu') 
app.state.startup()
app.main_game_loop()
pg.quit()
sys.exit()