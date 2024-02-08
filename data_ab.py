import pygame as pg
from config_ab import Config
import sqlite3
import pandas as pd


def row_to_dict(dataframe, name) -> dict:
    name_index_df = dataframe.set_index('name')
    row_dict = name_index_df.loc[name].to_dict()
    return row_dict

def get_data(table: str) -> pd.DataFrame:
    db = sqlite3.connect('./ab_data/stats.db')
    db.isolation_level = None
    # "SELECT * FROM Monsters WHERE name IN ('goblin', 'orc')"
    query = "SELECT * FROM " + table
    df = pd.read_sql_query(query, db)
    db.close()
    return df

def get_adv_monsters(adventure: str) -> pd.DataFrame:
    db = sqlite3.connect('./ab_data/stats.db')

    mob_query = """
        SELECT m.*
        FROM Monsters m
        JOIN Adventure_monsters am ON m.id = am.monster_id
        JOIN Adventures a ON a.id = am.adventure_id
        WHERE a.name = ?
        """

    mobs_df = pd.read_sql_query(mob_query, db, params=(adventure,))
    db.close()
    return mobs_df

def get_monster_encounters(adventure: str, tier: int) -> pd.DataFrame:
    db = sqlite3.connect('./ab_data/stats.db')

    id_query = "SELECT id FROM adventures WHERE name = ?"
    id = db.execute(id_query, (adventure,)).fetchone()[0]
    
    mob_group_query = """
        SELECT *
        FROM Loc_Content 
        WHERE Adventure_id = ? AND Tier = ?"""
        
    mob_group_df = pd.read_sql_query(mob_group_query, db, params=(id, tier,))
    db.close()
    return mob_group_df

def get_talent_data(hero_class: str) -> pd.DataFrame:
    db = sqlite3.connect('./ab_data/stats.db')

    talents_query = """
        SELECT talents.*
        FROM talents
        INNER JOIN classes ON talents.class_id = classes.id
        WHERE classes.type = ?
        """
    
    # Use COLLATE NOCASE for case-insensitive comparison
    #query = f"SELECT * FROM talents WHERE name = ? COLLATE NOCASE"

    talents_df = pd.read_sql_query(talents_query, db, params=(hero_class,))
    db.close()
    return talents_df

def get_hero_id(db, result_id, hero_name):

    hero_id_query = """
        SELECT id FROM Heroes WHERE result_id = ? AND name = ?"""

    cursor = db.execute(hero_id_query, (result_id, hero_name))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None


def enter_simulation_result(row):
    db = sqlite3.connect('./ab_data/simulation_results.db')
    db.isolation_level = None
    cursor = db.cursor()

    exp = row['exp']
    boss = row['boss_defeated']

    result_query = """
        INSERT INTO Results (exp, boss) VALUES (?, ?)"""
    
    cursor.execute(result_query, (exp, boss))
    result_id = cursor.lastrowid
    
    nodes = row['nodes']
    node_query = """
        INSERT INTO Nodes (result_id, node1, node2, node3, node4, node5, node6, node7, node8, node9, node10, node11, node12, node13) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    db.execute(node_query, (result_id,) + tuple(nodes))

    heroes_query = """
        INSERT INTO Heroes (result_id, name, class) VALUES (?, ?, ?)"""
    
    for name, class_ in row['heroes']:
        db.execute(heroes_query, (result_id, name, class_))
  

    talent_dicts = []
    for hero_name, talents in row['talents'].items():
        talent_dict = {'hero_name': hero_name, 'talents': talents}
        talent_dicts.append(talent_dict)
    
    talent_query = """
        INSERT INTO Talents (result_id, hero_id, talent1, talent2, talent3, talent4, talent5)
        VALUES (?, ?, ?, ?, ?, ?, ?)"""

    for t_dict in talent_dicts:
        hero_name = t_dict['hero_name']
        talents = t_dict['talents']
        hero_id = get_hero_id(db, result_id, hero_name)
        if hero_id is not None:
            talents.extend([None] * (5 - len(talents)))
            db.execute(talent_query, (result_id, hero_id,) + tuple(talents))

    cursor.close()
    db.commit()
    db.close()

def enter_sim_list_result(lst):
    db = sqlite3.connect('./ab_data/simulation_results.db')
    db.isolation_level = None

    exp = lst[3]
    boss = lst[4]
    result_query = """
        INSERT INTO Results (exp, boss) VALUES (?, ?)"""
    db.execute(result_query, (exp, boss,))
    
    result_id = db.lastrowid

    nodes = lst[0]
    node_query = """
        INSERT INTO Nodes (result_id, node1, node2, node3, node4, node5, node6, node7, node8, node9, node10, node11, node12, node13) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    db.execute(node_query, (result_id,) + tuple(nodes))

    heroes = lst[1]
    heroes_query = """
        INSERT INTO Heroes (result_id, name, class)
        VALUES (?, ?, ?)"""

    for hero in heroes:
        db.execute(heroes_query, (result_id,) + hero)
    

    talent_dicts = lst[2]
    talent_query = """
        INSERT INTO Talents (result_id, hero_id, talent1, talent2, talent3, talent4, talent5)
        VALUES (?, ?, ?, ?, ?, ?, ?)"""


    for t_dict in talent_dicts:
        for hero_name, talents in t_dict.items():
            hero_id = get_hero_id(db, result_id, hero_name)
            if hero_id is not None:
                talents.extend([None] * (5 - len(talents)))
                db.execute(talent_query, (result_id, hero_id,) + tuple(talents))

    db.commit()
    db.close()

        




