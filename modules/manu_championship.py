import sqlite3
import modules.acLap as acLap
import json
import modules.driver_championship as driver_championship
from pathlib import Path
import re
import sys
import os

# gets the raw data from the teams.json file

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
    

# def get_teams_data():
#     project_root = Path(__file__).resolve().parent.parent
#     teams_path = project_root / 'config' / 'teams.json'
#     with open(teams_path, 'r') as n:
#         return json.load(n)

# def get_teams_data():
#     teams_path = acLap.path_to_files('config/teams.json')
#     with open(teams_path, 'r') as n:
#         return json.load(n)
    
# uses the data from the teams.json file to create and populate the teams database
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
    
# Gets a list of teams and its drivers and uses ordernate_position() to check which driver from the team finished first.
# As per WEC rules, teams only get rewarded points for the driver on the better position.
def set_eligible_drivers(race_result):
    teams = get_teams()
    ordered_driver_lists = driver_championship.arrange_driver_position(race_result)

    eligible_drivers = [[],[]]

    # Populates the 2 driver lists with tuples based on the driver with the best position on each team.
    for category in range(len(ordered_driver_lists)):
        for team in teams:
            for driver in ordered_driver_lists[category]:
                if driver in team[1]:
                    eligible_drivers[category].append([team[0], driver])
                    continue
    
    return eligible_drivers

# This function creates a list of dicts with the keys 'team', 'driver' and 'points', based on the eligible driver for points on a team;
# And how many points he scored on a the last race;
def assign_team_points(ordered_position, teams, points: list) -> list:
    team_driver_points = []
    point_itr = 0
    # ordered_position is a list of lists where [0] is a list of GT3 drivers and [1] is a list of LMH drivers.
    for category in range(len(ordered_position)):
        # Loops through all the drivers in the category.
        for driver in ordered_position[category]:
            # Loops through all the teams in their respective category.
            for team in teams[category]:
                # If a driver on the list of eligible drivers is on a team, it appends to the dict all the necessary info.
                if driver == team[1]:
                    team_driver_points.append({
                        "name": team[0],
                        "driver": driver,
                        "points": points[point_itr]
                    })
            # This iterator is exclusive to the points list because in WEC teams/drivers get awarded points based on their class standing not overall standing;
            if point_itr >= len(teams[category]):
                point_itr = 0
            else:
                point_itr += 1
    return team_driver_points

def get_manufacturers_data():
    with acLap.db_manager() as con:
        cur = con.cursor()
        cur.execute('SELECT name, drivers, points FROM teams_db')
        manu_data = cur.fetchall()
        manu_data = [list(item) for item in manu_data]
        for team in manu_data:
            team[1] = re.sub("(\[|\]|')", '', team[1])
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