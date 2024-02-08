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

def get_simulation_data() -> pd.DataFrame:
    db = sqlite3.connect('./ab_data/simulation_results.db')

    sim_query = """
        SELECT 
            results.exp, 
            results.boss_defeated, 
            heroes.name AS hero_name, 
            heroes.class AS hero_class, 
            talents.talent1, talents.talent2, talents.talent3, talents.talent4, talents.talent5,
            talents.talent1_2, talents.talent2_2, talents.talent3_2, talents.talent4_2, talents.talent5_2,
            talents.talent1_3, talents.talent2_3, talents.talent3_3, talents.talent4_3, talents.talent5_3
        FROM 
            results
        INNER JOIN 
            heroes ON heroes.result_id = results.id
        INNER JOIN 
            talents ON talents.hero_id = heroes.id
        """
    
    data_df = pd.read_sql_query(sim_query, db)
    db.close()
    return data_df
    

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

    heroes = row['heroes']
    hero_data = [hero for hero_tuple in heroes for hero in hero_tuple]

    hero_query = """
        INSERT INTO Heroes (result_id, name1, class1, name2, class2, name3, class3) 
        VALUES (?, ?, ?, ?, ?, ?, ?)"""
    db.execute(hero_query, (result_id,) + tuple(hero_data))
  

    talent_dicts = []
    for hero_name, talents in row['talents'].items():
        talent_dict = {'hero_name': hero_name, 'talents': talents}
        talent_dicts.append(talent_dict)
    
    talent_query = """
        INSERT INTO Talents 
        (result_id, hero1_talent1, hero1_talent2, hero1_talent3, hero1_talent4, hero1_talent5,
        hero2_talent1, hero2_talent2, hero2_talent3, hero2_talent4, hero2_talent5, 
        hero3_talent1, hero3_talent2, hero3_talent3, hero3_talent4, hero3_talent5)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

    
    talent_values = [result_id]

    for t_dict in talent_dicts:
        talents = t_dict['talents']
        talents.extend([None] * (5 - len(talents)))
        talent_values += talents

    db.execute(talent_query, tuple(talent_values))

    cursor.close()
    db.commit()
    db.close()
