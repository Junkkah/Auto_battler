"""
Main Game Script

This script serves as the entry point for the game and operates the main game loop,
state management, and screen rendering.

Usage:
    Run this script to start the game. The game initializes various game states such as
    the menu, shop, world map, battle, and others, and transitions between them based on
    user input and game events.

Attributes:
    size (tuple): The size of the game window in pixels (width, height).
    fps (int): The target frames per second for the game.

Classes:
    Control: A class representing the main game controller. It manages the game loop,
    state transitions, and screen rendering.

Methods:
    setup_states(state_dict, start_state): Initialize the game states with the provided
    dictionary mapping state names to state objects. Set the initial game state.
    flip_state(): Transition to the next game state based on the current state's 'next'
    attribute. Cleanup the current state and initialize the new state.
    update(dt): Update the game state and perform any necessary state transitions based
    on user input and game events.
    event_loop(): Handle user input events such as mouse clicks and keyboard inputs.
    main_game_loop(): Start the main game loop, continuously updating and rendering the
    game until the user exits or the game is terminated.

Usage Example:
    Run the script with the appropriate Python interpreter to start the game:

    ```
    python main.py
    ```

"""
import pygame as pg
import sys
from menu_ab import MainMenu, SettingsMenu
from shop_ab import Shop
from overworld_ab import WorldMap
from path_ab import Path
from battle_ab import BattleManager
from config_ab import Config
from levelup_ab import LevelUp
from simulator_ab import Simulator
from inventory_ab import Inventory

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
    'menu': MainMenu(),
    'settings': SettingsMenu(),
    'shop': Shop(),
    'map': WorldMap(),
    'path': Path(),
    'battle': BattleManager(),
    'levelup': LevelUp(),
    'simulator': Simulator(),
    'inventory': Inventory()
}
app.setup_states(state_dict, 'menu') 
app.state.startup()
app.main_game_loop()
pg.quit()
sys.exit()