"""
Loading module for the game.

Contains:
    - Loading: Handles the creation and storage of game objects.
"""

import pygame as pg
import sys
from config_ab import Config
from sprites_ab import EquipmentSlot
from data_ab import get_json_data

class Loading(Config):
    """
    Manages the creation and storage of game objects.

    This class initializes lists of game objects, optimizing loading times 
    by preparing essential resources in advance.
    """

    def __init__(self):
        """Initialize loading with default settings and set next state to 'shop'."""
        super().__init__()
        self.next = 'shop'
    
    def cleanup(self):
        """Reset class-specific variables"""
        self.updated = False
    
    def create_equipment_slots(self, slot_list):
        """Create and initialize character slot objects for the inventory."""
        slots_data = get_json_data('inventory_slots')
        for i in range(self.max_party_size):
            figure_slots = {}
            for row, ratio in slots_data.items():
                x_ratio = ratio[i][0]
                y_ratio = ratio[i][1]
                pos_x = self.screen_width * x_ratio
                pos_y = self.screen_height * y_ratio
                spot_number = i + 1
                slot_type = row
                slot_name = slot_type + str(spot_number)
                slot = EquipmentSlot(slot_name, pos_x, pos_y, self.slot_side_length, self.slot_side_length, slot_type, spot_number)
                figure_slots[slot_type] = slot
            slot_list.append(figure_slots)

    def create_backpack_slots(self, slot_list):
        """Create and initialize backpack slot objects for the inventory."""
        first_slot_x_ratio = 0.05
        first_slot_y_ratio = 0.11
        backpack_row = 5
        backpack_column = 4
        gutter = 5
        backpack_slot_number = 1
        for row_i in range(backpack_row):
            for column_j in range(backpack_column):
                spot_number = 0
                slot_type = 'backpack'
                width_gap =  self.slot_side_length + gutter
                height_gap =  self.slot_side_length + gutter
                pos_x = self.screen_width * first_slot_x_ratio + (column_j) * width_gap
                pos_y = self.screen_height * first_slot_y_ratio + (row_i) * height_gap
                slot_name = f'backpack_slot{backpack_slot_number}'
                slot = EquipmentSlot(slot_name, pos_x, pos_y, self.slot_side_length, self.slot_side_length, slot_type, spot_number)
                setattr(self, slot_name, slot)
                slot_list.append(slot)
                Config.party_backpack[slot_name] = None
                backpack_slot_number += 1
    
    def startup(self):
        """Initialize resources and set up the loading state."""
        LOADING_FONT_NAME = "Arial"
        LOADING_FONT_SIZE = 50
        MIDDLE_WIDTH = self.screen_width * 0.50
        MIDDLE_HEIGHT = self.screen_height * 0.50
        COORDS_LOADING = (MIDDLE_WIDTH, MIDDLE_HEIGHT)
        LOADING_FONT = pg.font.SysFont(LOADING_FONT_NAME, LOADING_FONT_SIZE)
        LOADING = 'Loading...'
        self.LOADING_TEXT = LOADING_FONT.render(LOADING, True, self.black)
        self.LOADING_RECT = self.LOADING_TEXT.get_rect(center=COORDS_LOADING)
        
        self.create_backpack_slots(Config.backpack_slots)
        self.create_equipment_slots(Config.equipment_slots)

    def get_event(self, event):
        """Handle user input events for the loading state."""
        if event.type == pg.KEYDOWN:
            pass

    def update(self, screen, dt):
        """Update the loading state."""
        self.draw(screen)
        self.done = True

    def draw(self, window):
        """Draw the loading state to the screen."""
        self.screen.fill(self.grey)
        self.screen.blit(self.LOADING_TEXT, self.LOADING_RECT)