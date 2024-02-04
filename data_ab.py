import pygame as pg
import csv
from csv import DictReader
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


        




