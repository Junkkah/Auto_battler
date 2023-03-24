import pygame as pg
import pickle

def save_game(data):
    with open('save_game.pickle', 'wb') as sl:
        pickle.dump(data, sl)

def load_game():
    with open('save_game.pickle', 'rb') as ls:
        data = pickle.load(ls)
    return data

game_data = {} #prgoression, resources, exp/stats/talents