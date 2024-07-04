"""
Data module for handling data retrieval and entry.

This module provides functions for pulling data from databases and JSON files,
and entering data into databases. It supports various game-related data
operations such as retrieving character info, adventure data, and simulation results.
"""

import sqlite3
import pandas as pd
import json

def row_to_dict(dataframe, name) -> dict:
    name_index_df = dataframe.set_index('name')
    row_dict = name_index_df.loc[name].to_dict()
    return row_dict

def get_data(table: str) -> pd.DataFrame:
    db = sqlite3.connect('./ab_data/stats.db')
    db.isolation_level = None
    query = "SELECT * FROM " + table
    df = pd.read_sql_query(query, db)
    db.close()
    return df

def get_json_data(file_name: str) -> dict:
    with open('./ab_data/json_data/' + file_name + '.json') as j:
        json_data = json.load(j)
    return json_data

def get_affix(item_type: str, affix_type: str):
    db = sqlite3.connect('./ab_data/stats.db')
    db.isolation_level = None                                   
    affix_query = "SELECT * FROM item_modifiers WHERE mod_affix = ? AND item_type = ?"
    affix_df = pd.read_sql_query(affix_query, db, params=(affix_type, item_type,))
    db.close()
    return affix_df

def get_monster_encounters(adventure: str, tier: int) -> pd.DataFrame:
    db = sqlite3.connect('./ab_data/stats.db')

    id_query = "SELECT id FROM adventures WHERE name = ?"
    id = db.execute(id_query, (adventure,)).fetchone()[0]
    
    mob_group_query = """
        SELECT *
        FROM Location_encounters
        WHERE Adventure_id = ? AND Tier = ?"""
        
    mob_group_df = pd.read_sql_query(mob_group_query, db, params=(id, tier,))
    db.close()
    return mob_group_df

def get_talent_data(hero_class: str) -> pd.DataFrame:
    db = sqlite3.connect('./ab_data/stats.db')

    talents_query = """SELECT talents.*
        FROM talents
        INNER JOIN talent_class_association ON talents.id = talent_class_association.talent_id
        INNER JOIN classes ON talent_class_association.class_id = classes.id
        WHERE classes.type = ?;"""
    
    talents_df = pd.read_sql_query(talents_query, db, params=(hero_class,))
    db.close()
    return talents_df

def get_simulation_results() -> pd.DataFrame:
    db = sqlite3.connect('./ab_data/simulation_results.db')
    db.isolation_level = None
    query = "SELECT * FROM Results"
    df = pd.read_sql_query(query, db)
    db.close()
    return df

def get_simulation_dataset(set_number: int) -> pd.DataFrame:
    num = str(set_number)
    db = sqlite3.connect('./ab_data/simulation_datasets/simulation_results_' + num + '.db')

    sim_query = """
        SELECT 
            results.exp, 
            results.boss, 
            heroes.name1 AS hero1_name, 
            heroes.class1 AS hero1_class, 
            heroes.name2 AS hero2_name, 
            heroes.class2 AS hero2_class, 
            heroes.name3 AS hero3_name, 
            heroes.class3 AS hero3_class, 
            talents.hero1_talent1, talents.hero1_talent2, talents.hero1_talent3, talents.hero1_talent4, talents.hero1_talent5,
            talents.hero2_talent1, talents.hero2_talent2, talents.hero2_talent3, talents.hero2_talent4, talents.hero2_talent5,
            talents.hero3_talent1, talents.hero3_talent2, talents.hero3_talent3, talents.hero3_talent4, talents.hero3_talent5
        FROM 
            results
        INNER JOIN 
            heroes ON heroes.result_id = results.id
        INNER JOIN 
            talents ON talents.result_id = results.id
        """
    
    data_df = pd.read_sql_query(sim_query, db)
    db.close()
    return data_df
    

def enter_simulation_result(row):
    db = sqlite3.connect('./ab_data/simulation_results.db')
    db.isolation_level = None
    cursor = db.cursor()

    exp = row['exp']
    boss = row['bosses']
    heroes = row['heroes']
    hero_data = [hero for hero_tuple in heroes for hero in hero_tuple]

    #up to (Config).max_party_size
    hero1_talents = row['talents1']
    hero2_talents = row['talents2']
    hero3_talents = row['talents3']
    hero1_json = json.dumps(hero1_talents)
    hero2_json = json.dumps(hero2_talents)
    hero3_json = json.dumps(hero3_talents)

    result_query = """
        INSERT INTO Results (exp, boss, name1, class1, name2, class2, name3, class3, hero1_talents, hero2_talents, hero3_talents) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    cursor.execute(result_query, (exp, boss, *hero_data, hero1_json, hero2_json, hero3_json))

    cursor.close()
    db.commit()
    db.close()

def get_monster_sim_stats():
    db = sqlite3.connect('./ab_data/simulation_results.db')
    db.isolation_level = None

    query = "SELECT * FROM monster_stats"
    existing_stats = pd.read_sql_query(query, db, index_col='name')
    db.close()
    return existing_stats

def update_monster_sim_stats(updated_stats):
    db = sqlite3.connect('./ab_data/simulation_results.db')
    db.isolation_level = None
    cursor = db.cursor()
    
    for name, row in updated_stats.iterrows():
        query = """
        INSERT OR REPLACE INTO monster_stats (name, dam_in, dam_out, count)
        VALUES (?, ?, ?, ?)
        """
        cursor.execute(query, (name, int(row['dam_in']), int(row['dam_out']), int(row['count'])))
    
    cursor.close()
    db.commit()
    db.close()

def get_data_simulation(table: str, set_number: int):
    num = str(set_number)
    db = sqlite3.connect('./ab_data/simulation_datasets/simulation_results_' + num + '.db')
    db.isolation_level = None
    query = "SELECT * FROM " + table
    df = pd.read_sql_query(query, db)
    db.close()
    return df