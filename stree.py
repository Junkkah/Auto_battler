import pygame as pg
import sys
from sstates import States
#import objects?
#throw this in sobjects

class Tree():
    def __init__(self, location):
        self.location = location
        self.left = None
        self.right = None

city = Tree(self.city) #current_location
tree1 = Tree(self.tree1)
bush1 = Tree(self.bush1)
city.left = tree1
city.right = bush1

tree2 = Tree(self.tree2)
bush2 = Tree(self.bush2)
tree1.left = tree2
tree1.right = bush2

tree3 = Tree(self.tree3)
tree4 = Tree(self.tree4)
bush1.left = tree3
bush1.right = tree4

bush3 = Tree(self.bush3)
tree2.right = bush3
bush2.left = bush3

bush4 = Tree(self.bush4)
tree3.right = bush4
tree4.left = bush4

cave = Tree(self.cave)
bush4.left = cave
bush3.right = cave

def traverse_binary_tree(current_location):
    # If the current location is None, return None
    if current_location is None:
        return None
    
    # Process the current location (e.g. display location description)
    process_location(current_location)
    
    # Traverse the left subtree
    next_location = traverse_binary_tree(current_location.left)
    
    # If there is no next location in the left subtree, traverse the right subtree
    if next_location is None:
        next_location = traverse_binary_tree(current_location.right)
    
    # Return the next location to move to
    return next_location

    #list we are searching States.party_heroes or States.room_monsters
        #we know which list we are searching with self.actions_ordered[0].hero/monster
        #target = self.actions_ordered[0]
        #States.party_heroes.index(target) gives the index of the hero in question

def write_hdata(): #import csv
    with open('auto_battle/ab_data/heroes.csv', 'w') as fek:
        a = ["class", "health", "max_health", "damage", "speed"]
        b = ["cleric", 12, 12, 2, 3]
        c = ["thief", 8, 8, 2, 4]
        d = ["warrior", 15, 15, 2, 3]
        e = ["wizard", 6, 6, 2, 3]
        f = ["bard", 7, 7, 2, 3]
        g = ["ranger", 13, 13, 2, 3]
        h = ["paladin", 15, 15, 2, 3]
        i = ["barbarian", 17, 17, 2, 3]

        writer = csv.writer(fek)

        writer.writerow(a)
        writer.writerow(b)
        writer.writerow(c)
        writer.writerow(d)
        writer.writerow(e)
        writer.writerow(f)
        writer.writerow(g)
        writer.writerow(h)
        writer.writerow(i)
#write_hdata()
