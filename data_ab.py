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

def get_slots_data() -> dict:
    with open('./ab_data/inventory_slots.json') as s:
        slots_data = json.load(s)
    return slots_data

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

# Produces dataframe with duplicates from dataset2
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

def get_data_simulation(table: str, set_number: int):
    num = str(set_number)
    db = sqlite3.connect('./ab_data/simulation_datasets/simulation_results_' + num + '.db')
    db.isolation_level = None
    query = "SELECT * FROM " + table
    df = pd.read_sql_query(query, db)
    db.close()
    return df
