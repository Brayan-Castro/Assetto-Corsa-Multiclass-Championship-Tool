import sqlite3
import modules.acLap as acLap
import json
import modules.driver_championship as driver_championship
from pathlib import Path
import re
import sys
import os
from collections import defaultdict

def teams_path():
    return Path.home() / 'Documents' / 'Ac Timer'

def get_teams_data():
    default = default_teams()
    file_path = os.path.join(teams_path(), 'teams_config.json')
    if check_if_teams_exist():
        with open(file_path, 'r') as f:
            return json.load(f)
    else:
        with open(file_path, 'w') as file:
            json.dump(default, file, indent=4)
            return default_teams()
    
def create_teams_champ(teams_data):
    with acLap.db_manager() as con:
        cur = con.cursor()
        try:
            cur.execute('SELECT COUNT(*) FROM teams_db')
        except sqlite3.OperationalError:
            cur.execute('CREATE TABLE IF NOT EXISTS teams_db (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, drivers TEXT NOT NULL, points INT)')
        else:
            if cur.fetchone()[0] == 0:
                for teams in teams_data:
                    cur.execute('INSERT INTO teams_db (name, drivers, points) VALUES (?, ?, ?)', (teams['name'], str(teams['drivers']), str(0)))

def get_teams() -> tuple:
    with acLap.db_manager() as con:
        cur = con.cursor()
        cur.execute('SELECT name, drivers FROM teams_db')
        return cur.fetchall()
    
def get_team_points() -> tuple:
    with acLap.db_manager() as con:
        cur = con.cursor()
        cur.execute('SELECT name, points FROM teams_db')
        return cur.fetchall()
    
# Just as arrange_driver_position, does a bunch of random things and somehow is the heart and soul of the manufacturer championship.
def set_eligible_drivers(race_result):
    teams = get_teams()
    ordered_driver_lists = driver_championship.arrange_driver_position(race_result)
    eligible_drivers = [[],[]]
    ordered_team = [[],[]]
    no_duplicates = []
    seen = []

    for category in range(len(ordered_driver_lists)):
        for team in teams:
            for driver in ordered_driver_lists[category]:
                if driver[0] in team[1]:
                    eligible_drivers[category].append((team[0], driver[0], driver[1]))

        for name in ordered_driver_lists[category]:
            for team_name in eligible_drivers[category]:
                if name[0] == team_name[1]:
                    ordered_team[category].append(team_name)

        for team in ordered_team[category]:
            if team[0] not in seen:
                no_duplicates.append({
                    "name": team[0],
                    "driver": team[1],
                    "points": team[2]
                })
                seen.append(team[0])
    return no_duplicates

def get_manufacturers_data():
    drivers = [driver[0] for driver in driver_championship.get_driver_class()]
    team_dict = defaultdict(list)
    with acLap.db_manager() as con:
        cur = con.cursor()
        cur.execute('SELECT name, drivers, points FROM teams_db')
        manu_data = cur.fetchall()

        for team in manu_data:
            for driver in drivers:
                if driver in team[1]:
                    team_dict[(team[0], team[2])].append(driver)

        result = [(team, tuple(drivers), number) for (team, number), drivers in team_dict.items()]
        
        manu_data = [list(item) for item in result]

        return manu_data
    
def check_if_teams_exist():
    teams_file = os.path.join(teams_path(), 'teams_config.json')
    if os.path.exists(teams_file):
        return True
    else:
        return False
    
def default_teams():
    return [
    {
        "name": "Alpine", 
        "drivers": ["Habsburg", "Schumacher"]
    },
    {
        "name": "Aston LMH", 
        "drivers": ["Gunn", "De Angelis"]
    },
    {
        "name": "BMW LMH", 
        "drivers": ["Magnussen", "Van der Linde"]
    },
    {
        "name": "Cadillac LMH", 
        "drivers": ["Nato", "Button"]
    },
    {
        "name": "Ferrari LMH", 
        "drivers": ["Fuoco", "Pier Guidi", "Kubica"]
    },
    {
        "name": "Porsche LMH", 
        "drivers": ["Christensen", "Vanthoor", "Pino"]
    },
    {
        "name": "Peugeot LMH", 
        "drivers": ["Jensen", "Jakobsen"]
    },
    {
        "name": "Toyota LMH", 
        "drivers": ["De Vries", "Buemi"]
    },
    {
        "name": "Aston GT3", 
        "drivers": ["Robichon", "Barrichello"]
    },
    {
        "name": "BMW GT3", 
        "drivers": ["Farfus", "Rossi"]
    },
    {
        "name": "Corvette", 
        "drivers": ["Edgar", "Andrade"]
    },
    {
        "name": "Ferrari GT3", 
        "drivers": ["Mann", "Castellacci"]
    },
    {
        "name": "Mustang GT3", 
        "drivers": ["Sousa", "Olsen"]
    },
    {
        "name": "Lexus GT3", 
        "drivers": ["Robin", "Schmid"]
    },
    {
        "name": "Mclaren GT3", 
        "drivers": ["Baud", "Gelael"]
    },
    {
        "name": "Mercedes GT3", 
        "drivers": ["Cressoni", "Martin"]
    },
    {
        "name": "Porsche GT3", 
        "drivers": ["Frey", "Pera"]
    }
]